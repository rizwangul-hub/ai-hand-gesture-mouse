"""AI Hand Gesture Control System - Professional Desktop Application.

Transforms webcam hand gestures into natural, jitter-free cursor control and workflow actions.
"""

import sys
import os

# Prevent OpenBLAS thread allocation issues on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

# Ensure current directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from config.settings import settings
from core.engine import HandControlEngine
from shortcuts.hotkeys import GlobalHotkeyManager
from ui.main_window import MainWindow
from utils.logger import logger


def main():
    logger.info("Initializing AI Hand Gesture Control System...")

    # Enable High DPI pixmaps
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("AI Hand Gesture Control System")
    app.setApplicationDisplayName("AI Hand Mouse")
    app.setOrganizationName("AI Workplace Solutions")

    # Initialize Core Engine and Hotkey subsystem
    engine = HandControlEngine()
    hotkeys = GlobalHotkeyManager()

    # Start global hotkeys listener
    try:
        hotkeys.start()
    except Exception as exc:
        logger.warning(f"Could not initialize global Win32 hotkeys: {exc}")

    # Initialize Main Desktop UI Window
    window = MainWindow(engine=engine, hotkeys=hotkeys)

    if settings.system.start_minimized:
        window.hide()
        logger.info("Application started in system tray.")
    else:
        window.show()
        logger.info("Application main window launched.")

    # Execute Qt event loop
    exit_code = app.exec()

    # Cleanup upon exit
    logger.info("Finalizing application shutdown...")
    engine.stop()
    hotkeys.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
