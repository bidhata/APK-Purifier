#!/bin/bash
# Linux build script for APK Purifier

echo "APK Purifier - Linux Build"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: src/main.py not found. Run from project root."
    exit 1
fi

# Install PyInstaller
echo "Installing PyInstaller..."
python3 -m pip install pyinstaller

# Build executable
echo "Building Linux executable..."
pyinstaller \
    --onefile \
    --windowed \
    --name APK-Purifier \
    --add-data "src/data:data" \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import lxml \
    --hidden-import cryptography \
    --exclude-module tkinter \
    --exclude-module matplotlib \
    --clean \
    --noconfirm \
    src/main.py

if [ -f "dist/APK-Purifier" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "✓ Executable: dist/APK-Purifier"
    
    # Show file size
    size=$(stat -c%s "dist/APK-Purifier")
    size_mb=$((size / 1024 / 1024))
    echo "✓ Size: ${size_mb} MB"
    
    # Make executable
    chmod +x "dist/APK-Purifier"
    echo "✓ Made executable"
    
    echo ""
    echo "Next steps:"
    echo "1. Test the executable: ./dist/APK-Purifier"
    echo "2. Copy tools/ directory alongside the executable"
    echo "3. Ensure Java is installed on target systems"
else
    echo ""
    echo "✗ Build failed! Check the output above for errors."
    exit 1
fi