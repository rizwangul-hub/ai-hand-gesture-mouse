"""UI Views package."""
from ui.views.calibration_view import CalibrationWizardView
from ui.views.camera_view import CameraSettingsView
from ui.views.cursor_view import CursorSettingsView
from ui.views.dashboard_view import DashboardView
from ui.views.gestures_view import GestureSettingsView
from ui.views.live_view import LiveTrackingView

__all__ = [
    "DashboardView",
    "LiveTrackingView",
    "GestureSettingsView",
    "CursorSettingsView",
    "CameraSettingsView",
    "CalibrationWizardView",
]
