"""
视频流转换服务
将RTSP流转换为HLS格式，供前端播放
"""
import subprocess
import os
import threading
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class StreamConverter:
    """视频流转换器"""
    
    def __init__(self):
        self.converters = {}  # 存储转换进程
        self.hls_base_url = "http://172.16.160.100:8003/hls/"
        
    def start_conversion(self, camera_id, rtsp_url):
        """启动RTSP到HLS的转换"""
        try:
            # 创建HLS输出目录
            hls_dir = f"media/hls/{camera_id}"
            os.makedirs(hls_dir, exist_ok=True)
            
            # HLS输出文件路径
            playlist_path = f"{hls_dir}/playlist.m3u8"
            
            # 先停止该摄像头的现有转换
            if camera_id in self.converters:
                self.stop_conversion(camera_id)
            
            # FFmpeg命令：将RTSP流转换为HLS
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',          # 使用TCP传输
                '-analyzeduration', '2000000',     # 增加分析时间
                '-probesize', '2000000',           # 增加探测大小
                '-i', rtsp_url,                    # 输入RTSP流
                '-c:v', 'libx264',                 # 视频编码器
                '-an',                             # 禁用音频
                '-preset', 'ultrafast',            # 编码预设
                '-tune', 'zerolatency',            # 零延迟调优
                '-f', 'hls',                       # 输出格式为HLS
                '-hls_time', '2',                  # 每个片段2秒
                '-hls_list_size', '3',             # 保持3个片段
                '-hls_flags', 'delete_segments',   # 删除旧片段
                '-hls_allow_cache', '0',           # 不允许缓存
                '-y',                              # 覆盖输出文件
                playlist_path
            ]
            
            # 启动转换进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.converters[camera_id] = process
            logger.info(f"启动摄像头 {camera_id} 的流转换，进程ID: {process.pid}")
            
            # 等待几秒检查进程是否正常运行
            time.sleep(3)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8') if stderr else '未知错误'
                logger.error(f"FFmpeg进程启动失败: {error_msg}")
                return {
                    'success': False,
                    'error': f'FFmpeg启动失败: {error_msg}'
                }
            
            return {
                'success': True,
                'hls_url': f"{self.hls_base_url}{camera_id}/playlist.m3u8",
                'process_id': process.pid
            }
            
        except Exception as e:
            logger.error(f"启动流转换失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def stop_conversion(self, camera_id):
        """停止转换"""
        try:
            if camera_id in self.converters:
                process = self.converters[camera_id]
                process.terminate()
                process.wait(timeout=5)
                del self.converters[camera_id]
                logger.info(f"停止摄像头 {camera_id} 的流转换")
                return True
        except Exception as e:
            logger.error(f"停止流转换失败: {str(e)}")
        return False
    
    def stop_all_conversions(self):
        """停止所有转换"""
        for camera_id in list(self.converters.keys()):
            self.stop_conversion(camera_id)
    
    def get_conversion_status(self, camera_id):
        """获取转换状态"""
        if camera_id in self.converters:
            process = self.converters[camera_id]
            return {
                'running': process.poll() is None,
                'hls_url': f"{self.hls_base_url}{camera_id}/playlist.m3u8"
            }
        return {'running': False, 'hls_url': None}

# 全局转换器实例
stream_converter = StreamConverter()
