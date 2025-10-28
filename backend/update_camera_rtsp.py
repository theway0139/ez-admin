#!/usr/bin/env python
"""
更新摄像头RTSP地址脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ops.models import Camera

# 新的RTSP地址
NEW_RTSP_URL = "rtsp://36.139.10.47:25544/live/RPWtWUrhCDphd_01?expired=20251231110240"

def list_cameras():
    """列出所有摄像头"""
    cameras = Camera.objects.all()
    print("\n" + "="*80)
    print("当前数据库中的摄像头列表:")
    print("="*80)
    for cam in cameras:
        print(f"ID: {cam.id}")
        print(f"名称: {cam.name}")
        print(f"编号: {cam.camera_id}")
        print(f"状态: {cam.get_status_display()}")
        print(f"RTSP地址: {cam.rtsp_url}")
        print(f"所属虚拟犬: {cam.dog.name}")
        print("-"*80)
    print(f"总计: {cameras.count()} 个摄像头\n")
    return cameras

def update_camera_rtsp(camera_id, new_rtsp_url):
    """更新指定摄像头的RTSP地址"""
    try:
        camera = Camera.objects.get(id=camera_id)
        old_url = camera.rtsp_url
        camera.rtsp_url = new_rtsp_url
        camera.save()
        
        print(f"✅ 成功更新摄像头 {camera.name} (ID: {camera_id})")
        print(f"   旧地址: {old_url}")
        print(f"   新地址: {new_rtsp_url}")
        return True
    except Camera.DoesNotExist:
        print(f"❌ 摄像头 ID {camera_id} 不存在")
        return False
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
        return False

def update_all_cameras_rtsp(new_rtsp_url):
    """更新所有摄像头的RTSP地址"""
    cameras = Camera.objects.all()
    success_count = 0
    
    for camera in cameras:
        old_url = camera.rtsp_url
        camera.rtsp_url = new_rtsp_url
        camera.save()
        print(f"✅ 更新摄像头 {camera.name} (ID: {camera.id})")
        success_count += 1
    
    print(f"\n总计更新 {success_count}/{cameras.count()} 个摄像头")

if __name__ == '__main__':
    # 1. 先列出所有摄像头
    cameras = list_cameras()
    
    if cameras.count() == 0:
        print("⚠️ 数据库中没有摄像头记录")
        exit(0)
    
    # 2. 询问更新方式
    print("\n请选择更新方式:")
    print("1. 更新指定摄像头")
    print("2. 更新所有摄像头")
    print("3. 退出")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        camera_id = input("请输入要更新的摄像头ID: ").strip()
        try:
            camera_id = int(camera_id)
            update_camera_rtsp(camera_id, NEW_RTSP_URL)
        except ValueError:
            print("❌ 无效的摄像头ID")
    elif choice == '2':
        confirm = input(f"确认要更新所有 {cameras.count()} 个摄像头的RTSP地址吗? (yes/no): ").strip().lower()
        if confirm == 'yes':
            update_all_cameras_rtsp(NEW_RTSP_URL)
        else:
            print("已取消")
    else:
        print("退出")

