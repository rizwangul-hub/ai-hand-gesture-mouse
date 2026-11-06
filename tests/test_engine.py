"""Integration tests for HandControlEngine with mocked hardware."""

import time
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from config.settings import settings
from core.engine import HandControlEngine
from core.types import GestureType, HandInfo, LandmarkPoint, TrackingState


@pytest.fixture
def mock_engine():
    settings.system.smart_pause_enabled = True
    settings.system.smart_pause_timeout_sec = 0.5

    engine = HandControlEngine()
    engine.camera.start = MagicMock(return_value=True)
    engine.camera.stop = MagicMock()
    engine.cursor.emergency_release = MagicMock()
    return engine


def test_engine_start_stop(mock_engine):
    mock_engine.camera.read_frame = MagicMock(return_value=(True, np.zeros((480, 640, 3), dtype=np.uint8)))
    mock_engine.tracker.process_frame = MagicMock(return_value=[])

    mock_engine.start()
    assert mock_engine.is_running is True
    assert mock_engine.state == TrackingState.RUNNING

    time.sleep(0.05)
    mock_engine.stop()
    assert mock_engine.is_running is False
    assert mock_engine.state == TrackingState.STOPPED


def test_engine_pause_toggle(mock_engine):
    mock_engine._state = TrackingState.RUNNING
    mock_engine.toggle_pause()
    assert mock_engine.state == TrackingState.PAUSED
    assert mock_engine.cursor.emergency_release.called

    mock_engine.toggle_pause()
    assert mock_engine.state == TrackingState.RUNNING


def test_engine_emergency_stop(mock_engine):
    mock_engine._state = TrackingState.RUNNING
    mock_engine.emergency_stop()
    assert mock_engine.state == TrackingState.PAUSED
    assert mock_engine.cursor.emergency_release.called
