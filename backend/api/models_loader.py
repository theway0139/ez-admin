# api/models_loader.py
import os
import torch
from ultralytics import YOLO

# 模块级变量，在导入时初始化
print("正在加载YOLOv8模型...")

# 模型路径配置
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
PERSON_MODEL_PATH = os.path.join(MODELS_DIR, 'yolo11n.pt')
BEHAVIOR_MODEL_PATH = os.path.join(MODELS_DIR, 'phoneSmoke.pt')  # 行为检测模型路径
RUBBISH_MODEL_PATH = os.path.join(MODELS_DIR, 'rubbish.pt')  # 垃圾检测模型路径
FIRESMOKE_MODEL_PATH = os.path.join(MODELS_DIR, 'firesmoke.pt')  # 烟火检测模型路径
CROSS_MODEL_PATH = os.path.join(MODELS_DIR, 'cross.pt')  # 翻越检测模型路径

# 模型实例作为模块级变量
try:
    # 检查CUDA可用性
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    # 加载人物检测模型
    person_model = YOLO(PERSON_MODEL_PATH)
    print("人物检测模型加载成功")
    
    # 加载行为检测模型
    behavior_model = YOLO(BEHAVIOR_MODEL_PATH)
    print("行为检测模型加载成功")
    
    # 加载垃圾检测模型
    rubbish_model = YOLO(RUBBISH_MODEL_PATH)
    print("垃圾检测模型加载成功")
    
    # 加载烟火检测模型
    firesmoke_model = YOLO(FIRESMOKE_MODEL_PATH)
    print("烟火检测模型加载成功")
    
    # 加载翻越检测模型
    cross_model = YOLO(CROSS_MODEL_PATH)
    print("翻越检测模型加载成功")
    
    MODELS_LOADED = True
except Exception as e:
    print(f"模型加载失败: {str(e)}")
    person_model = None
    behavior_model = None
    rubbish_model = None
    firesmoke_model = None
    cross_model = None
    MODELS_LOADED = False

# 提供获取模型的函数
def get_person_model():
    return person_model

def get_behavior_model():
    return behavior_model

def get_rubbish_model():
    return rubbish_model

def get_firesmoke_model():
    return firesmoke_model

def get_cross_model():
    return cross_model

def is_models_loaded():
    return MODELS_LOADED