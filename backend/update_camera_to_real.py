#!/usr/bin/env python
"""
更新数据库中的摄像头为真实海康摄像头
IP: 172.16.160.43
用户: admin
密码: okwy1234
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ops.models import Camera, Dog

# 真实摄像头配置
CAMERA_IP = "172.16.160.43"
CAMERA_USER = "admin"
CAMERA_PASSWORD = "okwy1234"
CAMERA_PORT = 554

# 海康摄像头的RTSP地址格式
# 主码流：rtsp://username:password@ip:port/Streaming/Channels/101
# 子码流：rtsp://username:password@ip:port/Streaming/Channels/102
def generate_rtsp_url(channel=1, sub_stream=False):
    """
    生成海康摄像头RTSP地址
    channel: 通道号（通常从1开始）
    sub_stream: True=子码流（更流畅），False=主码流（高清）
    """
    stream_id = channel * 100 + (2 if sub_stream else 1)
    return f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/Streaming/Channels/{stream_id}"

def update_cameras():
    """更新数据库中的摄像头配置"""
    
    # 获取所有摄像头
    cameras = Camera.objects.all()
    
    if cameras.count() == 0:
        print("❌ 数据库中没有摄像头记录")
        
        # 创建一个测试摄像头
        print("\n创建新的摄像头记录...")
        
        # 先获取或创建一个虚拟犬
        dog, created = Dog.objects.get_or_create(
            dog_id='DOG001',
            defaults={
                'name': '巡逻犬01',
                'location': 'A区',
                'status': 'active',
                'description': '测试巡逻犬'
            }
        )
        
        if created:
            print(f"✅ 创建虚拟犬: {dog.name}")
        
        # 创建摄像头
        camera = Camera.objects.create(
            dog=dog,
            name='海康摄像头-01',
            camera_id='CAM001',
            rtsp_url=generate_rtsp_url(channel=1, sub_stream=False),  # 使用主码流
            location='A区入口',
            status='online',
            resolution='1920x1080',
            fps=25,
            description=f'海康威视网络摄像机 ({CAMERA_IP})'
        )
        print(f"✅ 创建摄像头: {camera.name}")
        print(f"   RTSP地址: {camera.rtsp_url}")
        
    else:
        print(f"\n找到 {cameras.count()} 个摄像头记录")
        print("\n请选择操作：")
        print("1. 更新第一个摄像头")
        print("2. 更新所有摄像头")
        print("3. 查看所有摄像头信息")
        
        choice = input("\n请输入选项 (1/2/3): ").strip()
        
        if choice == '1':
            camera = cameras.first()
            old_url = camera.rtsp_url
            camera.rtsp_url = generate_rtsp_url(channel=1, sub_stream=False)
            camera.location = f'{camera.location} (已更新为真实摄像头)'
            camera.status = 'online'
            camera.save()
            
            print(f"\n✅ 已更新摄像头: {camera.name}")
            print(f"   旧地址: {old_url}")
            print(f"   新地址: {camera.rtsp_url}")
            
        elif choice == '2':
            for idx, camera in enumerate(cameras, 1):
                old_url = camera.rtsp_url
                camera.rtsp_url = generate_rtsp_url(channel=idx, sub_stream=False)
                camera.status = 'online'
                camera.save()
                
                print(f"\n✅ 已更新摄像头 {idx}: {camera.name}")
                print(f"   旧地址: {old_url}")
                print(f"   新地址: {camera.rtsp_url}")
                
        elif choice == '3':
            print("\n📋 当前摄像头列表：")
            for idx, camera in enumerate(cameras, 1):
                print(f"\n{idx}. {camera.name} (ID: {camera.id})")
                print(f"   编号: {camera.camera_id}")
                print(f"   状态: {camera.get_status_display()}")
                print(f"   位置: {camera.location}")
                print(f"   RTSP: {camera.rtsp_url}")
        else:
            print("❌ 无效的选项")
            return

    print("\n" + "="*60)
    print("💡 提示：")
    print("1. 确保摄像头已开机且网络可达")
    print("2. 测试RTSP连接: ffmpeg -i 'RTSP地址' -frames:v 1 test.jpg")
    print(f"3. 测试命令: ffmpeg -i 'rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554' -frames:v 1 test.jpg")
    print("4. 如需使用子码流（更流畅），修改URL中的101为102")
    print("="*60)

if __name__ == '__main__':
    try:
        update_cameras()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

