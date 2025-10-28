#!/usr/bin/env python3
"""
测试报警事件创建脚本
用于验证检测结果能否正确创建报警事件
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/root/Dog2/admin/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ops.models import Camera, AlarmEvent
from django.utils import timezone

def test_create_alarm():
    """测试创建报警事件"""
    try:
        # 获取第一个摄像头
        camera = Camera.objects.first()
        if not camera:
            print("❌ 没有找到摄像头")
            return
        
        print(f"✓ 使用摄像头: {camera.name} (ID: {camera.id})")
        
        # 创建测试报警事件
        alarm = AlarmEvent.objects.create(
            dog=camera.dog,
            camera=camera,
            event_type='fire',
            severity='critical',
            status='pending',
            title='测试：检测到火灾',
            description='这是一个测试报警事件',
            image_path='/test/image.jpg',
            confidence=0.95,
            detected_at=timezone.now()
        )
        
        print(f"✅ 成功创建测试报警事件 ID: {alarm.id}")
        
        # 查询所有报警事件
        total = AlarmEvent.objects.count()
        print(f"📊 数据库中共有 {total} 条报警事件")
        
        # 显示最近5条
        recent = AlarmEvent.objects.order_by('-detected_at')[:5]
        print("\n最近5条报警事件：")
        for event in recent:
            print(f"  - ID: {event.id}, 类型: {event.event_type}, 标题: {event.title}, 时间: {event.detected_at}")
        
        # 删除测试事件
        alarm.delete()
        print(f"\n✓ 已删除测试事件")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_create_alarm()

