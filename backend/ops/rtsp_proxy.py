"""
RTSP代理服务
将RTSP流转换为HTTP流，供前端播放
"""
import cv2
import threading
import time
import logging
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

class RTSPProxy:
    """RTSP代理"""
    
    def __init__(self):
        self.cameras = {}
        self.running = False
    
    def start_camera_stream(self, camera_id, rtsp_url):
        """启动摄像头流"""
        try:
            cap = cv2.VideoCapture(rtsp_url)
            
            # 设置RTSP连接参数
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, 10)  # 设置帧率
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 降低分辨率
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # 设置超时时间（30秒）
            cap.set(cv2.CAP_PROP_TIMEOUT, 30000)
            
            if not cap.isOpened():
                logger.error(f"无法打开摄像头 {camera_id} 的RTSP流")
                return False
            
            self.cameras[camera_id] = {
                'cap': cap,
                'rtsp_url': rtsp_url,
                'last_frame': None,
                'last_time': 0,
                'frame_count': 0,
                'error_count': 0
            }
            
            # 启动读取线程
            thread = threading.Thread(
                target=self._read_frames,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            logger.info(f"启动摄像头 {camera_id} 的流代理")
            return True
            
        except Exception as e:
            logger.error(f"启动摄像头 {camera_id} 流代理失败: {str(e)}")
            return False
    
    def _read_frames(self, camera_id):
        """读取视频帧"""
        while camera_id in self.cameras:
            try:
                camera = self.cameras[camera_id]
                cap = camera['cap']
                
                ret, frame = cap.read()
                if ret:
                    camera['frame_count'] += 1
                    camera['error_count'] = 0  # 重置错误计数
                    
                    # 编码为JPEG，降低质量以减少传输量
                    _, buffer = cv2.imencode('.jpg', frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 60,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1
                    ])
                    camera['last_frame'] = buffer.tobytes()
                    camera['last_time'] = time.time()
                else:
                    camera['error_count'] += 1
                    if camera['error_count'] > 5:  # 减少重连阈值
                        logger.warning(f"摄像头 {camera_id} 连续读取失败，尝试重新连接")
                        # 重新连接
                        cap.release()
                        time.sleep(2)  # 等待2秒再重连
                        cap = cv2.VideoCapture(camera['rtsp_url'])
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_FPS, 10)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_TIMEOUT, 30000)
                        camera['cap'] = cap
                        camera['error_count'] = 0
                    time.sleep(0.2)  # 增加等待时间
                    
            except Exception as e:
                camera['error_count'] += 1
                logger.error(f"摄像头 {camera_id} 读取帧异常: {str(e)}")
                if camera['error_count'] > 5:
                    time.sleep(2)
                else:
                    time.sleep(0.5)
    
    def get_frame(self, camera_id):
        """获取最新帧"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            # 检查帧是否新鲜（5秒内）
            if camera['last_frame'] and time.time() - camera['last_time'] < 5:
                return camera['last_frame']
            # 如果帧太旧，返回None
            elif time.time() - camera['last_time'] > 10:
                logger.warning(f"摄像头 {camera_id} 帧数据过期")
        return None
    
    def get_camera_status(self, camera_id):
        """获取摄像头状态"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            current_time = time.time()
            last_frame_time = camera.get('last_time', 0)
            
            return {
                'connected': True,
                'frame_count': camera.get('frame_count', 0),
                'error_count': camera.get('error_count', 0),
                'last_frame_time': last_frame_time,
                'is_active': current_time - last_frame_time < 10,  # 10秒内活跃
                'time_since_last_frame': current_time - last_frame_time,
                'health_score': max(0, 100 - camera.get('error_count', 0) * 10)
            }
        return {'connected': False}
    
    def health_check(self):
        """健康检查，清理不活跃的摄像头"""
        current_time = time.time()
        to_remove = []
        
        for camera_id, camera in self.cameras.items():
            last_frame_time = camera.get('last_time', 0)
            if current_time - last_frame_time > 60:  # 1分钟无活动
                logger.warning(f"摄像头 {camera_id} 超过1分钟无活动，准备清理")
                to_remove.append(camera_id)
        
        for camera_id in to_remove:
            self.stop_camera_stream(camera_id)
    
    def stop_camera_stream(self, camera_id):
        """停止摄像头流"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            camera['cap'].release()
            del self.cameras[camera_id]
            logger.info(f"停止摄像头 {camera_id} 的流代理")

# 全局代理实例
rtsp_proxy = RTSPProxy()

def generate_frames(camera_id):
    """生成视频帧"""
    frame_interval = 0.1  # 10fps，降低帧率减少解码压力
    last_frame_time = 0
    
    while True:
        current_time = time.time()
        if current_time - last_frame_time >= frame_interval:
            frame = rtsp_proxy.get_frame(camera_id)
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                last_frame_time = current_time
            else:
                # 发送占位帧
                placeholder = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
        else:
            time.sleep(0.01)  # 短暂休眠

@csrf_exempt
@require_http_methods(["GET"])
def rtsp_stream(request, camera_id):
    """RTSP流代理端点"""
    try:
        # 启动流代理
        if camera_id not in rtsp_proxy.cameras:
            from .models import Camera
            camera = Camera.objects.get(id=camera_id)
            rtsp_proxy.start_camera_stream(camera_id, camera.rtsp_url)
        
        return StreamingHttpResponse(
            generate_frames(camera_id),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"RTSP流代理错误: {str(e)}")
        return HttpResponse("Stream Error", status=500)
