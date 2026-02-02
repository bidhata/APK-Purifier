#!/usr/bin/env python3
"""
Simple build script for APK Purifier
Creates single executable binary
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if needed."""
    try:
        import PyInstaller
        print("✓ PyInstaller available")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed")
            return True
        except Exception as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            return False

def build_executable():
    """Build the executable."""
    print("Building APK Purifier executable...")
    
    # Try to find pyinstaller
    pyinstaller_cmd = "pyinstaller"
    
    # Check if pyinstaller is in PATH
    try:
        subprocess.run([pyinstaller_cmd, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try with python -m
        pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
    
    # PyInstaller command
    if isinstance(pyinstaller_cmd, str):
        cmd = [pyinstaller_cmd]
    else:
        cmd = pyinstaller_cmd
    
    cmd.extend([
        "--onefile",                    # Single file
        "--windowed",                   # No console (GUI app)
        "--name", "APK-Purifier",
        "--add-data", "src/data" + (";data" if os.name == 'nt' else ":data"),
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "lxml",
        "--hidden-import", "cryptography",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--clean",
        "--noconfirm",
        "src/main.py"
    ])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build completed successfully")
        
        # Check output
        dist_dir = Path("dist")
        if os.name == 'nt':
            exe_file = dist_dir / "APK-Purifier.exe"
        else:
            exe_file = dist_dir / "APK-Purifier"
        
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✓ Executable: {exe_file}")
            print(f"✓ Size: {size_mb:.1f} MB")
            return True
        else:
            print("✗ Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Main build function."""
    print("APK Purifier - Build Script")
    print("=" * 40)
    
    # Check environment
    if not Path("src/main.py").exists():
        print("✗ Error: Run from project root directory")
        return 1
    
    # Install PyInstaller
    if not install_pyinstaller():
        return 1
    
    # Build
    if build_executable():
        print("\n✅ BUILD SUCCESSFUL!")
        print("\nNext steps:")
        print("1. Test the executable in dist/ directory")
        print("2. Copy tools/ directory alongside the executable")
        print("3. Ensure Java is installed on target systems")
        return 0
    else:
        print("\n❌ BUILD FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())