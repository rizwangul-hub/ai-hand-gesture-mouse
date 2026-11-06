"""Data structures, enums, and types for hand tracking and gesture recognition."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
import numpy as np


class TrackingState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class GestureType(Enum):
    NONE = "none"
    MOVE = "move"
    LEFT_CLICK = "left_click"
    DOUBLE_CLICK = "double_click"
    DRAG = "drag"
    RIGHT_CLICK = "right_click"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    PAUSE = "pause"
    RESUME = "resume"
    PRECISION = "precision"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class LandmarkPoint:
    x: float
    y: float
    z: float = 0.0


@dataclass
class HandInfo:
    landmarks: List[LandmarkPoint]
    handedness: str  # "Left" or "Right"
    confidence: float = 1.0

    @property
    def wrist(self) -> LandmarkPoint:
        return self.landmarks[0]

    @property
    def thumb_tip(self) -> LandmarkPoint:
        return self.landmarks[4]

    @property
    def index_tip(self) -> LandmarkPoint:
        return self.landmarks[8]

    @property
    def index_mcp(self) -> LandmarkPoint:
        return self.landmarks[5]

    @property
    def middle_tip(self) -> LandmarkPoint:
        return self.landmarks[12]

    @property
    def middle_mcp(self) -> LandmarkPoint:
        return self.landmarks[9]

    @property
    def ring_tip(self) -> LandmarkPoint:
        return self.landmarks[16]

    @property
    def ring_mcp(self) -> LandmarkPoint:
        return self.landmarks[13]

    @property
    def pinky_tip(self) -> LandmarkPoint:
        return self.landmarks[20]

    @property
    def pinky_mcp(self) -> LandmarkPoint:
        return self.landmarks[17]


@dataclass
class FramePacket:
    frame: np.ndarray
    hands: List[HandInfo]
    gesture: GestureType = GestureType.NONE
    gesture_text: str = ""
    cursor_pos: Optional[Tuple[int, int]] = None
    fps: float = 0.0
    timestamp: float = 0.0
    is_paused: bool = False
    is_precision: bool = False
    is_dragging: bool = False
