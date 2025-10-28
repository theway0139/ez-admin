"""
稳定的视频流处理器
使用更保守的方法处理RTSP流，避免H.264解码问题
"""
import cv2
import threading
import time
import logging
import base64
import numpy as np
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

class StableVideoStream:
    """稳定的视频流处理器"""
    
    def __init__(self):
        self.cameras = {}
        self.running = False
    
    def start_camera(self, camera_id, rtsp_url):
        """启动摄像头"""
        try:
            # 先停止现有的连接
            if camera_id in self.cameras:
                self.stop_camera(camera_id)
            
            # 使用FFmpeg读取RTSP流并输出JPEG帧
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', rtsp_url,
                '-f', 'image2pipe',
                '-vcodec', 'mjpeg',
                '-q:v', '5',
                '-r', '5',  # 5fps
                '-'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            
            self.cameras[camera_id] = {
                'process': process,
                'rtsp_url': rtsp_url,
                'last_frame': None,
                'last_time': 0,
                'frame_count': 0,
                'error_count': 0,
                'running': True,
                'last_successful_frame': None
            }
            
            # 启动读取线程
            thread = threading.Thread(
                target=self._read_frames_ffmpeg,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            logger.info(f"启动摄像头 {camera_id} 的FFmpeg视频流处理")
            return True
            
        except Exception as e:
            logger.error(f"启动摄像头 {camera_id} 失败: {str(e)}")
            return False
    
    def _read_frames(self, camera_id):
        """读取视频帧"""
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                camera = self.cameras[camera_id]
                cap = camera['cap']
                
                ret, frame = cap.read()
                if ret and frame is not None:
                    camera['frame_count'] += 1
                    camera['error_count'] = 0
                    consecutive_errors = 0
                    
                    try:
                        # 直接编码，不调整大小
                        _, buffer = cv2.imencode('.jpg', frame, [
                            cv2.IMWRITE_JPEG_QUALITY, 50
                        ])
                        
                        if buffer is not None:
                            camera['last_frame'] = buffer.tobytes()
                            camera['last_time'] = time.time()
                            camera['last_successful_frame'] = buffer.tobytes()
                            logger.info(f"摄像头 {camera_id} 成功获取帧，大小: {len(buffer.tobytes())} 字节")
                    except Exception as e:
                        logger.warning(f"处理帧时出错: {str(e)}")
                        consecutive_errors += 1
                    
                else:
                    consecutive_errors += 1
                    camera['error_count'] += 1
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.warning(f"摄像头 {camera_id} 连续失败，尝试重连")
                        if self._reconnect_camera(camera_id):
                            consecutive_errors = 0
                        else:
                            time.sleep(5)  # 重连失败，等待5秒
                    else:
                        time.sleep(1)
                    
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"摄像头 {camera_id} 异常: {str(e)}")
                if consecutive_errors >= max_consecutive_errors:
                    time.sleep(5)
                else:
                    time.sleep(2)
    
    def _read_frames_ffmpeg(self, camera_id):
        """使用FFmpeg读取视频帧的后台线程"""
        consecutive_errors = 0
        
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                camera = self.cameras[camera_id]
                process = camera['process']
                
                # 读取JPEG标记 - JPEG文件以FFD8开始，以FFD9结束
                start_marker = b'\xff\xd8'
                end_marker = b'\xff\xd9'
                
                # 查找JPEG帧的开始
                buffer = b''
                while len(buffer) < 2:
                    chunk = process.stdout.read(1)
                    if not chunk:
                        raise Exception("FFmpeg process ended")
                    buffer += chunk
                    if len(buffer) >= 2 and buffer[-2:] == start_marker:
                        break
                    if len(buffer) > 1000:
                        buffer = buffer[-2:]
                
                # 读取直到找到结束标记
                frame_data = start_marker
                while True:
                    chunk = process.stdout.read(1024)  # 每次读取1KB
                    if not chunk:
                        raise Exception("FFmpeg process ended")
                    frame_data += chunk
                    if end_marker in frame_data:
                        # 找到结束标记，截取完整帧
                        end_pos = frame_data.find(end_marker) + 2
                        frame_data = frame_data[:end_pos]
                        break
                    if len(frame_data) > 10*1024*1024:  # 超过10MB，重置
                        raise Exception("Frame too large")
                
                camera['frame_count'] += 1
                camera['error_count'] = 0
                consecutive_errors = 0
                camera['last_frame'] = frame_data
                camera['last_time'] = time.time()
                camera['last_successful_frame'] = frame_data
                
                if camera['frame_count'] % 10 == 0:
                    logger.info(f"摄像头 {camera_id} 成功获取第 {camera['frame_count']} 帧，大小: {len(frame_data)} 字节")
                    
            except Exception as e:
                logger.error(f"摄像头 {camera_id} 读取帧异常: {str(e)}")
                consecutive_errors += 1
                
                if consecutive_errors >= 5:
                    logger.warning(f"摄像头 {camera_id} 连续读取失败 {consecutive_errors} 次，重启FFmpeg...")
                    self._restart_ffmpeg(camera_id)
                    consecutive_errors = 0
                    time.sleep(2)
                else:
                    time.sleep(1)
    
    def _restart_ffmpeg(self, camera_id):
        """重启FFmpeg进程"""
        try:
            camera = self.cameras[camera_id]
            camera['process'].terminate()
            camera['process'].wait(timeout=5)
        except:
            pass
        
        try:
            # 重新启动
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', camera['rtsp_url'],
                '-f', 'image2pipe',
                '-vcodec', 'mjpeg',
                '-q:v', '5',
                '-r', '5',
                '-'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            
            camera['process'] = process
            camera['error_count'] = 0
            logger.info(f"摄像头 {camera_id} FFmpeg重启成功")
            
        except Exception as e:
            logger.error(f"摄像头 {camera_id} FFmpeg重启失败: {str(e)}")
    
    def _reconnect_camera(self, camera_id):
        """重新连接摄像头"""
        try:
            camera = self.cameras[camera_id]
            camera['cap'].release()
            time.sleep(3)  # 等待3秒
            
            cap = cv2.VideoCapture(camera['rtsp_url'])
            
            if cap.isOpened():
                camera['cap'] = cap
                camera['error_count'] = 0
                logger.info(f"摄像头 {camera_id} 重连成功")
                return True
            else:
                logger.error(f"摄像头 {camera_id} 重连失败")
                return False
                
        except Exception as e:
            logger.error(f"重连摄像头 {camera_id} 失败: {str(e)}")
            return False
    
    def get_latest_frame(self, camera_id):
        """获取最新帧"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            current_time = time.time()
            
            # 如果最近有帧，返回最新帧
            if camera['last_frame'] and current_time - camera['last_time'] < 15:
                return camera['last_frame']
            # 如果有历史成功帧，返回历史帧
            elif camera['last_successful_frame']:
                return camera['last_successful_frame']
            # 否则返回占位符
            else:
                return self._create_placeholder_frame()
        return self._create_placeholder_frame()
    
    def _create_placeholder_frame(self):
        """创建占位符帧"""
        # 创建一个简单的占位符图像
        placeholder = np.zeros((120, 160, 3), dtype=np.uint8)
        placeholder.fill(50)  # 深灰色背景
        
        # 添加文字
        cv2.putText(placeholder, 'No Signal', (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', placeholder, [
            cv2.IMWRITE_JPEG_QUALITY, 50
        ])
        
        return buffer.tobytes()
    
    def get_camera_info(self, camera_id):
        """获取摄像头信息"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            current_time = time.time()
            return {
                'connected': True,
                'frame_count': camera['frame_count'],
                'error_count': camera['error_count'],
                'last_frame_time': camera['last_time'],
                'is_active': current_time - camera['last_time'] < 10,
                'has_successful_frame': camera['last_successful_frame'] is not None
            }
        return {'connected': False}
    
    def stop_camera(self, camera_id):
        """停止摄像头"""
        if camera_id in self.cameras:
            self.cameras[camera_id]['running'] = False
            
            # 停止FFmpeg进程或OpenCV capture
            if 'process' in self.cameras[camera_id]:
                try:
                    self.cameras[camera_id]['process'].terminate()
                    self.cameras[camera_id]['process'].wait(timeout=5)
                except:
                    pass
            elif 'cap' in self.cameras[camera_id]:
                self.cameras[camera_id]['cap'].release()
            
            del self.cameras[camera_id]
            logger.info(f"停止摄像头 {camera_id}")

# 全局实例
stable_video_stream = StableVideoStream()

@csrf_exempt
@require_http_methods(["GET"])
def get_stable_video_frame(request, camera_id):
    """获取稳定的视频帧"""
    try:
        frame = stable_video_stream.get_latest_frame(camera_id)
        frame_base64 = base64.b64encode(frame).decode('utf-8')
        return JsonResponse({
            'success': True,
            'frame': frame_base64,
            'timestamp': time.time()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def start_stable_video_stream(request, camera_id):
    """启动稳定视频流"""
    try:
        from .models import Camera
        camera = Camera.objects.get(id=camera_id)
        
        success = stable_video_stream.start_camera(camera_id, camera.rtsp_url)
        
        return JsonResponse({
            'success': success,
            'message': '稳定视频流启动成功' if success else '稳定视频流启动失败'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_stable_video_status(request, camera_id):
    """获取稳定视频流状态"""
    try:
        status = stable_video_stream.get_camera_info(camera_id)
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

def mjpeg_stream(request, camera_id):
    """MJPEG流端点 - 使用FFmpeg直接从RTSP转码"""
    from django.http import StreamingHttpResponse
    
    def generate():
        """生成MJPEG流"""
        try:
            from .models import Camera
            camera = Camera.objects.get(id=camera_id)
            
            # 使用FFmpeg将RTSP转为MJPEG
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', camera.rtsp_url,
                '-f', 'mjpeg',
                '-q:v', '5',
                '-r', '10',  # 10fps
                '-s', '640x480',
                '-'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            
            # 读取并生成MJPEG帧
            while True:
                # 查找JPEG开始标记
                buffer = b''
                while len(buffer) < 2 or buffer[-2:] != b'\xff\xd8':
                    chunk = process.stdout.read(1)
                    if not chunk:
                        break
                    buffer += chunk
                    if len(buffer) > 10000:
                        buffer = buffer[-2:]
                
                if not buffer:
                    break
                
                # 读取完整的JPEG帧
                frame_data = buffer[-2:]  # 保留开始标记
                while True:
                    chunk = process.stdout.read(1024)
                    if not chunk:
                        break
                    frame_data += chunk
                    if b'\xff\xd9' in frame_data:
                        # 找到结束标记
                        end_pos = frame_data.find(b'\xff\xd9') + 2
                        frame_data = frame_data[:end_pos]
                        break
                    if len(frame_data) > 5*1024*1024:  # 超过5MB
                        break
                
                # 生成multipart响应
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            
            process.terminate()
            
        except Exception as e:
            logger.error(f"MJPEG流生成失败: {str(e)}")
            yield b'--frame\r\n'
    
    return StreamingHttpResponse(
        generate(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
