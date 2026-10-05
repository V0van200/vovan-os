@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 start.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10+ is required. Install from https://www.python.org/downloads/
  ) else (
    python start.py
  )
)
pause
