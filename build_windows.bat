@echo off
REM Windows build script for APK Purifier
echo APK Purifier - Windows Build
echo ==============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\main.py" (
    echo Error: src\main.py not found. Run from project root.
    pause
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller

REM Build executable
echo Building Windows executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name APK-Purifier ^
    --add-data "src\data;data" ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import lxml ^
    --hidden-import cryptography ^
    --exclude-module tkinter ^
    --exclude-module matplotlib ^
    --clean ^
    --noconfirm ^
    src\main.py

if exist "dist\APK-Purifier.exe" (
    echo.
    echo ✓ Build successful!
    echo ✓ Executable: dist\APK-Purifier.exe
    
    REM Show file size
    for %%I in ("dist\APK-Purifier.exe") do echo ✓ Size: %%~zI bytes
    
    echo.
    echo Next steps:
    echo 1. Test the executable: dist\APK-Purifier.exe
    echo 2. Copy tools\ directory alongside the executable
    echo 3. Ensure Java is installed on target systems
) else (
    echo.
    echo ✗ Build failed! Check the output above for errors.
)

echo.
pause