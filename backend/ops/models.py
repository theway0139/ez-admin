from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    """任务模型"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name="部门名称")
    description = models.TextField(blank=True, null=True, verbose_name="部门描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
        ordering = ['name']


class Role(models.Model):
    """角色模型"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('editor', '编辑员'),
        ('viewer', '观察者'),
        ('auditor', '审计员'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name="角色名称")
    display_name = models.CharField(max_length=100, verbose_name="显示名称")
    description = models.TextField(blank=True, null=True, verbose_name="角色描述")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ['name']


class UserProfile(models.Model):
    """用户扩展信息模型"""
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '未激活'),
        ('locked', '已锁定'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    real_name = models.CharField(max_length=100, verbose_name="真实姓名")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="头像")
    
    # 组织信息
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="部门")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="角色")
    
    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="最后登录IP")
    login_count = models.IntegerField(default=0, verbose_name="登录次数")
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.real_name}({self.user.username})"

    @property
    def role_display(self):
        return self.role.display_name if self.role else "未分配"
    
    @property
    def department_display(self):
        return self.department.name if self.department else "未分配"
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"
        ordering = ['-created_at']


class SystemSettings(models.Model):
    """系统设置模型"""
    SETTING_TYPES = [
        ('general', '常规设置'),
        ('security', '安全设置'),
        ('notification', '通知设置'),
        ('performance', '性能设置'),
    ]
    
    # 基本信息
    key = models.CharField(max_length=100, unique=True, verbose_name="设置键")
    value = models.TextField(verbose_name="设置值")
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, verbose_name="设置类型")
    description = models.TextField(blank=True, null=True, verbose_name="设置描述")
    
    # 元数据
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"
        ordering = ['setting_type', 'key']


class NotificationSettings(models.Model):
    """通知设置模型"""
    # 通知方式
    email_enabled = models.BooleanField(default=True, verbose_name="邮件通知")
    sms_enabled = models.BooleanField(default=False, verbose_name="短信通知")
    push_enabled = models.BooleanField(default=True, verbose_name="推送通知")
    webhook_enabled = models.BooleanField(default=False, verbose_name="Webhook通知")
    
    # 邮件服务器配置
    smtp_server = models.CharField(max_length=200, blank=True, verbose_name="SMTP服务器")
    smtp_port = models.IntegerField(default=587, verbose_name="SMTP端口")
    smtp_username = models.CharField(max_length=200, blank=True, verbose_name="发件人邮箱")
    smtp_password = models.CharField(max_length=200, blank=True, verbose_name="SMTP密码")
    sender_name = models.CharField(max_length=100, default="系统通知", verbose_name="发件人名称")
    
    # 通知事件配置
    system_error_notify = models.BooleanField(default=True, verbose_name="系统错误")
    security_alert_notify = models.BooleanField(default=True, verbose_name="安全警报")
    task_complete_notify = models.BooleanField(default=True, verbose_name="备份完成")
    
    # 时间设置
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "通知设置"

    class Meta:
        verbose_name = "通知设置"
        verbose_name_plural = "通知设置"


class SecuritySettings(models.Model):
    """安全设置模型"""
    # 会话设置
    session_timeout = models.IntegerField(default=60, verbose_name="会话超时时间(分钟)")
    
    # 密码策略
    password_strength = models.CharField(
        max_length=20,
        choices=[
            ('low', '低强度'),
            ('medium', '中等强度'),
            ('high', '高强度'),
        ],
        default='medium',
        verbose_name="密码强度"
    )
    max_login_attempts = models.IntegerField(default=5, verbose_name="最大登录尝试次数")
    account_lockout_time = models.IntegerField(default=30, verbose_name="账户锁定时间(分钟)")
    
    # 安全选项
    two_factor_auth = models.BooleanField(default=False, verbose_name="启用双因素认证")
    force_password_change = models.BooleanField(default=True, verbose_name="强制定期修改密码")
    audit_logging = models.BooleanField(default=True, verbose_name="启用审计日志")
    
    # 时间设置
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "安全设置"

    class Meta:
        verbose_name = "安全设置"
        verbose_name_plural = "安全设置"


class PerformanceSettings(models.Model):
    """性能设置模型"""
    # 数据保留
    data_retention_days = models.IntegerField(default=90, verbose_name="数据保留时间(天)")
    log_level = models.CharField(
        max_length=20,
        choices=[
            ('DEBUG', '调试'),
            ('INFO', '信息'),
            ('WARNING', '警告'),
            ('ERROR', '错误'),
        ],
        default='INFO',
        verbose_name="日志级别"
    )
    
    # 自动备份
    auto_backup_enabled = models.BooleanField(default=False, verbose_name="启用自动备份")
    backup_interval = models.CharField(
        max_length=20,
        choices=[
            ('daily', '每天'),
            ('weekly', '每周'),
            ('monthly', '每月'),
        ],
        default='daily',
        verbose_name="备份间隔"
    )
    
    # 监控设置
    monitoring_interval = models.IntegerField(default=60, verbose_name="监控数据采样间隔(秒)")
    
    # 性能优化
    enable_data_compression = models.BooleanField(default=True, verbose_name="启用数据缓存")
    enable_cache_optimization = models.BooleanField(default=False, verbose_name="启用数据压缩缓存")
    enable_realtime_monitoring = models.BooleanField(default=True, verbose_name="启用实时监控")
    
    # 时间设置
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "性能设置"

    class Meta:
        verbose_name = "性能设置"
        verbose_name_plural = "性能设置"


class OperationLog(models.Model):
    """操作日志模型"""
    OPERATION_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
        ('import', '导入'),
        ('download', '下载'),
        ('backup', '备份'),
        ('restore', '恢复'),
        ('config', '系统设置'),
        ('user_mgmt', '用户管理'),
        ('robot_mgmt', '机器人配置'),
        ('task_mgmt', '任务调度'),
        ('file_mgmt', '录像文件'),
    ]
    
    OPERATION_RESULTS = [
        ('success', '成功'),
        ('failed', '失败'),
        ('warning', '警告'),
    ]
    
    # 基本信息
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES, verbose_name="操作类型")
    operation_target = models.CharField(max_length=100, verbose_name="操作对象")
    operation_detail = models.TextField(verbose_name="操作详情")
    
    # 操作人信息
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="操作人员")
    operator_name = models.CharField(max_length=100, verbose_name="操作人姓名")
    operator_ip = models.GenericIPAddressField(verbose_name="操作IP地址")
    
    # 操作结果
    result = models.CharField(max_length=20, choices=OPERATION_RESULTS, default='success', verbose_name="操作结果")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")
    
    # 时间信息
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    duration = models.FloatField(default=0.0, verbose_name="操作耗时(秒)")
    
    # 附加信息
    user_agent = models.TextField(blank=True, null=True, verbose_name="用户代理")
    request_data = models.JSONField(blank=True, null=True, verbose_name="请求数据")
    response_data = models.JSONField(blank=True, null=True, verbose_name="响应数据")

    def __str__(self):
        return f"{self.operator_name} - {self.get_operation_type_display()} - {self.operation_target}"

    @property
    def operation_type_display(self):
        return dict(self.OPERATION_TYPES).get(self.operation_type, self.operation_type)
    
    @property
    def result_display(self):
        return dict(self.OPERATION_RESULTS).get(self.result, self.result)

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"


class BackupFile(models.Model):
    """备份文件模型"""
    BACKUP_TYPES = [
        ('full', '完整备份'),
        ('incremental', '增量备份'),
        ('differential', '差异备份'),
    ]
    
    BACKUP_STATUS = [
        ('completed', '已完成'),
        ('running', '备份中'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="备份名称")
    file_path = models.CharField(max_length=500, verbose_name="文件路径")
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full', verbose_name="备份类型")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小(字节)")
    status = models.CharField(max_length=20, choices=BACKUP_STATUS, default='completed', verbose_name="备份状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    description = models.TextField(blank=True, verbose_name="备份描述")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    
    class Meta:
        db_table = 'backup_files'
        ordering = ['-created_at']
        verbose_name = "备份文件"
        verbose_name_plural = "备份文件"
    
    @property
    def file_size_display(self):
        """格式化文件大小显示"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    @property
    def backup_type_display(self):
        """备份类型显示名称"""
        return dict(self.BACKUP_TYPES).get(self.backup_type, self.backup_type)
    
    @property
    def status_display(self):
        """状态显示名称"""
        return dict(self.BACKUP_STATUS).get(self.status, self.status)


class BackupSettings(models.Model):
    """备份设置模型"""
    auto_backup_enabled = models.BooleanField(default=True, verbose_name="启用自动备份")
    backup_frequency = models.CharField(max_length=20, default='daily', verbose_name="备份频率")  # daily, weekly, monthly
    max_backup_files = models.IntegerField(default=30, verbose_name="保留备份数量")
    backup_type = models.CharField(
        max_length=20,
        choices=[
            ('full', '完整备份'),
            ('incremental', '增量备份'),
            ('differential', '差异备份'),
        ],
        default='full',
        verbose_name="备份类型"
    )
    
    class Meta:
        db_table = 'backup_settings'
        verbose_name = "备份设置"
        verbose_name_plural = "备份设置"


class AuditLog(models.Model):
    """审计日志模型"""
    LOG_TYPES = [
        ('system', '系统日志'),
        ('security', '安全日志'),
        ('operation', '操作日志'),
        ('performance', '性能日志'),
        ('application', '应用日志'),
    ]
    
    LOG_LEVELS = [
        ('DEBUG', '调试'),
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('CRITICAL', '严重'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间戳")
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name="日志类型")
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name="日志级别")
    source_module = models.CharField(max_length=100, verbose_name="来源模块")
    message = models.TextField(verbose_name="消息内容")
    details = models.JSONField(null=True, blank=True, verbose_name="详细信息")
    user = models.CharField(max_length=100, default='system', verbose_name="用户")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp} - {self.log_type} - {self.level} - {self.message[:50]}"


# ============= 虚拟犬监控系统模型 =============

class Dog(models.Model):
    """虚拟犬模型"""
    STATUS_CHOICES = [
        ('active', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="虚拟犬名称")
    dog_id = models.CharField(max_length=50, unique=True, default='DOG_DEFAULT', verbose_name="虚拟犬编号")
    location = models.CharField(max_length=200, verbose_name="巡逻区域")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name="状态")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "虚拟犬"
        verbose_name_plural = "虚拟犬"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.dog_id})"


class Camera(models.Model):
    """摄像头模型"""
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('error', '故障'),
    ]
    
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, related_name='cameras', verbose_name="所属虚拟犬")
    name = models.CharField(max_length=100, verbose_name="摄像头名称")
    camera_id = models.CharField(max_length=50, unique=True, default='CAM_DEFAULT', verbose_name="摄像头编号")
    rtsp_url = models.CharField(max_length=500, verbose_name="RTSP流地址")
    location = models.CharField(max_length=200, verbose_name="安装位置")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name="状态")
    resolution = models.CharField(max_length=20, default='1920x1080', verbose_name="分辨率")
    fps = models.IntegerField(default=25, verbose_name="帧率")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "摄像头"
        verbose_name_plural = "摄像头"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.camera_id})"


class AlarmEvent(models.Model):
    """报警事件模型"""
    EVENT_TYPES = [
        ('smoking', '吸烟检测'),
        ('phone', '打电话检测'),
        ('fire', '火灾检测'),
        ('stranger', '陌生人检测'),
        ('fighting', '打架斗殴检测'),
        ('rubbish', '垃圾检测'),
        ('crossover', '翻越检测'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '严重'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE, related_name='alarm_events', verbose_name="所属虚拟犬")
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alarm_events', verbose_name="触发摄像头")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="事件类型")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium', verbose_name="严重程度")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    
    title = models.CharField(max_length=200, verbose_name="事件标题")
    description = models.TextField(verbose_name="事件描述")
    
    # 媒体文件
    image_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="截图路径")
    video_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="视频路径")
    
    # 检测信息
    confidence = models.FloatField(default=0.0, verbose_name="置信度")
    detection_data = models.JSONField(blank=True, null=True, verbose_name="检测详细数据")
    
    # 时间信息
    detected_at = models.DateTimeField(verbose_name="检测时间")
    handled_at = models.DateTimeField(blank=True, null=True, verbose_name="处理时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 处理信息
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="处理人")
    handle_note = models.TextField(blank=True, null=True, verbose_name="处理备注")
    
    class Meta:
        verbose_name = "报警事件"
        verbose_name_plural = "报警事件"
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['-detected_at']),
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['camera', '-detected_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.camera.name} - {self.detected_at}"


# ============= 人脸管理模型 =============

class FaceRecord(models.Model):
    """人脸记录模型"""
    STATUS_CHOICES = [
        ('active', '已激活'),
        ('inactive', '未激活'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name="姓名")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="人员ID")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="部门")
    
    # 人脸图像
    avatar = models.ImageField(upload_to='faces/', blank=True, null=True, verbose_name="人脸照片")
    avatar_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="人脸照片路径")
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    
    # 特征数据（用于人脸识别）
    face_encoding = models.TextField(blank=True, null=True, verbose_name="人脸特征编码")
    
    # 备注信息
    description = models.TextField(blank=True, null=True, verbose_name="备注")
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "人脸记录"
        verbose_name_plural = "人脸记录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"