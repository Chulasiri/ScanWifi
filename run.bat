@echo off
echo ========================================
echo WiFi & Network Scanner
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install dependencies if not already installed
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting server...
echo Open browser: http://localhost:5000
echo Press Ctrl+C to stop
echo.

REM Run the app
python app.py

pause
