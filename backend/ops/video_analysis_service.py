"""
视频流自动分析服务
- 10秒截图用于：行为检测(吸烟、打电话)、火灾烟雾检测、垃圾检测、翻越检测
- 30秒录制5秒视频用于：打架斗殴检测(暂时由于RTSP流不稳定，使用FFmpeg录制)
"""
import cv2
import time
import threading
import logging
import os
from datetime import datetime
from django.utils import timezone
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class VideoAnalysisService:
    """视频流自动分析服务"""
    
    def __init__(self):
        self.cameras = {}  # {camera_id: {'thread': Thread, 'running': bool}}
        self.running = False
        self.media_root = 'media/alarm_events'
        os.makedirs(self.media_root, exist_ok=True)
        os.makedirs(f'{self.media_root}/images', exist_ok=True)
        os.makedirs(f'{self.media_root}/videos', exist_ok=True)
        
        # 配置：是否启用视频检测（由于RTSP流不稳定，默认禁用）
        self.enable_video_detection = False
    
    def start_all_cameras(self):
        """启动所有在线摄像头的分析"""
        from .models import Camera
        
        self.running = True
        cameras = Camera.objects.filter(status='online')
        
        for camera in cameras:
            self.start_camera_analysis(camera.id, camera.rtsp_url)
        
        logger.info(f"启动了 {len(cameras)} 个摄像头的视频分析")
    
    def start_camera_analysis(self, camera_id, rtsp_url):
        """启动单个摄像头的分析"""
        if camera_id in self.cameras and self.cameras[camera_id]['running']:
            logger.info(f"摄像头 {camera_id} 的分析已在运行")
            return
        
        self.cameras[camera_id] = {
            'running': True,
            'rtsp_url': rtsp_url
        }
        
        # 启动图像检测线程（10秒截图）
        image_thread = threading.Thread(
            target=self._image_detection_loop,
            args=(camera_id, rtsp_url),
            daemon=True
        )
        image_thread.start()
        self.cameras[camera_id]['image_thread'] = image_thread
        
        # 启动视频检测线程（仅在启用时）
        if self.enable_video_detection:
            video_thread = threading.Thread(
                target=self._video_detection_loop,
                args=(camera_id, rtsp_url),
                daemon=True
            )
            video_thread.start()
            self.cameras[camera_id]['video_thread'] = video_thread
            logger.info(f"启动摄像头 {camera_id} 的图像和视频分析")
        else:
            logger.info(f"启动摄像头 {camera_id} 的图像分析（视频检测已禁用）")
    
    def _image_detection_loop(self, camera_id, rtsp_url):
        """图像检测循环 - 每10秒截图并检测"""
        logger.info(f"摄像头 {camera_id} 图像检测线程启动")
        
        last_capture_time = 0
        capture_interval = 10  # 10秒
        
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                current_time = time.time()
                
                if current_time - last_capture_time >= capture_interval:
                    # 使用FFmpeg截图
                    image_path = self._capture_image_ffmpeg(camera_id, rtsp_url)
                    
                    if image_path:
                        # 执行图像检测
                        self._perform_image_detections(camera_id, image_path)
                        last_capture_time = current_time
                    
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"摄像头 {camera_id} 图像检测异常: {str(e)}")
                time.sleep(5)
    
    def _video_detection_loop(self, camera_id, rtsp_url):
        """视频检测循环 - 每30秒录制3秒视频并检测"""
        logger.info(f"摄像头 {camera_id} 视频检测线程启动")
        
        last_capture_time = 0
        capture_interval = 30  # 30秒
        video_duration = 3  # 3秒（减少录制时长以避免超时）
        
        while camera_id in self.cameras and self.cameras[camera_id]['running']:
            try:
                current_time = time.time()
                
                if current_time - last_capture_time >= capture_interval:
                    # 使用FFmpeg录制视频片段
                    video_path = self._capture_video_ffmpeg(camera_id, rtsp_url, video_duration)
                    
                    if video_path:
                        # 执行视频检测（打架斗殴）
                        self._perform_video_detections(camera_id, video_path)
                        last_capture_time = current_time
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"摄像头 {camera_id} 视频检测异常: {str(e)}")
                time.sleep(5)
    
    def _capture_image_ffmpeg(self, camera_id, rtsp_url):
        """使用OpenCV截取单帧图像（优化版）"""
        cap = None
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"camera_{camera_id}_{timestamp}.jpg"
            filepath = os.path.join(self.media_root, 'images', filename)
            
            # 使用OpenCV快速截图
            cap = cv2.VideoCapture(rtsp_url)
            
            # 优化设置
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减小缓冲
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)  # 3秒超时
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)  # 3秒读取超时
            
            if not cap.isOpened():
                logger.warning(f"摄像头 {camera_id} 无法打开RTSP流")
                return None
            
            # 尝试读取5次，跳过前几帧（可能是损坏的）
            for i in range(5):
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    # 检查图像质量
                    if frame.shape[0] > 100 and frame.shape[1] > 100:
                        # 保存图像
                        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if success:
                            # 验证文件大小
                            file_size = os.path.getsize(filepath)
                            if file_size > 10000:  # 至少10KB
                                logger.info(f"摄像头 {camera_id} 截图成功: {filename} ({file_size/1024:.1f}KB)")
                                cap.release()
                                return f'/media/alarm_events/images/{filename}'
                            else:
                                logger.warning(f"摄像头 {camera_id} 截图文件过小: {file_size}B")
                                os.remove(filepath)
                time.sleep(0.3)
            
            logger.warning(f"摄像头 {camera_id} 截图失败: 无法获取有效帧")
            
        except Exception as e:
            logger.error(f"摄像头 {camera_id} 截图异常: {str(e)}")
        finally:
            if cap is not None:
                cap.release()
        
        return None
    
    def _capture_video_ffmpeg(self, camera_id, rtsp_url, duration):
        """使用FFmpeg录制RTSP流 - 优化版本"""
        filepath = None
        try:
            # 测试RTSP连接
            logger.debug(f"测试RTSP连接: {rtsp_url}")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"camera_{camera_id}_{timestamp}.mp4"
            filepath = os.path.join(self.media_root, 'videos', filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 优化的FFmpeg命令 - 针对不稳定RTSP流
            # -loglevel warning: 减少日志输出
            # -rtsp_transport tcp: 使用TCP传输（UDP可能丢包）
            # -timeout 3000000: 3秒连接超时 (微秒)
            # -analyzeduration 1000000: 快速分析流（1秒）
            # -probesize 500000: 减小探测大小（500KB）
            # -fflags nobuffer: 禁用缓冲，减少延迟
            # -flags low_delay: 低延迟模式
            # -err_detect ignore_err: 忽略错误，继续处理
            # -i: 输入RTSP流
            # -t: 录制时长（秒）
            # -vf fps=10: 强制帧率为10fps
            # -c:v libx264: 重新编码为H.264
            # -preset ultrafast: 最快编码速度
            # -crf 30: 质量系数（30=低质量，文件更小）
            # -an: 不录音频
            # -y: 覆盖已存在文件
            ffmpeg_cmd = [
                'ffmpeg',
                '-loglevel', 'warning',
                '-rtsp_transport', 'tcp',
                '-timeout', '3000000',
                '-analyzeduration', '1000000',
                '-probesize', '500000',
                '-fflags', 'nobuffer',
                '-flags', 'low_delay',
                '-err_detect', 'ignore_err',
                '-i', rtsp_url,
                '-t', str(duration),
                '-vf', 'fps=10',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '30',
                '-an',
                '-y',
                filepath
            ]
            
            logger.info(f"🎬 开始录制摄像头 {camera_id}，时长 {duration}秒")
            
            # 执行FFmpeg命令 - 使用更短的超时时间
            # 如果5秒视频超过10秒还没完成，说明流有问题
            timeout_seconds = duration + 10
            result = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                text=True
            )
            
            # 检查FFmpeg返回码
            if result.returncode != 0:
                logger.error(f"FFmpeg退出码: {result.returncode}")
            
            # 输出FFmpeg错误信息（用于调试）
            if result.stderr:
                # 过滤掉常见的无害警告
                stderr_lines = result.stderr.split('\n')
                important_errors = [line for line in stderr_lines 
                                   if any(keyword in line.lower() for keyword in 
                                         ['error', 'failed', 'unable', 'cannot', 'timeout', 'connection'])]
                if important_errors:
                    logger.warning(f"FFmpeg错误: {'; '.join(important_errors[:3])}")
                else:
                    logger.debug(f"FFmpeg stderr: {result.stderr[:300]}")
            
            # 检查文件
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                if file_size > 5000:  # 降低最小大小要求到5KB
                    logger.info(f"✅ 摄像头 {camera_id} 录制成功: {filename} ({file_size/1024:.1f}KB)")
                    return f'/media/alarm_events/videos/{filename}'
                else:
                    logger.warning(f"摄像头 {camera_id} 文件过小({file_size}B)，删除")
                    os.remove(filepath)
            else:
                logger.warning(f"摄像头 {camera_id} 文件未生成")
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"摄像头 {camera_id} FFmpeg超时")
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
        except FileNotFoundError:
            logger.error(f"FFmpeg未安装！请执行: apt-get install ffmpeg")
            return None  # 不再重试
        except Exception as e:
            logger.error(f"摄像头 {camera_id} 录制异常: {str(e)}")
            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
        
        return None
    
    def _perform_image_detections(self, camera_id, image_path):
        """执行图像检测：行为(吸烟、打电话)、火灾烟雾、垃圾、翻越"""
        from .models import Camera, AlarmEvent
        import requests
        
        try:
            camera = Camera.objects.get(id=camera_id)
            full_path = f'/root/Dog2/admin/backend{image_path}'
            
            # 检查文件是否存在
            if not os.path.exists(full_path):
                logger.error(f"图像文件不存在: {full_path}")
                return
            
            # 1. 行为检测 (吸烟、打电话)
            try:
                with open(full_path, 'rb') as f:
                    files = {'file': (os.path.basename(full_path), f, 'image/jpeg')}
                    response = requests.post(
                        'http://127.0.0.1:8003/api/detect-behavior',
                        files=files,
                        timeout=10
                    )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"👤 行为检测结果: {result}")
                    if result.get('has_warning', False):
                        warnings = result.get('warnings', [])
                        for warning in warnings:
                            warning_type = warning.get('type')
                            confidence = warning.get('confidence', 0.8)
                            
                            if warning_type == 'smoke':
                                logger.info(f"⚠️ 检测到吸烟行为！置信度: {confidence:.2%}, 准备创建报警事件...")
                                self._create_alarm_event(
                                    camera=camera,
                                    event_type='smoking',
                                    title='检测到吸烟行为',
                                    description=f"检测到有人在监控区域吸烟, 置信度: {confidence:.2%}",
                                    image_path=image_path,
                                    confidence=confidence,
                                    detection_data=result,
                                    severity='medium'
                                )
                            elif warning_type == 'phone':
                                logger.info(f"⚠️ 检测到使用电话！置信度: {confidence:.2%}, 准备创建报警事件...")
                                self._create_alarm_event(
                                    camera=camera,
                                    event_type='phone',
                                    title='检测到使用电话',
                                    description=f"检测到有人在监控区域使用电话, 置信度: {confidence:.2%}",
                                    image_path=image_path,
                                    confidence=confidence,
                                    detection_data=result,
                                    severity='low'
                                )
                    else:
                        logger.info(f"✓ 行为检测：未发现异常")
            except Exception as e:
                logger.error(f"行为检测失败: {str(e)}")
            
            # 2. 火灾烟雾检测 (使用文件上传)
            try:
                with open(full_path, 'rb') as f:
                    files = {'file': (os.path.basename(full_path), f, 'image/jpeg')}
                    response = requests.post(
                        'http://127.0.0.1:8003/api/detect-firesmoke',
                        files=files,
                        timeout=10
                    )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"🔥 火灾烟雾检测结果: {result}")
                    if result.get('has_firesmoke', False):
                        # 从detections数组中提取最高置信度
                        detections = result.get('detections', [])
                        confidence = max([d.get('confidence', 0.8) for d in detections]) if detections else 0.8
                        logger.info(f"⚠️ 检测到火灾或烟雾！置信度: {confidence:.2%}, 准备创建报警事件...")
                        self._create_alarm_event(
                            camera=camera,
                            event_type='fire',
                            title='检测到火灾或烟雾',
                            description=f"检测到火灾或烟雾, 置信度: {confidence:.2%}",
                            image_path=image_path,
                            confidence=confidence,
                            detection_data=result,
                            severity='critical'
                        )
                    else:
                        logger.info(f"✓ 火灾烟雾检测：未发现异常")
            except Exception as e:
                logger.error(f"火灾烟雾检测失败: {str(e)}")
            
            # 3. 垃圾检测
            try:
                with open(full_path, 'rb') as f:
                    files = {'file': (os.path.basename(full_path), f, 'image/jpeg')}
                    response = requests.post(
                        'http://127.0.0.1:8003/api/detect-rubbish',
                        files=files,
                        timeout=10
                    )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"🗑️ 垃圾检测结果: {result}")
                    if result.get('has_rubbish', False):
                        # 从detections数组中提取最高置信度
                        detections = result.get('detections', [])
                        confidence = max([d.get('confidence', 0.8) for d in detections]) if detections else 0.8
                        logger.info(f"⚠️ 检测到垃圾！置信度: {confidence:.2%}, 准备创建报警事件...")
                        self._create_alarm_event(
                            camera=camera,
                            event_type='rubbish',
                            title='检测到垃圾',
                            description=f"检测到垃圾物品, 置信度: {confidence:.2%}",
                            image_path=image_path,
                            confidence=confidence,
                            detection_data=result,
                            severity='medium'
                        )
                    else:
                        logger.info(f"✓ 垃圾检测：未发现异常")
            except Exception as e:
                logger.error(f"垃圾检测失败: {str(e)}")
            
            # 4. 翻越检测
            try:
                with open(full_path, 'rb') as f:
                    files = {'file': (os.path.basename(full_path), f, 'image/jpeg')}
                    response = requests.post(
                        'http://127.0.0.1:8003/api/detect-cross',
                        files=files,
                        timeout=10
                    )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"🚶 翻越检测结果: {result}")
                    if result.get('has_cross', False):
                        # 从detections数组中提取最高置信度
                        detections = result.get('detections', [])
                        confidence = max([d.get('confidence', 0.8) for d in detections]) if detections else 0.8
                        logger.info(f"⚠️ 检测到翻越行为！置信度: {confidence:.2%}, 准备创建报警事件...")
                        self._create_alarm_event(
                            camera=camera,
                            event_type='crossover',
                            title='检测到翻越行为',
                            description=f"检测到翻越围栏, 置信度: {confidence:.2%}",
                            image_path=image_path,
                            confidence=confidence,
                            detection_data=result,
                            severity='high'
                        )
                    else:
                        logger.info(f"✓ 翻越检测：未发现异常")
            except Exception as e:
                logger.error(f"翻越检测失败: {str(e)}")
            
        except Exception as e:
            logger.error(f"图像检测异常: {str(e)}")
    
    def _perform_video_detections(self, camera_id, video_path):
        """执行视频检测：打架斗殴"""
        from .models import Camera, AlarmEvent
        import requests
        
        try:
            camera = Camera.objects.get(id=camera_id)
            full_path = f'/root/Dog2/admin/backend{video_path}'
            
            # 检查文件是否存在
            if not os.path.exists(full_path):
                logger.error(f"视频文件不存在: {full_path}")
                return
            
            # 行为检测 (使用文件上传)
            try:
                with open(full_path, 'rb') as f:
                    files = {'file': (os.path.basename(full_path), f, 'video/avi')}
                    response = requests.post(
                        'http://127.0.0.1:8003/api/detect-behavior',
                        files=files,
                        timeout=60
                    )
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"🥊 行为检测结果: {result}")
                    if result.get('has_warning', False):
                        # 从warnings数组中提取最高置信度
                        warnings = result.get('warnings', [])
                        confidence = max([w.get('confidence', 0.8) for w in warnings]) if warnings else 0.8
                        logger.info(f"⚠️ 检测到异常行为！置信度: {confidence:.2%}, 准备创建报警事件...")
                        self._create_alarm_event(
                            camera=camera,
                            event_type='fighting',
                            title='检测到异常行为',
                            description=f"检测到打架、奔跑等异常行为, 置信度: {confidence:.2%}",
                            video_path=video_path,
                            confidence=confidence,
                            detection_data=result,
                            severity='high'
                        )
                    else:
                        logger.info(f"✓ 行为检测：未发现异常")
            except Exception as e:
                logger.error(f"行为检测失败: {str(e)}")
            
        except Exception as e:
            logger.error(f"视频检测异常: {str(e)}")
    
    def _create_alarm_event(self, camera, event_type, title, description, 
                           image_path=None, video_path=None, confidence=0.0, 
                           detection_data=None, severity='medium'):
        """创建报警事件"""
        from .models import AlarmEvent
        
        try:
            logger.info(f"准备创建报警事件 - 类型: {event_type}, 标题: {title}, 摄像头: {camera.id}")
            
            alarm = AlarmEvent.objects.create(
                dog=camera.dog,
                camera=camera,
                event_type=event_type,
                severity=severity,
                status='pending',
                title=title,
                description=description,
                image_path=image_path,
                video_path=video_path,
                confidence=confidence,
                detection_data=detection_data,
                detected_at=timezone.now()
            )
            logger.info(f"✅ 成功创建报警事件 ID: {alarm.id} - {title} - 严重程度: {severity}")
            
            # 验证事件是否真的保存到数据库
            count = AlarmEvent.objects.count()
            logger.info(f"📊 当前数据库中共有 {count} 条报警事件")
            
            return alarm
        except Exception as e:
            logger.error(f"❌ 创建报警事件失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def stop_camera_analysis(self, camera_id):
        """停止摄像头分析"""
        if camera_id in self.cameras:
            self.cameras[camera_id]['running'] = False
            del self.cameras[camera_id]
            logger.info(f"停止摄像头 {camera_id} 的视频分析")
    
    def stop_all(self):
        """停止所有分析"""
        self.running = False
        for camera_id in list(self.cameras.keys()):
            self.stop_camera_analysis(camera_id)
        logger.info("停止所有视频分析")

# 全局实例
video_analysis_service = VideoAnalysisService()

