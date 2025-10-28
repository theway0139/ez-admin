"""
简化的视频流服务
不依赖FFmpeg，直接提供RTSP流信息
"""
import logging
from .models import Camera

logger = logging.getLogger(__name__)

class SimpleStreamService:
    """简化的流服务"""
    
    def __init__(self):
        self.active_streams = {}
    
    def get_stream_info(self, camera_id):
        """获取摄像头流信息"""
        try:
            camera = Camera.objects.get(id=camera_id)
            
            # 检查摄像头状态
            if camera.status != 'online':
                return {
                    'success': False,
                    'error': f'摄像头 {camera.name} 状态为 {camera.status}',
                    'camera_status': camera.status
                }
            
            # 返回流信息
            return {
                'success': True,
                'camera_id': camera.id,
                'camera_name': camera.name,
                'rtsp_url': camera.rtsp_url,
                'status': camera.status,
                'ip_address': camera.ip_address,
                'port': camera.port,
                'location': camera.location,
                'resolution': camera.resolution,
                'fps': camera.fps,
                'message': '流信息获取成功'
            }
            
        except Camera.DoesNotExist:
            return {
                'success': False,
                'error': '摄像头不存在'
            }
        except Exception as e:
            logger.error(f"获取流信息失败: {str(e)}")
            return {
                'success': False,
                'error': f'获取流信息失败: {str(e)}'
            }
    
    def test_rtsp_connection(self, rtsp_url):
        """测试RTSP连接"""
        try:
            import cv2
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret
            return False
        except Exception as e:
            logger.error(f"测试RTSP连接失败: {str(e)}")
            return False

# 全局服务实例
simple_stream_service = SimpleStreamService()
