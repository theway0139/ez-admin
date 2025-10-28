#!/usr/bin/env python
"""
创建狗和摄像头测试数据脚本
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ops.models import Dog, Camera, AlarmEvent

def create_dog_camera_data():
    print("开始创建狗和摄像头测试数据...")
    
    # 创建虚拟狗
    dog_data = {
        'name': '智能监控狗',
        'breed': '德国牧羊犬',
        'status': 'active',
        'location': '监控中心',
        'description': '智能监控系统虚拟狗，负责实时监控和异常检测'
    }
    
    dog, created = Dog.objects.get_or_create(
        name=dog_data['name'],
        defaults=dog_data
    )
    print(f"创建狗: {dog.name}")
    
    # 创建摄像头
    camera_data = {
        'dog': dog,
        'name': '主监控摄像头',
        'ip_address': '36.139.10.47',
        'port': 25544,
        'rtsp_url': 'rtsp://36.139.10.47:25544/live/RPWtWUrhCDphd_01?expired=20251231110240',
        'status': 'online',
        'location': '监控中心主摄像头',
        'resolution': '1920x1080',
        'fps': 25,
        'is_recording': True
    }
    
    camera, created = Camera.objects.get_or_create(
        dog=dog,
        name=camera_data['name'],
        defaults=camera_data
    )
    print(f"创建摄像头: {camera.name}")
    
    # 创建一些模拟的报警事件
    event_types = [
        ('smoking', '吸烟检测'),
        ('phone', '电话检测'),
        ('fire', '火灾检测'),
        ('stranger', '陌生人检测'),
        ('fighting', '打架斗殴'),
    ]
    
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['pending', 'processing', 'resolved', 'ignored']
    
    for i in range(20):
        event_type, event_name = random.choice(event_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        # 随机时间（最近30天内）
        detected_time = datetime.now() - timedelta(days=random.randint(0, 30))
        
        event = AlarmEvent.objects.create(
            dog=dog,
            camera=camera,
            event_type=event_type,
            severity=severity,
            status=status,
            title=f"{event_name}事件 #{i+1}",
            description=f"在{camera.location}检测到{event_name}，置信度: {random.uniform(0.6, 0.95):.2f}",
            image_path=f"media/screenshots/{dog.id}/{camera.id}/screenshot_{detected_time.strftime('%Y%m%d_%H%M%S')}.jpg",
            video_path=f"media/videos/{dog.id}/{camera.id}/video_{detected_time.strftime('%Y%m%d_%H%M%S')}.mp4" if event_type == 'fighting' else None,
            confidence=random.uniform(0.6, 0.95),
            detected_at=detected_time,
            resolution_notes=f"处理备注 #{i+1}" if status == 'resolved' else None
        )
        
        print(f"创建报警事件: {event.title}")
    
    print("测试数据创建完成！")
    print(f"狗数量: {Dog.objects.count()}")
    print(f"摄像头数量: {Camera.objects.count()}")
    print(f"报警事件数量: {AlarmEvent.objects.count()}")

if __name__ == '__main__':
    create_dog_camera_data()
