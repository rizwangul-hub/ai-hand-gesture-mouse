"""Gesture Customization and Live Gesture Testing View."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings


class GestureSettingsView(QWidget):
    """Customization panel for all hand gestures, thresholds, cooldowns, and interactive testing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)

        # 1. Gesture Enablement Toggles
        card_toggles = QFrame()
        card_toggles.setProperty("class", "card")
        vbox_tog = QVBoxLayout(card_toggles)

        title_tog = QLabel("Enabled Gestures")
        title_tog.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        vbox_tog.addWidget(title_tog)

        grid_tog = QGridLayout()
        grid_tog.setHorizontalSpacing(30)
        grid_tog.setVerticalSpacing(10)

        self.chk_left = QCheckBox("Left Click (Index + Thumb Pinch)")
        self.chk_left.setChecked(settings.gesture.enable_left_click)
        self.chk_left.toggled.connect(lambda v: self._update_val("enable_left_click", v))

        self.chk_double = QCheckBox("Double Click (Rapid Double Pinch)")
        self.chk_double.setChecked(settings.gesture.enable_double_click)
        self.chk_double.toggled.connect(lambda v: self._update_val("enable_double_click", v))

        self.chk_drag = QCheckBox("Drag & Drop (Hold Pinch to Grab)")
        self.chk_drag.setChecked(settings.gesture.enable_drag_drop)
        self.chk_drag.toggled.connect(lambda v: self._update_val("enable_drag_drop", v))

        self.chk_right = QCheckBox("Right Click (Two Fingers Extended)")
        self.chk_right.setChecked(settings.gesture.enable_right_click)
        self.chk_right.toggled.connect(lambda v: self._update_val("enable_right_click", v))

        self.chk_scroll = QCheckBox("Scrolling (Two Fingers Vertical Motion)")
        self.chk_scroll.setChecked(settings.gesture.enable_scroll)
        self.chk_scroll.toggled.connect(lambda v: self._update_val("enable_scroll", v))

        self.chk_precision = QCheckBox("Precision Mode (Thumb + Middle Pinch)")
        self.chk_precision.setChecked(settings.gesture.enable_precision_mode)
        self.chk_precision.toggled.connect(lambda v: self._update_val("enable_precision_mode", v))

        self.chk_pause = QCheckBox("Pause Cursor (Open Palm / Closed Fist)")
        self.chk_pause.setChecked(settings.gesture.enable_pause)
        self.chk_pause.toggled.connect(lambda v: self._update_val("enable_pause", v))

        self.chk_resume = QCheckBox("Resume Cursor (Hold Palm 1s)")
        self.chk_resume.setChecked(settings.gesture.enable_resume)
        self.chk_resume.toggled.connect(lambda v: self._update_val("enable_resume", v))

        grid_tog.addWidget(self.chk_left, 0, 0)
        grid_tog.addWidget(self.chk_double, 0, 1)
        grid_tog.addWidget(self.chk_drag, 1, 0)
        grid_tog.addWidget(self.chk_right, 1, 1)
        grid_tog.addWidget(self.chk_scroll, 2, 0)
        grid_tog.addWidget(self.chk_precision, 2, 1)
        grid_tog.addWidget(self.chk_pause, 3, 0)
        grid_tog.addWidget(self.chk_resume, 3, 1)

        vbox_tog.addLayout(grid_tog)
        layout.addWidget(card_toggles)

        # 2. Sensitivity & Thresholds Card
        card_thresh = QFrame()
        card_thresh.setProperty("class", "card")
        vbox_thr = QVBoxLayout(card_thresh)

        title_thr = QLabel("Gesture Distance Thresholds & Timings")
        title_thr.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        vbox_thr.addWidget(title_thr)

        grid_thr = QGridLayout()
        grid_thr.setSpacing(14)

        # Pinch Threshold
        lbl_pinch = QLabel("Pinch Trigger Distance:")
        self.spin_pinch = QDoubleSpinBox()
        self.spin_pinch.setRange(0.02, 0.15)
        self.spin_pinch.setSingleStep(0.005)
        self.spin_pinch.setDecimals(3)
        self.spin_pinch.setValue(settings.gesture.pinch_threshold)
        self.spin_pinch.valueChanged.connect(lambda v: self._update_val("pinch_threshold", v))
        grid_thr.addWidget(lbl_pinch, 0, 0)
        grid_thr.addWidget(self.spin_pinch, 0, 1)

        # Pinch Release
        lbl_release = QLabel("Pinch Release Distance:")
        self.spin_release = QDoubleSpinBox()
        self.spin_release.setRange(0.04, 0.20)
        self.spin_release.setSingleStep(0.005)
        self.spin_release.setDecimals(3)
        self.spin_release.setValue(settings.gesture.pinch_release_threshold)
        self.spin_release.valueChanged.connect(lambda v: self._update_val("pinch_release_threshold", v))
        grid_thr.addWidget(lbl_release, 0, 2)
        grid_thr.addWidget(self.spin_release, 0, 3)

        # Drag Hold Duration
        lbl_drag_hold = QLabel("Drag Hold Duration (sec):")
        self.spin_drag = QDoubleSpinBox()
        self.spin_drag.setRange(0.2, 1.5)
        self.spin_drag.setSingleStep(0.05)
        self.spin_drag.setValue(settings.gesture.drag_hold_duration)
        self.spin_drag.valueChanged.connect(lambda v: self._update_val("drag_hold_duration", v))
        grid_thr.addWidget(lbl_drag_hold, 1, 0)
        grid_thr.addWidget(self.spin_drag, 1, 1)

        # Double Click Interval
        lbl_double = QLabel("Double Click Max Interval (sec):")
        self.spin_double = QDoubleSpinBox()
        self.spin_double.setRange(0.2, 0.8)
        self.spin_double.setSingleStep(0.05)
        self.spin_double.setValue(settings.gesture.double_click_interval)
        self.spin_double.valueChanged.connect(lambda v: self._update_val("double_click_interval", v))
        grid_thr.addWidget(lbl_double, 1, 2)
        grid_thr.addWidget(self.spin_double, 1, 3)

        # Scroll Sensitivity
        lbl_scroll = QLabel("Scroll Speed / Sensitivity:")
        self.spin_scroll = QSpinBox()
        self.spin_scroll.setRange(5, 80)
        self.spin_scroll.setValue(int(settings.gesture.scroll_sensitivity))
        self.spin_scroll.valueChanged.connect(lambda v: self._update_val("scroll_sensitivity", float(v)))
        grid_thr.addWidget(lbl_scroll, 2, 0)
        grid_thr.addWidget(self.spin_scroll, 2, 1)

        vbox_thr.addLayout(grid_thr)
        layout.addWidget(card_thresh)

        # 3. Interactive Gesture Test Zone
        card_test = QFrame()
        card_test.setProperty("class", "card")
        vbox_test = QVBoxLayout(card_test)

        title_test = QLabel("🎯 Interactive Worker Test Pad")
        title_test.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        desc_test = QLabel("Test your hand gestures safely in the box below before working:")
        desc_test.setStyleSheet("color: #94A3B8; margin-bottom: 10px;")
        vbox_test.addWidget(title_test)
        vbox_test.addWidget(desc_test)

        test_row = QHBoxLayout()
        test_row.setSpacing(14)

        # Test Button 1: Click Tester
        self.btn_test_click = QPushButton("Click Me to Test (Pinch)")
        self.btn_test_click.setProperty("class", "secondaryBtn")
        self.btn_test_click.setFixedHeight(50)
        self._click_count = 0
        self.btn_test_click.clicked.connect(self._on_test_clicked)

        # Test Button 2: Double Click Tester
        self.btn_test_dbl = QPushButton("Double Click Me")
        self.btn_test_dbl.setProperty("class", "secondaryBtn")
        self.btn_test_dbl.setFixedHeight(50)
        self._dbl_count = 0
        self.btn_test_dbl.mouseDoubleClickEvent = lambda e: self._on_test_dbl()

        # Test Button 3: Reset Counters
        btn_reset = QPushButton("Reset Counters")
        btn_reset.setProperty("class", "secondaryBtn")
        btn_reset.setFixedHeight(50)
        btn_reset.clicked.connect(self._reset_test_counters)

        test_row.addWidget(self.btn_test_click, 2)
        test_row.addWidget(self.btn_test_dbl, 2)
        test_row.addWidget(btn_reset, 1)
        vbox_test.addLayout(test_row)

        self.lbl_test_result = QLabel("Result: Waiting for interaction...")
        self.lbl_test_result.setStyleSheet("color: #38BDF8; font-weight: 600; margin-top: 8px;")
        vbox_test.addWidget(self.lbl_test_result)

        layout.addWidget(card_test)

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

    def _update_val(self, key: str, val):
        if hasattr(settings.gesture, key):
            setattr(settings.gesture, key, val)
            settings.save()

    def _on_test_clicked(self):
        self._click_count += 1
        self.lbl_test_result.setText(f"Result: Left Click Registered! (Total clicks: {self._click_count})")
        self.lbl_test_result.setStyleSheet("color: #10B981; font-weight: 600;")

    def _on_test_dbl(self):
        self._dbl_count += 1
        self.lbl_test_result.setText(f"Result: Double Click Success! (Total double clicks: {self._dbl_count})")
        self.lbl_test_result.setStyleSheet("color: #0284C7; font-weight: 600;")

    def _reset_test_counters(self):
        self._click_count = 0
        self._dbl_count = 0
        self.lbl_test_result.setText("Result: Counters reset.")
        self.lbl_test_result.setStyleSheet("color: #94A3B8; font-weight: 600;")
