"""
视频流处理服务
"""
import cv2
import numpy as np
import os
import time
import threading
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Dog, Camera, AlarmEvent
from .log_utils import LogRecorder

logger = logging.getLogger(__name__)

class VideoStreamProcessor:
    """视频流处理器"""
    
    def __init__(self):
        self.running = False
        self.threads = {}
        self.last_screenshot_time = {}
        self.last_video_time = {}
        
    def start_processing(self):
        """启动所有摄像头的视频流处理"""
        self.running = True
        cameras = Camera.objects.filter(status='online')
        
        for camera in cameras:
            if camera.id not in self.threads:
                thread = threading.Thread(
                    target=self._process_camera_stream,
                    args=(camera,),
                    daemon=True
                )
                thread.start()
                self.threads[camera.id] = thread
                logger.info(f"启动摄像头 {camera.name} 的视频流处理")
    
    def stop_processing(self):
        """停止所有视频流处理"""
        self.running = False
        for thread in self.threads.values():
            thread.join(timeout=5)
        self.threads.clear()
        logger.info("停止所有视频流处理")
    
    def _process_camera_stream(self, camera):
        """处理单个摄像头的视频流"""
        cap = None
        try:
            # 连接RTSP流
            cap = cv2.VideoCapture(camera.rtsp_url)
            if not cap.isOpened():
                logger.error(f"无法连接到摄像头 {camera.name}: {camera.rtsp_url}")
                return
            
            logger.info(f"开始处理摄像头 {camera.name} 的视频流")
            frame_count = 0
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"摄像头 {camera.name} 读取帧失败")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                current_time = timezone.now()
                
                # 每10秒截图一次，用于吸烟、电话、火灾、陌生人检测
                if self._should_take_screenshot(camera.id, current_time):
                    self._take_screenshot_and_detect(camera, frame, current_time)
                
                # 每30秒截取5秒视频，用于打架斗殴检测
                if self._should_record_video(camera.id, current_time):
                    self._record_video_for_fight_detection(camera, cap, current_time)
                
                # 控制帧率
                time.sleep(1.0 / camera.fps)
                
        except Exception as e:
            logger.error(f"处理摄像头 {camera.name} 视频流时出错: {str(e)}")
        finally:
            if cap:
                cap.release()
    
    def _should_take_screenshot(self, camera_id, current_time):
        """判断是否应该截图"""
        if camera_id not in self.last_screenshot_time:
            self.last_screenshot_time[camera_id] = current_time - timedelta(seconds=10)
        
        return (current_time - self.last_screenshot_time[camera_id]).total_seconds() >= 10
    
    def _should_record_video(self, camera_id, current_time):
        """判断是否应该录制视频"""
        if camera_id not in self.last_video_time:
            self.last_video_time[camera_id] = current_time - timedelta(seconds=30)
        
        return (current_time - self.last_video_time[camera_id]).total_seconds() >= 30
    
    def _take_screenshot_and_detect(self, camera, frame, current_time):
        """截图并进行检测"""
        try:
            # 保存截图
            screenshot_dir = f"media/screenshots/{camera.dog.id}/{camera.id}"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            timestamp_str = current_time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"{screenshot_dir}/screenshot_{timestamp_str}.jpg"
            
            cv2.imwrite(screenshot_path, frame)
            self.last_screenshot_time[camera.id] = current_time
            
            # 进行各种检测
            self._detect_smoking(camera, frame, screenshot_path, current_time)
            self._detect_phone(camera, frame, screenshot_path, current_time)
            self._detect_fire(camera, frame, screenshot_path, current_time)
            self._detect_stranger(camera, frame, screenshot_path, current_time)
            
        except Exception as e:
            logger.error(f"截图检测失败: {str(e)}")
    
    def _record_video_for_fight_detection(self, camera, cap, current_time):
        """录制视频用于打架斗殴检测"""
        try:
            video_dir = f"media/videos/{camera.dog.id}/{camera.id}"
            os.makedirs(video_dir, exist_ok=True)
            
            timestamp_str = current_time.strftime("%Y%m%d_%H%M%S")
            video_path = f"{video_dir}/video_{timestamp_str}.mp4"
            
            # 录制5秒视频
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_path, fourcc, camera.fps, (frame.shape[1], frame.shape[0]))
            
            start_time = time.time()
            while time.time() - start_time < 5:  # 录制5秒
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                time.sleep(1.0 / camera.fps)
            
            out.release()
            self.last_video_time[camera.id] = current_time
            
            # 进行打架斗殴检测
            self._detect_fighting(camera, video_path, current_time)
            
        except Exception as e:
            logger.error(f"视频录制和打架检测失败: {str(e)}")
    
    def _detect_smoking(self, camera, frame, image_path, current_time):
        """吸烟检测"""
        try:
            # 调用吸烟检测API
            import requests
            import base64
            
            # 将帧编码为base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 调用检测API
            response = requests.post(
                f'http://172.16.160.100:8003/api2/detect/smoking',
                json={'image': img_base64},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0.0)
                
                if confidence > 0.7:  # 检测到吸烟
                    self._create_alarm_event(
                        camera=camera,
                        event_type='smoking',
                        title="检测到吸烟行为",
                        description=f"在摄像头 {camera.name} 检测到吸烟行为，置信度: {confidence:.2f}",
                        image_path=image_path,
                        confidence=confidence,
                        detected_at=current_time
                    )
        except Exception as e:
            logger.error(f"吸烟检测失败: {str(e)}")
            # 如果API调用失败，使用模拟检测
            confidence = np.random.random() * 0.3
            if confidence > 0.7:
                self._create_alarm_event(
                    camera=camera,
                    event_type='smoking',
                    title="检测到吸烟行为",
                    description=f"在摄像头 {camera.name} 检测到吸烟行为，置信度: {confidence:.2f}",
                    image_path=image_path,
                    confidence=confidence,
                    detected_at=current_time
                )
    
    def _detect_phone(self, camera, frame, image_path, current_time):
        """电话检测"""
        try:
            import requests
            import base64
            
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            response = requests.post(
                f'http://172.16.160.100:8003/api2/detect/phone',
                json={'image': img_base64},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0.0)
                
                if confidence > 0.7:
                    self._create_alarm_event(
                        camera=camera,
                        event_type='phone',
                        title="检测到电话使用",
                        description=f"在摄像头 {camera.name} 检测到电话使用，置信度: {confidence:.2f}",
                        image_path=image_path,
                        confidence=confidence,
                        detected_at=current_time
                    )
        except Exception as e:
            logger.error(f"电话检测失败: {str(e)}")
            confidence = np.random.random() * 0.3
            if confidence > 0.7:
                self._create_alarm_event(
                    camera=camera,
                    event_type='phone',
                    title="检测到电话使用",
                    description=f"在摄像头 {camera.name} 检测到电话使用，置信度: {confidence:.2f}",
                    image_path=image_path,
                    confidence=confidence,
                    detected_at=current_time
                )
    
    def _detect_fire(self, camera, frame, image_path, current_time):
        """火灾检测"""
        try:
            import requests
            import base64
            
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            response = requests.post(
                f'http://172.16.160.100:8003/api2/detect/fire',
                json={'image': img_base64},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0.0)
                
                if confidence > 0.8:
                    self._create_alarm_event(
                        camera=camera,
                        event_type='fire',
                        title="检测到火灾",
                        description=f"在摄像头 {camera.name} 检测到火灾，置信度: {confidence:.2f}",
                        image_path=image_path,
                        confidence=confidence,
                        detected_at=current_time,
                        severity='critical'
                    )
        except Exception as e:
            logger.error(f"火灾检测失败: {str(e)}")
            confidence = np.random.random() * 0.2
            if confidence > 0.8:
                self._create_alarm_event(
                    camera=camera,
                    event_type='fire',
                    title="检测到火灾",
                    description=f"在摄像头 {camera.name} 检测到火灾，置信度: {confidence:.2f}",
                    image_path=image_path,
                    confidence=confidence,
                    detected_at=current_time,
                    severity='critical'
                )
    
    def _detect_stranger(self, camera, frame, image_path, current_time):
        """陌生人检测"""
        try:
            import requests
            import base64
            
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            response = requests.post(
                f'http://172.16.160.100:8003/api2/detect/stranger',
                json={'image': img_base64},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0.0)
                
                if confidence > 0.6:
                    self._create_alarm_event(
                        camera=camera,
                        event_type='stranger',
                        title="检测到陌生人",
                        description=f"在摄像头 {camera.name} 检测到陌生人，置信度: {confidence:.2f}",
                        image_path=image_path,
                        confidence=confidence,
                        detected_at=current_time
                    )
        except Exception as e:
            logger.error(f"陌生人检测失败: {str(e)}")
            confidence = np.random.random() * 0.4
            if confidence > 0.6:
                self._create_alarm_event(
                    camera=camera,
                    event_type='stranger',
                    title="检测到陌生人",
                    description=f"在摄像头 {camera.name} 检测到陌生人，置信度: {confidence:.2f}",
                    image_path=image_path,
                    confidence=confidence,
                    detected_at=current_time
                )
    
    def _detect_fighting(self, camera, video_path, current_time):
        """打架斗殴检测"""
        try:
            import requests
            import base64
            
            # 读取视频文件并编码为base64
            with open(video_path, 'rb') as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            response = requests.post(
                f'http://172.16.160.100:8003/api2/detect/fighting',
                json={'video': video_base64},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence', 0.0)
                
                if confidence > 0.7:
                    self._create_alarm_event(
                        camera=camera,
                        event_type='fighting',
                        title="检测到打架斗殴",
                        description=f"在摄像头 {camera.name} 检测到打架斗殴行为，置信度: {confidence:.2f}",
                        video_path=video_path,
                        confidence=confidence,
                        detected_at=current_time,
                        severity='high'
                    )
        except Exception as e:
            logger.error(f"打架检测失败: {str(e)}")
            confidence = np.random.random() * 0.3
            if confidence > 0.7:
                self._create_alarm_event(
                    camera=camera,
                    event_type='fighting',
                    title="检测到打架斗殴",
                    description=f"在摄像头 {camera.name} 检测到打架斗殴行为，置信度: {confidence:.2f}",
                    video_path=video_path,
                    confidence=confidence,
                    detected_at=current_time,
                    severity='high'
                )
    
    def _create_alarm_event(self, camera, event_type, title, description, 
                           image_path=None, video_path=None, confidence=0.0, 
                           detected_at=None, severity='medium'):
        """创建报警事件"""
        try:
            alarm_event = AlarmEvent.objects.create(
                dog=camera.dog,
                camera=camera,
                event_type=event_type,
                severity=severity,
                title=title,
                description=description,
                image_path=image_path,
                video_path=video_path,
                confidence=confidence,
                detected_at=detected_at or timezone.now()
            )
            
            logger.info(f"创建报警事件: {alarm_event}")
            
            # 记录操作日志
            LogRecorder.log_user_action(
                request=None,
                action_type='alarm',
                target=f"报警事件-{event_type}",
                detail=f"检测到{alarm_event.get_event_type_display()}事件",
                result='success'
            )
            
        except Exception as e:
            logger.error(f"创建报警事件失败: {str(e)}")


# 全局视频流处理器实例
video_processor = VideoStreamProcessor()
