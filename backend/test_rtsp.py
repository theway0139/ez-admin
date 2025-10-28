#!/usr/bin/env python3
import cv2
import time
import sys

rtsp_url = 'rtsp://36.139.10.47:25544/live/RPWtWUrhCDphd_01?expired=20251231110240'
print(f'正在连接RTSP流: {rtsp_url}')

cap = cv2.VideoCapture(rtsp_url)
print(f'VideoCapture创建完成，isOpened: {cap.isOpened()}')

if cap.isOpened():
    print('尝试读取帧...')
    for i in range(10):
        ret, frame = cap.read()
        print(f'第{i+1}次读取: ret={ret}, frame_exists={frame is not None}')
        if ret and frame is not None:
            print(f'✓ 成功！帧大小: {frame.shape}, 数据类型: {frame.dtype}')
            
            # 尝试编码为JPEG
            success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            if success:
                print(f'✓ JPEG编码成功！大小: {len(buffer.tobytes())} 字节')
            else:
                print('✗ JPEG编码失败')
            break
        time.sleep(1)
else:
    print('✗ 无法打开RTSP流')
    sys.exit(1)

cap.release()
print('测试完成')

