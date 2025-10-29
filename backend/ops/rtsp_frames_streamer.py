import os
import threading
import time
from typing import Dict, Optional

import cv2


class FrameStreamer:
    """
    Per-robot RTSP frame streamer using OpenCV.
    - Reads frames from RTSP.
    - Saves into a ring buffer of 20 JPEG files under media/rtsp_frames/<robotId>/.
    - Notifies a callback per frame with the public URL.
    """

    def __init__(self, media_root: str, on_frame_cb):
        self.media_root = media_root
        self.on_frame_cb = on_frame_cb  # callable(robot_id: str, url: str, ts_ms: int)
        self._lock = threading.Lock()
        self._workers: Dict[str, threading.Thread] = {}
        self._stops: Dict[str, threading.Event] = {}
        self._subscribers: Dict[str, int] = {}
        self._rtsp_urls: Dict[str, str] = {}

    def ensure_started(self, robot_id: str, rtsp_url: str):
        with self._lock:
            self._rtsp_urls[robot_id] = rtsp_url
            if robot_id not in self._workers or not self._workers[robot_id].is_alive():
                stop_evt = threading.Event()
                self._stops[robot_id] = stop_evt
                t = threading.Thread(target=self._run_stream, args=(robot_id, stop_evt), daemon=True)
                self._workers[robot_id] = t
                t.start()
            # track subscribers count
            self._subscribers[robot_id] = self._subscribers.get(robot_id, 0) + 1

    def unsubscribe(self, robot_id: str):
        with self._lock:
            if robot_id in self._subscribers:
                self._subscribers[robot_id] = max(0, self._subscribers[robot_id] - 1)
                if self._subscribers[robot_id] == 0:
                    # stop worker
                    if robot_id in self._stops:
                        self._stops[robot_id].set()

    def _run_stream(self, robot_id: str, stop_evt: threading.Event):
        rtsp_url = self._rtsp_urls.get(robot_id)
        if not rtsp_url:
            return

        # Prepare directory
        out_dir = os.path.join(self.media_root, 'rtsp_frames', robot_id)
        os.makedirs(out_dir, exist_ok=True)

        cap: Optional[cv2.VideoCapture] = None
        frame_idx = 0
        last_frame = None
        target_interval_ms = 50  # ~20 fps

        def open_capture() -> Optional[cv2.VideoCapture]:
            try:
                return cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            except Exception:
                return cv2.VideoCapture(rtsp_url)

        backoff_ms = 500
        while not stop_evt.is_set():
            if cap is None or not cap.isOpened():
                cap = open_capture()
                if cap is None or not cap.isOpened():
                    time.sleep(backoff_ms / 1000.0)
                    backoff_ms = min(backoff_ms * 2, 10000)
                    continue
                backoff_ms = 500

            start_ms = int(time.time() * 1000)
            ret, frame = cap.read()
            if not ret or frame is None:
                # Repeat last frame to maintain cadence
                if last_frame is None:
                    time.sleep(target_interval_ms / 1000.0)
                    continue
                img = last_frame
            else:
                img = frame
                last_frame = frame

            # Optional resize for performance: clamp width to 1280
            try:
                h, w = img.shape[:2]
                if w > 1280:
                    scale = 1280 / float(w)
                    img = cv2.resize(img, (int(w * scale), int(h * scale)))
            except Exception:
                pass

            # Encode JPEG with quality 80
            try:
                ok, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ok:
                    fname = f'frame_{frame_idx % 20}.jpg'
                    fpath = os.path.join(out_dir, fname)
                    with open(fpath, 'wb') as f:
                        f.write(buf.tobytes())
                    ts_ms = int(time.time() * 1000)
                    # Construct public URL under /media
                    url = f'/media/rtsp_frames/{robot_id}/{fname}?t={ts_ms}'
                    self.on_frame_cb(robot_id, url, ts_ms)
                    frame_idx += 1
            except Exception:
                # Silently skip encoding errors
                pass

            # pacing
            elapsed_ms = int(time.time() * 1000) - start_ms
            sleep_ms = max(0, target_interval_ms - elapsed_ms)
            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

        # Cleanup
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass