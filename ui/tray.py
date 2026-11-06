"""Windows System Tray integration and notification manager."""

from typing import TYPE_CHECKING
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config.settings import settings
from core.types import TrackingState

if TYPE_CHECKING:
    from ui.main_window import MainWindow


def create_tray_icon(active: bool = False) -> QIcon:
    """Generate a clean colored circle icon programmatically."""
    pix = QPixmap(32, 32)
    pix.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    # Outer circle
    color = QColor("#10B981") if active else QColor("#0284C7")
    painter.setBrush(color)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawEllipse(3, 3, 26, 26)

    # Inner hand dot
    painter.setBrush(QColor("#FFFFFF"))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(12, 12, 8, 8)
    painter.end()

    return QIcon(pix)


class SystemTrayManager:
    """Manages system tray icon, context menu, and desktop notifications."""

    def __init__(self, main_window: "MainWindow"):
        self.window = main_window
        self.engine = main_window.engine
        self.tray_icon = QSystemTrayIcon(main_window)
        self.tray_icon.setIcon(create_tray_icon(False))
        self.tray_icon.setToolTip("AI Hand Gesture Control System")

        self._create_menu()
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _create_menu(self):
        menu = QMenu()

        self.action_show = QAction("Open Dashboard", menu)
        self.action_show.triggered.connect(self.window.show_normal)
        menu.addAction(self.action_show)

        menu.addSeparator()

        self.action_start = QAction("Start Tracking", menu)
        self.action_start.triggered.connect(self.engine.start)
        menu.addAction(self.action_start)

        self.action_pause = QAction("Pause / Resume", menu)
        self.action_pause.triggered.connect(self.engine.toggle_pause)
        menu.addAction(self.action_pause)

        self.action_stop = QAction("Stop Tracking", menu)
        self.action_stop.triggered.connect(self.engine.stop)
        menu.addAction(self.action_stop)

        menu.addSeparator()

        self.action_exit = QAction("Exit Completely", menu)
        self.action_exit.triggered.connect(self.window.quit_application)
        menu.addAction(self.action_exit)

        self.tray_icon.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.window.isVisible():
                self.window.hide()
            else:
                self.window.show_normal()

    def show_message(self, title: str, message: str):
        """Display Windows native balloon notification."""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2500)

    def update_state(self, state: TrackingState):
        """Update icon appearance based on engine tracking state."""
        if state == TrackingState.RUNNING:
            self.tray_icon.setIcon(create_tray_icon(True))
            self.tray_icon.setToolTip("AI Hand Mouse: Active")
        elif state == TrackingState.PAUSED:
            self.tray_icon.setIcon(create_tray_icon(False))
            self.tray_icon.setToolTip("AI Hand Mouse: Paused")
        else:
            self.tray_icon.setIcon(create_tray_icon(False))
            self.tray_icon.setToolTip("AI Hand Mouse: Stopped")
