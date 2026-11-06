"""Unit tests for cursor mapping, deadzone, smoothing, and boundary clamping."""

from unittest.mock import patch
import pytest
from config.settings import settings
from core.cursor import CursorController


@pytest.fixture
def cursor_ctrl():
    settings.cursor.margin_x = 0.10
    settings.cursor.margin_y = 0.10
    settings.cursor.deadzone = 0.02
    settings.cursor.speed = 1.0
    ctrl = CursorController()
    ctrl._screen_w = 1920
    ctrl._screen_h = 1080
    return ctrl


def test_map_to_screen_center(cursor_ctrl):
    # Normalized center (0.5, 0.5) should map to center of 1920x1080
    sx, sy = cursor_ctrl.map_to_screen(0.5, 0.5)
    assert abs(sx - 960) < 5
    assert abs(sy - 540) < 5


def test_map_to_screen_margins(cursor_ctrl):
    # Within margin (e.g. 0.05 when margin is 0.10) should clamp to 0
    sx, sy = cursor_ctrl.map_to_screen(0.05, 0.05)
    assert sx == 0.0
    assert sy == 0.0

    # Past margin on the right (0.95 when margin is 0.10) should clamp to max screen
    sx, sy = cursor_ctrl.map_to_screen(0.95, 0.95)
    assert sx == 1919.0
    assert sy == 1079.0


def test_deadzone_suppression(cursor_ctrl):
    with patch("pyautogui.moveTo") as mock_move, patch("pyautogui.position", return_value=(960, 540)):
        # First entry sets initial anchor
        cursor_ctrl.move_to(0.5, 0.5)

        # Micro movement smaller than deadzone (0.005 < 0.02)
        pos = cursor_ctrl.move_to(0.505, 0.505)
        # Position should not have moved
        assert pos == (960, 540)


def test_hand_lost_and_reentry(cursor_ctrl):
    with patch("pyautogui.moveTo") as mock_move, patch("pyautogui.position", return_value=(100, 200)):
        cursor_ctrl.notify_hand_lost()
        assert cursor_ctrl._hand_reentered is True

        # When hand re-enters at different spot, cursor shouldn't jerk wildly
        pos = cursor_ctrl.move_to(0.8, 0.8)
        assert pos == (100, 200)  # Anchors at current OS cursor pos


def test_emergency_release(cursor_ctrl):
    with patch("pyautogui.mouseUp") as mock_up:
        cursor_ctrl._is_mouse_down = True
        cursor_ctrl.emergency_release()
        assert cursor_ctrl._is_mouse_down is False
        assert mock_up.call_count >= 1
