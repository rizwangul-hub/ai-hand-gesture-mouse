"""Main Window hosting sidebar navigation, top status bar, stacked views, and tray integration."""

from typing import Optional
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from core.engine import HandControlEngine
from core.types import FramePacket, TrackingState
from shortcuts.hotkeys import GlobalHotkeyManager
from ui.theme import get_theme_stylesheet
from ui.tray import SystemTrayManager, create_tray_icon
from ui.views.calibration_view import CalibrationWizardView
from ui.views.camera_view import CameraSettingsView
from ui.views.cursor_view import CursorSettingsView
from ui.views.dashboard_view import DashboardView
from ui.views.gestures_view import GestureSettingsView
from ui.views.live_view import LiveTrackingView
from utils.logger import logger


class EngineSignalBridge(QObject):
    """Bridge for cross-thread communication from background engine to Qt UI thread."""
    frame_received = Signal(object)
    state_changed = Signal(object)


class MainWindow(QMainWindow):
    """Main desktop interface for AI Hand Gesture Control System."""

    def __init__(self, engine: HandControlEngine, hotkeys: GlobalHotkeyManager):
        super().__init__()
        self.engine = engine
        self.hotkeys = hotkeys

        self.setWindowTitle("AI Hand Gesture Control System")
        self.resize(1150, 760)
        self.setMinimumSize(950, 640)
        self.setWindowIcon(create_tray_icon(False))

        # Setup Thread Signal Bridge
        self.bridge = EngineSignalBridge()
        self.bridge.frame_received.connect(self._on_frame_received)
        self.bridge.state_changed.connect(self._on_state_changed)

        self.engine.on_frame_ready = lambda packet: self.bridge.frame_received.emit(packet)
        self.engine.on_state_changed = lambda state: self.bridge.state_changed.emit(state)

        # Build UI layout
        self._init_ui()
        self._apply_theme(settings.system.theme)

        # Setup System Tray
        self.tray_manager = SystemTrayManager(self)

        # Register global shortcuts
        self.hotkeys.register(
            on_toggle=self._hotkey_toggle,
            on_pause=self._hotkey_pause,
            on_emergency_stop=self._hotkey_emergency_stop,
        )

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Navigation Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 0, 8, 16)
        sb_layout.setSpacing(4)

        app_title = QLabel("AI Hand Mouse")
        app_title.setObjectName("appTitle")
        app_sub = QLabel("Professional Edition v2.0")
        app_sub.setObjectName("appSubtitle")

        sb_layout.addWidget(app_title)
        sb_layout.addWidget(app_sub)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_buttons = []
        nav_items = [
            ("📊  Dashboard", 0),
            ("📹  Live Tracking", 1),
            ("✋  Gesture Controls", 2),
            ("🎯  Cursor Settings", 3),
            ("⚙️  Camera Settings", 4),
            ("🛠️  Calibration Wizard", 5),
        ]

        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "navBtn")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, i=idx: self.view_stack.setCurrentIndex(i))
            self.nav_group.addButton(btn, idx)
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # Theme toggle in sidebar footer
        self.btn_theme = QPushButton("☀️ Light Theme" if settings.system.theme == "dark" else "🌙 Dark Theme")
        self.btn_theme.setProperty("class", "secondaryBtn")
        self.btn_theme.clicked.connect(self._toggle_theme)
        sb_layout.addWidget(self.btn_theme)

        root_layout.addWidget(sidebar)

        # 2. Main Content Area (Header + Stacked Views + Status Bar)
        content_pane = QWidget()
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Header Bar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(20, 10, 20, 10)

        self.lbl_status_pill = QLabel("● Engine Idle")
        self.lbl_status_pill.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 13px;")

        hotkey_hint = QLabel("Hotkeys: Ctrl+Alt+H (Toggle) | Ctrl+Alt+P (Pause) | Ctrl+Alt+Q (Emergency)")
        hotkey_hint.setStyleSheet("color: #64748B; font-size: 12px;")

        tb_layout.addWidget(self.lbl_status_pill)
        tb_layout.addStretch()
        tb_layout.addWidget(hotkey_hint)

        content_layout.addWidget(top_bar)

        # Stacked Views
        self.view_stack = QStackedWidget()
        self.view_dashboard = DashboardView(self.engine)
        self.view_live = LiveTrackingView(self.engine)
        self.view_gestures = GestureSettingsView()
        self.view_cursor = CursorSettingsView(self.engine.cursor)
        self.view_camera = CameraSettingsView(self.engine)
        self.view_calibration = CalibrationWizardView(self.engine)

        self.view_stack.addWidget(self.view_dashboard)
        self.view_stack.addWidget(self.view_live)
        self.view_stack.addWidget(self.view_gestures)
        self.view_stack.addWidget(self.view_cursor)
        self.view_stack.addWidget(self.view_camera)
        self.view_stack.addWidget(self.view_calibration)

        content_layout.addWidget(self.view_stack, stretch=1)
        root_layout.addWidget(content_pane, stretch=1)

    def _apply_theme(self, theme_name: str):
        self.setStyleSheet(get_theme_stylesheet(theme_name))
        settings.system.theme = theme_name
        settings.save()

    def _toggle_theme(self):
        new_theme = "light" if settings.system.theme == "dark" else "dark"
        self._apply_theme(new_theme)
        self.btn_theme.setText("☀️ Light Theme" if new_theme == "dark" else "🌙 Dark Theme")

    def _on_frame_received(self, packet: FramePacket):
        """Dispatched in main GUI thread."""
        self.view_live.update_frame(packet)
        self.view_dashboard.update_packet(packet)
        self.view_calibration.update_packet(packet)

    def _on_state_changed(self, state: TrackingState):
        """Update status pill and tray on state change."""
        self.tray_manager.update_state(state)
        if state == TrackingState.RUNNING:
            self.lbl_status_pill.setText("● Tracking Active")
            self.lbl_status_pill.setStyleSheet("color: #10B981; font-weight: 600; font-size: 13px;")
        elif state == TrackingState.PAUSED:
            self.lbl_status_pill.setText("● Tracking Paused")
            self.lbl_status_pill.setStyleSheet("color: #F59E0B; font-weight: 600; font-size: 13px;")
        else:
            self.lbl_status_pill.setText("● Engine Stopped")
            self.lbl_status_pill.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 13px;")

    def _hotkey_toggle(self):
        if self.engine.is_running:
            self.engine.stop()
            self.tray_manager.show_message("Hand Mouse", "Tracking Stopped")
        else:
            self.engine.start()
            self.tray_manager.show_message("Hand Mouse", "Tracking Started")

    def _hotkey_pause(self):
        self.engine.toggle_pause()
        state_str = "Paused" if self.engine.state == TrackingState.PAUSED else "Resumed"
        self.tray_manager.show_message("Hand Mouse", f"Tracking {state_str}")

    def _hotkey_emergency_stop(self):
        self.engine.emergency_stop()
        self.tray_manager.show_message("Hand Mouse Emergency", "Cursor control halted immediately!")

    def show_normal(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """Intercept close: minimize to tray if enabled, or confirm shutdown."""
        if settings.system.minimize_to_tray and self.tray_manager.tray_icon.isVisible():
            self.hide()
            self.tray_manager.show_message("Hand Mouse Minimized", "Application is still active in system tray.")
            event.ignore()
        else:
            self.quit_application()
            event.accept()

    def quit_application(self):
        """Clean shutdown of engine, camera, hotkeys, and app exit."""
        logger.info("Application shutting down...")
        self.engine.stop()
        self.hotkeys.stop()
        self.tray_manager.tray_icon.hide()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
