"""Camera Settings View: device selection, resolution presets, and hardware test."""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QCheckBox,
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
from core.camera import CameraManager

if TYPE_CHECKING:
    from core.engine import HandControlEngine


class CameraSettingsView(QWidget):
    """Device configuration panel for webcam enumeration, resolution, FPS, and auto-reconnect."""

    def __init__(self, engine: "HandControlEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        card = QFrame()
        card.setProperty("class", "card")
        vbox = QVBoxLayout(card)
        vbox.setSpacing(18)

        title = QLabel("Hardware Webcam Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #38BDF8;")
        vbox.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Camera Device Selector
        lbl_cam = QLabel("Active Camera Device:")
        self.combo_cam = QComboBox()
        self._populate_cameras()
        self.combo_cam.currentIndexChanged.connect(self._on_camera_selected)

        btn_refresh = QPushButton("🔄 Scan Devices")
        btn_refresh.setProperty("class", "secondaryBtn")
        btn_refresh.clicked.connect(self._populate_cameras)

        grid.addWidget(lbl_cam, 0, 0)
        grid.addWidget(self.combo_cam, 0, 1)
        grid.addWidget(btn_refresh, 0, 2)

        # Resolution Preset
        lbl_res = QLabel("Capture Resolution:")
        self.combo_res = QComboBox()
        self.combo_res.addItems(["640 x 480 (Recommended, Low Latency)", "1280 x 720 (HD)", "1920 x 1080 (Full HD)"])
        current_res = f"{settings.camera.width} x {settings.camera.height}"
        for i in range(self.combo_res.count()):
            if current_res in self.combo_res.itemText(i):
                self.combo_res.setCurrentIndex(i)
                break
        self.combo_res.currentIndexChanged.connect(self._on_res_changed)
        grid.addWidget(lbl_res, 1, 0)
        grid.addWidget(self.combo_res, 1, 1)

        # Target FPS
        lbl_fps = QLabel("Target Hardware FPS:")
        self.combo_fps = QComboBox()
        self.combo_fps.addItems(["30 FPS (Standard)", "60 FPS (Ultra Smooth)"])
        if settings.camera.fps == 60:
            self.combo_fps.setCurrentIndex(1)
        else:
            self.combo_fps.setCurrentIndex(0)
        self.combo_fps.currentIndexChanged.connect(self._on_fps_changed)
        grid.addWidget(lbl_fps, 2, 0)
        grid.addWidget(self.combo_fps, 2, 1)

        # Horizontal Flip
        self.chk_flip = QCheckBox("Mirror Camera Horizontally (Natural selfie movement)")
        self.chk_flip.setChecked(settings.camera.flip_horizontal)
        self.chk_flip.toggled.connect(self._on_flip_toggled)
        grid.addWidget(self.chk_flip, 3, 0, 1, 2)

        # Auto Reconnect
        self.chk_reconnect = QCheckBox("Automatic Camera Reconnection on Disconnect / Sleep")
        self.chk_reconnect.setChecked(settings.camera.auto_reconnect)
        self.chk_reconnect.toggled.connect(self._on_reconnect_toggled)
        grid.addWidget(self.chk_reconnect, 4, 0, 1, 2)

        vbox.addLayout(grid)

        # Action Buttons
        btn_box = QHBoxLayout()
        self.btn_test = QPushButton("🔍 Test Camera Stream")
        self.btn_test.setProperty("class", "primaryBtn")
        self.btn_test.clicked.connect(self._test_camera)

        self.lbl_test_status = QLabel("")
        self.lbl_test_status.setStyleSheet("font-weight: 600; margin-left: 12px;")

        btn_box.addWidget(self.btn_test)
        btn_box.addWidget(self.lbl_test_status)
        btn_box.addStretch()
        vbox.addLayout(btn_box)

        layout.addWidget(card)
        layout.addStretch()

    def _populate_cameras(self):
        self.combo_cam.clear()
        cams = CameraManager.list_available_cameras(max_tested=4)
        for c in cams:
            self.combo_cam.addItem(f"Camera #{c}", c)
        idx = self.combo_cam.findData(settings.camera.camera_index)
        if idx >= 0:
            self.combo_cam.setCurrentIndex(idx)

    def _on_camera_selected(self, index: int):
        cam_id = self.combo_cam.itemData(index)
        if cam_id is not None:
            settings.camera.camera_index = cam_id
            settings.save()

    def _on_res_changed(self, index: int):
        if index == 0:
            settings.camera.width = 640
            settings.camera.height = 480
        elif index == 1:
            settings.camera.width = 1280
            settings.camera.height = 720
        elif index == 2:
            settings.camera.width = 1920
            settings.camera.height = 1080
        settings.save()

    def _on_fps_changed(self, index: int):
        settings.camera.fps = 60 if index == 1 else 30
        settings.save()

    def _on_flip_toggled(self, checked: bool):
        settings.camera.flip_horizontal = checked
        settings.save()

    def _on_reconnect_toggled(self, checked: bool):
        settings.camera.auto_reconnect = checked
        settings.save()

    def _test_camera(self):
        cam_id = settings.camera.camera_index
        self.lbl_test_status.setText(f"Testing Camera #{cam_id}...")
        self.lbl_test_status.setStyleSheet("color: #38BDF8; font-weight: 600;")

        # Test read
        test_mgr = CameraManager()
        ok = test_mgr._open_capture(cam_id)
        if ok and test_mgr._cap is not None:
            ret, frame = test_mgr._cap.read()
            test_mgr._cap.release()
            if ret and frame is not None:
                self.lbl_test_status.setText(f"✓ Camera #{cam_id} is operating perfectly ({frame.shape[1]}x{frame.shape[0]})!")
                self.lbl_test_status.setStyleSheet("color: #10B981; font-weight: 600;")
                return

        self.lbl_test_status.setText(f"✗ Camera #{cam_id} could not be opened or is busy.")
        self.lbl_test_status.setStyleSheet("color: #EF4444; font-weight: 600;")
