# api/detection_utils.py
import cv2
import numpy as np
import tempfile
import os
from .models_loader import get_person_model, get_behavior_model, is_models_loaded

# 扩展边界框函数
def expand_bbox(bbox, expand_ratio=0.2, img_width=None, img_height=None):
    """扩展边界框，确保不超出图像边界"""
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    
    # 计算扩展量
    dx = width * expand_ratio / 2
    dy = height * expand_ratio / 2
    
    # 扩展边界框
    new_x1 = max(0, x1 - dx) if img_width else x1 - dx
    new_y1 = max(0, y1 - dy) if img_height else y1 - dy
    new_x2 = min(img_width, x2 + dx) if img_width else x2 + dx
    new_y2 = min(img_height, y2 + dy) if img_height else y2 + dy
    
    return [new_x1, new_y1, new_x2, new_y2]

# 处理单帧图像
def process_image(image_data):
    """处理单张图像，检测人物和行为"""
    if not is_models_loaded():
        return {"error": "模型未成功加载"}
    
    # 获取模型
    person_model = get_person_model()
    behavior_model = get_behavior_model()
    
    # 转换为OpenCV格式
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_height, img_width = img.shape[:2]
    
    # 人物检测
    person_results = person_model(img, classes=[0])  # 0是COCO数据集中的人类类别
    
    warnings = []
    for result in person_results:
        boxes = result.boxes
        for box in boxes:
            # 获取边界框坐标
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # 扩展边界框
            expanded_bbox = expand_bbox([x1, y1, x2, y2], 0.2, img_width, img_height)
            ex1, ey1, ex2, ey2 = [int(coord) for coord in expanded_bbox]
            
            # 裁剪人物区域
            person_crop = img[ey1:ey2, ex1:ex2]
            
            # 行为检测
            behavior_results = behavior_model(person_crop)
            
            # 分析行为结果
            for b_result in behavior_results:
                b_boxes = b_result.boxes
                for b_box in b_boxes:
                    cls_id = int(b_box.cls[0].item())
                    conf = b_box.conf[0].item()
                    
                    # 类别0是phone(手机)，类别1是smoke(吸烟)
                    if cls_id == 0 and conf > 0.5:
                        warnings.append({"type": "phone", "confidence": conf})
                    elif cls_id == 1 and conf > 0.5:
                        warnings.append({"type": "smoke", "confidence": conf})
    
    return {
        "has_warning": len(warnings) > 0,
        "warnings": warnings
    }

# 处理视频
def process_video(video_data, sample_interval=30):
    """处理视频文件，每隔sample_interval帧采样一次"""
    if not is_models_loaded():
        return {"error": "模型未成功加载"}
    
    # 创建临时文件保存视频数据
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(video_data)
        temp_file_path = temp_file.name
    
    try:
        # 打开视频文件
        cap = cv2.VideoCapture(temp_file_path)
        if not cap.isOpened():
            return {"error": "无法打开视频文件"}
        
        frame_count = 0
        all_warnings = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每隔sample_interval帧处理一次
            if frame_count % sample_interval == 0:
                # 将帧转换为字节
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # 处理帧
                result = process_image(frame_bytes)
                if "error" not in result and result["has_warning"]:
                    # 记录帧号和警告
                    frame_warnings = {
                        "frame": frame_count,
                        "time": frame_count / cap.get(cv2.CAP_PROP_FPS),
                        "warnings": result["warnings"]
                    }
                    all_warnings.append(frame_warnings)
            
            frame_count += 1
        
        cap.release()
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        return {
            "has_warning": len(all_warnings) > 0,
            "total_frames": frame_count,
            "warning_frames": len(all_warnings),
            "warnings": all_warnings
        }
    
    except Exception as e:
        # 确保清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return {"error": str(e)}