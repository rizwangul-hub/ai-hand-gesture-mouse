"""Live Tracking Video Preview View with interactive HUD overlays and CPU saver mode."""

from typing import TYPE_CHECKING
import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from core.types import FramePacket

if TYPE_CHECKING:
    from core.engine import HandControlEngine


class LiveTrackingView(QWidget):
    """Provides a live video preview showing hand skeleton, tracking boundaries, and gesture status."""

    def __init__(self, engine: "HandControlEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self._preview_enabled = True
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Toolbar Card
        toolbar = QFrame()
        toolbar.setProperty("class", "card")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(14, 10, 14, 10)
        tb_layout.setSpacing(18)

        self.chk_preview = QCheckBox("Enable Camera Preview")
        self.chk_preview.setChecked(True)
        self.chk_preview.toggled.connect(self._toggle_preview)

        self.chk_landmarks = QCheckBox("Show Skeleton Landmarks")
        self.chk_landmarks.setChecked(settings.system.show_landmarks)
        self.chk_landmarks.toggled.connect(self._toggle_landmarks)

        self.chk_box = QCheckBox("Show Tracking Active Box")
        self.chk_box.setChecked(settings.system.show_tracking_box)
        self.chk_box.toggled.connect(self._toggle_box)

        self.chk_fps = QCheckBox("Show FPS")
        self.chk_fps.setChecked(settings.system.show_fps_overlay)
        self.chk_fps.toggled.connect(self._toggle_fps)

        tb_layout.addWidget(self.chk_preview)
        tb_layout.addWidget(self.chk_landmarks)
        tb_layout.addWidget(self.chk_box)
        tb_layout.addWidget(self.chk_fps)
        tb_layout.addStretch()

        layout.addWidget(toolbar)

        # Video Canvas Container Card
        canvas_card = QFrame()
        canvas_card.setProperty("class", "card")
        canvas_layout = QVBoxLayout(canvas_card)
        canvas_layout.setAlignment(Qt.AlignCenter)
        canvas_layout.setContentsMargins(12, 12, 12, 12)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #0B0C10; border-radius: 8px; border: 1px solid #1E222D;")
        self.video_label.setText("Camera is currently idle.\nClick 'Start Tracking' on the Dashboard or press Ctrl+Alt+H.")

        canvas_layout.addWidget(self.video_label)
        layout.addWidget(canvas_card, stretch=1)

    def _toggle_preview(self, checked: bool):
        self._preview_enabled = checked
        if not checked:
            self.video_label.setText("Preview disabled (CPU Saver Mode active).\nHand tracking and mouse control are running normally in background.")

    def _toggle_landmarks(self, checked: bool):
        settings.system.show_landmarks = checked
        settings.save()

    def _toggle_box(self, checked: bool):
        settings.system.show_tracking_box = checked
        settings.save()

    def _toggle_fps(self, checked: bool):
        settings.system.show_fps_overlay = checked
        settings.save()

    def update_frame(self, packet: FramePacket):
        """Render new video frame to UI canvas if preview is enabled."""
        if not self._preview_enabled or packet.frame is None:
            return

        frame = packet.frame
        h, w, ch = frame.shape
        bytes_per_line = ch * w

        # OpenCV BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Scale pixmap maintaining aspect ratio
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
