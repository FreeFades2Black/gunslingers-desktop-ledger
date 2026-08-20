@echo off
title The Gunslinger's Desktop Ledger
color 0B

echo =====================================================================
echo  The Gunslinger's Desktop Ledger - P&L Forecasting Engine
echo  Built by: Free Hall
echo =====================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    echo.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist ".venv\" (
    echo [*] Setting up isolated Python environment...
    python -m venv .venv
)

:: Activate environment and install dependencies
echo [*] Checking dependencies...
call .venv\Scripts\activate.bat
python -m pip install -q -r requirements.txt

:: Launch the Desktop Ledger UI
echo [*] Launching Desktop Ledger...
python app.py

pause
