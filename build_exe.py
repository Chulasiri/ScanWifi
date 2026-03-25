import PyInstaller.__main__
import os
import sys

print('=' * 50)
print('Building WiFi Scanner EXE')
print('=' * 50)

# PyInstaller arguments
args = [
    'app.py',
    '--onefile',           # Single executable
    '--windowed',          # No console window
    '--name=WiFiScanner',  # Executable name
    '--add-data=app.py:.', # Include app.py
    '--clean',             # Clean build
    '--noconfirm',        # Don't ask
]

try:
    PyInstaller.__main__.run(args)
    print('=' * 50)
    print('Build Complete!')
    print('Executable: dist/WiFiScanner.exe')
    print('=' * 50)
except Exception as e:
    print(f'Error: {e}')
