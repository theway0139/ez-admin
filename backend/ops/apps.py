from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


def is_port_open(host: str, port: int) -> bool:
    import socket
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def start_rtsp_socket_server():
    """在模型加载成功后启动 FastAPI Socket 服务（uvicorn）
    以独立进程运行（由 ready() 中的 multiprocessing 启动）。
    """
    import sys
    import os
    import logging
    logger = logging.getLogger(__name__)

    try:
        # 仅在主进程且 runserver 模式下运行，防止重复启动
        if 'runserver' not in sys.argv:
            logger.info("跳过RTSP Socket服务启动（非runserver模式）")
            return
        if os.environ.get('RUN_MAIN') != 'true':
            logger.info("跳过RTSP Socket服务启动（非Django主进程）")
            return

        # 如果端口已被占用则不再启动
        host, port = '0.0.0.0', 5001
        if is_port_open(host, port):
            logger.info(f"RTSP Socket服务 {host}:{port} 已在运行，跳过启动")
            return

        # 确保模型已加载（导入即触发加载）
        logger.info("检查模型加载状态...")
        from api.models_loader import is_models_loaded  # 导入会触发模型加载
        if not is_models_loaded():
            logger.warning("模型未成功加载，RTSP Socket服务暂不启动")
            return

        # 在当前进程中直接运行 uvicorn（由父进程以 multiprocessing 启动）
        logger.info("使用独立子进程运行 Uvicorn RTSP Socket服务...")
        import uvicorn
        uvicorn.run("ops.rtsp_socket_server:app", host=host, port=port)
        # 注意：此调用会阻塞子进程直至服务停止
    except Exception as e:
        logger.error(f"❌ 启动 RTSP Socket服务失败: {str(e)}", exc_info=True)


class OpsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ops'
    verbose_name = '运维管理'
    
    def ready(self):
        """Django启动时执行"""
        import threading
        import time
        import sys
        import multiprocessing
        
        # 避免在Django migrate/makemigrations时启动服务
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

        # 启动 RTSP Socket 服务（以单独子进程运行）
        logger.info("创建RTSP Socket服务子进程...")
        rtsp_process = multiprocessing.Process(target=start_rtsp_socket_server)
        rtsp_process.start()
        logger.info(f"RTSP Socket服务子进程已启动 (pid={rtsp_process.pid})")

