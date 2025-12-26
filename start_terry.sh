#!/bin/bash

echo "Starting Terry AI for Linux..."
cd "$(dirname "$0")"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    echo "Please install python3 and python3-venv."
    exit 1
fi

# Check for ffmpeg (System or Local)
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg found (System)."
elif [ -f "$(dirname "$0")/bin/ffmpeg" ]; then
    echo "FFmpeg found (Local)."
    export PATH="$(dirname "$0")/bin:$PATH"
else
    echo "[ERROR] ffmpeg is missing."
    echo "Please install ffmpeg (e.g., sudo apt install ffmpeg)."
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing/Checking requirements..."
pip install -r requirements.txt

# Run Terry
echo "Running Terry..."
python main.py
