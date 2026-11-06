"""High-performance cursor controller with One-Euro smoothing, deadzone, dynamic acceleration, and safety mechanisms."""

import math
import time
from typing import Optional, Tuple
import pyautogui

from config.settings import settings
from utils.filter import PointFilter2D
from utils.logger import logger

# Safety: disable pyautogui pause delay
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False


class CursorController:
    """Handles mapping from normalized camera coordinates to OS desktop coordinates."""

    def __init__(self):
        self._screen_w, self._screen_h = pyautogui.size()
        self._filter = PointFilter2D(
            min_cutoff=settings.cursor.min_cutoff,
            beta=settings.cursor.beta
        )
        self._last_raw_x: Optional[float] = None
        self._last_raw_y: Optional[float] = None
        self._last_screen_x = self._screen_w // 2
        self._last_screen_y = self._screen_h // 2
        self._is_mouse_down = False
        self._hand_reentered = True

    def update_screen_size(self):
        """Refresh current screen dimensions."""
        self._screen_w, self._screen_h = pyautogui.size()

    def notify_hand_lost(self):
        """Mark hand as lost so next detection smoothly transitions without snapping."""
        self._hand_reentered = True
        self._filter.reset()
        self.emergency_release()

    def update_settings(self):
        """Update active filter parameters from settings."""
        self._filter.update_params(
            min_cutoff=settings.cursor.min_cutoff,
            beta=settings.cursor.beta
        )

    def map_to_screen(self, norm_x: float, norm_y: float) -> Tuple[float, float]:
        """
        Map normalized [0, 1] camera coordinates to full screen pixels [0, W] and [0, H]
        accounting for margins (active tracking area).
        """
        mx = settings.cursor.margin_x
        my = settings.cursor.margin_y

        # Scale from [mx, 1 - mx] to [0, 1]
        clamped_x = (norm_x - mx) / max(0.001, (1.0 - 2.0 * mx))
        clamped_y = (norm_y - my) / max(0.001, (1.0 - 2.0 * my))

        # Clamp between 0.0 and 1.0
        clamped_x = max(0.0, min(1.0, clamped_x))
        clamped_y = max(0.0, min(1.0, clamped_y))

        # Map to physical screen resolution
        target_x = clamped_x * (self._screen_w - 1)
        target_y = clamped_y * (self._screen_h - 1)
        return target_x, target_y

    def move_to(self, norm_x: float, norm_y: float, precision_mode: bool = False) -> Tuple[int, int]:
        """
        Calculate smoothed, accelerated cursor target and dispatch to OS cursor.
        """
        now = time.perf_counter()

        # Handle hand re-entry after absence: prevent sudden jump
        if self._hand_reentered or self._last_raw_x is None:
            self._last_raw_x = norm_x
            self._last_raw_y = norm_y
            curr_pos = pyautogui.position()
            self._last_screen_x = curr_pos[0]
            self._last_screen_y = curr_pos[1]
            self._hand_reentered = False
            return int(self._last_screen_x), int(self._last_screen_y)

        # Deadzone calculation in normalized space
        dx_norm = norm_x - self._last_raw_x
        dy_norm = norm_y - self._last_raw_y
        dist_norm = math.hypot(dx_norm, dy_norm)

        deadzone = settings.cursor.deadzone
        if precision_mode:
            deadzone *= 0.5

        if dist_norm < deadzone:
            # Within deadzone: suppress micro-jitter completely
            return int(self._last_screen_x), int(self._last_screen_y)

        self._last_raw_x = norm_x
        self._last_raw_y = norm_y

        # Map to target screen coordinates
        raw_target_x, raw_target_y = self.map_to_screen(norm_x, norm_y)

        # Dynamic Acceleration
        speed_factor = settings.cursor.speed
        if precision_mode:
            speed_factor *= settings.cursor.precision_multiplier

        if settings.cursor.use_acceleration:
            # Velocity proportional to normalized distance
            accel_boost = 1.0 + (settings.cursor.acceleration * min(dist_norm * 10.0, 3.0))
            speed_factor *= accel_boost

        # Smooth using 1€ Filter
        smooth_x, smooth_y = self._filter.filter(raw_target_x, raw_target_y, now)

        # Combine smoothed coordinates with speed factor relative to last screen position
        dx = (smooth_x - self._last_screen_x) * speed_factor
        dy = (smooth_y - self._last_screen_y) * speed_factor

        final_x = self._last_screen_x + dx
        final_y = self._last_screen_y + dy

        # Clamp to screen boundary
        final_x = max(0, min(self._screen_w - 1, int(round(final_x))))
        final_y = max(0, min(self._screen_h - 1, int(round(final_y))))

        self._last_screen_x = final_x
        self._last_screen_y = final_y

        try:
            pyautogui.moveTo(final_x, final_y)
        except Exception as exc:
            logger.debug(f"pyautogui moveTo error: {exc}")

        return final_x, final_y

    def click(self, button: str = "left"):
        """Execute a single click."""
        try:
            pyautogui.click(button=button)
            logger.debug(f"Dispatched {button} click")
        except Exception as exc:
            logger.error(f"Error executing click: {exc}")

    def double_click(self):
        """Execute a double click."""
        try:
            pyautogui.doubleClick()
            logger.debug("Dispatched double click")
        except Exception as exc:
            logger.error(f"Error executing double click: {exc}")

    def mouse_down(self, button: str = "left"):
        """Press and hold mouse button."""
        if not self._is_mouse_down:
            try:
                pyautogui.mouseDown(button=button)
                self._is_mouse_down = True
                logger.debug(f"Dispatched mouse down ({button})")
            except Exception as exc:
                logger.error(f"Error executing mouse down: {exc}")

    def mouse_up(self, button: str = "left"):
        """Release held mouse button."""
        if self._is_mouse_down:
            try:
                pyautogui.mouseUp(button=button)
                self._is_mouse_down = False
                logger.debug(f"Dispatched mouse up ({button})")
            except Exception as exc:
                logger.error(f"Error executing mouse up: {exc}")

    def scroll(self, amount: int):
        """Scroll vertical wheel (positive = up, negative = down)."""
        try:
            pyautogui.scroll(amount)
        except Exception as exc:
            logger.debug(f"Error scrolling: {exc}")

    def emergency_release(self):
        """Release any held buttons immediately."""
        if self._is_mouse_down:
            try:
                pyautogui.mouseUp(button="left")
                pyautogui.mouseUp(button="right")
                self._is_mouse_down = False
                logger.info("Emergency release: mouse buttons released.")
            except Exception as exc:
                logger.warning(f"Error during emergency release: {exc}")
