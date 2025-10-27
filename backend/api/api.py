from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import Task
from .detection_utils import process_image, process_video, process_rubbish_image, process_rubbish_video, process_firesmoke_image, process_firesmoke_video, process_cross_image, process_cross_video
from .models_loader import is_models_loaded
import mimetypes
from camera.ptz_service import PTZController

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


class PTZTurnLeftRequestSchema(Schema):
    ip: str
    username: str
    password: str
    channel: int = 1
    speed: int = 4
    duration: float = 0.8

class PTZMoveRequestSchema(Schema):
    ip: str
    username: str
    password: str
    direction: str  # 'up' | 'down' | 'left' | 'right'
    channel: int = 1
    speed: int = 4
    duration: float = 0.8

class PTZResponseSchema(Schema):
    success: bool
    message: str = None
    error: str = None

@api.post("/ptz/turn-left", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_turn_left(request, body: PTZTurnLeftRequestSchema):
    controller = PTZController()
    try:
        if not controller.load_sdk():
            return 500, {"success": False, "error": "HCNetSDK加载失败"}
        controller.set_sdk_init_cfg()
        if not controller.init_sdk():
            return 500, {"success": False, "error": "HCNetSDK初始化失败"}

        ip_b = body.ip.encode("utf-8")
        user_b = body.username.encode("utf-8")
        pwd_b = body.password.encode("utf-8")

        if not controller.login(ip_b, user_b, pwd_b, 9000):
            err = controller.hikSDK.NET_DVR_GetLastError()
            return 500, {"success": False, "error": f"登录失败，错误码: {err}"}

        ok, msg = controller.ptz_turn_left(channel=body.channel, speed=body.speed, duration_sec=body.duration)
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}
    finally:
        try:
            controller.logout()
        finally:
            controller.cleanup_sdk()

@api.post("/ptz/turn-right", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_turn_right(request, body: PTZTurnLeftRequestSchema):
    controller = PTZController()
    try:
        if not controller.load_sdk():
            return 500, {"success": False, "error": "HCNetSDK加载失败"}
        controller.set_sdk_init_cfg()
        if not controller.init_sdk():
            return 500, {"success": False, "error": "HCNetSDK初始化失败"}
        ip_b = body.ip.encode("utf-8")
        user_b = body.username.encode("utf-8")
        pwd_b = body.password.encode("utf-8")
        if not controller.login(ip_b, user_b, pwd_b, 9000):
            err = controller.hikSDK.NET_DVR_GetLastError()
            return 500, {"success": False, "error": f"登录失败，错误码: {err}"}
        ok, msg = controller.ptz_turn_right(channel=body.channel, speed=body.speed, duration_sec=body.duration)
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}
    finally:
        try:
            controller.logout()
        finally:
            controller.cleanup_sdk()

@api.post("/ptz/tilt-up", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_tilt_up(request, body: PTZTurnLeftRequestSchema):
    controller = PTZController()
    try:
        if not controller.load_sdk():
            return 500, {"success": False, "error": "HCNetSDK加载失败"}
        controller.set_sdk_init_cfg()
        if not controller.init_sdk():
            return 500, {"success": False, "error": "HCNetSDK初始化失败"}
        ip_b = body.ip.encode("utf-8")
        user_b = body.username.encode("utf-8")
        pwd_b = body.password.encode("utf-8")
        if not controller.login(ip_b, user_b, pwd_b, 9000):
            err = controller.hikSDK.NET_DVR_GetLastError()
            return 500, {"success": False, "error": f"登录失败，错误码: {err}"}
        ok, msg = controller.ptz_tilt_up(channel=body.channel, speed=body.speed, duration_sec=body.duration)
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}
    finally:
        try:
            controller.logout()
        finally:
            controller.cleanup_sdk()

@api.post("/ptz/tilt-down", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_tilt_down(request, body: PTZTurnLeftRequestSchema):
    controller = PTZController()
    try:
        if not controller.load_sdk():
            return 500, {"success": False, "error": "HCNetSDK加载失败"}
        controller.set_sdk_init_cfg()
        if not controller.init_sdk():
            return 500, {"success": False, "error": "HCNetSDK初始化失败"}
        ip_b = body.ip.encode("utf-8")
        user_b = body.username.encode("utf-8")
        pwd_b = body.password.encode("utf-8")
        if not controller.login(ip_b, user_b, pwd_b, 9000):
            err = controller.hikSDK.NET_DVR_GetLastError()
            return 500, {"success": False, "error": f"登录失败，错误码: {err}"}
        ok, msg = controller.ptz_tilt_down(channel=body.channel, speed=body.speed, duration_sec=body.duration)
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}
    finally:
        try:
            controller.logout()
        finally:
            controller.cleanup_sdk()

@api.post("/ptz/move/start", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_move_start(request, body: PTZMoveRequestSchema):
    from camera.controller_pool import get_pool
    pool = get_pool()
    try:
        ok, msg = pool.start_move(ip=body.ip, username=body.username, password=body.password,
                                   direction=body.direction, channel=body.channel, speed=body.speed)
        pool.cleanup_idle()
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}

@api.post("/ptz/move/stop", response={200: PTZResponseSchema, 500: PTZResponseSchema})
def ptz_move_stop(request, body: PTZMoveRequestSchema):
    from camera.controller_pool import get_pool
    pool = get_pool()
    try:
        ok, msg = pool.stop_move(ip=body.ip, username=body.username, password=body.password,
                                  direction=body.direction, channel=body.channel, speed=body.speed)
        pool.cleanup_idle()
        if not ok:
            return 500, {"success": False, "error": msg}
        return 200, {"success": True, "message": msg}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}