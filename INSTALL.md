# Installation Guide

This guide will help you install and set up APK Purifier on Windows and Linux.

**Author:** Krishnendu Paul  
**Website:** https://krishnendu.com  
**GitHub:** https://github.com/bidhata/APK-Purifier  
**Email:** me@krishnendu.com

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 or Linux (Ubuntu 18.04+, Debian 10+, or equivalent)
- **Python**: 3.8 or higher
- **Java**: JDK 8 or higher (required for APKTool and signing tools)
- **Memory**: At least 4GB RAM (8GB recommended for large APKs)
- **Storage**: At least 2GB free space for tools and temporary files

### Required Software

#### 1. Python 3.8+
**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip
```

#### 2. Java JDK 8+
**Windows:**
- Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://openjdk.org/)
- Add Java to your PATH environment variable

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# CentOS/RHEL/Fedora
sudo dnf install java-11-openjdk-devel
```

Verify Java installation:
```bash
java -version
```

## Installation Steps

### Method 1: Install from Source (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/bidhata/APK-Purifier.git
cd APK-Purifier
```

2. **Create a virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download required tools:**

Create a `tools` directory and download the following:

- **APKTool**: Download `apktool.jar` from [APKTool website](https://ibotpeaches.github.io/Apktool/)
- **uber-apk-signer**: Download from [GitHub releases](https://github.com/patrickfav/uber-apk-signer/releases)

```bash
mkdir tools
cd tools

# Download APKTool (replace with latest version)
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar
mv apktool_2.8.1.jar apktool.jar

# Download uber-apk-signer (replace with latest version)
wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.2.1/uber-apk-signer-1.2.1.jar
mv uber-apk-signer-1.2.1.jar uber-apk-signer.jar

cd ..
```

5. **Run the application:**
```bash
python src/main.py
```

### Method 2: Install using pip (if published)

```bash
pip install apk-purifier
apk-purifier-gui
```

## Post-Installation Setup

### 1. Verify Installation

Run the application and check that all dependencies are detected:
```bash
python src/main.py
```

The application should start and show no missing dependency errors.

### 2. Configure Settings

1. Open the application
2. Go to **Tools → Settings**
3. Configure paths and options as needed:
   - Set temporary directory (optional)
   - Set backup directory (optional)
   - Configure custom keystore if needed

### 3. Test with Sample APK

1. Download a sample APK file
2. Add it to the application
3. Run a test patch with default settings
4. Verify the output APK is created and signed

## Troubleshooting

### Common Issues

#### "Java not found" error
- Ensure Java is installed and in your PATH
- Try setting JAVA_HOME environment variable
- On Windows, restart command prompt/PowerShell after Java installation

#### "APKTool not found" error
- Verify `apktool.jar` is in the `tools/` directory
- Check file permissions (should be readable)

#### "uber-apk-signer not found" error
- Verify `uber-apk-signer.jar` is in the `tools/` directory
- Check file permissions (should be readable)

#### PyQt6 installation issues
**Linux:**
```bash
# Install system dependencies
sudo apt install python3-pyqt6 python3-pyqt6-dev

# Or install via pip
pip install PyQt6
```

**Windows:**
- Usually installs automatically with pip
- If issues occur, try installing Visual C++ Redistributable

#### Permission errors on Linux
```bash
# Make sure tools are executable
chmod +x tools/apktool
chmod +r tools/*.jar
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](FAQ.md)
2. Search existing [GitHub Issues](https://github.com/bidhata/APK-Purifier/issues)
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Java version (`java -version`)
   - Full error message
   - Steps to reproduce

You can also contact the author:
- **Krishnendu Paul**
- Website: https://krishnendu.com
- Email: me@krishnendu.com

## Development Setup

For developers who want to contribute:

1. **Fork the repository**
2. **Clone your fork:**
```bash
git clone https://github.com/your-username/APK-Purifier.git
cd APK-Purifier
```

3. **Install development dependencies:**
```bash
pip install -r requirements.txt
pip install pytest black flake8
```

4. **Run tests:**
```bash
pytest
```

5. **Format code:**
```bash
black src/
```

6. **Lint code:**
```bash
flake8 src/
```

## Building Executable

To create a standalone executable:

### Using PyInstaller

1. **Install PyInstaller:**
```bash
pip install pyinstaller
```

2. **Create executable:**
```bash
# Windows
pyinstaller --windowed --onefile --name "APK Purifier" src/main.py

# Linux
pyinstaller --windowed --onefile --name "apk-purifier" src/main.py
```

3. **Copy tools directory:**
```bash
cp -r tools/ dist/
```

The executable will be in the `dist/` directory.

## Uninstallation

### If installed from source:
1. Delete the project directory
2. Remove the virtual environment
3. Remove any created shortcuts

### If installed via pip:
```bash
pip uninstall apk-purifier
```

## Security Considerations

- Only use this tool on APKs you have the right to modify
- Always scan APKs for malware before and after patching
- Keep backups of original APKs
- Be cautious with APKs from unknown sources
- This tool is for educational and legitimate security research purposes only