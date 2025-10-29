import os
import asyncio
from typing import Dict, Optional

import socketio
from .rtsp_frames_streamer import FrameStreamer


MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')

# Socket.IO server (ASGI)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# Keep a map of latest frame ts to throttle if needed
latest_ts: Dict[str, int] = {}

# ASGI event loop, captured on first client connect
sio_loop: Optional[asyncio.AbstractEventLoop] = None


def _on_frame(robot_id: str, url: str, ts_ms: int):
    """Thread-safe emit from OpenCV background thread to ASGI loop."""
    global sio_loop
    if sio_loop is None:
        # No loop captured yet, skip emitting
        return
    try:
        fut = asyncio.run_coroutine_threadsafe(
            sio.emit('frame', {'robotId': robot_id, 'url': url, 'ts': ts_ms}, room=robot_id),
            sio_loop
        )
        # Optionally wait a tiny bit to surface errors
        # fut.result(timeout=0.01)
        latest_ts[robot_id] = ts_ms
    except Exception:
        # Swallow errors to keep streaming robust
        pass


streamer = FrameStreamer(media_root=MEDIA_ROOT, on_frame_cb=_on_frame)


@sio.event
async def connect(sid, environ):
    global sio_loop
    try:
        sio_loop = asyncio.get_running_loop()
    except RuntimeError:
        sio_loop = None
    await sio.emit('connected', {'sid': sid}, to=sid)


@sio.event
async def subscribe(sid, data):
    """
    data: { robotId: str, rtsp: str }
    """
    robot_id = data.get('robotId')
    rtsp = data.get('rtsp')
    if not robot_id or not rtsp:
        await sio.emit('error', {'message': 'robotId/rtsp required'}, to=sid)
        return
    await sio.save_session(sid, {'robotId': robot_id})
    await sio.enter_room(sid, robot_id)
    streamer.ensure_started(robot_id, rtsp)
    await sio.emit('subscribed', {'robotId': robot_id}, to=sid)


@sio.event
async def unsubscribe(sid, data):
    robot_id = data.get('robotId')
    await sio.leave_room(sid, robot_id)
    streamer.unsubscribe(robot_id)


@sio.event
async def disconnect(sid):
    sess = await sio.get_session(sid)
    robot_id = sess.get('robotId') if sess else None
    if robot_id:
        streamer.unsubscribe(robot_id)


# Entrypoint to run: uvicorn backend.ops.rtsp_socket_server:app --port 5001