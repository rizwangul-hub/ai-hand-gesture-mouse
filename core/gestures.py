"""Advanced hand gesture recognition engine with finite state machine and debouncing."""

import math
import time
from typing import Optional, Tuple
from config.settings import settings
from core.types import GestureType, HandInfo, LandmarkPoint
from utils.logger import logger


def euclidean_distance(p1: LandmarkPoint, p2: LandmarkPoint) -> float:
    """Compute 2D/3D Euclidean distance between two landmark points."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


class GestureRecognizer:
    """
    Finite State Machine for multi-gesture recognition.
    Distinguishes single click, double click, drag-and-drop, right click,
    two-finger scrolling, open palm pause/resume, and closed-fist emergency stop.
    """

    def __init__(self):
        # Pinch state tracking
        self._is_pinching = False
        self._pinch_start_time = 0.0
        self._is_dragging = False

        # Double click timing
        self._last_click_release_time = 0.0
        self._pending_single_click = False
        self._click_cooldown_until = 0.0

        # Scroll tracking
        self._prev_scroll_y: Optional[float] = None
        self._last_scroll_time = 0.0

        # Pause / Resume holding
        self._pause_gesture_start = 0.0
        self._resume_gesture_start = 0.0

        # Right click cooldown
        self._right_click_cooldown_until = 0.0

    def is_finger_extended(self, hand: HandInfo, tip_idx: int, pip_idx: int) -> bool:
        """Determine if a given finger is extended relative to its PIP joint."""
        return hand.landmarks[tip_idx].y < hand.landmarks[pip_idx].y

    def are_fingers_open_palm(self, hand: HandInfo) -> bool:
        """Check if all 5 fingers are fully extended (open palm)."""
        idx_ext = self.is_finger_extended(hand, 8, 6)
        mid_ext = self.is_finger_extended(hand, 12, 10)
        rng_ext = self.is_finger_extended(hand, 16, 14)
        pnk_ext = self.is_finger_extended(hand, 20, 18)
        # Thumb extended away from pinky MCP
        thumb_ext = euclidean_distance(hand.thumb_tip, hand.landmarks[17]) > 0.20
        return idx_ext and mid_ext and rng_ext and pnk_ext and thumb_ext

    def is_closed_fist(self, hand: HandInfo) -> bool:
        """Check if all fingers are curled in towards the palm (fist)."""
        idx_curled = hand.landmarks[8].y > hand.landmarks[6].y
        mid_curled = hand.landmarks[12].y > hand.landmarks[10].y
        rng_curled = hand.landmarks[16].y > hand.landmarks[14].y
        pnk_curled = hand.landmarks[20].y > hand.landmarks[18].y
        # Tips close to wrist or palm center
        dist_to_wrist = (
            euclidean_distance(hand.index_tip, hand.wrist)
            + euclidean_distance(hand.middle_tip, hand.wrist)
            + euclidean_distance(hand.ring_tip, hand.wrist)
            + euclidean_distance(hand.pinky_tip, hand.wrist)
        ) / 4.0

        return idx_curled and mid_curled and rng_curled and pnk_curled and (dist_to_wrist < 0.35)

    def process(
        self,
        hand: HandInfo,
        is_paused: bool = False
    ) -> Tuple[GestureType, str]:
        """
        Evaluate hand geometry and return the detected gesture action.
        """
        now = time.perf_counter()
        cfg = settings.gesture

        # 1. Closed Fist -> Emergency Pause
        if cfg.enable_pause and self.is_closed_fist(hand):
            self.reset_state()
            return GestureType.EMERGENCY_STOP, "Closed Fist (Emergency Stop)"

        # 2. Open Palm -> Pause / Resume Check
        if self.are_fingers_open_palm(hand):
            if is_paused and cfg.enable_resume:
                if self._resume_gesture_start == 0.0:
                    self._resume_gesture_start = now
                elif now - self._resume_gesture_start >= cfg.pause_hold_duration:
                    self._resume_gesture_start = 0.0
                    return GestureType.RESUME, "Open Palm (Resume Tracking)"
                return GestureType.NONE, f"Hold Palm to Resume ({int((cfg.pause_hold_duration - (now - self._resume_gesture_start)) * 10) / 10}s)"
            elif not is_paused and cfg.enable_pause:
                if self._pause_gesture_start == 0.0:
                    self._pause_gesture_start = now
                elif now - self._pause_gesture_start >= cfg.pause_hold_duration:
                    self._pause_gesture_start = 0.0
                    return GestureType.PAUSE, "Open Palm (Pause Tracking)"
                return GestureType.NONE, f"Hold Palm to Pause ({int((cfg.pause_hold_duration - (now - self._pause_gesture_start)) * 10) / 10}s)"
        else:
            self._pause_gesture_start = 0.0
            self._resume_gesture_start = 0.0

        # If system is paused, ignore cursor/click gestures
        if is_paused:
            return GestureType.NONE, "Paused"

        # Calculate pinch distances
        thumb_tip = hand.thumb_tip
        index_tip = hand.index_tip
        middle_tip = hand.middle_tip

        pinch_dist = euclidean_distance(thumb_tip, index_tip)
        two_finger_dist = euclidean_distance(index_tip, middle_tip)

        index_extended = self.is_finger_extended(hand, 8, 6)
        middle_extended = self.is_finger_extended(hand, 12, 10)
        ring_extended = self.is_finger_extended(hand, 16, 14)
        pinky_extended = self.is_finger_extended(hand, 20, 18)

        # 3. Two Fingers (Index + Middle) extended together -> Scroll or Right Click
        if (
            index_extended
            and middle_extended
            and not ring_extended
            and not pinky_extended
            and two_finger_dist < cfg.two_finger_threshold
        ):
            avg_y = (index_tip.y + middle_tip.y) / 2.0

            # Vertical movement test for scrolling
            if cfg.enable_scroll and self._prev_scroll_y is not None:
                dy = avg_y - self._prev_scroll_y
                if abs(dy) > 0.015:  # Movement threshold
                    self._prev_scroll_y = avg_y
                    if dy < 0:
                        return GestureType.SCROLL_UP, "Scrolling Up"
                    else:
                        return GestureType.SCROLL_DOWN, "Scrolling Down"

            self._prev_scroll_y = avg_y

            # If stationary and right click is enabled
            if (
                cfg.enable_right_click
                and now >= self._right_click_cooldown_until
                and self._prev_scroll_y is not None
            ):
                self._right_click_cooldown_until = now + 0.60
                return GestureType.RIGHT_CLICK, "Two Fingers (Right Click)"

            return GestureType.MOVE, "Two Fingers Ready"
        else:
            self._prev_scroll_y = None

        # 4. Precision Mode Gesture: Thumb and Middle finger pinched, Index finger extended
        if (
            cfg.enable_precision_mode
            and index_extended
            and euclidean_distance(thumb_tip, middle_tip) < cfg.pinch_threshold
        ):
            return GestureType.PRECISION, "Precision Mode"

        # 5. Index + Thumb Pinch: Left Click, Double Click, or Drag & Drop
        if pinch_dist < cfg.pinch_threshold:
            if not self._is_pinching:
                # Pinch started
                self._is_pinching = True
                self._pinch_start_time = now
            else:
                # Pinch held
                hold_duration = now - self._pinch_start_time
                if cfg.enable_drag_drop and hold_duration >= cfg.drag_hold_duration:
                    self._is_dragging = True
                    return GestureType.DRAG, "Dragging"

            return GestureType.MOVE, "Pinching"

        elif pinch_dist > cfg.pinch_release_threshold:
            # Pinch released
            if self._is_pinching:
                self._is_pinching = False
                hold_duration = now - self._pinch_start_time

                if self._is_dragging:
                    # Finished dragging
                    self._is_dragging = False
                    return GestureType.DRAG, "Drop (Drag Complete)"

                # If pinch was short, evaluate single vs double click
                if hold_duration < cfg.drag_hold_duration and now >= self._click_cooldown_until:
                    time_since_last_release = now - self._last_click_release_time
                    if cfg.enable_double_click and time_since_last_release <= cfg.double_click_interval:
                        self._last_click_release_time = 0.0
                        self._click_cooldown_until = now + cfg.click_cooldown
                        return GestureType.DOUBLE_CLICK, "Double Click"
                    else:
                        self._last_click_release_time = now
                        self._click_cooldown_until = now + cfg.click_cooldown
                        if cfg.enable_left_click:
                            return GestureType.LEFT_CLICK, "Left Click"

        # Standard Pointer Movement
        return GestureType.MOVE, "Pointer Move"

    def reset_state(self):
        """Reset internal pinch, drag, and timing trackers."""
        self._is_pinching = False
        self._is_dragging = False
        self._pinch_start_time = 0.0
        self._last_click_release_time = 0.0
        self._prev_scroll_y = None
        self._pause_gesture_start = 0.0
        self._resume_gesture_start = 0.0
