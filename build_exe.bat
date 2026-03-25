@echo off
echo ========================================
echo Build WiFi Scanner EXE
echo ========================================
echo.

REM Install dependencies
pip install -r requirements.txt

REM Build the executable
pyinstaller --onefile --windowed --name "WiFiScanner" --add-data "app.py;." --noconfirm --clean app.py

echo.
echo ========================================
echo Build Complete!
echo Executable is in: dist\WiFiScanner.exe
echo ========================================
echo.

pause
