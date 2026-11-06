"""Unit tests for gesture recognition: pinch, drag, double pinch, 2-finger scroll, fist, and open palm."""

import time
from unittest.mock import patch
import pytest

from config.settings import settings
from core.gestures import GestureRecognizer
from core.types import GestureType, HandInfo, LandmarkPoint


def create_mock_hand(
    thumb_pos=(0.4, 0.4),
    index_pos=(0.4, 0.4),
    middle_pos=(0.4, 0.6),
    ring_pos=(0.4, 0.7),
    pinky_pos=(0.4, 0.8),
    wrist_pos=(0.4, 0.9),
    all_extended=False,
    all_curled=False,
) -> HandInfo:
    """Helper to create synthetic 21 hand landmarks for deterministic tests."""
    landmarks = [LandmarkPoint(x=0.5, y=0.5, z=0.0) for _ in range(21)]

    # Wrist
    landmarks[0] = LandmarkPoint(x=wrist_pos[0], y=wrist_pos[1])

    # Thumb
    landmarks[4] = LandmarkPoint(x=thumb_pos[0], y=thumb_pos[1])

    # Index (tip=8, pip=6)
    landmarks[8] = LandmarkPoint(x=index_pos[0], y=index_pos[1])
    landmarks[6] = LandmarkPoint(x=index_pos[0], y=index_pos[1] + (0.1 if all_extended or not all_curled else -0.1))

    # Middle (tip=12, pip=10)
    landmarks[12] = LandmarkPoint(x=middle_pos[0], y=middle_pos[1])
    landmarks[10] = LandmarkPoint(x=middle_pos[0], y=middle_pos[1] + (0.1 if all_extended else -0.1))

    # Ring (tip=16, pip=14)
    landmarks[16] = LandmarkPoint(x=ring_pos[0], y=ring_pos[1])
    landmarks[14] = LandmarkPoint(x=ring_pos[0], y=ring_pos[1] + (0.1 if all_extended else -0.1))

    # Pinky (tip=20, pip=18)
    landmarks[20] = LandmarkPoint(x=pinky_pos[0], y=pinky_pos[1])
    landmarks[18] = LandmarkPoint(x=pinky_pos[0], y=pinky_pos[1] + (0.1 if all_extended else -0.1))

    # Pinky MCP (17)
    landmarks[17] = LandmarkPoint(x=pinky_pos[0] + 0.1, y=pinky_pos[1] + 0.2)

    return HandInfo(landmarks=landmarks, handedness="Right", confidence=0.95)


@pytest.fixture
def recognizer():
    settings.gesture.pinch_threshold = 0.05
    settings.gesture.pinch_release_threshold = 0.08
    settings.gesture.drag_hold_duration = 0.35
    settings.gesture.double_click_interval = 0.35
    settings.gesture.click_cooldown = 0.15
    return GestureRecognizer()


def test_pointer_movement(recognizer):
    """When fingers are separated, recognizer should return MOVE."""
    hand = create_mock_hand(
        thumb_pos=(0.3, 0.4),
        index_pos=(0.5, 0.2),  # distance ~ 0.28 > pinch_threshold
    )
    g, text = recognizer.process(hand)
    assert g == GestureType.MOVE


def test_single_left_click(recognizer):
    """Pinch and then release within drag_hold_duration triggers LEFT_CLICK."""
    # 1. Hand pinches
    hand_pinch = create_mock_hand(
        thumb_pos=(0.4, 0.4),
        index_pos=(0.41, 0.41),  # distance ~ 0.014 < 0.05
    )
    g1, _ = recognizer.process(hand_pinch)
    assert recognizer._is_pinching is True

    # 2. Hand releases pinch quickly
    hand_release = create_mock_hand(
        thumb_pos=(0.3, 0.4),
        index_pos=(0.5, 0.2),  # distance > 0.08
    )
    g2, text2 = recognizer.process(hand_release)
    assert g2 == GestureType.LEFT_CLICK
    assert "Left Click" in text2


def test_drag_and_drop(recognizer):
    """Holding pinch longer than drag_hold_duration triggers DRAG."""
    hand_pinch = create_mock_hand(thumb_pos=(0.4, 0.4), index_pos=(0.41, 0.41))

    # Start pinch at t=100
    with patch("time.perf_counter", return_value=100.0):
        recognizer.process(hand_pinch)

    # Continue pinch at t=100.4 (> 0.35s drag threshold)
    with patch("time.perf_counter", return_value=100.45):
        g, text = recognizer.process(hand_pinch)
        assert g == GestureType.DRAG
        assert recognizer._is_dragging is True

    # Release pinch
    hand_release = create_mock_hand(thumb_pos=(0.3, 0.4), index_pos=(0.5, 0.2))
    with patch("time.perf_counter", return_value=100.6):
        g_drop, text_drop = recognizer.process(hand_release)
        assert g_drop == GestureType.DRAG
        assert "Drop" in text_drop
        assert recognizer._is_dragging is False


def test_closed_fist_emergency_stop(recognizer):
    """Curling all fingers into fist triggers EMERGENCY_STOP."""
    hand_fist = create_mock_hand(
        wrist_pos=(0.5, 0.6),
        thumb_pos=(0.5, 0.55),
        index_pos=(0.5, 0.55),
        middle_pos=(0.5, 0.55),
        ring_pos=(0.5, 0.55),
        pinky_pos=(0.5, 0.55),
        all_curled=True,
    )
    g, text = recognizer.process(hand_fist)
    assert g == GestureType.EMERGENCY_STOP
    assert "Emergency" in text


def test_open_palm_pause_and_resume(recognizer):
    """Showing open palm for configured duration toggles pause/resume."""
    hand_palm = create_mock_hand(
        thumb_pos=(0.2, 0.3),
        index_pos=(0.4, 0.2),
        middle_pos=(0.5, 0.2),
        ring_pos=(0.6, 0.2),
        pinky_pos=(0.7, 0.2),
        wrist_pos=(0.5, 0.8),
        all_extended=True,
    )

    # First moment palm seen (starts timer)
    with patch("time.perf_counter", return_value=200.0):
        g1, _ = recognizer.process(hand_palm, is_paused=False)
        assert g1 == GestureType.NONE

    # After holding 0.85s (> 0.8s threshold)
    with patch("time.perf_counter", return_value=200.85):
        g2, text2 = recognizer.process(hand_palm, is_paused=False)
        assert g2 == GestureType.PAUSE
        assert "Pause" in text2

    # While paused, hold palm to resume
    with patch("time.perf_counter", return_value=300.0):
        recognizer.process(hand_palm, is_paused=True)

    with patch("time.perf_counter", return_value=300.85):
        g3, text3 = recognizer.process(hand_palm, is_paused=True)
        assert g3 == GestureType.RESUME
        assert "Resume" in text3
