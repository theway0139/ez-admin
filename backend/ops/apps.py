from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class OpsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ops'
    verbose_name = '运维管理'
    
    def ready(self):
        """Django启动时执行"""
        import threading
        import time
        
        # 避免在Django migrate/makemigrations时启动服务
        import sys
        if 'runserver' not in sys.argv and 'manage.py' in sys.argv[0]:
            logger.info("跳过视频分析服务启动（非runserver模式）")
            return
        
        logger.info("=" * 60)
        logger.info("OpsConfig.ready() 被调用")
        logger.info("=" * 60)
        
        def start_video_analysis():
            """延迟启动视频分析服务"""
            logger.info("视频分析服务启动线程开始，等待5秒...")
            time.sleep(5)  # 等待Django完全启动
            
            try:
                logger.info("开始导入video_analysis_service...")
                from .video_analysis_service import video_analysis_service
                
                logger.info("开始调用start_all_cameras()...")
                video_analysis_service.start_all_cameras()
                
                logger.info("✅ 视频分析服务已启动！")
            except Exception as e:
                logger.error(f"❌ 视频分析服务启动失败: {str(e)}", exc_info=True)
        
        # 在后台线程中启动
        logger.info("创建视频分析服务后台线程...")
        thread = threading.Thread(target=start_video_analysis, daemon=True)
        thread.start()
        logger.info("视频分析服务后台线程已启动")

