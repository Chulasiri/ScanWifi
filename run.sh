#!/bin/bash

echo "========================================"
echo "WiFi & Network Scanner"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python3: sudo apt install python3"
    exit 1
fi

# Install dependencies if not already installed
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting server..."
echo "Open browser: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Run the app
python3 app.py
