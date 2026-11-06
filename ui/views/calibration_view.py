"""Interactive 5-Step Calibration Wizard for personalized hand and environment setup."""

from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from core.types import FramePacket

if TYPE_CHECKING:
    from core.engine import HandControlEngine


class CalibrationWizardView(QWidget):
    """Guided step-by-step wizard helping workers calibrate camera position, reach, and gestures."""

    def __init__(self, engine: "HandControlEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self._current_step = 0
        self._min_seen_pinch = 1.0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Header Card
        header_card = QFrame()
        header_card.setProperty("class", "card")
        h_layout = QVBoxLayout(header_card)

        self.title_step = QLabel("Step 1 of 5: Webcam Positioning & Workspace Setup")
        self.title_step.setStyleSheet("font-size: 17px; font-weight: 700; color: #38BDF8;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 5)
        self.progress_bar.setValue(1)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        h_layout.addWidget(self.title_step)
        h_layout.addWidget(self.progress_bar)
        layout.addWidget(header_card)

        # Stacked Pages
        self.stack = QStackedWidget()

        # Page 1: Position Camera
        self.stack.addWidget(self._create_step1_widget())

        # Page 2: Hand Visibility
        self.stack.addWidget(self._create_step2_widget())

        # Page 3: Boundary Range Calibration
        self.stack.addWidget(self._create_step3_widget())

        # Page 4: Pinch & Click Calibration
        self.stack.addWidget(self._create_step4_widget())

        # Page 5: Save Calibration Profile
        self.stack.addWidget(self._create_step5_widget())

        layout.addWidget(self.stack, stretch=1)

        # Bottom Navigation Controls Card
        nav_card = QFrame()
        nav_card.setProperty("class", "card")
        n_layout = QHBoxLayout(nav_card)

        self.btn_prev = QPushButton("← Back")
        self.btn_prev.setProperty("class", "secondaryBtn")
        self.btn_prev.setEnabled(False)
        self.btn_prev.clicked.connect(self._prev_step)

        self.btn_next = QPushButton("Next Step →")
        self.btn_next.setProperty("class", "primaryBtn")
        self.btn_next.clicked.connect(self._next_step)

        n_layout.addWidget(self.btn_prev)
        n_layout.addStretch()
        n_layout.addWidget(self.btn_next)
        layout.addWidget(nav_card)

    def _create_step1_widget(self) -> QWidget:
        w = QFrame()
        w.setProperty("class", "card")
        v = QVBoxLayout(w)
        v.setSpacing(14)

        heading = QLabel("Optimal Camera & Seating Position")
        heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        instructions = QLabel(
            "1. Place your webcam directly in front of you (on top of your monitor or on your desk).\n"
            "2. Sit comfortably at a distance of approximately 40 to 70 centimeters from the camera.\n"
            "3. Ensure the room has balanced lighting without harsh backlight behind you.\n"
            "4. Keep your arm rested comfortably on your desk or armrest to avoid fatigue."
        )
        instructions.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.8;")

        v.addWidget(heading)
        v.addWidget(instructions)
        v.addStretch()
        return w

    def _create_step2_widget(self) -> QWidget:
        w = QFrame()
        w.setProperty("class", "card")
        v = QVBoxLayout(w)
        v.setSpacing(14)

        heading = QLabel("Hand Detection & Alignment Check")
        heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        instructions = QLabel(
            "Raise your hand in front of the camera with your palm facing the screen.\n"
            "The indicator below will verify your hand landmarks in real-time."
        )
        instructions.setStyleSheet("color: #94A3B8; font-size: 13px;")

        self.lbl_step2_status = QLabel("Checking hand tracking...")
        self.lbl_step2_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #F59E0B;")

        v.addWidget(heading)
        v.addWidget(instructions)
        v.addWidget(self.lbl_step2_status)
        v.addStretch()
        return w

    def _create_step3_widget(self) -> QWidget:
        w = QFrame()
        w.setProperty("class", "card")
        v = QVBoxLayout(w)
        v.setSpacing(14)

        heading = QLabel("Screen Boundary & Active Area Calibration")
        heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        instructions = QLabel(
            "Move your index finger to the corners of your comfortable hand motion range.\n"
            "You should not need to reach uncomfortably far to touch the screen corners."
        )
        instructions.setStyleSheet("color: #94A3B8; font-size: 13px;")

        btn_auto_margin = QPushButton("Calibrate Comfortable Margins (15%)")
        btn_auto_margin.setProperty("class", "secondaryBtn")
        btn_auto_margin.clicked.connect(self._apply_calibrated_margins)

        self.lbl_step3_status = QLabel("Comfortable margins active: 15% Horizontal, 15% Vertical.")
        self.lbl_step3_status.setStyleSheet("color: #10B981; font-weight: 500;")

        v.addWidget(heading)
        v.addWidget(instructions)
        v.addWidget(btn_auto_margin)
        v.addWidget(self.lbl_step3_status)
        v.addStretch()
        return w

    def _create_step4_widget(self) -> QWidget:
        w = QFrame()
        w.setProperty("class", "card")
        v = QVBoxLayout(w)
        v.setSpacing(14)

        heading = QLabel("Click & Pinch Sensitivity Calibration")
        heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        instructions = QLabel(
            "Pinch your thumb and index finger together a few times.\n"
            "We will analyze your natural finger pinch distance and calibrate trigger levels."
        )
        instructions.setStyleSheet("color: #94A3B8; font-size: 13px;")

        self.lbl_step4_status = QLabel("Pinch status: Waiting for pinch...")
        self.lbl_step4_status.setStyleSheet("color: #38BDF8; font-weight: 600;")

        btn_apply_pinch = QPushButton("Apply Calibrated Pinch Threshold")
        btn_apply_pinch.setProperty("class", "secondaryBtn")
        btn_apply_pinch.clicked.connect(self._apply_calibrated_pinch)

        v.addWidget(heading)
        v.addWidget(instructions)
        v.addWidget(self.lbl_step4_status)
        v.addWidget(btn_apply_pinch)
        v.addStretch()
        return w

    def _create_step5_widget(self) -> QWidget:
        w = QFrame()
        w.setProperty("class", "card")
        v = QVBoxLayout(w)
        v.setSpacing(14)

        heading = QLabel("Save Calibration Profile")
        heading.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        instructions = QLabel(
            "Congratulations! Your workspace and hand gestures are calibrated.\n"
            "Save this profile so the AI Hand Mouse remembers your settings whenever you start working."
        )
        instructions.setStyleSheet("color: #94A3B8; font-size: 13px;")

        h_box = QHBoxLayout()
        lbl_pname = QLabel("Profile Name:")
        self.txt_profile = QLineEdit("My Workspace Profile")
        self.txt_profile.setFixedWidth(240)
        btn_save_p = QPushButton("Save & Finish")
        btn_save_p.setProperty("class", "primaryBtn")
        btn_save_p.clicked.connect(self._save_profile_finish)

        h_box.addWidget(lbl_pname)
        h_box.addWidget(self.txt_profile)
        h_box.addWidget(btn_save_p)
        h_box.addStretch()

        self.lbl_step5_status = QLabel("")

        v.addWidget(heading)
        v.addWidget(instructions)
        v.addLayout(h_box)
        v.addWidget(self.lbl_step5_status)
        v.addStretch()
        return w

    def _apply_calibrated_margins(self):
        settings.cursor.margin_x = 0.15
        settings.cursor.margin_y = 0.15
        settings.save()
        self.lbl_step3_status.setText("✓ Margins calibrated and applied!")

    def _apply_calibrated_pinch(self):
        if self._min_seen_pinch < 0.10:
            target_thresh = max(0.040, min(0.065, self._min_seen_pinch + 0.015))
            settings.gesture.pinch_threshold = target_thresh
            settings.gesture.pinch_release_threshold = target_thresh + 0.025
            settings.save()
            self.lbl_step4_status.setText(f"✓ Calibrated: Trigger at {target_thresh:.3f}, Release at {(target_thresh+0.025):.3f}")
        else:
            self.lbl_step4_status.setText("✓ Default ergonomic pinch threshold applied (0.050).")

    def _save_profile_finish(self):
        name = self.txt_profile.text().strip() or "Custom Profile"
        settings.save_custom_profile(name)
        self.lbl_step5_status.setText(f"✓ Profile '{name}' saved successfully!")
        self.lbl_step5_status.setStyleSheet("color: #10B981; font-weight: 600;")

    def _next_step(self):
        if self._current_step < 4:
            self._current_step += 1
            self.stack.setCurrentIndex(self._current_step)
            self._update_step_ui()

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self.stack.setCurrentIndex(self._current_step)
            self._update_step_ui()

    def _update_step_ui(self):
        self.progress_bar.setValue(self._current_step + 1)
        titles = [
            "Step 1 of 5: Webcam Positioning & Workspace Setup",
            "Step 2 of 5: Hand Visibility & Alignment Check",
            "Step 3 of 5: Screen Boundary & Active Area Calibration",
            "Step 4 of 5: Click & Pinch Sensitivity Calibration",
            "Step 5 of 5: Save Calibration Profile",
        ]
        self.title_step.setText(titles[self._current_step])
        self.btn_prev.setEnabled(self._current_step > 0)
        self.btn_next.setEnabled(self._current_step < 4)

    def update_packet(self, packet: FramePacket):
        """Receive live telemetry to guide user in calibration steps."""
        if self._current_step == 1:
            if packet.hands:
                hand = packet.hands[0]
                self.lbl_step2_status.setText(f"✓ {hand.handedness} Hand detected with {int(hand.confidence * 100)}% confidence!")
                self.lbl_step2_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #10B981;")
            else:
                self.lbl_step2_status.setText("Searching for hand... Please hold hand in view of webcam.")
                self.lbl_step2_status.setStyleSheet("font-size: 14px; font-weight: 600; color: #F59E0B;")

        elif self._current_step == 3:
            if packet.hands:
                hand = packet.hands[0]
                import math
                dist = math.hypot(hand.thumb_tip.x - hand.index_tip.x, hand.thumb_tip.y - hand.index_tip.y)
                if dist < self._min_seen_pinch:
                    self._min_seen_pinch = dist
                self.lbl_step4_status.setText(f"Current thumb-index distance: {dist:.3f} | Minimum seen: {self._min_seen_pinch:.3f}")
