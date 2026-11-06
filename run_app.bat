@echo off
setlocal
cd /d "%~dp0"
title AI Hand Gesture Control System

set "OPENBLAS_NUM_THREADS=1"
set "NUMEXPR_NUM_THREADS=1"
set "OMP_NUM_THREADS=1"

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" main.py
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" main.py
) else (
    start "" python main.py
)
exit
