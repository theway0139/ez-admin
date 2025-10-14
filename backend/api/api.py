from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import Task
from .detection_utils import process_image, process_video, process_rubbish_image, process_rubbish_video, process_firesmoke_image, process_firesmoke_video, process_cross_image, process_cross_video
from .models_loader import is_models_loaded
import mimetypes

api = NinjaAPI()

# 定义Schema
class TaskSchema(Schema):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str

class TaskCreateSchema(Schema):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# 行为检测Schema
class DetectionResponseSchema(Schema):
    has_warning: bool
    warnings: list = None
    error: str = None

class VideoDetectionResponseSchema(Schema):
    has_warning: bool
    total_frames: int = None
    warning_frames: int = None
    warnings: list = None
    error: str = None

# 垃圾检测Schema
class RubbishDetectionResponseSchema(Schema):
    has_rubbish: bool
    detections: list = None
    count: int = None
    error: str = None

class RubbishVideoDetectionResponseSchema(Schema):
    has_rubbish: bool
    total_frames: int = None
    detection_frames: int = None
    detections: list = None
    error: str = None

# 烟火检测Schema
class FiresmokeDetectionResponseSchema(Schema):
    has_firesmoke: bool
    detections: list = None
    count: int = None
    error: str = None

class FiresmokeVideoDetectionResponseSchema(Schema):
    has_firesmoke: bool
    total_frames: int = None
    detection_frames: int = None
    detections: list = None
    error: str = None

# 翻越检测Schema
class CrossDetectionResponseSchema(Schema):
    has_cross: bool
    detections: list = None
    count: int = None
    error: str = None

class CrossVideoDetectionResponseSchema(Schema):
    has_cross: bool
    total_frames: int = None
    detection_frames: int = None
    detections: list = None
    error: str = None

# API路由
@api.get("/tasks", response=List[TaskSchema])
def list_tasks(request):
    tasks = Task.objects.all()
    return tasks

@api.get("/tasks/{task_id}", response=TaskSchema)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return task

@api.post("/tasks", response=TaskSchema)
def create_task(request, task: TaskCreateSchema):
    task_obj = Task.objects.create(**task.dict())
    return task_obj

@api.put("/tasks/{task_id}", response=TaskSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    task = get_object_or_404(Task, id=task_id)
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(task, attr, value)
    
    task.save()
    return task

@api.delete("/tasks/{task_id}")
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return {"success": True}

@api.post("/detect-behavior", response={200: DetectionResponseSchema, 500: DetectionResponseSchema})
def detect_behavior(request, file: UploadedFile = File(...)):
    """检测图像或视频中的人物行为"""
    # 检查模型是否已加载
    if not is_models_loaded():
        return 500, {"has_warning": False, "error": "模型未成功加载"}
    
    try:
        # 读取文件内容
        file_content = file.read()
        
        # 检测文件类型
        mime_type, _ = mimetypes.guess_type(file.name)
        
        # 根据文件类型处理
        if mime_type and mime_type.startswith('image/'):
            # 处理图像
            result = process_image(file_content)
        elif mime_type and mime_type.startswith('video/'):
            # 处理视频
            result = process_video(file_content)
        else:
            return 500, {"has_warning": False, "error": "不支持的文件类型"}
        
        # 检查处理结果
        if "error" in result:
            return 500, {"has_warning": False, "error": result["error"]}
        
        return 200, result
    
    except Exception as e:
        return 500, {"has_warning": False, "error": str(e)}

@api.post("/detect-rubbish", response={200: RubbishDetectionResponseSchema, 500: RubbishDetectionResponseSchema})
def detect_rubbish(request, file: UploadedFile = File(...)):
    """检测图像或视频中的垃圾物品"""
    # 检查模型是否已加载
    if not is_models_loaded():
        return 500, {"has_rubbish": False, "error": "模型未成功加载"}
    
    try:
        # 读取文件内容
        file_content = file.read()
        
        # 检测文件类型
        mime_type, _ = mimetypes.guess_type(file.name)
        
        # 根据文件类型处理
        if mime_type and mime_type.startswith('image/'):
            # 处理图像
            result = process_rubbish_image(file_content)
        elif mime_type and mime_type.startswith('video/'):
            # 处理视频
            result = process_rubbish_video(file_content)
        else:
            return 500, {"has_rubbish": False, "error": "不支持的文件类型"}
        
        # 检查处理结果
        if "error" in result:
            return 500, {"has_rubbish": False, "error": result["error"]}
        
        return 200, result
    
    except Exception as e:
        return 500, {"has_rubbish": False, "error": str(e)}

@api.post("/detect-firesmoke", response={200: FiresmokeDetectionResponseSchema, 500: FiresmokeDetectionResponseSchema})
def detect_firesmoke(request, file: UploadedFile = File(...)):
    """检测图像或视频中的烟火"""
    # 检查模型是否已加载
    if not is_models_loaded():
        return 500, {"has_firesmoke": False, "error": "模型未成功加载"}
    
    try:
        # 读取文件内容
        file_content = file.read()
        
        # 检测文件类型
        mime_type, _ = mimetypes.guess_type(file.name)
        
        # 根据文件类型处理
        if mime_type and mime_type.startswith('image/'):
            # 处理图像
            result = process_firesmoke_image(file_content)
        elif mime_type and mime_type.startswith('video/'):
            # 处理视频
            result = process_firesmoke_video(file_content)
        else:
            return 500, {"has_firesmoke": False, "error": "不支持的文件类型"}
        
        # 检查处理结果
        if "error" in result:
            return 500, {"has_firesmoke": False, "error": result["error"]}
        
        return 200, result
    
    except Exception as e:
        return 500, {"has_firesmoke": False, "error": str(e)}

@api.post("/detect-cross", response={200: CrossDetectionResponseSchema, 500: CrossDetectionResponseSchema})
def detect_cross(request, file: UploadedFile = File(...)):
    """检测图像或视频中的翻越行为"""
    # 检查模型是否已加载
    if not is_models_loaded():
        return 500, {"has_cross": False, "error": "模型未成功加载"}
    
    try:
        # 读取文件内容
        file_content = file.read()
        
        # 检测文件类型
        mime_type, _ = mimetypes.guess_type(file.name)
        
        # 根据文件类型处理
        if mime_type and mime_type.startswith('image/'):
            # 处理图像
            result = process_cross_image(file_content)
        elif mime_type and mime_type.startswith('video/'):
            # 处理视频
            result = process_cross_video(file_content)
        else:
            return 500, {"has_cross": False, "error": "不支持的文件类型"}
        
        # 检查处理结果
        if "error" in result:
            return 500, {"has_cross": False, "error": result["error"]}
        
        return 200, result
    
    except Exception as e:
        return 500, {"has_cross": False, "error": str(e)}