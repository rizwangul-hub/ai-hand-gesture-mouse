"""Central Hand Control Engine coordinating camera, tracking, gestures, and cursor."""

import threading
import time
from typing import Callable, List, Optional, Tuple
import cv2
import numpy as np

from config.settings import settings
from core.camera import CameraManager
from core.cursor import CursorController
from core.gestures import GestureRecognizer
from core.tracker import HandTracker
from core.types import FramePacket, GestureType, HandInfo, TrackingState
from utils.logger import logger

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]


class HandControlEngine:
    """Core tracking and control pipeline operating on a dedicated background thread."""

    def __init__(self):
        self.camera = CameraManager()
        self.tracker = HandTracker()
        self.cursor = CursorController()
        self.recognizer = GestureRecognizer()

        self._state = TrackingState.STOPPED
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._running = False

        # Metrics
        self._fps = 0.0
        self._frame_count = 0
        self._fps_start_time = time.time()
        self._session_start_time = 0.0

        # Smart pause
        self._last_hand_seen_time = time.time()
        self._smart_paused = False

        # Callbacks for GUI
        self.on_frame_ready: Optional[Callable[[FramePacket], None]] = None
        self.on_state_changed: Optional[Callable[[TrackingState], None]] = None

    @property
    def state(self) -> TrackingState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state in (TrackingState.RUNNING, TrackingState.PAUSED)

    @property
    def session_duration_sec(self) -> float:
        if self._session_start_time > 0 and self.is_running:
            return time.time() - self._session_start_time
        return 0.0

    def start(self) -> bool:
        """Start tracking and control loop."""
        with self._lock:
            if self._running:
                return True

            logger.info("Starting Hand Control Engine...")
            cam_ok = self.camera.start()
            self._running = True
            self._state = TrackingState.RUNNING
            self._session_start_time = time.time()
            self._last_hand_seen_time = time.time()
            self._smart_paused = False

            self._thread = threading.Thread(target=self._loop, name="EngineWorker", daemon=True)
            self._thread.start()

            if self.on_state_changed:
                self.on_state_changed(self._state)
            return cam_ok

    def stop(self):
        """Stop tracking, release hardware and held buttons."""
        with self._lock:
            self._running = False
            self._state = TrackingState.STOPPED

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

        self.cursor.emergency_release()
        self.camera.stop()
        self.recognizer.reset_state()
        logger.info("Hand Control Engine stopped.")

        if self.on_state_changed:
            self.on_state_changed(self._state)

    def toggle_pause(self):
        """Toggle pause state."""
        with self._lock:
            if self._state == TrackingState.RUNNING:
                self._state = TrackingState.PAUSED
                self.cursor.emergency_release()
                logger.info("Tracking paused by user.")
            elif self._state == TrackingState.PAUSED:
                self._state = TrackingState.RUNNING
                self._last_hand_seen_time = time.time()
                self._smart_paused = False
                logger.info("Tracking resumed by user.")

        if self.on_state_changed:
            self.on_state_changed(self._state)

    def emergency_stop(self):
        """Immediately halt cursor actions and pause tracking."""
        self.cursor.emergency_release()
        with self._lock:
            self._state = TrackingState.PAUSED
        self.recognizer.reset_state()
        logger.warning("Emergency stop triggered!")

        if self.on_state_changed:
            self.on_state_changed(self._state)

    def _loop(self):
        """Main engine processing loop."""
        while self._running:
            ret, frame = self.camera.read_frame()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # Calculate FPS
            self._frame_count += 1
            elapsed = time.time() - self._fps_start_time
            if elapsed >= 0.5:
                self._fps = self._frame_count / elapsed
                self._frame_count = 0
                self._fps_start_time = time.time()

            # Process hand landmarks
            hands = self.tracker.process_frame(frame)
            now = time.time()

            active_gesture = GestureType.NONE
            gesture_text = ""
            cursor_pos: Optional[Tuple[int, int]] = None
            is_precision = False
            is_dragging = False

            if hands:
                self._last_hand_seen_time = now
                if self._smart_paused:
                    self._smart_paused = False
                    logger.info("Hand detected: exiting smart pause.")

                primary_hand = hands[0]
                is_paused = (self._state == TrackingState.PAUSED) or self._smart_paused

                active_gesture, gesture_text = self.recognizer.process(primary_hand, is_paused)

                # Handle gesture state changes
                if active_gesture == GestureType.PAUSE:
                    self.cursor.emergency_release()
                    self._state = TrackingState.PAUSED
                    if self.on_state_changed:
                        self.on_state_changed(self._state)

                elif active_gesture == GestureType.RESUME:
                    self._state = TrackingState.RUNNING
                    if self.on_state_changed:
                        self.on_state_changed(self._state)

                elif active_gesture == GestureType.EMERGENCY_STOP:
                    self.emergency_stop()

                # Dispatch cursor actions if active
                if self._state == TrackingState.RUNNING and not self._smart_paused:
                    index_tip = primary_hand.index_tip

                    if active_gesture == GestureType.PRECISION:
                        is_precision = True
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y, precision_mode=True)

                    elif active_gesture in (GestureType.MOVE, GestureType.DRAG):
                        if active_gesture == GestureType.DRAG:
                            is_dragging = True
                            self.cursor.mouse_down(button="left")
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y, precision_mode=False)

                    elif active_gesture == GestureType.LEFT_CLICK:
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y)
                        self.cursor.click(button="left")

                    elif active_gesture == GestureType.DOUBLE_CLICK:
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y)
                        self.cursor.double_click()

                    elif active_gesture == GestureType.RIGHT_CLICK:
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y)
                        self.cursor.click(button="right")

                    elif active_gesture == GestureType.SCROLL_UP:
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y)
                        self.cursor.scroll(int(settings.gesture.scroll_sensitivity))

                    elif active_gesture == GestureType.SCROLL_DOWN:
                        cursor_pos = self.cursor.move_to(index_tip.x, index_tip.y)
                        self.cursor.scroll(-int(settings.gesture.scroll_sensitivity))

                    if active_gesture != GestureType.DRAG:
                        self.cursor.mouse_up(button="left")

            else:
                # No hands detected in frame
                self.cursor.notify_hand_lost()
                self.recognizer.reset_state()

                # Check smart pause timeout
                if (
                    settings.system.smart_pause_enabled
                    and self._state == TrackingState.RUNNING
                    and not self._smart_paused
                ):
                    if now - self._last_hand_seen_time >= settings.system.smart_pause_timeout_sec:
                        self._smart_paused = True
                        self.cursor.emergency_release()
                        logger.info("Smart pause triggered: no hand in frame.")

                if self._smart_paused:
                    gesture_text = "Smart Pause (Hand Absent)"
                elif self._state == TrackingState.PAUSED:
                    gesture_text = "Paused"
                else:
                    gesture_text = "Searching for hand..."

            # Annotate visual frame HUD
            annotated_frame = self._render_hud(frame, hands, gesture_text, is_precision, is_dragging)

            packet = FramePacket(
                frame=annotated_frame,
                hands=hands,
                gesture=active_gesture,
                gesture_text=gesture_text,
                cursor_pos=cursor_pos,
                fps=self._fps,
                timestamp=now,
                is_paused=(self._state == TrackingState.PAUSED or self._smart_paused),
                is_precision=is_precision,
                is_dragging=is_dragging,
            )

            if self.on_frame_ready:
                try:
                    self.on_frame_ready(packet)
                except Exception as exc:
                    logger.debug(f"Error in on_frame_ready callback: {exc}")

            time.sleep(0.005)

    def _render_hud(
        self,
        frame: np.ndarray,
        hands: List[HandInfo],
        gesture_text: str,
        is_precision: bool,
        is_dragging: bool,
    ) -> np.ndarray:
        """Render modern overlay landmarks, margins, and status indicators onto the frame."""
        h, w, _ = frame.shape
        hud = frame.copy()

        # Draw Active Tracking Boundary Box
        if settings.system.show_tracking_box:
            mx = int(settings.cursor.margin_x * w)
            my = int(settings.cursor.margin_y * h)
            cv2.rectangle(hud, (mx, my), (w - mx, h - my), (70, 70, 70), 1)
            cv2.putText(
                hud,
                "Active Screen Area",
                (mx + 6, my + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (140, 140, 140),
                1,
                cv2.LINE_AA,
            )

        # Draw Landmarks and Skeleton
        if settings.system.show_landmarks and hands:
            for hand in hands:
                pts = [(int(p.x * w), int(p.y * h)) for p in hand.landmarks]

                # Draw connections
                for start_idx, end_idx in HAND_CONNECTIONS:
                    if start_idx < len(pts) and end_idx < len(pts):
                        cv2.line(hud, pts[start_idx], pts[end_idx], (0, 200, 255), 2, cv2.LINE_AA)

                # Draw joint points
                for i, (px, py) in enumerate(pts):
                    if i in (4, 8, 12):  # Thumb, Index, Middle tips
                        color = (0, 255, 128) if i == 8 else (255, 128, 0)
                        cv2.circle(hud, (px, py), 6, color, -1, cv2.LINE_AA)
                        cv2.circle(hud, (px, py), 8, (255, 255, 255), 1, cv2.LINE_AA)
                    else:
                        cv2.circle(hud, (px, py), 3, (220, 220, 220), -1, cv2.LINE_AA)

        # Draw Status Bar at Bottom
        bar_h = 36
        cv2.rectangle(hud, (0, h - bar_h), (w, h), (20, 20, 25), -1)

        # Gesture Badge
        badge_color = (0, 200, 100) if "Click" in gesture_text or "Drag" in gesture_text else (200, 200, 200)
        cv2.putText(
            hud,
            f"Gesture: {gesture_text}",
            (14, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            badge_color,
            1,
            cv2.LINE_AA,
        )

        # FPS overlay
        if settings.system.show_fps_overlay:
            fps_str = f"FPS: {self._fps:.1f}"
            cv2.putText(
                hud,
                fps_str,
                (w - 95, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (0, 255, 200),
                1,
                cv2.LINE_AA,
            )

        return hud
