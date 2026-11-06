"""Configuration and profile manager for AI Hand Gesture Control System."""

import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from utils.logger import logger

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".hand_mouse_ai")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


@dataclass
class CameraConfig:
    camera_index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    flip_horizontal: bool = True
    auto_reconnect: bool = True
    reconnect_interval_sec: float = 2.0


@dataclass
class CursorConfig:
    speed: float = 1.3
    acceleration: float = 1.4
    use_acceleration: bool = True
    min_cutoff: float = 1.2
    beta: float = 0.02
    deadzone: float = 0.015
    precision_multiplier: float = 0.4
    margin_x: float = 0.15
    margin_y: float = 0.15
    monitor_index: int = 0


@dataclass
class GestureConfig:
    enable_left_click: bool = True
    enable_double_click: bool = True
    enable_drag_drop: bool = True
    enable_right_click: bool = True
    enable_scroll: bool = True
    enable_pause: bool = True
    enable_resume: bool = True
    enable_precision_mode: bool = True

    # Detection thresholds (normalized distances)
    pinch_threshold: float = 0.050
    pinch_release_threshold: float = 0.075
    two_finger_threshold: float = 0.060
    fist_threshold: float = 0.12

    # Timings (in seconds)
    double_click_interval: float = 0.38
    drag_hold_duration: float = 0.40
    click_cooldown: float = 0.25
    scroll_cooldown: float = 0.04
    scroll_sensitivity: float = 25.0
    pause_hold_duration: float = 0.8


@dataclass
class SystemConfig:
    theme: str = "dark"
    minimize_to_tray: bool = True
    start_minimized: bool = False
    run_on_startup: bool = False
    show_fps_overlay: bool = True
    show_landmarks: bool = True
    show_tracking_box: bool = True
    smart_pause_enabled: bool = True
    smart_pause_timeout_sec: float = 3.0
    active_profile: str = "Office Work"


DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
    "Office Work": {
        "cursor": {
            "speed": 1.3,
            "acceleration": 1.4,
            "use_acceleration": True,
            "min_cutoff": 1.2,
            "beta": 0.02,
            "deadzone": 0.015,
            "precision_multiplier": 0.4,
            "margin_x": 0.15,
            "margin_y": 0.15,
        },
        "gesture": {
            "enable_left_click": True,
            "enable_double_click": True,
            "enable_drag_drop": True,
            "enable_right_click": True,
            "enable_scroll": True,
            "enable_pause": True,
            "enable_resume": True,
            "enable_precision_mode": True,
            "pinch_threshold": 0.050,
            "pinch_release_threshold": 0.075,
            "drag_hold_duration": 0.40,
            "scroll_sensitivity": 25.0,
        },
    },
    "Precision Control": {
        "cursor": {
            "speed": 0.85,
            "acceleration": 1.1,
            "use_acceleration": False,
            "min_cutoff": 0.8,
            "beta": 0.008,
            "deadzone": 0.010,
            "precision_multiplier": 0.3,
            "margin_x": 0.18,
            "margin_y": 0.18,
        },
        "gesture": {
            "enable_left_click": True,
            "enable_double_click": True,
            "enable_drag_drop": True,
            "enable_right_click": True,
            "enable_scroll": True,
            "enable_pause": True,
            "enable_resume": True,
            "enable_precision_mode": True,
            "pinch_threshold": 0.045,
            "pinch_release_threshold": 0.070,
            "drag_hold_duration": 0.50,
            "scroll_sensitivity": 15.0,
        },
    },
    "Presentation": {
        "cursor": {
            "speed": 1.8,
            "acceleration": 1.6,
            "use_acceleration": True,
            "min_cutoff": 1.5,
            "beta": 0.03,
            "deadzone": 0.02,
            "precision_multiplier": 0.5,
            "margin_x": 0.12,
            "margin_y": 0.12,
        },
        "gesture": {
            "enable_left_click": True,
            "enable_double_click": False,
            "enable_drag_drop": False,
            "enable_right_click": True,
            "enable_scroll": True,
            "enable_pause": True,
            "enable_resume": True,
            "enable_precision_mode": False,
            "pinch_threshold": 0.060,
            "pinch_release_threshold": 0.085,
            "drag_hold_duration": 0.60,
            "scroll_sensitivity": 35.0,
        },
    },
    "Accessibility": {
        "cursor": {
            "speed": 1.0,
            "acceleration": 1.0,
            "use_acceleration": False,
            "min_cutoff": 0.9,
            "beta": 0.01,
            "deadzone": 0.025,
            "precision_multiplier": 0.35,
            "margin_x": 0.20,
            "margin_y": 0.20,
        },
        "gesture": {
            "enable_left_click": True,
            "enable_double_click": True,
            "enable_drag_drop": True,
            "enable_right_click": True,
            "enable_scroll": True,
            "enable_pause": True,
            "enable_resume": True,
            "enable_precision_mode": True,
            "pinch_threshold": 0.065,
            "pinch_release_threshold": 0.090,
            "drag_hold_duration": 0.60,
            "scroll_sensitivity": 20.0,
        },
    },
}


class SettingsManager:
    """Manages application configurations, profiles, and persistence."""

    def __init__(self, file_path: str = CONFIG_PATH):
        self.file_path = file_path
        self.camera = CameraConfig()
        self.cursor = CursorConfig()
        self.gesture = GestureConfig()
        self.system = SystemConfig()
        self.profiles = dict(DEFAULT_PROFILES)
        self.load()

    def apply_profile(self, profile_name: str) -> bool:
        """Apply a named profile's cursor and gesture settings."""
        if profile_name not in self.profiles:
            logger.warning(f"Profile '{profile_name}' not found.")
            return False

        profile_data = self.profiles[profile_name]
        if "cursor" in profile_data:
            for k, v in profile_data["cursor"].items():
                if hasattr(self.cursor, k):
                    setattr(self.cursor, k, v)
        if "gesture" in profile_data:
            for k, v in profile_data["gesture"].items():
                if hasattr(self.gesture, k):
                    setattr(self.gesture, k, v)

        self.system.active_profile = profile_name
        self.save()
        logger.info(f"Applied profile: {profile_name}")
        return True

    def save_custom_profile(self, name: str):
        """Save current settings as a custom profile."""
        self.profiles[name] = {
            "cursor": asdict(self.cursor),
            "gesture": asdict(self.gesture),
        }
        self.system.active_profile = name
        self.save()
        logger.info(f"Saved custom profile '{name}'")

    def load(self):
        """Load settings from JSON disk file if available, or initialize defaults."""
        if not os.path.exists(self.file_path):
            self.save()
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "camera" in data:
                for k, v in data["camera"].items():
                    if hasattr(self.camera, k):
                        setattr(self.camera, k, v)
            if "cursor" in data:
                for k, v in data["cursor"].items():
                    if hasattr(self.cursor, k):
                        setattr(self.cursor, k, v)
            if "gesture" in data:
                for k, v in data["gesture"].items():
                    if hasattr(self.gesture, k):
                        setattr(self.gesture, k, v)
            if "system" in data:
                for k, v in data["system"].items():
                    if hasattr(self.system, k):
                        setattr(self.system, k, v)
            if "profiles" in data:
                self.profiles.update(data["profiles"])

            logger.info(f"Settings loaded successfully from {self.file_path}")
        except Exception as exc:
            logger.error(f"Failed to parse settings file: {exc}. Using defaults.")

    def save(self):
        """Persist current settings to JSON file atomically."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            payload = {
                "camera": asdict(self.camera),
                "cursor": asdict(self.cursor),
                "gesture": asdict(self.gesture),
                "system": asdict(self.system),
                "profiles": self.profiles,
            }
            tmp_path = self.file_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            shutil.move(tmp_path, self.file_path)
            logger.debug(f"Saved settings to {self.file_path}")
        except Exception as exc:
            logger.error(f"Failed to save settings: {exc}")

    def reset_to_defaults(self):
        """Reset all configurations to factory defaults."""
        self.camera = CameraConfig()
        self.cursor = CursorConfig()
        self.gesture = GestureConfig()
        self.system = SystemConfig()
        self.profiles = dict(DEFAULT_PROFILES)
        self.save()
        logger.info("Settings reset to defaults.")


# Global singleton instance
settings = SettingsManager()
