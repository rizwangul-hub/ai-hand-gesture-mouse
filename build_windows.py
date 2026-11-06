"""Automated Windows Executable Builder using PyInstaller."""

import os
import subprocess
import sys


def build_executable():
    print("=" * 60)
    print("AI Hand Gesture Control System - Windows Build Script")
    print("=" * 60)

    # Project directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    model_path = os.path.join(base_dir, "hand_landmarker.task")
    main_script = os.path.join(base_dir, "main.py")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--name=AIHandMouse",
        f"--icon={icon_path}",
        f"--add-data={model_path};.",
        f"--add-data={icon_path};assets",
        "--clean",
        main_script,
    ]

    print("Running command:")
    print(" ".join(cmd))
    print("-" * 60)

    try:
        res = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✓ Build completed successfully!")
        print("Output directory: dist/AIHandMouse/AIHandMouse.exe")
        print("=" * 60)
    except subprocess.CalledProcessError as exc:
        print(f"✗ Build failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)


if __name__ == "__main__":
    build_executable()
