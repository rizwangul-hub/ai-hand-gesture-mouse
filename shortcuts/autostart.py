"""Windows Startup Integration via Current User Registry (Non-Admin)."""

import os
import sys
import winreg
from utils.logger import logger

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "AIHandGestureControl"


def set_run_on_startup(enable: bool) -> bool:
    """Add or remove application from Windows user login startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        if enable:
            if getattr(sys, "frozen", False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            logger.info("Enabled application launch on Windows startup.")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("Removed application from Windows startup.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as exc:
        logger.error(f"Failed to configure Windows startup registry: {exc}")
        return False


def is_run_on_startup_enabled() -> bool:
    """Check if app is currently registered in Windows user startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False
