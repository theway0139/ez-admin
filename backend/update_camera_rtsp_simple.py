#!/usr/bin/env python
"""
简单的摄像头RTSP地址更新脚本
使用方法: python manage.py shell < update_camera_rtsp_simple.py
"""
from ops.models import Camera

# 新的RTSP地址
NEW_RTSP_URL = "rtsp://36.139.10.47:25544/live/RPWtWUrhCDphd_01?expired=20251231110240"

# 列出所有摄像头
print("\n" + "="*80)
print("当前数据库中的摄像头列表:")
print("="*80)
cameras = Camera.objects.all()
for cam in cameras:
    print(f"ID: {cam.id} | 名称: {cam.name} | 编号: {cam.camera_id}")
    print(f"当前RTSP: {cam.rtsp_url}")
    print("-"*80)

print(f"\n总计: {cameras.count()} 个摄像头")

# 如果有摄像头，询问是否更新
if cameras.exists():
    camera_id = input("\n请输入要更新的摄像头ID (输入'all'更新所有, 输入'exit'退出): ").strip()
    
    if camera_id.lower() == 'exit':
        print("已退出")
    elif camera_id.lower() == 'all':
        confirm = input(f"确认要更新所有 {cameras.count()} 个摄像头吗? (yes/no): ").strip().lower()
        if confirm == 'yes':
            count = 0
            for cam in cameras:
                old_url = cam.rtsp_url
                cam.rtsp_url = NEW_RTSP_URL
                cam.save()
                print(f"✅ 更新摄像头 {cam.name} (ID: {cam.id})")
                count += 1
            print(f"\n成功更新 {count} 个摄像头")
        else:
            print("已取消")
    else:
        try:
            cam = Camera.objects.get(id=int(camera_id))
            old_url = cam.rtsp_url
            cam.rtsp_url = NEW_RTSP_URL
            cam.save()
            print(f"\n✅ 成功更新摄像头 {cam.name} (ID: {cam.id})")
            print(f"   旧地址: {old_url}")
            print(f"   新地址: {NEW_RTSP_URL}")
        except Camera.DoesNotExist:
            print(f"❌ 摄像头 ID {camera_id} 不存在")
        except ValueError:
            print("❌ 无效的摄像头ID")
else:
    print("\n⚠️ 数据库中没有摄像头记录")

