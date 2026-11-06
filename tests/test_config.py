"""Unit tests for configuration persistence and profile switching."""

import os
import tempfile
import pytest

from config.settings import DEFAULT_PROFILES, SettingsManager


@pytest.fixture
def temp_config_file():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_settings_initialization(temp_config_file):
    mgr = SettingsManager(file_path=temp_config_file)
    assert mgr.camera.camera_index == 0
    assert mgr.cursor.speed == 1.3
    assert mgr.gesture.enable_left_click is True
    assert "Office Work" in mgr.profiles


def test_settings_save_and_reload(temp_config_file):
    mgr = SettingsManager(file_path=temp_config_file)
    mgr.cursor.speed = 2.4
    mgr.camera.fps = 60
    mgr.system.theme = "light"
    mgr.save()

    # Create new instance pointing to same file
    mgr2 = SettingsManager(file_path=temp_config_file)
    assert mgr2.cursor.speed == 2.4
    assert mgr2.camera.fps == 60
    assert mgr2.system.theme == "light"


def test_profile_switch(temp_config_file):
    mgr = SettingsManager(file_path=temp_config_file)

    # Apply Precision Control profile
    ok = mgr.apply_profile("Precision Control")
    assert ok is True
    assert mgr.system.active_profile == "Precision Control"
    assert mgr.cursor.speed == 0.85

    # Apply Presentation profile
    ok = mgr.apply_profile("Presentation")
    assert ok is True
    assert mgr.cursor.speed == 1.8


def test_custom_profile_save(temp_config_file):
    mgr = SettingsManager(file_path=temp_config_file)
    mgr.cursor.speed = 3.3
    mgr.save_custom_profile("HighSpeedCustom")

    assert "HighSpeedCustom" in mgr.profiles
    assert mgr.profiles["HighSpeedCustom"]["cursor"]["speed"] == 3.3
