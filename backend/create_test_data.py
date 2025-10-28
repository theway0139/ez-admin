#!/usr/bin/env python
"""
创建测试数据脚本
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from ops.models import (
    UserProfile, Department, Role, SystemSettings, NotificationSettings, 
    SecuritySettings, PerformanceSettings, OperationLog, BackupFile, 
    BackupSettings, AuditLog
)

def create_test_data():
    print("开始创建测试数据...")
    
    # 创建部门
    departments = [
        {'name': '技术部', 'description': '负责技术开发'},
        {'name': '产品部', 'description': '负责产品设计'},
        {'name': '运营部', 'description': '负责运营推广'},
        {'name': '人事部', 'description': '负责人事管理'},
    ]
    
    dept_objects = []
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        dept_objects.append(dept)
        print(f"创建部门: {dept.name}")
    
    # 创建角色
    roles = [
        {'name': 'admin', 'display_name': '系统管理员', 'description': '系统管理员'},
        {'name': 'manager', 'display_name': '部门经理', 'description': '部门经理'},
        {'name': 'employee', 'display_name': '普通员工', 'description': '普通员工'},
        {'name': 'guest', 'display_name': '访客', 'description': '访客用户'},
    ]
    
    role_objects = []
    for role_data in roles:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'display_name': role_data['display_name'],
                'description': role_data['description']
            }
        )
        role_objects.append(role)
        print(f"创建角色: {role.display_name}")
    
    # 创建用户
    users_data = [
        {'username': 'admin', 'email': 'admin@example.com', 'first_name': '管理员', 'last_name': '系统'},
        {'username': 'zhangsan', 'email': 'zhangsan@example.com', 'first_name': '三', 'last_name': '张'},
        {'username': 'lisi', 'email': 'lisi@example.com', 'first_name': '四', 'last_name': '李'},
        {'username': 'wangwu', 'email': 'wangwu@example.com', 'first_name': '五', 'last_name': '王'},
        {'username': 'zhaoliu', 'email': 'zhaoliu@example.com', 'first_name': '六', 'last_name': '赵'},
    ]
    
    for i, user_data in enumerate(users_data):
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': i == 0,  # 第一个用户是管理员
                'is_superuser': i == 0,
            }
        )
        if created:
            user.set_password('123456')
            user.save()
        
        # 创建用户档案
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'real_name': f"{user_data['last_name']}{user_data['first_name']}",
                'department': random.choice(dept_objects),
                'role': role_objects[0] if i == 0 else random.choice(role_objects[1:]),
                'phone': f'138{random.randint(10000000, 99999999)}',
                'status': 'active' if random.random() > 0.2 else 'inactive',
                'login_count': random.randint(0, 100),
            }
        )
        print(f"创建用户: {user.username}")
    
    # 创建系统设置
    SystemSettings.objects.get_or_create(
        key='site_name',
        defaults={'value': '管理系统', 'description': '网站名称'}
    )
    SystemSettings.objects.get_or_create(
        key='site_description',
        defaults={'value': '企业管理系统', 'description': '网站描述'}
    )
    
    # 创建备份设置
    BackupSettings.objects.get_or_create(
        defaults={
            'auto_backup_enabled': True,
            'backup_frequency': 'daily',
            'max_backup_files': 30,
            'backup_type': 'full',
        }
    )
    
    # 创建一些操作日志
    operation_types = ['login', 'logout', 'create', 'update', 'delete', 'backup', 'restore', 'config']
    operation_targets = ['用户管理', '系统设置', '数据备份', '权限管理', '任务调度']
    
    for i in range(50):
        OperationLog.objects.create(
            operation_type=random.choice(operation_types),
            operation_target=random.choice(operation_targets),
            operation_detail=f"操作详情 {i}",
            operator=User.objects.first(),
            operator_name=f"操作员_{random.randint(1, 5)}",
            operator_ip=f"192.168.1.{random.randint(1, 255)}",
            result=random.choice(['success', 'failed', 'warning']),
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            operation_time=datetime.now() - timedelta(days=random.randint(0, 30))
        )
    
    # 创建一些审计日志
    audit_operations = [
        '系统启动', '用户认证', '数据访问', '配置修改', '安全事件'
    ]
    
    for i in range(30):
        AuditLog.objects.create(
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
            log_type=random.choice(['system', 'security', 'user', 'application']),
            level=random.choice(['INFO', 'WARNING', 'ERROR']),
            source_module=random.choice(['auth', 'database', 'api', 'frontend']),
            message=f"审计日志消息 {i}",
            details=f"详细信息 {i}",
            user=f"user_{random.randint(1, 5)}",
            ip_address=f"192.168.1.{random.randint(1, 255)}"
        )
    
    print("测试数据创建完成！")
    print(f"用户数量: {User.objects.count()}")
    print(f"用户档案数量: {UserProfile.objects.count()}")
    print(f"部门数量: {Department.objects.count()}")
    print(f"角色数量: {Role.objects.count()}")
    print(f"操作日志数量: {OperationLog.objects.count()}")
    print(f"审计日志数量: {AuditLog.objects.count()}")

if __name__ == '__main__':
    create_test_data()
