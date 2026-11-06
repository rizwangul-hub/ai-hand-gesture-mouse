# AI Hand Gesture Control System (Professional Edition v2.0)

> A modern, production-grade AI desktop application that transforms natural webcam hand gestures into responsive, jitter-free cursor control and daily computer workflow actions for real workers.

---

## 🌟 Key Features

### 1. Core Hand Tracking Engine
- **Next-Gen MediaPipe AI**: Powered by Google MediaPipe Hand Landmarker with XNNPACK acceleration for sub-millisecond landmark inference.
- **1€ Adaptive Filter**: Dynamic velocity-based smoothing (Casiez et al.) eliminates hand tremor/jitter while maintaining zero lag during rapid swipes.
- **Dynamic Cursor Acceleration**: Automatically boosts cursor speed during quick sweeps while granting sub-pixel precision during slow micro-movements.
- **Smart Pause & Auto-Recovery**: Automatically halts cursor dispatch when the user steps away from the camera, and smoothly reconnects without sudden cursor snapping when the hand returns.
- **Low Resource Consumption**: Multi-threaded frame grabber with single-frame buffers and a CPU Saver Mode (toggle camera preview off) to preserve laptop battery and office PC resources.

### 2. Ergonomic Gesture Control Suite
| Hand Gesture | Computer Action | Description |
|---|---|---|
| **Index Finger Motion** | Move Cursor | Smooth, mapped cursor movement across full display |
| **Index + Thumb Pinch** | Left Click | Fast debounced click with release hysteresis |
| **Double Pinch** | Double Click | Opens files, folders, and selects words |
| **Hold Pinch & Move** | Drag and Drop | Grabs windows or desktop icons; releases on finger release |
| **Two Fingers Together** | Right Click | Displays context menus |
| **Two Fingers Up / Down** | Vertical Scroll | Natural continuous scrolling for long web pages and spreadsheets |
| **Thumb + Middle Pinch** | Precision Mode | Drops cursor speed by 60% for clicking small checkboxes and fine UI elements |
| **Open Palm (Hold 0.8s)** | Pause / Standby | Disengages cursor tracking so you can type or drink coffee |
| **Open Palm (Hold 1.0s)** | Resume Tracking | Resumes active mouse control |
| **Closed Fist** | Emergency Stop | Immediate safety lock that releases all held mouse buttons |

### 3. Modern Desktop UI (PySide6)
- **Dark & Light Mode**: Styled with clean typography, rounded card layouts, and responsive controls.
- **Real-Time Telemetry**: Live FPS indicator, camera connection status, hand tracking confidence, and active gesture badge.
- **Live Preview Canvas**: Displays colored hand skeleton landmarks and active tracking boundaries with one-click CPU saver toggle.
- **Interactive Calibration Wizard**: A 5-step guided wizard to help users position their camera, calibrate active tracking reach, set custom pinch thresholds, and save personalized profiles.
- **Windows System Tray & Hotkeys**:
  - `Ctrl + Alt + H`: Toggle tracking On/Off
  - `Ctrl + Alt + P`: Pause / Resume tracking
  - `Ctrl + Alt + Q`: Emergency Halt (releases buttons immediately)

---

## 📁 Project Architecture

```
hand-mouse/
├── main.py                    # Application launcher and Qt entry point
├── run_app.bat                # 1-Click Windows Batch Launcher
├── requirements.txt           # Verified Python dependencies
├── pytest.ini                 # Automated testing configuration
├── conftest.py                # Environment bootstrapping
├── hand_landmarker.task       # MediaPipe Neural Network model asset
├── assets/
│   └── icon.ico               # Multi-resolution application icon
├── core/
│   ├── __init__.py
│   ├── types.py               # HandLandmark, FramePacket, GestureType dataclasses
│   ├── camera.py              # Threaded camera manager with auto-reconnection
│   ├── tracker.py             # MediaPipe HandLandmarker wrapper with model management
│   ├── gestures.py            # Multi-gesture recognition state machine
│   ├── cursor.py              # 1€ Filter, deadzone, dynamic acceleration, screen mapping
│   └── engine.py              # Central engine coordinating background threads and GUI signals
├── config/
│   ├── __init__.py
│   └── settings.py            # JSON configuration, profiles, and persistence
├── shortcuts/
│   ├── __init__.py
│   ├── hotkeys.py             # Global Windows Win32 hotkeys listener
│   └── autostart.py           # Optional Windows user login startup integration
├── utils/
│   ├── __init__.py
│   ├── filter.py              # OneEuroFilter & LowPassFilter implementations
│   └── logger.py              # Rotating file and console logger
├── ui/
│   ├── __init__.py
│   ├── theme.py               # Dark and Light QSS themes
│   ├── tray.py                # Windows System Tray icon, menu, and notifications
│   ├── main_window.py         # Main window, navigation sidebar, and status bar
│   └── views/
│       ├── __init__.py
│       ├── dashboard_view.py  # Primary controls, telemetry cards, gesture guide
│       ├── live_view.py       # Live camera canvas with HUD overlays & CPU saver
│       ├── gestures_view.py   # Gesture toggles, sliders, and interactive test pad
│       ├── cursor_view.py     # Speed, acceleration, smoothing, and boundary margins
│       ├── camera_view.py     # Camera device selector, resolutions, and test tool
│       └── calibration_view.py# Step-by-step interactive setup wizard
├── tests/
│   ├── __init__.py
│   ├── test_filter.py         # Mathematical filter verification
│   ├── test_cursor.py         # Screen mapping and boundary clamping tests
│   ├── test_gestures.py       # Gesture recognition and debouncing tests
│   ├── test_config.py         # Settings persistence and profiles tests
│   └── test_engine.py         # Multi-threaded engine integration tests
├── installer/
│   └── setup.iss              # Inno Setup Windows installer script
└── build_windows.py           # PyInstaller packaging script
```

---

## 🚀 Quick Start Guide

### Option 1: 1-Click Launch (Recommended for Windows Users)
Double-click `run_app.bat` in the project root directory. The application will start immediately.

### Option 2: Running via Terminal
```powershell
# Activate project virtual environment
.\.venv\Scripts\Activate.ps1

# Run the desktop application
python main.py
```

---

## 🧪 Automated Testing

The project includes a comprehensive automated test suite with mock inputs and zero physical mouse disruption during testing:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

All 21 test suites cover:
- Mathematical 1€ signal filtering and derivative acceleration
- Normalized camera coordinate mapping to physical screen resolutions
- Micro-jitter deadzone suppression
- Gesture state transitions (Pinch -> Click -> Double Pinch -> Drag -> Drop)
- Hand absence handling and smooth cursor re-entry
- Settings file serialization, recovery, and profile switching
- Engine thread lifecycles and emergency halt safety

---

## 📋 Manual Testing Checklist for Hardware Webcam

1. **Camera Feed & Detection**:
   - Open the **Camera Settings** tab and click **Scan Devices**. Verify your webcam index is selected.
   - Navigate to the **Live Tracking** tab and verify the colored skeleton joints follow your hand movements.
2. **Cursor Motion**:
   - Move your hand around the center of the webcam view. Verify the cursor glides across your Windows desktop without trembling or sticking.
3. **Clicking**:
   - Pinch your index finger and thumb together briefly. Verify a standard Windows left click occurs.
   - On the **Gesture Controls** tab, test the "Click Me to Test" button in the Interactive Test Pad.
4. **Dragging**:
   - Pinch and hold for 0.4 seconds. Move your hand to drag an item or highlight text, then release your fingers to drop.
5. **Scrolling**:
   - Extend your index and middle fingers together and move your hand up and down. Verify web pages scroll smoothly.
6. **Smart Pause**:
   - Drop your hand below your desk. Observe the dashboard status switch to "Smart Pause (Hand Absent)".
   - Bring your hand back into view: notice cursor tracking resumes immediately without jumping.
7. **System Tray & Hotkeys**:
   - Press `Ctrl + Alt + H` to stop tracking, and press it again to resume.
   - Minimize the application to verify it nests cleanly in the Windows Taskbar Notification Area.

---

## 🛠️ Building Standalone Executable & Installer

To package a standalone `.exe` that does not require Python:
```powershell
# 1. Run the packaging script
.\.venv\Scripts\python.exe build_windows.py

# 2. Output will be generated in:
dist\AIHandMouse\AIHandMouse.exe
```

To generate the complete Windows Setup Wizard (`AIHandMouse_Setup_v2.0.exe`):
1. Download and install [Inno Setup](https://jrsoftware.org/isdl.php).
2. Open `installer\setup.iss` and click **Build -> Compile**.
#   a i - h a n d - g e s t u r e - m o u s e  
 