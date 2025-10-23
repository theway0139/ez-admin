"""
操作日志工具类
提供手动记录重要操作的功能
"""
from .models import OperationLog
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class LogRecorder:
    """操作日志记录器"""
    
    @staticmethod
    def log_user_action(request, action_type, target, detail, result='success', error_msg=None):
        """记录用户操作"""
        try:
            # 获取操作人信息
            operator_name = 'anonymous'
            operator = None
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                operator = request.user
                operator_name = request.user.username
            
            # 获取客户端IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                operator_ip = x_forwarded_for.split(',')[0]
            else:
                operator_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            # 创建日志记录
            OperationLog.objects.create(
                operation_type=action_type,
                operation_target=target,
                operation_detail=detail,
                operator=operator,
                operator_name=operator_name,
                operator_ip=operator_ip,
                result=result,
                error_message=error_msg,
                duration=0.0
            )
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
    
    @staticmethod
    def log_user_login(request, username, success=True, error_msg=None):
        """记录用户登录"""
        LogRecorder.log_user_action(
            request, 
            'login', 
            '用户认证', 
            f'用户 {username} 登录系统',
            'success' if success else 'failed',
            error_msg
        )
    
    @staticmethod
    def log_user_logout(request, username):
        """记录用户登出"""
        LogRecorder.log_user_action(
            request,
            'logout',
            '用户认证',
            f'用户 {username} 退出系统'
        )
    
    @staticmethod
    def log_user_create(request, username):
        """记录用户创建"""
        LogRecorder.log_user_action(
            request,
            'create',
            '用户管理',
            f'创建新用户: {username}'
        )
    
    @staticmethod
    def log_user_update(request, user_id, username):
        """记录用户更新"""
        LogRecorder.log_user_action(
            request,
            'update',
            '用户管理',
            f'更新用户信息: {username} (ID: {user_id})'
        )
    
    @staticmethod
    def log_user_delete(request, user_id, username):
        """记录用户删除"""
        LogRecorder.log_user_action(
            request,
            'delete',
            '用户管理',
            f'删除用户: {username} (ID: {user_id})'
        )
    
    @staticmethod
    def log_password_reset(request, user_id, username):
        """记录密码重置"""
        LogRecorder.log_user_action(
            request,
            'update',
            '用户管理',
            f'重置用户密码: {username} (ID: {user_id})'
        )
    
    @staticmethod
    def log_user_status_toggle(request, user_id, username, new_status):
        """记录用户状态切换"""
        action = '启用' if new_status else '禁用'
        LogRecorder.log_user_action(
            request,
            'update',
            '用户管理',
            f'{action}用户: {username} (ID: {user_id})'
        )
    
    @staticmethod
    def log_settings_update(request, setting_type, details=None):
        """记录系统设置修改"""
        setting_names = {
            'general': '常规设置',
            'security': '安全设置', 
            'notification': '通知设置',
            'performance': '性能设置'
        }
        
        setting_name = setting_names.get(setting_type, '系统设置')
        detail = details or f'修改{setting_name}'
        
        LogRecorder.log_user_action(
            request,
            'config',
            '系统设置',
            detail
        )
    
    @staticmethod
    def log_settings_restore(request, setting_type):
        """记录设置恢复默认"""
        setting_names = {
            'general': '常规设置',
            'security': '安全设置',
            'notification': '通知设置', 
            'performance': '性能设置'
        }
        
        setting_name = setting_names.get(setting_type, '系统设置')
        
        LogRecorder.log_user_action(
            request,
            'config',
            '系统设置',
            f'恢复{setting_name}为默认值'
        )
    
    @staticmethod
    def log_backup_create(request, backup_name, backup_type):
        """记录备份创建"""
        type_names = {
            'full': '完整备份',
            'incremental': '增量备份',
            'differential': '差异备份'
        }
        type_display = type_names.get(backup_type, backup_type)
        
        LogRecorder.log_user_action(
            request,
            'backup',
            '数据备份',
            f'创建{type_display}: {backup_name}'
        )
    
    @staticmethod
    def log_backup_download(request, backup_name):
        """记录备份下载"""
        LogRecorder.log_user_action(
            request,
            'download',
            '数据备份',
            f'下载备份文件: {backup_name}'
        )
    
    @staticmethod
    def log_backup_restore(request, backup_name):
        """记录备份恢复"""
        LogRecorder.log_user_action(
            request,
            'restore',
            '数据备份',
            f'恢复数据库备份: {backup_name}'
        )
    
    @staticmethod
    def log_backup_delete(request, backup_name):
        """记录备份删除"""
        LogRecorder.log_user_action(
            request,
            'delete',
            '数据备份',
            f'删除备份文件: {backup_name}'
        )
