@echo off
REM Setup script for Windows

echo ==========================================
echo   Intraday Token Fetcher - Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed!
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo + Python found
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo + Dependencies installed successfully!
) else (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo To run the CLI version:
echo   python intraday_fetcher.py BTCUSDT
echo.
echo To run the web version:
echo   python web_app.py
echo   Then open: http://localhost:5000
echo.
echo ==========================================
pause
