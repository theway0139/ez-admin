"""
基于FFmpeg的视频流处理器
使用FFmpeg将RTSP流转换为HTTP流，供前端播放
"""
import subprocess
import threading
import time
import logging
import os
import base64
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

class FFmpegVideoStream:
    """基于FFmpeg的视频流处理器"""
    
    def __init__(self):
        self.cameras = {}
        self.running = False
    
    def start_camera(self, camera_id, rtsp_url):
        """启动摄像头"""
        try:
            # 先停止现有的连接
            if camera_id in self.cameras:
                self.stop_camera(camera_id)
            
            # 创建输出目录
            output_dir = f"media/streams/{camera_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 使用FFmpeg将RTSP流转换为MJPEG流
            cmd = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-analyzeduration', '2000000',
                '-probesize', '2000000',
                '-i', rtsp_url,
                '-c:v', 'mjpeg',
                '-q:v', '5',
                '-f', 'mjpeg',
                '-r', '5',  # 5fps
                '-s', '640x480',  # 固定分辨率
                '-y',
                f'{output_dir}/stream.mjpg'
            ]
            
            # 启动FFmpeg进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.cameras[camera_id] = {
                'process': process,
                'rtsp_url': rtsp_url,
                'output_dir': output_dir,
                'stream_file': f'{output_dir}/stream.mjpg',
                'last_frame': None,
                'last_time': 0,
                'frame_count': 0,
                'error_count': 0,
                'running': True
            }
            
            # 启动读取线程
            thread = threading.Thread(
                target=self._read_stream,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            logger.info(f"启动摄像头 {camera_id} 的FFmpeg流处理")
            return True
            
        except Exception as e:
            logger.error(f"启动摄像头 {camera_id} 失败: {str(e)}")
            return False
    
    def _read_stream(self, camera_id):
        """读取流数据"""
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                camera = self.cameras[camera_id]
                stream_file = camera['stream_file']
                
                if os.path.exists(stream_file):
                    # 读取最新的帧
                    with open(stream_file, 'rb') as f:
                        data = f.read()
                        if data:
                            # 查找最后一个JPEG帧
                            frames = self._extract_jpeg_frames(data)
                            if frames:
                                camera['last_frame'] = frames[-1]
                                camera['last_time'] = time.time()
                                camera['frame_count'] += 1
                                camera['error_count'] = 0
                
                time.sleep(0.2)  # 5fps
                
            except Exception as e:
                logger.error(f"读取流数据失败: {str(e)}")
                time.sleep(1)
    
    def _extract_jpeg_frames(self, data):
        """从MJPEG流中提取JPEG帧"""
        frames = []
        start_marker = b'\xff\xd8'
        end_marker = b'\xff\xd9'
        
        start = 0
        while True:
            start_pos = data.find(start_marker, start)
            if start_pos == -1:
                break
            
            end_pos = data.find(end_marker, start_pos)
            if end_pos == -1:
                break
            
            frame = data[start_pos:end_pos + 2]
            frames.append(frame)
            start = end_pos + 2
        
        return frames
    
    def get_latest_frame(self, camera_id):
        """获取最新帧"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            if camera['last_frame'] and time.time() - camera['last_time'] < 10:
                return camera['last_frame']
        return self._create_placeholder_frame()
    
    def _create_placeholder_frame(self):
        """创建占位符帧"""
        # 创建一个简单的JPEG占位符
        placeholder = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        return placeholder
    
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
                'process_running': camera['process'].poll() is None
            }
        return {'connected': False}
    
    def stop_camera(self, camera_id):
        """停止摄像头"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            camera['running'] = False
            camera['process'].terminate()
            camera['process'].wait(timeout=5)
            del self.cameras[camera_id]
            logger.info(f"停止摄像头 {camera_id}")

# 全局实例
ffmpeg_video_stream = FFmpegVideoStream()

@csrf_exempt
@require_http_methods(["GET"])
def get_ffmpeg_video_frame(request, camera_id):
    """获取FFmpeg视频帧"""
    try:
        frame = ffmpeg_video_stream.get_latest_frame(camera_id)
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
def start_ffmpeg_video_stream(request, camera_id):
    """启动FFmpeg视频流"""
    try:
        from .models import Camera
        camera = Camera.objects.get(id=camera_id)
        
        success = ffmpeg_video_stream.start_camera(camera_id, camera.rtsp_url)
        
        return JsonResponse({
            'success': success,
            'message': 'FFmpeg视频流启动成功' if success else 'FFmpeg视频流启动失败'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_ffmpeg_video_status(request, camera_id):
    """获取FFmpeg视频流状态"""
    try:
        status = ffmpeg_video_stream.get_camera_info(camera_id)
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
