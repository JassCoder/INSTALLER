@echo off
title ComfyUI Addon Installer

echo Checking Python...
call bin\python_check.bat
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Install Python first.
    pause
    exit /b
)

echo Checking Git...
call bin\git_check.bat
if %ERRORLEVEL% NEQ 0 (
    echo Git not found. Install Git before running installer.
    pause
    exit /b
)

echo.
echo Launching Installer GUI...
python comfy_installer.py
pause
