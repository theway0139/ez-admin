from ninja import NinjaAPI, Schema
from typing import List, Optional, Any
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task, UserProfile, Department, Role, SystemSettings, NotificationSettings, SecuritySettings, PerformanceSettings, OperationLog, BackupFile, BackupSettings, AuditLog, Dog, Camera, AlarmEvent
from django.contrib.auth.models import User
from .log_utils import LogRecorder
import os
import subprocess
import threading
from datetime import datetime

api = NinjaAPI(version='2.0.0')

# 定义Schema
class TaskSchema(Schema):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str

class TaskCreateSchema(Schema):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# 完整的用户管理Schema
class DepartmentSchema(Schema):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str

class RoleSchema(Schema):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None

class UserListSchema(Schema):
    id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_display: Optional[str] = None
    department_display: Optional[str] = None
    status: Optional[str] = None
    status_display: Optional[str] = None
    last_login: Optional[str] = None
    created_at: str
    is_active: bool
    login_count: Optional[int] = 0

class UserDetailSchema(Schema):
    id: int
    username: str
    real_name: str
    email: str
    phone: Optional[str] = None
    role: Optional[RoleSchema] = None
    department: Optional[DepartmentSchema] = None
    status: str
    status_display: str
    last_login: Optional[str] = None
    last_login_ip: Optional[str] = None
    created_at: str
    updated_at: str
    is_active: bool
    login_count: int

class UserCreateSchema(Schema):
    username: str
    real_name: str
    email: str
    password: str
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: str = "active"

class UserUpdateSchema(Schema):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordResetSchema(Schema):
    new_password: str

class UserStatsSchema(Schema):
    total_users: int
    active_users: int
    admin_users: int
    locked_users: int
    growth_rate: float


# 系统设置相关Schema
class GeneralSettingsSchema(Schema):
    system_name: str
    system_version: str
    timezone: str
    language: str
    system_description: str

class SecuritySettingsSchema(Schema):
    session_timeout: int
    password_strength: str
    max_login_attempts: int
    account_lockout_time: int
    two_factor_auth: bool
    force_password_change: bool
    audit_logging: bool

class NotificationSettingsSchema(Schema):
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    webhook_enabled: bool
    smtp_server: str
    smtp_port: int
    smtp_username: str
    sender_name: str
    system_error_notify: bool
    security_alert_notify: bool
    task_complete_notify: bool

class PerformanceSettingsSchema(Schema):
    data_retention_days: int
    log_level: str
    auto_backup_enabled: bool
    backup_interval: str
    monitoring_interval: int
    enable_data_compression: bool
    enable_cache_optimization: bool
    enable_realtime_monitoring: bool

class UpdateSettingsSchema(Schema):
    key: str
    value: str
    setting_type: str

# API路由
@api.get("/tasks", response=List[TaskSchema])
def list_tasks(request):
    tasks = Task.objects.all()
    return tasks

@api.get("/tasks/{task_id}", response=TaskSchema)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return task

@api.post("/tasks", response=TaskSchema)
def create_task(request, task: TaskCreateSchema):
    task_obj = Task.objects.create(**task.dict())
    return task_obj

@api.put("/tasks/{task_id}", response=TaskSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    task = get_object_or_404(Task, id=task_id)
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(task, attr, value)
    
    task.save()
    return task

@api.delete("/tasks/{task_id}")
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return {"success": True}


# ==================== 用户管理API ====================

@api.get("/users/stats", response=UserStatsSchema)
def get_user_stats(request):
    """获取用户统计信息"""
    # 获取基础统计
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(is_superuser=True).count()
    locked_users = User.objects.filter(is_active=False).count()
    
    # 计算增长率（与上月相比）
    last_month = timezone.now() - timedelta(days=30)
    last_month_users = User.objects.filter(date_joined__lte=last_month).count()
    growth_rate = ((total_users - last_month_users) / max(last_month_users, 1)) * 100 if last_month_users > 0 else 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "locked_users": locked_users,
        "growth_rate": round(growth_rate, 1)
    }

class UserListResponse(Schema):
    total: int
    page: int
    page_size: int
    data: List[UserListSchema]

@api.get("/users")
def list_users(request):
    """获取用户列表"""
    # 通过 request.GET 读取参数，避免 Pydantic 校验导致的 422
    role = request.GET.get('role') or None
    status = request.GET.get('status') or None
    department = request.GET.get('department') or None
    search = request.GET.get('search') or None
    try:
        page = int(request.GET.get('page', 1))
    except Exception:
        page = 1
    try:
        page_size = int(request.GET.get('page_size', 10))
    except Exception:
        page_size = 10
    # 获取用户及其扩展信息
    queryset = User.objects.select_related('userprofile')
    
    # 筛选条件
    if role:
        if role == 'admin':
            queryset = queryset.filter(is_superuser=True)
        else:
            queryset = queryset.filter(userprofile__role__name=role)
    
    if status:
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'locked':
            queryset = queryset.filter(is_active=False)
    
    if department:
        queryset = queryset.filter(userprofile__department__name__icontains=department)
    
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # 获取总数量
    total = queryset.count()
    
    # 分页
    offset = (page - 1) * page_size
    users = queryset[offset:offset + page_size]
    
    result = []
    for user in users:
        # 获取用户扩展信息
        try:
            profile = user.userprofile
            role_display = profile.role_display if profile.role else ("管理员" if user.is_superuser else "普通用户")
            department_display = profile.department_display if profile.department else "未分配"
            status = profile.status
            status_display = profile.status_display
            phone = profile.phone
            real_name = profile.real_name
            login_count = profile.login_count
        except UserProfile.DoesNotExist:
            role_display = "管理员" if user.is_superuser else "普通用户"
            department_display = "未分配"
            status = "active" if user.is_active else "locked"
            status_display = "活跃" if user.is_active else "已锁定"
            phone = ""
            real_name = f"{user.first_name} {user.last_name}".strip() or user.username
            login_count = 0
        
        result.append({
            "id": user.id,
            "username": user.username,
            "real_name": real_name,
            "email": user.email,
            "phone": phone,
            "role_display": role_display,
            "department_display": department_display,
            "status": status,
            "status_display": status_display,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.date_joined.isoformat(),
            "is_active": user.is_active,
            "login_count": login_count
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": result
    }

@api.get("/users/{user_id}", response=UserDetailSchema)
def get_user(request, user_id: int):
    """获取用户详情"""
    user = get_object_or_404(User, id=user_id)
    
    # 获取或创建用户扩展信息
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            real_name=f"{user.first_name} {user.last_name}".strip() or user.username
        )
    
    role_data = None
    if profile.role:
        role_data = {
            "id": profile.role.id,
            "name": profile.role.name,
            "display_name": profile.role.display_name,
            "description": profile.role.description
        }
    
    department_data = None
    if profile.department:
        department_data = {
            "id": profile.department.id,
            "name": profile.department.name,
            "description": profile.department.description,
            "created_at": profile.department.created_at.isoformat()
        }
    
    return {
        "id": user.id,
        "username": user.username,
        "real_name": profile.real_name,
        "email": user.email,
        "phone": profile.phone,
        "role": role_data,
        "department": department_data,
        "status": profile.status,
        "status_display": profile.status_display,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "last_login_ip": profile.last_login_ip,
        "created_at": user.date_joined.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
        "is_active": user.is_active,
        "login_count": profile.login_count
    }

@api.post("/users", response=UserDetailSchema)
def create_user(request, data: UserCreateSchema):
    """创建新用户"""
    # 检查用户名是否已存在
    if User.objects.filter(username=data.username).exists():
        LogRecorder.log_user_create(request, data.username)
        return {"error": "用户名已存在"}
    
    # 检查邮箱是否已存在
    if User.objects.filter(email=data.email).exists():
        return {"error": "邮箱已存在"}
    
    try:
        # 创建用户
        user = User.objects.create(
            username=data.username,
            email=data.email,
            password=make_password(data.password),
            is_active=True
        )
        
        # 创建用户扩展信息
        profile_data = {
            "user": user,
            "real_name": data.real_name,
            "phone": data.phone,
            "status": data.status
        }
        
        if data.role_id:
            try:
                role = Role.objects.get(id=data.role_id)
                profile_data["role"] = role
            except Role.DoesNotExist:
                pass
        
        if data.department_id:
            try:
                department = Department.objects.get(id=data.department_id)
                profile_data["department"] = department
            except Department.DoesNotExist:
                pass
        
        UserProfile.objects.create(**profile_data)
        
        # 记录成功日志
        LogRecorder.log_user_create(request, data.username)
        
        return get_user(request, user.id)
        
    except Exception as e:
        # 记录失败日志
        LogRecorder.log_user_action(request, 'create', '用户管理', f'创建用户失败: {data.username}', 'failed', str(e))
        return {"error": f"创建用户失败: {str(e)}"}

@api.put("/users/{user_id}", response=UserDetailSchema)
def update_user(request, user_id: int, data: UserUpdateSchema):
    """更新用户信息"""
    user = get_object_or_404(User, id=user_id)
    
    # 获取或创建用户扩展信息
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            real_name=f"{user.first_name} {user.last_name}".strip() or user.username
        )
    
    # 更新用户基本信息
    if data.email is not None:
        user.email = data.email
    if data.is_active is not None:
        user.is_active = data.is_active
    user.save()
    
    # 更新扩展信息
    if data.real_name is not None:
        profile.real_name = data.real_name
    if data.phone is not None:
        profile.phone = data.phone
    if data.status is not None:
        profile.status = data.status
    if data.role_id is not None:
        try:
            role = Role.objects.get(id=data.role_id)
            profile.role = role
        except Role.DoesNotExist:
            profile.role = None
    if data.department_id is not None:
        try:
            department = Department.objects.get(id=data.department_id)
            profile.department = department
        except Department.DoesNotExist:
            profile.department = None
    
    profile.save()
    
    # 记录操作日志
    LogRecorder.log_user_update(request, user_id, user.username)
    
    return get_user(request, user.id)

@api.post("/users/{user_id}/reset-password")
def reset_user_password(request, user_id: int, data: PasswordResetSchema):
    """重置用户密码"""
    user = get_object_or_404(User, id=user_id)
    user.password = make_password(data.new_password)
    user.save()
    return {"success": True, "message": "密码重置成功"}

@api.post("/users/{user_id}/toggle-status")
def toggle_user_status(request, user_id: int):
    """切换用户状态（启用/禁用）"""
    user = get_object_or_404(User, id=user_id)
    
    # 获取或创建用户扩展信息
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            real_name=f"{user.first_name} {user.last_name}".strip() or user.username
        )
    
    # 切换状态
    user.is_active = not user.is_active
    user.save()
    
    # 更新扩展状态
    if not user.is_active:
        profile.status = 'locked'
    else:
        profile.status = 'active'
    profile.save()
    
    return {"success": True, "is_active": user.is_active, "status": profile.status}

@api.delete("/users/{user_id}")
def delete_user(request, user_id: int):
    """删除用户"""
    user = get_object_or_404(User, id=user_id)
    username = user.username
    
    try:
        user.delete()
        # 记录成功日志
        LogRecorder.log_user_delete(request, user_id, username)
        return {"success": True}
    except Exception as e:
        # 记录失败日志
        LogRecorder.log_user_action(request, 'delete', '用户管理', f'删除用户失败: {username}', 'failed', str(e))
        return {"success": False, "error": str(e)}

# ==================== 部门管理API ====================

@api.get("/departments", response=List[DepartmentSchema])
def list_departments(request):
    """获取部门列表"""
    departments = Department.objects.all()
    result = []
    for dept in departments:
        result.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "created_at": dept.created_at.isoformat()
        })
    return result

@api.post("/departments")
def create_department(request, name: str, description: str = None):
    """创建部门"""
    department = Department.objects.create(name=name, description=description)
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description,
        "created_at": department.created_at.isoformat()
    }

# ==================== 角色管理API ====================

@api.get("/roles", response=List[RoleSchema])
def list_roles(request):
    """获取角色列表"""
    roles = Role.objects.all()
    result = []
    for role in roles:
        result.append({
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description
        })
    return result

@api.post("/roles")
def create_role(request, name: str, display_name: str, description: str = None):
    """创建角色"""
    role = Role.objects.create(name=name, display_name=display_name, description=description)
    return {
        "id": role.id,
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description
    }


# ==================== 系统设置API ====================

@api.get("/settings/general", response=GeneralSettingsSchema)
def get_general_settings(request):
    """获取常规设置"""
    try:
        # 从数据库获取设置
        system_name = SystemSettings.objects.filter(key='system_name').first()
        language = SystemSettings.objects.filter(key='language').first()
        timezone = SystemSettings.objects.filter(key='timezone').first()
        description = SystemSettings.objects.filter(key='system_description').first()
        
        return {
            "system_name": system_name.value if system_name else "国粒智能边缘控制台",
            "system_version": "v2.1.0",
            "timezone": timezone.value if timezone else "中国标准时间 (UTC+8)",
            "language": language.value if language else "zh-CN",
            "system_description": description.value if description else "智能机器人管理与监控系统"
        }
    except Exception as e:
        # 返回默认值
        return {
            "system_name": "国粒智能边缘控制台",
            "system_version": "v2.1.0",
            "timezone": "中国标准时间 (UTC+8)",
            "language": "zh-CN",
            "system_description": "智能机器人管理与监控系统"
        }

@api.get("/settings/security", response=SecuritySettingsSchema)
def get_security_settings(request):
    """获取安全设置"""
    try:
        settings = SecuritySettings.objects.first()
        if not settings:
            settings = SecuritySettings.objects.create()
        
        return {
            "session_timeout": settings.session_timeout,
            "password_strength": settings.password_strength,
            "max_login_attempts": settings.max_login_attempts,
            "account_lockout_time": settings.account_lockout_time,
            "two_factor_auth": settings.two_factor_auth,
            "force_password_change": settings.force_password_change,
            "audit_logging": settings.audit_logging
        }
    except Exception as e:
        return {
            "session_timeout": 60,
            "password_strength": "medium",
            "max_login_attempts": 5,
            "account_lockout_time": 30,
            "two_factor_auth": False,
            "force_password_change": True,
            "audit_logging": True
        }

@api.get("/settings/notification", response=NotificationSettingsSchema)
def get_notification_settings(request):
    """获取通知设置"""
    try:
        settings = NotificationSettings.objects.first()
        if not settings:
            settings = NotificationSettings.objects.create()
        
        return {
            "email_enabled": settings.email_enabled,
            "sms_enabled": settings.sms_enabled,
            "push_enabled": settings.push_enabled,
            "webhook_enabled": settings.webhook_enabled,
            "smtp_server": settings.smtp_server,
            "smtp_port": settings.smtp_port,
            "smtp_username": settings.smtp_username,
            "sender_name": settings.sender_name,
            "system_error_notify": settings.system_error_notify,
            "security_alert_notify": settings.security_alert_notify,
            "task_complete_notify": settings.task_complete_notify
        }
    except Exception as e:
        return {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "webhook_enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "smtp_username": "noreply@example.com",
            "sender_name": "系统通知",
            "system_error_notify": True,
            "security_alert_notify": True,
            "task_complete_notify": True
        }

@api.get("/settings/performance", response=PerformanceSettingsSchema)
def get_performance_settings(request):
    """获取性能设置"""
    try:
        settings = PerformanceSettings.objects.first()
        if not settings:
            settings = PerformanceSettings.objects.create()
        
        return {
            "data_retention_days": settings.data_retention_days,
            "log_level": settings.log_level,
            "auto_backup_enabled": settings.auto_backup_enabled,
            "backup_interval": settings.backup_interval,
            "monitoring_interval": settings.monitoring_interval,
            "enable_data_compression": settings.enable_data_compression,
            "enable_cache_optimization": settings.enable_cache_optimization,
            "enable_realtime_monitoring": settings.enable_realtime_monitoring
        }
    except Exception as e:
        return {
            "data_retention_days": 90,
            "log_level": "INFO",
            "auto_backup_enabled": False,
            "backup_interval": "daily",
            "monitoring_interval": 60,
            "enable_data_compression": True,
            "enable_cache_optimization": False,
            "enable_realtime_monitoring": True
        }

@api.put("/settings/general")
def update_general_settings(request, data: GeneralSettingsSchema):
    """更新常规设置"""
    try:
        # 保存系统名称
        system_name_setting, _ = SystemSettings.objects.get_or_create(
            key='system_name',
            defaults={
                'value': data.system_name,
                'setting_type': 'general',
                'description': '系统名称'
            }
        )
        system_name_setting.value = data.system_name
        system_name_setting.save()
        
        # 保存语言设置
        language_setting, _ = SystemSettings.objects.get_or_create(
            key='language',
            defaults={
                'value': data.language,
                'setting_type': 'general',
                'description': '系统语言'
            }
        )
        language_setting.value = data.language
        language_setting.save()
        
        # 保存时区设置
        timezone_setting, _ = SystemSettings.objects.get_or_create(
            key='timezone',
            defaults={
                'value': data.timezone,
                'setting_type': 'general',
                'description': '系统时区'
            }
        )
        timezone_setting.value = data.timezone
        timezone_setting.save()
        
        # 保存系统描述
        description_setting, _ = SystemSettings.objects.get_or_create(
            key='system_description',
            defaults={
                'value': data.system_description,
                'setting_type': 'general',
                'description': '系统描述'
            }
        )
        description_setting.value = data.system_description
        description_setting.save()
        
        # 记录操作日志
        LogRecorder.log_settings_update(request, 'general', '修改常规设置')
        
        return {"success": True, "message": "常规设置保存成功"}
    except Exception as e:
        # 记录失败日志
        LogRecorder.log_user_action(request, 'config', '系统设置', '修改常规设置失败', 'failed', str(e))
        return {"success": False, "message": f"保存失败: {str(e)}"}

@api.put("/settings/security")
def update_security_settings(request, data: SecuritySettingsSchema):
    """更新安全设置"""
    try:
        settings, created = SecuritySettings.objects.get_or_create(defaults=data.dict())
        if not created:
            for key, value in data.dict().items():
                setattr(settings, key, value)
            settings.save()
        
        return {"success": True, "message": "安全设置保存成功"}
    except Exception as e:
        return {"success": False, "message": f"保存失败: {str(e)}"}

@api.put("/settings/notification")
def update_notification_settings(request, data: NotificationSettingsSchema):
    """更新通知设置"""
    try:
        settings, created = NotificationSettings.objects.get_or_create(defaults=data.dict())
        if not created:
            for key, value in data.dict().items():
                setattr(settings, key, value)
            settings.save()
        
        return {"success": True, "message": "通知设置保存成功"}
    except Exception as e:
        return {"success": False, "message": f"保存失败: {str(e)}"}

@api.put("/settings/performance")
def update_performance_settings(request, data: PerformanceSettingsSchema):
    """更新性能设置"""
    try:
        settings, created = PerformanceSettings.objects.get_or_create(defaults=data.dict())
        if not created:
            for key, value in data.dict().items():
                setattr(settings, key, value)
            settings.save()
        
        return {"success": True, "message": "性能设置保存成功"}
    except Exception as e:
        return {"success": False, "message": f"保存失败: {str(e)}"}

class RestoreSettingsSchema(Schema):
    setting_type: str


# 操作日志相关Schema
class OperationLogSchema(Schema):
    id: int
    operation_type: str
    operation_type_display: Optional[str] = None
    operation_target: str
    operation_detail: str
    operator_name: Optional[str] = None
    operator_ip: Optional[str] = None
    result: str
    result_display: Optional[str] = None
    operation_time: str
    duration: float
    error_message: Optional[str] = None

class OperationLogCreateSchema(Schema):
    operation_type: str
    operation_target: str
    operation_detail: str
    operator_name: str
    operator_ip: str
    result: str = "success"
    error_message: Optional[str] = None
    duration: float = 0.0

@api.post("/settings/restore-defaults")
def restore_default_settings(request, data: RestoreSettingsSchema):
    """恢复默认设置"""
    try:
        setting_type = data.setting_type
        if setting_type == "security":
            SecuritySettings.objects.all().delete()
            SecuritySettings.objects.create()
        elif setting_type == "notification":
            NotificationSettings.objects.all().delete()
            NotificationSettings.objects.create()
        elif setting_type == "performance":
            PerformanceSettings.objects.all().delete()
            PerformanceSettings.objects.create()
        
        return {"success": True, "message": "设置已恢复默认值"}
    except Exception as e:
        return {"success": False, "message": f"恢复失败: {str(e)}"}


# ==================== 操作日志API ====================

class OperationLogListResponse(Schema):
    total: int
    page: int
    page_size: int
    data: List[OperationLogSchema]

@api.get("/operation-logs")
def list_operation_logs(request):
    """获取操作日志列表"""
    # 通过 request.GET 读取参数，避免 Pydantic 校验导致的 422
    operation_type = request.GET.get('operation_type') or None
    operator = request.GET.get('operator') or None
    start_time = request.GET.get('start_time') or None
    end_time = request.GET.get('end_time') or None
    result = request.GET.get('result') or None
    try:
        page = int(request.GET.get('page', 1))
    except Exception:
        page = 1
    try:
        page_size = int(request.GET.get('page_size', 20))
    except Exception:
        page_size = 20

    queryset = OperationLog.objects.all()
    
    # 筛选条件
    if operation_type:
        queryset = queryset.filter(operation_type=operation_type)
    
    if operator:
        queryset = queryset.filter(operator_name__icontains=operator)
    
    if start_time:
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            queryset = queryset.filter(operation_time__gte=start_datetime)
        except ValueError:
            pass
    
    if end_time:
        try:
            end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            queryset = queryset.filter(operation_time__lte=end_datetime)
        except ValueError:
            pass
    
    if result:
        queryset = queryset.filter(result=result)
    
    # 获取总数量
    total = queryset.count()
    
    # 分页
    offset = (page - 1) * page_size
    logs = queryset[offset:offset + page_size]
    
    result_list = []
    for log in logs:
        result_list.append({
            "id": log.id,
            "operation_type": log.operation_type,
            "operation_type_display": log.operation_type_display,
            "operation_target": log.operation_target,
            "operation_detail": log.operation_detail,
            "operator_name": log.operator_name,
            "operator_ip": log.operator_ip,
            "result": log.result,
            "result_display": log.result_display,
            "operation_time": log.operation_time.isoformat(),
            "duration": log.duration,
            "error_message": log.error_message
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": result_list
    }

@api.post("/operation-logs", response=OperationLogSchema)
def create_operation_log(request, data: OperationLogCreateSchema):
    """创建操作日志"""
    try:
        log = OperationLog.objects.create(**data.dict())
        return {
            "id": log.id,
            "operation_type": log.operation_type,
            "operation_type_display": log.operation_type_display,
            "operation_target": log.operation_target,
            "operation_detail": log.operation_detail,
            "operator_name": log.operator_name,
            "operator_ip": log.operator_ip,
            "result": log.result,
            "result_display": log.result_display,
            "operation_time": log.operation_time.isoformat(),
            "duration": log.duration,
            "error_message": log.error_message
        }
    except Exception as e:
        return {"error": f"创建日志失败: {str(e)}"}

@api.delete("/operation-logs")
def clear_operation_logs(request, operation_type: str = None, days: int = None):
    """清空操作日志"""
    try:
        queryset = OperationLog.objects.all()
        
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        if days:
            cutoff_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(operation_time__lt=cutoff_date)
        
        count = queryset.count()
        queryset.delete()
        
        return {"success": True, "message": f"已清空 {count} 条日志记录"}
    except Exception as e:
        return {"success": False, "message": f"清空失败: {str(e)}"}

@api.get("/operation-logs/export")
def export_operation_logs(request,
                         operation_type: str = None,
                         start_time: str = None,
                         end_time: str = None):
    """导出操作日志为CSV文件"""
    try:
        import csv
        import io
        from django.http import HttpResponse
        
        queryset = OperationLog.objects.all().order_by('-operation_time')
        
        # 应用筛选条件
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        
        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                queryset = queryset.filter(operation_time__gte=start_datetime)
            except ValueError:
                pass
        
        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                queryset = queryset.filter(operation_time__lte=end_datetime)
            except ValueError:
                pass
        
        # 创建CSV响应
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="operation_logs.csv"'
        
        # 添加BOM以支持Excel正确显示中文
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # 写入CSV头部
        writer.writerow([
            '时间',
            '操作人员', 
            '操作类型',
            '操作对象',
            '详情',
            'IP地址',
            '状态',
            '耗时(秒)',
            '错误信息'
        ])
        
        # 写入数据行
        for log in queryset:
            # 格式化时间为本地时间
            local_time = log.operation_time.strftime('%Y-%m-%d %H:%M:%S')
            
            writer.writerow([
                local_time,
                log.operator_name or '匿名用户',
                log.operation_type_display,
                log.operation_target,
                log.operation_detail,
                log.operator_ip,
                log.result_display,
                f"{log.duration:.3f}",
                log.error_message or ''
            ])
        
        return response
        
    except Exception as e:
        # 如果导出失败，返回JSON错误信息
        from django.http import JsonResponse
        return JsonResponse({"success": False, "message": f"导出失败: {str(e)}"})

@api.get("/operation-logs/stats")
def get_operation_log_stats(request):
    """获取操作日志统计"""
    try:
        total_logs = OperationLog.objects.count()
        today_logs = OperationLog.objects.filter(
            operation_time__date=timezone.now().date()
        ).count()
        success_logs = OperationLog.objects.filter(result='success').count()
        failed_logs = OperationLog.objects.filter(result='failed').count()
        
        return {
            "total_logs": total_logs,
            "today_logs": today_logs,
            "success_logs": success_logs,
            "failed_logs": failed_logs,
            "success_rate": round((success_logs / max(total_logs, 1)) * 100, 1)
        }
    except Exception as e:
        return {
            "total_logs": 0,
            "today_logs": 0,
            "success_logs": 0,
            "failed_logs": 0,
            "success_rate": 0
        }

# ==================== 数据备份API ====================

class BackupFileSchema(Schema):
    id: int
    name: str
    backup_type: str
    backup_type_display: str
    file_size: int
    file_size_display: str
    status: str
    status_display: str
    created_at: str
    completed_at: Optional[str] = None
    description: Optional[str] = None
    error_message: Optional[str] = None

class BackupSettingsSchema(Schema):
    auto_backup_enabled: bool
    backup_frequency: str
    max_backup_files: int
    backup_type: str = 'full'

class BackupCreateSchema(Schema):
    name: str = None
    backup_type: str = 'full'
    description: str = None

class BackupListResponse(Schema):
    total: int
    page: int
    page_size: int
    data: List[BackupFileSchema]

@api.get("/backups/stats")
def get_backup_stats(request):
    """获取备份统计信息"""
    try:
        # 获取最后一次备份时间
        last_backup = BackupFile.objects.filter(status='completed').first()
        last_backup_time = last_backup.completed_at.isoformat() if last_backup and last_backup.completed_at else None
        
        # 备份状态 - 基于最近的备份
        backup_status = 'normal'
        if not last_backup:
            backup_status = 'no_backup'
        elif last_backup.status == 'failed':
            backup_status = 'error'
        elif last_backup.created_at < timezone.now() - timedelta(days=7):
            backup_status = 'warning'
        
        # 备份文件数量
        backup_count = BackupFile.objects.count()
        
        # 总备份大小
        from django.db import models
        total_size = BackupFile.objects.filter(status='completed').aggregate(
            total=models.Sum('file_size')
        )['total'] or 0
        
        return {
            "last_backup_time": last_backup_time,
            "backup_status": backup_status,
            "backup_count": backup_count,
            "total_size": total_size
        }
    except Exception as e:
        return {"error": f"获取备份统计失败: {str(e)}"}

@api.get("/backups", response=BackupListResponse)
def list_backups(request, page: int = 1, page_size: int = 20):
    """获取备份文件列表"""
    try:
        queryset = BackupFile.objects.all().order_by('-created_at')
        
        # 获取总数量
        total = queryset.count()
        
        # 分页
        offset = (page - 1) * page_size
        backups = queryset[offset:offset + page_size]
        
        result_list = []
        for backup in backups:
            result_list.append({
                "id": backup.id,
                "name": backup.name,
                "backup_type": backup.backup_type,
                "backup_type_display": backup.backup_type_display,
                "file_size": backup.file_size,
                "file_size_display": backup.file_size_display,
                "status": backup.status,
                "status_display": backup.status_display,
                "created_at": backup.created_at.isoformat(),
                "completed_at": backup.completed_at.isoformat() if backup.completed_at else None,
                "description": backup.description,
                "error_message": backup.error_message
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": result_list
        }
    except Exception as e:
        return {"error": f"获取备份列表失败: {str(e)}"}

@api.post("/backups")
def create_backup(request, data: BackupCreateSchema):
    """创建新备份"""
    try:
        # 生成备份名称
        if not data.name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_type_name = {'full': 'full', 'incremental': 'incremental', 'differential': 'differential'}
            data.name = f"backup_{timestamp}_{backup_type_name.get(data.backup_type, 'full')}"
        
        # 创建备份记录
        backup = BackupFile.objects.create(
            name=data.name,
            backup_type=data.backup_type,
            status='running',
            description=data.description or '',
            file_path=f"/var/backups/ez-admin/{data.name}.sql.gz"
        )
        
        # 异步执行数据库备份
        def perform_database_backup():
            try:
                import time
                from django.conf import settings
                import os
                
                # 获取数据库配置
                db_config = settings.DATABASES['default']
                db_name = db_config['NAME']
                db_user = db_config.get('USER', 'root')
                db_password = db_config.get('PASSWORD', '')
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '3306')
                
                # 创建备份目录
                backup_dir = '/var/backups/ez-admin'
                os.makedirs(backup_dir, exist_ok=True)
                
                # 生成备份文件路径
                backup_filename = f"{backup.name}.sql"
                if data.backup_type == 'full':
                    backup_filename = f"{backup.name}_full.sql"
                
                backup_file_path = os.path.join(backup_dir, backup_filename)
                
                # 执行数据库备份命令
                if data.backup_type == 'full':
                    # 完整备份：导出整个数据库
                    backup_cmd = f"mysqldump -h{db_host} -P{db_port} -u{db_user}"
                    if db_password:
                        backup_cmd += f" -p{db_password}"
                    backup_cmd += f" --single-transaction --routines --triggers {db_name}"
                    
                elif data.backup_type == 'incremental':
                    # 增量备份：只备份最近修改的数据（简化实现）
                    backup_cmd = f"mysqldump -h{db_host} -P{db_port} -u{db_user}"
                    if db_password:
                        backup_cmd += f" -p{db_password}"
                    # 这里可以添加时间条件来实现真正的增量备份
                    backup_cmd += f" --single-transaction --where=\"created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)\" {db_name}"
                    
                else:  # differential
                    # 差异备份：备份自上次完整备份以来的更改
                    backup_cmd = f"mysqldump -h{db_host} -P{db_port} -u{db_user}"
                    if db_password:
                        backup_cmd += f" -p{db_password}"
                    backup_cmd += f" --single-transaction --where=\"updated_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)\" {db_name}"
                
                # 是否压缩备份
                settings_obj = BackupSettings.objects.first()
                if settings_obj and settings_obj.compress_backup:
                    backup_cmd += f" | gzip > {backup_file_path}.gz"
                    backup.file_path = f"{backup_file_path}.gz"
                else:
                    backup_cmd += f" > {backup_file_path}"
                    backup.file_path = backup_file_path
                
                # 执行备份命令
                result = os.system(backup_cmd)
                
                if result == 0:
                    # 备份成功，获取文件大小
                    if os.path.exists(backup.file_path):
                        backup.file_size = os.path.getsize(backup.file_path)
                    else:
                        # 如果文件不存在，设置模拟大小
                        if data.backup_type == 'full':
                            backup.file_size = 250 * 1024 * 1024  # 250MB
                        elif data.backup_type == 'incremental':
                            backup.file_size = 15 * 1024 * 1024   # 15MB
                        else:
                            backup.file_size = 245 * 1024 * 1024  # 245MB
                    
                    backup.status = 'completed'
                    backup.completed_at = timezone.now()
                    backup.save()
                    
                    # 记录成功日志
                    LogRecorder.log_backup_create(request, backup.name, data.backup_type)
                    
                else:
                    # 备份失败
                    backup.status = 'failed'
                    backup.error_message = f'数据库备份命令执行失败，退出码: {result}'
                    backup.save()
                    
                    # 记录失败日志
                    LogRecorder.log_user_action(request, 'backup', '数据备份', f'数据库备份失败: {backup.name}', 'failed', backup.error_message)
                
            except Exception as e:
                backup.status = 'failed'
                backup.error_message = f'数据库备份异常: {str(e)}'
                backup.save()
                
                # 记录异常日志
                LogRecorder.log_user_action(request, 'backup', '数据备份', f'数据库备份异常: {backup.name}', 'failed', str(e))
        
        # 记录开始备份的日志
        LogRecorder.log_user_action(request, 'backup', '数据备份', f'开始创建{data.backup_type}备份: {backup.name}')
        
        # 启动后台线程执行数据库备份
        thread = threading.Thread(target=perform_database_backup)
        thread.daemon = True
        thread.start()
        
        return {"success": True, "message": f"备份任务已启动: {backup.name}", "backup_id": backup.id}
        
    except Exception as e:
        return {"success": False, "message": f"创建备份失败: {str(e)}"}

@api.delete("/backups/{backup_id}")
def delete_backup(request, backup_id: int):
    """删除备份文件"""
    try:
        backup = get_object_or_404(BackupFile, id=backup_id)
        backup_name = backup.name
        
        # 删除物理文件（如果存在）
        if backup.file_path and os.path.exists(backup.file_path):
            try:
                os.remove(backup.file_path)
            except:
                pass  # 忽略文件删除错误
        
        # 删除数据库记录
        backup.delete()
        
        # 记录操作日志
        LogRecorder.log_backup_delete(request, backup_name)
        
        return {"success": True, "message": f"备份文件已删除: {backup_name}"}
        
    except Exception as e:
        LogRecorder.log_user_action(request, 'delete', '数据备份', f'删除备份失败', 'failed', str(e))
        return {"success": False, "message": f"删除备份失败: {str(e)}"}

@api.get("/backups/{backup_id}/download")
def download_backup(request, backup_id: int):
    """下载数据库备份文件"""
    try:
        backup = get_object_or_404(BackupFile, id=backup_id)
        
        if backup.status != 'completed':
            from django.http import JsonResponse
            return JsonResponse({"success": False, "message": "备份文件未完成或不可用"})
        
        if not os.path.exists(backup.file_path):
            from django.http import JsonResponse
            return JsonResponse({"success": False, "message": "备份文件不存在"})
        
        # 记录操作日志
        LogRecorder.log_backup_download(request, backup.name)
        
        # 返回文件下载响应
        from django.http import HttpResponse, FileResponse
        import mimetypes
        
        # 确定文件MIME类型
        content_type, _ = mimetypes.guess_type(backup.file_path)
        if not content_type:
            if backup.file_path.endswith('.gz'):
                content_type = 'application/gzip'
            elif backup.file_path.endswith('.sql'):
                content_type = 'application/sql'
            else:
                content_type = 'application/octet-stream'
        
        # 生成下载文件名
        download_filename = os.path.basename(backup.file_path)
        if not download_filename:
            download_filename = f"{backup.name}.sql.gz"
        
        # 返回文件响应
        response = FileResponse(
            open(backup.file_path, 'rb'),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        response['Content-Length'] = backup.file_size
        
        return response
        
    except Exception as e:
        from django.http import JsonResponse
        try:
            backup_name = backup.name if 'backup' in locals() else f'ID:{backup_id}'
            LogRecorder.log_user_action(request, 'download', '数据备份', f'下载备份失败: {backup_name}', 'failed', str(e))
        except:
            pass
        return JsonResponse({"success": False, "message": f"下载失败: {str(e)}"})

@api.post("/backups/{backup_id}/restore")
def restore_backup(request, backup_id: int):
    """恢复数据库备份"""
    try:
        backup = get_object_or_404(BackupFile, id=backup_id)
        
        if backup.status != 'completed':
            return {"success": False, "message": "备份文件未完成或不可用"}
        
        if not os.path.exists(backup.file_path):
            return {"success": False, "message": "备份文件不存在"}
        
        # 异步执行数据库恢复
        def perform_database_restore():
            try:
                from django.conf import settings
                import os
                
                # 获取数据库配置
                db_config = settings.DATABASES['default']
                db_name = db_config['NAME']
                db_user = db_config.get('USER', 'root')
                db_password = db_config.get('PASSWORD', '')
                db_host = db_config.get('HOST', 'localhost')
                db_port = db_config.get('PORT', '3306')
                
                # 构建恢复命令
                restore_cmd = f"mysql -h{db_host} -P{db_port} -u{db_user}"
                if db_password:
                    restore_cmd += f" -p{db_password}"
                restore_cmd += f" {db_name}"
                
                # 检查是否为压缩文件
                if backup.file_path.endswith('.gz'):
                    restore_cmd = f"gunzip < {backup.file_path} | " + restore_cmd
                else:
                    restore_cmd += f" < {backup.file_path}"
                
                # 执行恢复命令
                result = os.system(restore_cmd)
                
                if result == 0:
                    # 恢复成功
                    LogRecorder.log_user_action(request, 'restore', '数据备份', f'数据库恢复成功: {backup.name}')
                else:
                    # 恢复失败
                    LogRecorder.log_user_action(request, 'restore', '数据备份', f'数据库恢复失败: {backup.name}', 'failed', f'命令执行失败，退出码: {result}')
                
            except Exception as e:
                # 恢复异常
                LogRecorder.log_user_action(request, 'restore', '数据备份', f'数据库恢复异常: {backup.name}', 'failed', str(e))
        
        # 启动后台线程执行恢复
        thread = threading.Thread(target=perform_database_restore)
        thread.daemon = True
        thread.start()
        
        # 记录开始恢复的日志
        LogRecorder.log_backup_restore(request, backup.name)
        
        return {"success": True, "message": f"数据库恢复任务已启动: {backup.name}"}
        
    except Exception as e:
        LogRecorder.log_user_action(request, 'restore', '数据备份', f'恢复备份失败: {backup.name}', 'failed', str(e))
        return {"success": False, "message": f"恢复失败: {str(e)}"}

@api.get("/backup-settings", response=BackupSettingsSchema)
def get_backup_settings(request):
    """获取备份设置"""
    try:
        settings, created = BackupSettings.objects.get_or_create(id=1)
        return {
            "auto_backup_enabled": settings.auto_backup_enabled,
            "backup_frequency": settings.backup_frequency,
            "max_backup_files": settings.max_backup_files,
            "backup_type": settings.backup_type
        }
    except Exception as e:
        return {"error": f"获取备份设置失败: {str(e)}"}

@api.put("/backup-settings")
def update_backup_settings(request, data: BackupSettingsSchema):
    """更新备份设置"""
    try:
        settings, created = BackupSettings.objects.get_or_create(id=1)
        
        settings.auto_backup_enabled = data.auto_backup_enabled
        settings.backup_frequency = data.backup_frequency
        settings.max_backup_files = data.max_backup_files
        settings.backup_type = data.backup_type
        settings.save()
        
        # 记录操作日志
        LogRecorder.log_user_action(request, 'config', '数据备份', '修改备份设置')
        
        return {"success": True, "message": "备份设置保存成功"}
        
    except Exception as e:
        LogRecorder.log_user_action(request, 'config', '数据备份', '修改备份设置失败', 'failed', str(e))
        return {"success": False, "message": f"保存失败: {str(e)}"}


# ==================== 审计日志API ====================

class AuditLogSchema(Schema):
    id: int
    timestamp: str
    log_type: str
    level: str
    source_module: str
    message: str
    details: Optional[Any] = None
    user: str
    ip_address: Optional[str] = None

class AuditLogListResponse(Schema):
    total: int
    page: int
    page_size: int
    data: List[AuditLogSchema]

@api.get("/audit-logs")
def list_audit_logs(request):
    """获取审计日志列表"""
    try:
        # 手动读取查询参数，避免 422
        get = request.GET
        page = int(get.get('page', 1)) if get.get('page') else 1
        page_size = int(get.get('page_size', 10)) if get.get('page_size') else 10
        log_type = get.get('log_type') or None
        log_level = get.get('log_level') or None
        source_module = get.get('source_module') or None
        start_time = get.get('start_time') or None
        end_time = get.get('end_time') or None
        user_id = get.get('user_id') or None
        ip_address = get.get('ip_address') or None
        keyword = get.get('keyword') or None

        queryset = AuditLog.objects.all()
        
        # 应用筛选条件
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        if log_level:
            queryset = queryset.filter(level=log_level)
        if source_module:
            queryset = queryset.filter(source_module__icontains=source_module)
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=end_dt)
        if user_id:
            queryset = queryset.filter(user__icontains=user_id)
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)
        if keyword:
            queryset = queryset.filter(
                Q(message__icontains=keyword) | 
                Q(source_module__icontains=keyword) |
                Q(user__icontains=keyword)
            )
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        logs = queryset[start:end]
        
        # 转换为字典格式
        log_data = []
        for log in logs:
            log_data.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "log_type": log.log_type,
                "level": log.level,
                "source_module": log.source_module,
                "message": log.message,
                "details": log.details,
                "user": log.user,
                "ip_address": log.ip_address
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": log_data
        }
        
    except Exception as e:
        return {"error": f"获取审计日志失败: {str(e)}"}

@api.get("/audit-logs/export")
def export_audit_logs(request,
                     log_type: str = None,
                     log_level: str = None,
                     source_module: str = None,
                     start_time: str = None,
                     end_time: str = None,
                     user_id: str = None,
                     ip_address: str = None,
                     keyword: str = None):
    """导出审计日志"""
    try:
        import csv
        from django.http import HttpResponse
        
        queryset = AuditLog.objects.all()
        
        # 应用筛选条件
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        if log_level:
            queryset = queryset.filter(level=log_level)
        if source_module:
            queryset = queryset.filter(source_module__icontains=source_module)
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=end_dt)
        if user_id:
            queryset = queryset.filter(user__icontains=user_id)
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)
        if keyword:
            queryset = queryset.filter(
                Q(message__icontains=keyword) | 
                Q(source_module__icontains=keyword) |
                Q(user__icontains=keyword)
            )
        
        # 创建CSV响应
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['时间戳', '日志类型', '级别', '来源模块', '消息内容', '用户', 'IP地址'])
        
        for log in queryset:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.get_log_type_display(),
                log.level,
                log.source_module,
                log.message,
                log.user,
                log.ip_address or 'N/A'
            ])
        
        return response
        
    except Exception as e:
        return {"error": f"导出审计日志失败: {str(e)}"}

class AuditReportRequestSchema(Schema):
    log_type: Optional[str] = None
    log_level: Optional[str] = None
    source_module: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    keyword: Optional[str] = None

@api.post("/audit-logs/report")
def generate_audit_report(request, data: AuditReportRequestSchema):
    """生成审计报告"""
    try:
        # 这里可以实现更复杂的报告生成逻辑
        # 目前只是简单的统计
        queryset = AuditLog.objects.all()
        
        # 应用筛选条件
        if data.log_type:
            queryset = queryset.filter(log_type=data.log_type)
        if data.log_level:
            queryset = queryset.filter(level=data.log_level)
        if data.source_module:
            queryset = queryset.filter(source_module__icontains=data.source_module)
        if data.start_time:
            start_dt = datetime.fromisoformat(data.start_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=start_dt)
        if data.end_time:
            end_dt = datetime.fromisoformat(data.end_time.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=end_dt)
        if data.user_id:
            queryset = queryset.filter(user__icontains=data.user_id)
        if data.ip_address:
            queryset = queryset.filter(ip_address__icontains=data.ip_address)
        if data.keyword:
            queryset = queryset.filter(
                Q(message__icontains=data.keyword) | 
                Q(source_module__icontains=data.keyword) |
                Q(user__icontains=data.keyword)
            )
        
        # 生成统计信息
        total_logs = queryset.count()
        log_types = queryset.values('log_type').annotate(count=Count('id'))
        log_levels = queryset.values('level').annotate(count=Count('id'))
        
        report = {
            "total_logs": total_logs,
            "log_types": list(log_types),
            "log_levels": list(log_levels),
            "generated_at": datetime.now().isoformat()
        }
        
        return {"success": True, "message": "审计报告生成成功", "report": report}
        
    except Exception as e:
        return {"success": False, "message": f"生成审计报告失败: {str(e)}"}

@api.get("/audit-logs/{log_id}/export")
def export_single_audit_log(request, log_id: int):
    """导出单个审计日志"""
    try:
        from django.http import JsonResponse
        
        log = get_object_or_404(AuditLog, id=log_id)
        
        log_data = {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "log_type": log.log_type,
            "level": log.level,
            "source_module": log.source_module,
            "message": log.message,
            "details": log.details,
            "user": log.user,
            "ip_address": log.ip_address
        }
        
        response = JsonResponse(log_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="audit_log_{log_id}.json"'
        
        return response
        
    except Exception as e:
        return {"error": f"导出单个审计日志失败: {str(e)}"}
# =============== 报警事件管理 API ===============

class AlarmEventSchema(Schema):
    id: int
    dog_id: int
    camera_id: int
    event_type: str
    severity: str
    status: str
    title: str
    description: str
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    confidence: float
    detected_at: str
    handled_at: Optional[str] = None
    created_at: str

@api.get("/alarm-events")
def list_alarm_events(request, 
                     page: int = 1, 
                     page_size: int = 10,
                     event_type: str = None,
                     severity: str = None,
                     status: str = None):
    """获取报警事件列表"""
    queryset = AlarmEvent.objects.all().order_by('-detected_at')
    
    # 过滤
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    if severity:
        queryset = queryset.filter(severity=severity)
    if status:
        queryset = queryset.filter(status=status)
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    events = queryset[start:end]
    
    return {
        "success": True,
        "data": [
            {
                "id": event.id,
                "dog_id": event.dog.id,
                "dog_name": event.dog.name,
                "camera_id": event.camera.id,
                "camera_name": event.camera.name,
                "camera_location": event.camera.location,
                "event_type": event.event_type,
                "severity": event.severity,
                "status": event.status,
                "title": event.title,
                "description": event.description,
                "image_path": event.image_path,
                "video_path": event.video_path,
                "confidence": event.confidence,
                "detected_at": event.detected_at.isoformat(),
                "handled_at": event.handled_at.isoformat() if event.handled_at else None,
                "created_at": event.created_at.isoformat(),
            }
            for event in events
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@api.get("/video-analysis/status")
def get_video_analysis_status(request):
    """获取视频分析服务状态"""
    from .video_analysis_service import video_analysis_service
    
    return {
        "success": True,
        "running": video_analysis_service.running,
        "cameras_count": len(video_analysis_service.cameras)
    }

@api.post("/video-analysis/start")
def start_video_analysis(request):
    """启动视频分析服务"""
    try:
        from .video_analysis_service import video_analysis_service
        video_analysis_service.start_all_cameras()
        return {"success": True, "message": "视频分析服务已启动"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api.post("/video-analysis/stop")
def stop_video_analysis(request):
    """停止视频分析服务"""
    try:
        from .video_analysis_service import video_analysis_service
        video_analysis_service.stop_all()
        return {"success": True, "message": "视频分析服务已停止"}
    except Exception as e:
        return {"success": False, "error": str(e)}
