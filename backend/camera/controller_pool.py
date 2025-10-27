# coding=utf-8
import time
import threading
from typing import Dict, Optional, Tuple

from .ptz_service import PTZController


class ControllerEntry:
    def __init__(self, controller: PTZController, ip: str, username: str, password: str):
        self.controller = controller
        self.ip = ip
        self.username = username
        self.password = password
        self.lock = threading.Lock()
        self.last_used = time.time()


class PTZControllerPool:
    def __init__(self, idle_timeout_sec: float = 300.0):
        # 空闲超过 idle_timeout_sec 将自动登出（保持 SDK 就绪）
        self._pool: Dict[str, ControllerEntry] = {}
        self._pool_lock = threading.Lock()
        self.idle_timeout_sec = idle_timeout_sec

    def _ensure_ready(self, entry: ControllerEntry) -> Tuple[bool, Optional[str]]:
        c = entry.controller
        # 加载并初始化 SDK（如果尚未加载）
        if c.hikSDK is None:
            if not c.load_sdk():
                return False, 'HCNetSDK加载失败'
            c.set_sdk_init_cfg()
            if not c.init_sdk():
                return False, 'HCNetSDK初始化失败'
        # 登录（如果尚未登录）
        if c.iUserID < 0:
            ip_b = entry.ip.encode('utf-8')
            user_b = entry.username.encode('utf-8')
            pwd_b = entry.password.encode('utf-8')
            if not c.login(ip_b, user_b, pwd_b, 9000):
                err = c.hikSDK.NET_DVR_GetLastError() if c.hikSDK else -1
                return False, f'登录失败，错误码: {err}'
        return True, None

    def get_entry(self, ip: str, username: str, password: str) -> Tuple[Optional[ControllerEntry], Optional[str]]:
        # 以 IP 作为键复用控制器；若凭据变更则强制重登
        with self._pool_lock:
            entry = self._pool.get(ip)
            if entry is None:
                c = PTZController()
                entry = ControllerEntry(c, ip, username, password)
                self._pool[ip] = entry
            else:
                if entry.username != username or entry.password != password:
                    entry.username = username
                    entry.password = password
                    # 凭据变化后如已登录则先登出，避免后续操作失败
                    try:
                        with entry.lock:
                            entry.controller.logout()
                    except Exception:
                        pass
        # 在条目级锁下确保 SDK/登录状态，避免并发竞态
        with entry.lock:
            ok, err = self._ensure_ready(entry)
            entry.last_used = time.time()
        return (entry if ok else None), err

    def start_move(self, ip: str, username: str, password: str, direction: str, channel: int, speed: int) -> Tuple[bool, str]:
        entry, err = self.get_entry(ip, username, password)
        if not entry:
            return False, err or '控制器不可用'
        with entry.lock:
            ok, msg = entry.controller.ptz_start_move(direction=direction, channel=channel, speed=speed)
            entry.last_used = time.time()
            return ok, msg

    def stop_move(self, ip: str, username: str, password: str, direction: str, channel: int, speed: int) -> Tuple[bool, str]:
        entry, err = self.get_entry(ip, username, password)
        if not entry:
            return False, err or '控制器不可用'
        with entry.lock:
            ok, msg = entry.controller.ptz_stop_move(direction=direction, channel=channel, speed=speed)
            entry.last_used = time.time()
            return ok, msg

    def cleanup_idle(self):
        now = time.time()
        with self._pool_lock:
            for ip, entry in list(self._pool.items()):
                if now - entry.last_used > self.idle_timeout_sec:
                    # 仅登出，保留 SDK 加载状态以便快速再次登录
                    try:
                        with entry.lock:
                            entry.controller.logout()
                    except Exception:
                        pass


# 单例实例供 API 使用
_pool_instance = PTZControllerPool()


def get_pool() -> PTZControllerPool:
    return _pool_instance