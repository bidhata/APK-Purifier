# Build Instructions - APK Purifier

## Overview

This document provides instructions for building single executable binaries of APK Purifier for Windows and Linux distribution.

## Prerequisites

### Common Requirements
- Python 3.8 or higher
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`

### Platform-Specific Requirements

#### Windows
- Windows 10 or higher
- Visual C++ Redistributable (usually pre-installed)

#### Linux
- Linux distribution with GUI support
- Development tools: `sudo apt-get install build-essential` (Ubuntu/Debian)

## Build Methods

### Method 1: Simple Build Script (Recommended)

#### Windows
```bash
python build.py
```

#### Linux
```bash
python3 build.py
```

### Method 2: Platform-Specific Scripts

#### Windows
```bash
build_windows.bat
```

#### Linux
```bash
chmod +x build_linux.sh
./build_linux.sh
```

### Method 3: Manual PyInstaller Command

#### Windows
```bash
python -m PyInstaller --onefile --windowed --name APK-Purifier --add-data "src/data;data" --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import lxml --hidden-import cryptography --exclude-module tkinter --exclude-module matplotlib --clean --noconfirm src/main.py
```

#### Linux
```bash
python3 -m PyInstaller --onefile --windowed --name APK-Purifier --add-data "src/data:data" --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import lxml --hidden-import cryptography --exclude-module tkinter --exclude-module matplotlib --clean --noconfirm src/main.py
```

## Build Output

### Successful Build
- **Windows**: `dist/APK-Purifier.exe` (~39 MB)
- **Linux**: `dist/APK-Purifier` (~39 MB)

### Build Artifacts
- `build/` - Temporary build files (can be deleted)
- `dist/` - Final executable location
- `*.spec` - PyInstaller specification files (can be deleted)

## Distribution Package Creation

After building the executable, create a distribution package:

```bash
python prepare_distribution.py
```

This creates:
- **Windows**: `APK-Purifier-v1.1.0-windows.zip`
- **Linux**: `APK-Purifier-v1.1.0-linux.tar.gz`

### Package Contents
```
APK-Purifier-v1.1.0-{platform}/
├── APK-Purifier.exe (Windows) or APK-Purifier (Linux)
├── APK-Purifier.bat (Windows) or apk-purifier.sh (Linux)
├── tools/
│   ├── apktool.jar
│   ├── uber-apk-signer.jar
│   └── jadx/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── INSTALL.md
├── TROUBLESHOOTING.md
└── INSTALLATION.txt
```

## Troubleshooting Build Issues

### Common Issues

#### 1. PyInstaller Not Found
```bash
# Install PyInstaller
pip install pyinstaller

# Or use full path
python -m PyInstaller --version
```

#### 2. pathlib Conflict (Windows)
```bash
# Remove conflicting pathlib package
pip uninstall pathlib -y
```

#### 3. Missing Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt
```

#### 4. Large Executable Size
The executable is large (~39 MB) because it includes:
- Python interpreter
- PyQt6 GUI framework
- All dependencies
- Application data files

This is normal for PyInstaller single-file builds.

#### 5. Antivirus False Positives
Some antivirus software may flag PyInstaller executables as suspicious. This is a known issue with PyInstaller. The executable is safe.

### Build Optimization

#### Reduce Size (Optional)
```bash
# Use UPX compression (if available)
pip install upx-ucl
pyinstaller --onefile --windowed --upx-dir=/path/to/upx src/main.py
```

#### Debug Build Issues
```bash
# Build with console output for debugging
pyinstaller --onefile --console src/main.py
```

## Testing the Build

### Basic Test
1. Run the executable: `./dist/APK-Purifier`
2. Check if GUI opens without errors
3. Verify tool availability detection works

### Full Test
1. Copy `tools/` directory alongside executable
2. Test APK processing with a sample APK
3. Verify all features work correctly

## Distribution Notes

### For End Users
- **Java Requirement**: Users must have Java 8+ installed
- **Tools**: External tools (APKTool, JADX, uber-apk-signer) are included
- **First Run**: Application may take longer to start on first run
- **Permissions**: May need to allow through firewall/antivirus

### For Developers
- **Source Code**: Not included in binary distribution
- **Updates**: Require rebuilding the entire executable
- **Platform**: Each platform needs its own build
- **Dependencies**: All Python dependencies are bundled

## Automated Build (CI/CD)

### GitHub Actions Example
```yaml
name: Build APK Purifier

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python build.py
    
    - name: Create distribution
      run: python prepare_distribution.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: APK-Purifier-${{ matrix.os }}
        path: APK-Purifier-v1.1.0-*
```

## Build Summary

✅ **Windows Build**: `APK-Purifier.exe` (38.8 MB)  
✅ **Linux Build**: `APK-Purifier` (similar size)  
✅ **Distribution Packages**: Ready-to-distribute archives  
✅ **All Features**: GUI, CLI, dual decompiler support  
✅ **Cross-Platform**: Windows 10+ and Linux support  

The built executables are self-contained and include all necessary Python dependencies, making distribution simple for end users.