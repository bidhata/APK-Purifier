#!/usr/bin/env python3
"""
Distribution preparation script for APK Purifier
Creates ready-to-distribute packages for Windows and Linux
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path

def create_distribution_package():
    """Create distribution package with executable and required files."""
    
    # Determine platform
    platform = "windows" if os.name == 'nt' else "linux"
    exe_name = "APK-Purifier.exe" if os.name == 'nt' else "APK-Purifier"
    
    print(f"Creating {platform} distribution package...")
    
    # Check if executable exists
    exe_path = Path("dist") / exe_name
    if not exe_path.exists():
        print(f"✗ Executable not found: {exe_path}")
        print("Run build script first!")
        return False
    
    # Create distribution directory
    dist_name = f"APK-Purifier-v1.1.0-{platform}"
    dist_dir = Path(dist_name)
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Copy executable
    shutil.copy2(exe_path, dist_dir / exe_name)
    print(f"✓ Copied executable: {exe_name}")
    
    # Copy standalone tool downloader
    downloader_script = Path("download_tools_standalone.py")
    if downloader_script.exists():
        shutil.copy2(downloader_script, dist_dir / "download_tools.py")
        print("✓ Copied tool downloader script")
    
    # Copy tools directory (if exists)
    tools_dir = Path("tools")
    if tools_dir.exists():
        shutil.copytree(tools_dir, dist_dir / "tools")
        print("✓ Copied tools directory")
    else:
        # Create empty tools directory with instructions
        (dist_dir / "tools").mkdir()
        with open(dist_dir / "tools" / "README.txt", "w") as f:
            f.write("""APK Purifier Tools Directory

This directory should contain the following tools:
1. apktool.jar - APK decompilation/recompilation tool
2. uber-apk-signer.jar - APK signing tool  
3. jadx/ - JADX decompiler directory

To download these tools automatically:
1. Run the main executable once
2. Or run: python download_tools.py (if you have the source)

These tools are required for APK Purifier to function properly.
""")
        print("✓ Created tools directory with instructions")
    
    # Copy documentation
    docs_to_copy = ["README.md", "LICENSE", "CHANGELOG.md", "INSTALL.md", "TROUBLESHOOTING.md"]
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, dist_dir / doc)
            print(f"✓ Copied {doc}")
    
    # Create startup script
    if platform == "windows":
        startup_script = dist_dir / "APK-Purifier.bat"
        with open(startup_script, "w") as f:
            f.write("""@echo off
REM APK Purifier Startup Script
echo Starting APK Purifier...

REM Check if Java is available
java -version >nul 2>&1
if errorlevel 1 (
    echo Warning: Java not found. APK Purifier requires Java 8+ to function properly.
    echo Please install Java from: https://openjdk.org/
    echo.
)

REM Check if tools directory exists
if not exist "tools" (
    echo Tools directory not found. Creating and downloading required tools...
    if exist "download_tools.py" (
        python download_tools.py
    ) else (
        echo Please run download_tools.py to get required tools.
        pause
        exit /b 1
    )
)

REM Start APK Purifier
APK-Purifier.exe

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo APK Purifier exited with an error.
    echo If tools are missing, try running: python download_tools.py
    pause
)
""")
        print("✓ Created Windows startup script")
    else:
        startup_script = dist_dir / "apk-purifier.sh"
        with open(startup_script, "w") as f:
            f.write("""#!/bin/bash
# APK Purifier Startup Script
echo "Starting APK Purifier..."

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo "Warning: Java not found. APK Purifier requires Java 8+ to function properly."
    echo "Please install Java from your package manager or https://openjdk.org/"
    echo ""
fi

# Check if tools directory exists
if [ ! -d "tools" ]; then
    echo "Tools directory not found. Creating and downloading required tools..."
    if [ -f "download_tools.py" ]; then
        python3 download_tools.py
    else
        echo "Please run: python3 download_tools.py to get required tools."
        read -p "Press Enter to continue..."
        exit 1
    fi
fi

# Make executable if needed
chmod +x APK-Purifier

# Start APK Purifier
./APK-Purifier

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "APK Purifier exited with an error."
    echo "If tools are missing, try running: python3 download_tools.py"
    read -p "Press Enter to close..."
fi
""")
        os.chmod(startup_script, 0o755)
        print("✓ Created Linux startup script")
    
    # Create installation instructions
    install_file = dist_dir / "INSTALLATION.txt"
    with open(install_file, "w") as f:
        f.write(f"""APK Purifier v1.1.0 - Installation Instructions

SYSTEM REQUIREMENTS:
- Java 8 or higher (required for APK processing tools)
- Windows 10+ or Linux with GUI support
- At least 500MB free disk space

INSTALLATION:
1. Extract this package to a folder of your choice
2. Ensure Java is installed on your system
3. Run the executable:
   {"- Windows: Double-click APK-Purifier.exe or APK-Purifier.bat" if platform == "windows" else "- Linux: ./APK-Purifier or ./apk-purifier.sh"}

FIRST RUN:
- The application will automatically download required tools (APKTool, JADX, uber-apk-signer)
- This requires an internet connection
- Tools will be saved in the tools/ directory

USAGE:
1. Launch APK Purifier
2. Add APK files using "Add APK Files" button
3. Configure patching options as needed
4. Click "Start Patching" to process APKs
5. Processed APKs will be saved with "_patched_signed.apk" suffix

TROUBLESHOOTING:
- If Java is not found, install it from: https://openjdk.org/
- Check TROUBLESHOOTING.md for common issues
- For support, visit: https://github.com/bidhata/APK-Purifier

Made by: Krishnendu Paul
Website: https://krishnendu.com
""")
    print("✓ Created installation instructions")
    
    # Create archive
    archive_name = f"{dist_name}.{'zip' if platform == 'windows' else 'tar.gz'}"
    
    if platform == "windows":
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in dist_dir.rglob('*'):
                if file_path.is_file():
                    arc_path = file_path.relative_to(dist_dir.parent)
                    zf.write(file_path, arc_path)
        print(f"✓ Created ZIP archive: {archive_name}")
    else:
        with tarfile.open(archive_name, 'w:gz') as tf:
            tf.add(dist_dir, arcname=dist_dir.name)
        print(f"✓ Created TAR.GZ archive: {archive_name}")
    
    # Show summary
    archive_size = Path(archive_name).stat().st_size / (1024 * 1024)
    print(f"✓ Archive size: {archive_size:.1f} MB")
    
    print(f"\n✅ Distribution package ready: {archive_name}")
    print(f"📁 Directory: {dist_dir}")
    
    return True

def main():
    """Main function."""
    print("APK Purifier - Distribution Preparation")
    print("=" * 50)
    
    if create_distribution_package():
        print("\n🎉 Distribution package created successfully!")
        print("\nYou can now distribute:")
        print("1. The archive file for easy sharing")
        print("2. The directory for direct use")
        print("\nUsers will need Java installed to run APK Purifier.")
        return 0
    else:
        print("\n❌ Failed to create distribution package")
        return 1

if __name__ == "__main__":
    sys.exit(main())