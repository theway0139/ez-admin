#!/usr/bin/env python
"""初始化报警系统：创建表、添加测试数据、启动视频分析"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from ops.models import Dog, Camera, AlarmEvent
from ops.video_analysis_service import video_analysis_service

print("=" * 60)
print("初始化报警系统")
print("=" * 60)

# 步骤1: 创建数据库表
print("\n[1/3] 创建数据库表...")
try:
    with connection.cursor() as cursor:
        # 创建Dog表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops_dog (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dog_id VARCHAR(50) UNIQUE DEFAULT 'DOG_DEFAULT',
            location VARCHAR(200) NOT NULL,
            status VARCHAR(20) DEFAULT 'offline',
            description TEXT,
            created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
        )
        ''')
        
        # 创建Camera表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops_camera (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dog_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            camera_id VARCHAR(50) UNIQUE DEFAULT 'CAM_DEFAULT',
            rtsp_url VARCHAR(500) NOT NULL,
            location VARCHAR(200) NOT NULL,
            status VARCHAR(20) DEFAULT 'offline',
            resolution VARCHAR(20) DEFAULT '1920x1080',
            fps INT DEFAULT 25,
            description TEXT,
            created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            FOREIGN KEY (dog_id) REFERENCES ops_dog(id) ON DELETE CASCADE
        )
        ''')
        
        # 创建AlarmEvent表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ops_alarmevent (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dog_id INT NOT NULL,
            camera_id INT NOT NULL,
            event_type VARCHAR(20) NOT NULL,
            severity VARCHAR(20) DEFAULT 'medium',
            status VARCHAR(20) DEFAULT 'pending',
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            image_path VARCHAR(500),
            video_path VARCHAR(500),
            confidence DOUBLE DEFAULT 0.0,
            detection_data JSON,
            detected_at DATETIME(6) NOT NULL,
            handled_at DATETIME(6),
            created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            handler_id INT,
            handle_note TEXT,
            FOREIGN KEY (dog_id) REFERENCES ops_dog(id) ON DELETE CASCADE,
            FOREIGN KEY (camera_id) REFERENCES ops_camera(id) ON DELETE CASCADE,
            INDEX idx_detected_at (detected_at),
            INDEX idx_event_status (event_type, status),
            INDEX idx_camera_time (camera_id, detected_at)
        )
        ''')
        print("✅ 数据库表创建成功")
except Exception as e:
    print(f"❌ 创建表失败: {str(e)}")
    exit(1)

# 步骤2: 添加测试数据
print("\n[2/3] 添加测试数据...")
try:
    # 检查是否已有数据
    if Dog.objects.exists():
        print("⚠️  数据已存在，跳过创建")
        dog = Dog.objects.first()
        camera = Camera.objects.first()
    else:
        # 创建虚拟犬
        dog = Dog.objects.create(
            name="测试虚拟犬1号",
            dog_id="DOG001",
            location="园区A栋",
            status="active",
            description="用于测试的虚拟犬"
        )
        print(f"✅ 创建虚拟犬: {dog.name}")
        
        # 创建摄像头（使用您的RTSP URL）
        camera = Camera.objects.create(
            dog=dog,
            name="监控摄像头1",
            camera_id="CAM001",
            rtsp_url="rtsp://36.139.10.47:25544/live/RPWtWUrhCDphd_01?expired=20251231110240",
            location="监控区域1",
            status="online",
            resolution="1920x1080",
            fps=25,
            description="主监控摄像头"
        )
        print(f"✅ 创建摄像头: {camera.name}")
        print(f"   RTSP URL: {camera.rtsp_url}")
except Exception as e:
    print(f"❌ 添加测试数据失败: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# 步骤3: 启动视频分析服务
print("\n[3/3] 启动视频分析服务...")
try:
    video_analysis_service.start_all_cameras()
    print(f"✅ 视频分析服务已启动")
    print(f"   监控摄像头数量: {len(video_analysis_service.cameras)}")
except Exception as e:
    print(f"❌ 启动视频分析服务失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("初始化完成！")
print("=" * 60)
print("\n提示：")
print("1. 检查摄像头状态：http://172.16.160.100:8003/api2/video-analysis/status")
print("2. 查看报警事件：http://172.16.160.100:8003/api2/alarm-events")
print("3. 如需修改RTSP地址，请编辑此脚本中的 rtsp_url")
print()

