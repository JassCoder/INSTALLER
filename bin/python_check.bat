@echo off
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    exit /b 0
) else (
    exit /b 1
)
