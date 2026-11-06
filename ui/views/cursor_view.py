"""Cursor Settings View: speed, dynamic acceleration, 1-Euro smoothing, and boundary margins."""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings

if TYPE_CHECKING:
    from core.cursor import CursorController


class CursorSettingsView(QWidget):
    """Configuration panel for cursor movement, speed, smoothing, acceleration, and boundaries."""

    def __init__(self, cursor: "CursorController", parent=None):
        super().__init__(parent)
        self.cursor = cursor
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

        # 1. Cursor Dynamics Card
        card_dynamics = QFrame()
        card_dynamics.setProperty("class", "card")
        vbox_dyn = QVBoxLayout(card_dynamics)

        title_dyn = QLabel("Cursor Speed & Acceleration")
        title_dyn.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        vbox_dyn.addWidget(title_dyn)

        grid_dyn = QGridLayout()
        grid_dyn.setSpacing(14)

        # Base Speed
        lbl_speed = QLabel("Movement Speed:")
        self.spin_speed = QDoubleSpinBox()
        self.spin_speed.setRange(0.2, 5.0)
        self.spin_speed.setSingleStep(0.1)
        self.spin_speed.setValue(settings.cursor.speed)
        self.spin_speed.valueChanged.connect(self._on_speed_changed)
        grid_dyn.addWidget(lbl_speed, 0, 0)
        grid_dyn.addWidget(self.spin_speed, 0, 1)

        # Dynamic Acceleration Toggle
        self.chk_accel = QCheckBox("Enable Dynamic Acceleration (Fast flick travel, slow precision)")
        self.chk_accel.setChecked(settings.cursor.use_acceleration)
        self.chk_accel.toggled.connect(self._on_accel_toggled)
        grid_dyn.addWidget(self.chk_accel, 1, 0, 1, 2)

        # Acceleration Factor
        lbl_accel_factor = QLabel("Acceleration Boost Factor:")
        self.spin_accel = QDoubleSpinBox()
        self.spin_accel.setRange(0.5, 3.5)
        self.spin_accel.setSingleStep(0.1)
        self.spin_accel.setValue(settings.cursor.acceleration)
        self.spin_accel.valueChanged.connect(self._on_accel_factor_changed)
        grid_dyn.addWidget(lbl_accel_factor, 2, 0)
        grid_dyn.addWidget(self.spin_accel, 2, 1)

        # Precision Mode Multiplier
        lbl_prec = QLabel("Precision Mode Speed Scale:")
        self.spin_prec = QDoubleSpinBox()
        self.spin_prec.setRange(0.1, 0.9)
        self.spin_prec.setSingleStep(0.05)
        self.spin_prec.setValue(settings.cursor.precision_multiplier)
        self.spin_prec.valueChanged.connect(self._on_prec_changed)
        grid_dyn.addWidget(lbl_prec, 3, 0)
        grid_dyn.addWidget(self.spin_prec, 3, 1)

        vbox_dyn.addLayout(grid_dyn)
        layout.addWidget(card_dynamics)

        # 2. Smoothing & Jitter Reduction Card
        card_smooth = QFrame()
        card_smooth.setProperty("class", "card")
        vbox_sm = QVBoxLayout(card_smooth)

        title_sm = QLabel("1€ Adaptive Smoothing & Jitter Suppression")
        title_sm.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        vbox_sm.addWidget(title_sm)

        grid_sm = QGridLayout()
        grid_sm.setSpacing(14)

        # Jitter Deadzone
        lbl_deadzone = QLabel("Micro-Jitter Deadzone (Norm):")
        self.spin_deadzone = QDoubleSpinBox()
        self.spin_deadzone.setRange(0.002, 0.08)
        self.spin_deadzone.setSingleStep(0.002)
        self.spin_deadzone.setDecimals(3)
        self.spin_deadzone.setValue(settings.cursor.deadzone)
        self.spin_deadzone.valueChanged.connect(self._on_deadzone_changed)
        grid_sm.addWidget(lbl_deadzone, 0, 0)
        grid_sm.addWidget(self.spin_deadzone, 0, 1)

        # Min Cutoff (Lower = smoother when still)
        lbl_cutoff = QLabel("Stillness Smoothing (min_cutoff):")
        self.spin_cutoff = QDoubleSpinBox()
        self.spin_cutoff.setRange(0.2, 5.0)
        self.spin_cutoff.setSingleStep(0.1)
        self.spin_cutoff.setValue(settings.cursor.min_cutoff)
        self.spin_cutoff.valueChanged.connect(self._on_cutoff_changed)
        grid_sm.addWidget(lbl_cutoff, 1, 0)
        grid_sm.addWidget(self.spin_cutoff, 1, 1)

        # Beta (Higher = zero latency when moving fast)
        lbl_beta = QLabel("Motion Responsiveness (beta):")
        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(0.001, 0.1)
        self.spin_beta.setSingleStep(0.005)
        self.spin_beta.setDecimals(3)
        self.spin_beta.setValue(settings.cursor.beta)
        self.spin_beta.valueChanged.connect(self._on_beta_changed)
        grid_sm.addWidget(lbl_beta, 2, 0)
        grid_sm.addWidget(self.spin_beta, 2, 1)

        vbox_sm.addLayout(grid_sm)
        layout.addWidget(card_smooth)

        # 3. Active Screen Area Margins Card
        card_area = QFrame()
        card_area.setProperty("class", "card")
        vbox_area = QVBoxLayout(card_area)

        title_area = QLabel("Camera Active Tracking Margins")
        title_area.setStyleSheet("font-size: 15px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;")
        desc_area = QLabel("Margins define the physical camera rectangle that stretches across 100% of your computer screen.")
        desc_area.setStyleSheet("color: #94A3B8; margin-bottom: 8px;")
        vbox_area.addWidget(title_area)
        vbox_area.addWidget(desc_area)

        grid_area = QGridLayout()
        grid_area.setSpacing(14)

        lbl_mx = QLabel("Horizontal Margin (%):")
        self.spin_mx = QDoubleSpinBox()
        self.spin_mx.setRange(0.05, 0.35)
        self.spin_mx.setSingleStep(0.02)
        self.spin_mx.setValue(settings.cursor.margin_x)
        self.spin_mx.valueChanged.connect(self._on_margin_x_changed)
        grid_area.addWidget(lbl_mx, 0, 0)
        grid_area.addWidget(self.spin_mx, 0, 1)

        lbl_my = QLabel("Vertical Margin (%):")
        self.spin_my = QDoubleSpinBox()
        self.spin_my.setRange(0.05, 0.35)
        self.spin_my.setSingleStep(0.02)
        self.spin_my.setValue(settings.cursor.margin_y)
        self.spin_my.valueChanged.connect(self._on_margin_y_changed)
        grid_area.addWidget(lbl_my, 1, 0)
        grid_area.addWidget(self.spin_my, 1, 1)

        vbox_area.addLayout(grid_area)
        layout.addWidget(card_area)

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

    def _on_speed_changed(self, val: float):
        settings.cursor.speed = val
        settings.save()

    def _on_accel_toggled(self, checked: bool):
        settings.cursor.use_acceleration = checked
        settings.save()

    def _on_accel_factor_changed(self, val: float):
        settings.cursor.acceleration = val
        settings.save()

    def _on_prec_changed(self, val: float):
        settings.cursor.precision_multiplier = val
        settings.save()

    def _on_deadzone_changed(self, val: float):
        settings.cursor.deadzone = val
        settings.save()

    def _on_cutoff_changed(self, val: float):
        settings.cursor.min_cutoff = val
        self.cursor.update_settings()
        settings.save()

    def _on_beta_changed(self, val: float):
        settings.cursor.beta = val
        self.cursor.update_settings()
        settings.save()

    def _on_margin_x_changed(self, val: float):
        settings.cursor.margin_x = val
        settings.save()

    def _on_margin_y_changed(self, val: float):
        settings.cursor.margin_y = val
        settings.save()
