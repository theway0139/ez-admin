"""
简化的视频流服务
使用更稳定的方法处理RTSP流
"""
import cv2
import threading
import time
import logging
import base64
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

class SimpleVideoStream:
    """简化的视频流处理器"""
    
    def __init__(self):
        self.cameras = {}
        self.running = False
    
    def start_camera(self, camera_id, rtsp_url):
        """启动摄像头"""
        try:
            # 使用更保守的RTSP参数
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            
            # 设置更保守的参数
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 5)  # 降低到5fps
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # 进一步降低分辨率
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            
            if not cap.isOpened():
                logger.error(f"无法打开摄像头 {camera_id}")
                return False
            
            self.cameras[camera_id] = {
                'cap': cap,
                'rtsp_url': rtsp_url,
                'last_frame': None,
                'last_time': 0,
                'frame_count': 0,
                'error_count': 0,
                'running': True
            }
            
            # 启动读取线程
            thread = threading.Thread(
                target=self._read_frames,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            logger.info(f"启动摄像头 {camera_id} 成功")
            return True
            
        except Exception as e:
            logger.error(f"启动摄像头 {camera_id} 失败: {str(e)}")
            return False
    
    def _read_frames(self, camera_id):
        """读取视频帧"""
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                camera = self.cameras[camera_id]
                cap = camera['cap']
                
                ret, frame = cap.read()
                if ret:
                    camera['frame_count'] += 1
                    camera['error_count'] = 0
                    
                    # 调整帧大小
                    frame = cv2.resize(frame, (320, 240))
                    
                    # 编码为JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 50,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1
                    ])
                    
                    camera['last_frame'] = buffer.tobytes()
                    camera['last_time'] = time.time()
                    
                else:
                    camera['error_count'] += 1
                    if camera['error_count'] > 3:
                        logger.warning(f"摄像头 {camera_id} 连续失败，尝试重连")
                        self._reconnect_camera(camera_id)
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"摄像头 {camera_id} 异常: {str(e)}")
                time.sleep(1)
    
    def _reconnect_camera(self, camera_id):
        """重新连接摄像头"""
        try:
            camera = self.cameras[camera_id]
            camera['cap'].release()
            time.sleep(2)
            
            cap = cv2.VideoCapture(camera['rtsp_url'], cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 5)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            
            camera['cap'] = cap
            camera['error_count'] = 0
            
        except Exception as e:
            logger.error(f"重连摄像头 {camera_id} 失败: {str(e)}")
    
    def get_latest_frame(self, camera_id):
        """获取最新帧"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            if camera['last_frame'] and time.time() - camera['last_time'] < 10:
                return camera['last_frame']
        return None
    
    def get_camera_info(self, camera_id):
        """获取摄像头信息"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            return {
                'connected': True,
                'frame_count': camera['frame_count'],
                'error_count': camera['error_count'],
                'last_frame_time': camera['last_time'],
                'is_active': time.time() - camera['last_time'] < 5
            }
        return {'connected': False}
    
    def stop_camera(self, camera_id):
        """停止摄像头"""
        if camera_id in self.cameras:
            self.cameras[camera_id]['running'] = False
            self.cameras[camera_id]['cap'].release()
            del self.cameras[camera_id]

# 全局实例
simple_video_stream = SimpleVideoStream()

@csrf_exempt
@require_http_methods(["GET"])
def get_video_frame(request, camera_id):
    """获取视频帧（Base64编码）"""
    try:
        frame = simple_video_stream.get_latest_frame(camera_id)
        if frame:
            frame_base64 = base64.b64encode(frame).decode('utf-8')
            return JsonResponse({
                'success': True,
                'frame': frame_base64,
                'timestamp': time.time()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No frame available'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def start_video_stream(request, camera_id):
    """启动视频流"""
    try:
        from .models import Camera
        camera = Camera.objects.get(id=camera_id)
        
        success = simple_video_stream.start_camera(camera_id, camera.rtsp_url)
        
        return JsonResponse({
            'success': success,
            'message': '视频流启动成功' if success else '视频流启动失败'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def stop_video_stream(request, camera_id):
    """停止视频流"""
    try:
        simple_video_stream.stop_camera(camera_id)
        return JsonResponse({
            'success': True,
            'message': '视频流已停止'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_stream_status(request, camera_id):
    """获取流状态"""
    try:
        status = simple_video_stream.get_camera_info(camera_id)
        return JsonResponse({
            'success': True,
            'camera_id': camera_id,
            'status': status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
