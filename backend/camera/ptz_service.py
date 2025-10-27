# coding=utf-8
"""
精简版海康摄像机云台控制服务
- 仅依赖 HCNetSDK，提供登录、左转、登出等能力
- 用于后端 API 直接调用，不涉及播放/GUI
"""
import time
from ctypes import byref, sizeof, create_string_buffer, c_uint

from .HCNetSDK import (
    load_library,
    netsdkdllpath,
    sys_platform,
    NET_SDK_INIT_CFG_TYPE,
    NET_DVR_USER_LOGIN_INFO,
    NET_DVR_DEVICEINFO_V40,
)


class PTZController:
    def __init__(self):
        self.hikSDK = None
        self.iUserID = -1
        self.basePath = b''

    def load_sdk(self):
        self.hikSDK = load_library(netsdkdllpath)
        return self.hikSDK is not None

    def set_sdk_init_cfg(self):
        # 配置依赖库路径（以本文件所在目录为基准，更稳健）
        import os
        base_dir = os.path.dirname(__file__)
        if sys_platform == 'windows':
            basePath = base_dir.encode('gbk')
            strPath = basePath + rb'\lib'
            self.basePath = basePath
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value, byref(sdk_ComPath))
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                              create_string_buffer(strPath + rb'\libcrypto-1_1-x64.dll'))
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                              create_string_buffer(strPath + rb'\libssl-1_1-x64.dll'))
        else:
            basePath = base_dir.encode('utf-8')
            strPath = basePath + rb'/lib'
            self.basePath = basePath
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value, byref(sdk_ComPath))
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                              create_string_buffer(strPath + b'/libcrypto.so.1.1'))
            self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                              create_string_buffer(strPath + b'/libssl.so.1.1'))

    def _get_cwd_bytes(self, encoding: str):
        import os
        return os.getcwd().encode(encoding)

    def init_sdk(self):
        return bool(self.hikSDK.NET_DVR_Init())

    def cleanup_sdk(self):
        try:
            self.hikSDK.NET_DVR_Cleanup()
        except Exception:
            pass

    def login(self, ip: bytes, username: bytes, password: bytes, port: int = 9000):
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0
        struLoginInfo.sDeviceAddress = ip
        struLoginInfo.wPort = port
        struLoginInfo.sUserName = username
        struLoginInfo.sPassword = password
        struLoginInfo.byLoginMode = 0

        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()
        self.iUserID = self.hikSDK.NET_DVR_Login_V40(byref(struLoginInfo), byref(struDeviceInfoV40))
        return self.iUserID >= 0

    def logout(self):
        if self.iUserID > -1:
            self.hikSDK.NET_DVR_Logout(self.iUserID)
            self.iUserID = -1

    def ptz_turn_left(self, channel: int = 1, speed: int = 4, duration_sec: float = 5.0):
        """
        左转指定时长，然后停止。
        - speed: 1~7 常见，越大越快
        - duration_sec: 简单阻塞实现；如需非阻塞可改后台线程
        """
        if self.iUserID < 0:
            return False, 'Not logged in'
        PAN_LEFT = 23
        # 开始
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_LEFT, 0, speed):
            return False, f'PTZ start fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        # 保持一段时间
        time.sleep(max(0.8, float(duration_sec)))
        # 停止
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_LEFT, 1, speed):
            return False, f'PTZ stop fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'

    def ptz_turn_right(self, channel: int = 1, speed: int = 4, duration_sec: float = 5.0):
        if self.iUserID < 0:
            return False, 'Not logged in'
        PAN_RIGHT = 24
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_RIGHT, 0, speed):
            return False, f'PTZ start fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        time.sleep(max(0.8, float(duration_sec)))
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_RIGHT, 1, speed):
            return False, f'PTZ stop fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'

    def ptz_tilt_up(self, channel: int = 1, speed: int = 4, duration_sec: float = 5.0):
        if self.iUserID < 0:
            return False, 'Not logged in'
        TILT_UP = 21
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, TILT_UP, 0, speed):
            return False, f'PTZ start fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        time.sleep(max(0.8, float(duration_sec)))
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, TILT_UP, 1, speed):
            return False, f'PTZ stop fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'

    def ptz_tilt_down(self, channel: int = 1, speed: int = 4, duration_sec: float = 5.0):
        if self.iUserID < 0:
            return False, 'Not logged in'
        TILT_DOWN = 22
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, TILT_DOWN, 0, speed):
            return False, f'PTZ start fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        time.sleep(max(0.8, float(duration_sec)))
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, TILT_DOWN, 1, speed):
            return False, f'PTZ stop fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'

    def ptz_start_move(self, direction: str, channel: int = 1, speed: int = 4):
        if self.iUserID < 0:
            return False, 'Not logged in'
        cmd_map = {
            'left': 23,   # PAN_LEFT
            'right': 24,  # PAN_RIGHT
            'up': 21,     # TILT_UP
            'down': 22    # TILT_DOWN
        }
        cmd = cmd_map.get(direction)
        if cmd is None:
            return False, 'Invalid direction'
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, cmd, 0, speed):
            return False, f'PTZ start fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'

    def ptz_stop_move(self, direction: str, channel: int = 1, speed: int = 4):
        if self.iUserID < 0:
            return False, 'Not logged in'
        cmd_map = {
            'left': 23,
            'right': 24,
            'up': 21,
            'down': 22
        }
        cmd = cmd_map.get(direction)
        if cmd is None:
            return False, 'Invalid direction'
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, cmd, 1, speed):
            return False, f'PTZ stop fail, err={self.hikSDK.NET_DVR_GetLastError()}'
        return True, 'ok'
# 引入本模块需要的结构体（HCNetSDK 中定义）
from .HCNetSDK import NET_DVR_LOCAL_SDK_PATH