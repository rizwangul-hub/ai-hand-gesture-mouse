"""Main Dashboard View: quick metrics, primary controls, and gesture cheatsheet."""

import time
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from core.types import TrackingState

if TYPE_CHECKING:
    from core.engine import HandControlEngine


class DashboardView(QWidget):
    """Main dashboard displaying high-level system metrics and primary tracking controls."""

    def __init__(self, engine: "HandControlEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self._init_ui()

        # Update timer for metrics and session duration
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_metrics)
        self._timer.start(250)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 1. Primary Control Bar Card
        control_card = QFrame()
        control_card.setProperty("class", "card")
        ctrl_layout = QHBoxLayout(control_card)
        ctrl_layout.setContentsMargins(16, 16, 16, 16)
        ctrl_layout.setSpacing(12)

        self.btn_start = QPushButton("▶  Start Tracking")
        self.btn_start.setProperty("class", "primaryBtn")
        self.btn_start.setFixedHeight(42)
        self.btn_start.clicked.connect(self._on_start_clicked)

        self.btn_pause = QPushButton("⏸  Pause Tracking")
        self.btn_pause.setProperty("class", "secondaryBtn")
        self.btn_pause.setFixedHeight(42)
        self.btn_pause.clicked.connect(self._on_pause_clicked)

        self.btn_stop = QPushButton("⏹  Stop Tracking")
        self.btn_stop.setProperty("class", "dangerBtn")
        self.btn_stop.setFixedHeight(42)
        self.btn_stop.clicked.connect(self._on_stop_clicked)

        # Profile Switcher
        profile_label = QLabel("Active Profile:")
        profile_label.setStyleSheet("font-weight: 600; color: #94A3B8;")
        self.combo_profile = QComboBox()
        self.combo_profile.addItems(list(settings.profiles.keys()))
        self.combo_profile.setCurrentText(settings.system.active_profile)
        self.combo_profile.currentTextChanged.connect(self._on_profile_changed)
        self.combo_profile.setFixedWidth(160)
        self.combo_profile.setFixedHeight(38)

        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addWidget(self.btn_pause)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(profile_label)
        ctrl_layout.addWidget(self.combo_profile)
        layout.addWidget(control_card)

        # 2. Metric Grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(14)

        # Metric 1: System State
        self.card_state, self.val_state = self._create_metric_card("System Status", "Idle (Stopped)")
        metrics_grid.addWidget(self.card_state, 0, 0)

        # Metric 2: Camera Status
        self.card_camera, self.val_camera = self._create_metric_card("Camera Status", "Disconnected")
        metrics_grid.addWidget(self.card_camera, 0, 1)

        # Metric 3: Hand Tracking
        self.card_tracking, self.val_tracking = self._create_metric_card("Hand Tracking", "No Hand")
        metrics_grid.addWidget(self.card_tracking, 0, 2)

        # Metric 4: Live FPS
        self.card_fps, self.val_fps = self._create_metric_card("Tracking FPS", "0.0 FPS")
        metrics_grid.addWidget(self.card_fps, 1, 0)

        # Metric 5: Active Gesture
        self.card_gesture, self.val_gesture = self._create_metric_card("Active Gesture", "None")
        metrics_grid.addWidget(self.card_gesture, 1, 1)

        # Metric 6: Session Duration
        self.card_duration, self.val_duration = self._create_metric_card("Session Time", "00:00:00")
        metrics_grid.addWidget(self.card_duration, 1, 2)

        layout.addLayout(metrics_grid)

        # 3. Gesture Cheatsheet Card
        guide_card = QFrame()
        guide_card.setProperty("class", "card")
        guide_layout = QVBoxLayout(guide_card)

        guide_title = QLabel("💡 Quick Gesture Reference Guide for Workers")
        guide_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 8px;")
        guide_layout.addWidget(guide_title)

        grid_guide = QGridLayout()
        grid_guide.setHorizontalSpacing(30)
        grid_guide.setVerticalSpacing(8)

        cheatsheet = [
            ("👆 Move Index Finger", "Moves mouse cursor smoothly across screen"),
            ("🤏 Pinch Index + Thumb", "Left Click (Instant and Debounced)"),
            ("🤏🤏 Double Pinch", "Double Click (e.g. open apps, select word)"),
            ("🤏 Hold Pinch & Move", "Drag and Drop (auto-releases on open)"),
            ("✌️ Two Fingers Together", "Right Click context menu"),
            ("✌️ Two Fingers Up/Down", "Smooth Vertical Scrolling"),
            ("✋ Show Open Palm", "Pause / Standby cursor movement"),
            ("✊ Closed Fist", "Emergency Stop / Immediate lock"),
        ]

        for i, (action, desc) in enumerate(cheatsheet):
            row = i % 4
            col = (i // 4) * 2
            lbl_act = QLabel(f"<b>{action}</b>")
            lbl_act.setStyleSheet("color: #F8FAFC;")
            lbl_desc = QLabel(desc)
            lbl_desc.setStyleSheet("color: #94A3B8;")
            grid_guide.addWidget(lbl_act, row, col)
            grid_guide.addWidget(lbl_desc, row, col + 1)

        guide_layout.addLayout(grid_guide)
        layout.addWidget(guide_card)

        layout.addStretch()
        self._update_button_states()

    def _create_metric_card(self, title: str, initial_value: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setProperty("class", "metricCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "metricTitle")

        lbl_val = QLabel(initial_value)
        lbl_val.setProperty("class", "metricValue")

        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        return card, lbl_val

    def _on_start_clicked(self):
        self.engine.start()
        self._update_button_states()

    def _on_pause_clicked(self):
        self.engine.toggle_pause()
        self._update_button_states()

    def _on_stop_clicked(self):
        self.engine.stop()
        self._update_button_states()

    def _on_profile_changed(self, profile_name: str):
        settings.apply_profile(profile_name)

    def _update_button_states(self):
        is_running = self.engine.is_running
        is_paused = (self.engine.state == TrackingState.PAUSED)

        self.btn_start.setEnabled(not is_running)
        self.btn_stop.setEnabled(is_running)
        self.btn_pause.setEnabled(is_running)

        if is_paused:
            self.btn_pause.setText("▶  Resume Tracking")
        else:
            self.btn_pause.setText("⏸  Pause Tracking")

    def _refresh_metrics(self):
        state = self.engine.state
        if state == TrackingState.RUNNING:
            self.val_state.setText("Active (Tracking)")
            self.val_state.setStyleSheet("color: #10B981;")
        elif state == TrackingState.PAUSED:
            self.val_state.setText("Paused")
            self.val_state.setStyleSheet("color: #F59E0B;")
        elif state == TrackingState.RECONNECTING:
            self.val_state.setText("Reconnecting...")
            self.val_state.setStyleSheet("color: #EF4444;")
        else:
            self.val_state.setText("Idle (Stopped)")
            self.val_state.setStyleSheet("color: #94A3B8;")

        # Camera
        cam_ok = self.engine.camera.is_connected
        self.val_camera.setText("Connected" if cam_ok else "Disconnected")
        self.val_camera.setStyleSheet("color: #10B981;" if cam_ok else "color: #EF4444;")

        # FPS
        self.val_fps.setText(f"{self.engine._fps:.1f} FPS")

        # Session Time
        dur = int(self.engine.session_duration_sec)
        h = dur // 3600
        m = (dur % 3600) // 60
        s = dur % 60
        self.val_duration.setText(f"{h:02d}:{m:02d}:{s:02d}")

        self._update_button_states()

    def update_packet(self, packet):
        """Update live gesture and tracking badge from latest frame packet."""
        if packet.hands:
            hand = packet.hands[0]
            self.val_tracking.setText(f"{hand.handedness} Hand ({int(hand.confidence * 100)}%)")
            self.val_tracking.setStyleSheet("color: #10B981;")
        else:
            self.val_tracking.setText("No Hand Visible")
            self.val_tracking.setStyleSheet("color: #94A3B8;")

        if packet.gesture_text:
            self.val_gesture.setText(packet.gesture_text)
            self.val_gesture.setStyleSheet("color: #38BDF8;")
        else:
            self.val_gesture.setText("None")
            self.val_gesture.setStyleSheet("color: #94A3B8;")
