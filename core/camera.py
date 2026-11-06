"""Robust, threaded camera manager with device enumeration and auto-reconnect."""

import threading
import time
from typing import List, Optional, Tuple
import cv2
import numpy as np

from config.settings import settings
from utils.logger import logger


class CameraManager:
    """Threaded camera reader delivering latest frames with low latency and auto-recovery."""

    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._last_frame_time = 0.0
        self._is_connected = False
        self._reconnect_pending = False

    @staticmethod
    def list_available_cameras(max_tested: int = 5) -> List[int]:
        """Scan and detect accessible camera indices."""
        available = []
        for index in range(max_tested):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(index)
                cap.release()
        return available if available else [0]

    def start(self, camera_index: Optional[int] = None) -> bool:
        """Start the camera capture loop in a background thread."""
        with self._lock:
            if self._running:
                return True

            idx = camera_index if camera_index is not None else settings.camera.camera_index
            success = self._open_capture(idx)
            if not success:
                logger.warning(f"Could not open camera {idx}. Starting in reconnecting state.")
                self._is_connected = False
            else:
                self._is_connected = True

            self._running = True
            self._thread = threading.Thread(target=self._capture_worker, name="CameraWorker", daemon=True)
            self._thread.start()
            return self._is_connected

    def _open_capture(self, index: int) -> bool:
        """Attempt to open and configure the hardware camera."""
        try:
            if self._cap is not None:
                self._cap.release()

            # Using CAP_DSHOW on Windows for fast startup and low latency
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # Fallback to default backend
                cap = cv2.VideoCapture(index)

            if not cap.isOpened():
                return False

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.camera.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.camera.height)
            cap.set(cv2.CAP_PROP_FPS, settings.camera.fps)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Test read
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.release()
                return False

            self._cap = cap
            logger.info(f"Successfully opened camera {index} ({frame.shape[1]}x{frame.shape[0]})")
            return True
        except Exception as exc:
            logger.error(f"Error opening camera {index}: {exc}")
            return False

    def _capture_worker(self):
        """Worker thread loop continuously fetching the newest camera frame."""
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                if settings.camera.auto_reconnect:
                    self._is_connected = False
                    time.sleep(settings.camera.reconnect_interval_sec)
                    if self._running:
                        logger.info("Attempting camera reconnection...")
                        self._open_capture(settings.camera.camera_index)
                else:
                    time.sleep(0.1)
                continue

            try:
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    logger.warning("Frame read failed. Triggering camera reconnect...")
                    self._is_connected = False
                    if self._cap:
                        self._cap.release()
                        self._cap = None
                    continue

                if settings.camera.flip_horizontal:
                    frame = cv2.flip(frame, 1)

                with self._lock:
                    self._latest_frame = frame
                    self._last_frame_time = time.time()
                    self._is_connected = True

            except Exception as exc:
                logger.error(f"Exception in camera capture loop: {exc}")
                self._is_connected = False
                time.sleep(0.5)

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Return the latest available frame. Safe to call from any thread."""
        with self._lock:
            if not self._is_connected or self._latest_frame is None:
                return False, None
            return True, self._latest_frame.copy()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def stop(self):
        """Safely shut down the camera thread and release the hardware handle."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

        with self._lock:
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception as exc:
                    logger.warning(f"Error releasing camera: {exc}")
                self._cap = None
            self._latest_frame = None
            self._is_connected = False
        logger.info("Camera manager stopped and camera released.")
