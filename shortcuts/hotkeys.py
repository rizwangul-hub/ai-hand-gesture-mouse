"""Global Windows Hotkey Manager using native Win32 API."""

import ctypes
import threading
from typing import Callable, Dict, Optional
from ctypes import wintypes
from utils.logger import logger

# Win32 Hotkey Modifiers
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# Virtual key codes
VK_H = 0x48
VK_P = 0x50
VK_Q = 0x51
WM_HOTKEY = 0x0312


class GlobalHotkeyManager:
    """Manages system-wide Windows hotkeys for background desktop control."""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._actions: Dict[int, Callable[[], None]] = {}
        self._thread_id: Optional[int] = None

    def register(
        self,
        on_toggle: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_emergency_stop: Optional[Callable[[], None]] = None,
    ):
        """Setup actions for default hotkeys."""
        if on_toggle:
            self._actions[1] = on_toggle  # Ctrl + Alt + H
        if on_pause:
            self._actions[2] = on_pause   # Ctrl + Alt + P
        if on_emergency_stop:
            self._actions[3] = on_emergency_stop  # Ctrl + Alt + Q

    def start(self):
        """Start Windows message loop in background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._msg_loop, name="GlobalHotkeys", daemon=True)
        self._thread.start()

    def _msg_loop(self):
        """Native Win32 message loop registering and listening for hotkeys."""
        user32 = ctypes.windll.user32
        self._thread_id = ctypes.windll.kernel32.GetCurrentThreadId()

        # Register hotkeys
        # 1: Ctrl + Alt + H (Toggle tracking)
        user32.RegisterHotKey(None, 1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_H)
        # 2: Ctrl + Alt + P (Pause / Resume)
        user32.RegisterHotKey(None, 2, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_P)
        # 3: Ctrl + Alt + Q (Emergency Stop)
        user32.RegisterHotKey(None, 3, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_Q)

        logger.info("Registered global hotkeys: Ctrl+Alt+H (Toggle), Ctrl+Alt+P (Pause), Ctrl+Alt+Q (Emergency)")

        msg = wintypes.MSG()
        while self._running:
            ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret == 0 or ret == -1:
                break
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id in self._actions:
                    try:
                        self._actions[hotkey_id]()
                    except Exception as exc:
                        logger.error(f"Error handling hotkey {hotkey_id}: {exc}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Unregister hotkeys
        user32.UnregisterHotKey(None, 1)
        user32.UnregisterHotKey(None, 2)
        user32.UnregisterHotKey(None, 3)
        logger.info("Global hotkeys unregistered.")

    def stop(self):
        """Terminate hotkey message loop."""
        self._running = False
        if self._thread_id:
            ctypes.windll.user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)  # WM_QUIT
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
