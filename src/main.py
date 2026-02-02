#!/usr/bin/env python3
"""
APK Purifier - Main Application Entry Point
A cross-platform desktop tool for purifying Android APKs by removing ads and malware.

Author: Krishnendu Paul
Website: https://krishnendu.com
GitHub: https://github.com/bidhata/APK-Purifier
Email: me@krishnendu.com
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.utils import setup_logging, check_dependencies


def check_and_download_tools():
    """Check if tools are available and download if missing."""
    from core.utils import get_tools_dir
    
    tools_dir = get_tools_dir()
    required_tools = ["apktool.jar", "uber-apk-signer.jar"]
    
    missing_tools = []
    for tool in required_tools:
        if not (tools_dir / tool).exists():
            missing_tools.append(tool)
    
    # Check for JADX
    jadx_dir = tools_dir / "jadx"
    if not jadx_dir.exists():
        missing_tools.append("jadx")
    
    if missing_tools:
        logger = logging.getLogger(__name__)
        logger.info(f"Missing tools: {missing_tools}")
        
        # Show dialog asking user if they want to download tools
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Download Required Tools")
        msg.setText("APK Purifier requires external tools to function properly.")
        msg.setInformativeText(f"Missing tools: {', '.join(missing_tools)}\n\nWould you like to download them now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # Download tools
            try:
                logger.info("Downloading required tools...")
                download_tools_embedded()
                logger.info("Tools downloaded successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to download tools: {e}")
                
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setWindowTitle("Download Failed")
                error_msg.setText("Failed to download required tools.")
                error_msg.setInformativeText(f"Error: {e}\n\nPlease download tools manually or check your internet connection.")
                error_msg.exec()
                return False
        else:
            # User chose not to download
            warning_msg = QMessageBox()
            warning_msg.setIcon(QMessageBox.Icon.Warning)
            warning_msg.setWindowTitle("Tools Required")
            warning_msg.setText("APK Purifier requires external tools to function.")
            warning_msg.setInformativeText("The application may not work properly without these tools. You can download them later from the Help menu.")
            warning_msg.exec()
            return False
    
    return True

def download_tools_embedded():
    """Download tools using embedded download functionality."""
    import requests
    import zipfile
    import shutil
    from core.utils import get_tools_dir
    
    tools_dir = get_tools_dir()
    tools_dir.mkdir(exist_ok=True)
    
    # Download APKTool
    apktool_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar"
    apktool_path = tools_dir / "apktool.jar"
    
    if not apktool_path.exists():
        response = requests.get(apktool_url)
        response.raise_for_status()
        with open(apktool_path, 'wb') as f:
            f.write(response.content)
    
    # Download uber-apk-signer
    signer_url = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.2.1/uber-apk-signer-1.2.1.jar"
    signer_path = tools_dir / "uber-apk-signer.jar"
    
    if not signer_path.exists():
        response = requests.get(signer_url)
        response.raise_for_status()
        with open(signer_path, 'wb') as f:
            f.write(response.content)
    
    # Download JADX
    jadx_url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
    jadx_dir = tools_dir / "jadx"
    
    if not jadx_dir.exists():
        response = requests.get(jadx_url)
        response.raise_for_status()
        
        # Save and extract zip
        jadx_zip = tools_dir / "jadx.zip"
        with open(jadx_zip, 'wb') as f:
            f.write(response.content)
        
        with zipfile.ZipFile(jadx_zip, 'r') as zip_ref:
            zip_ref.extractall(jadx_dir)
        
        # Make scripts executable on Unix
        if os.name != 'nt':
            for script in jadx_dir.glob("bin/*"):
                if script.is_file():
                    os.chmod(script, 0o755)
        
        # Clean up zip file
        jadx_zip.unlink()

def main():
    """Main application entry point."""

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("APK Purifier")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("Krishnendu Paul")
    app.setOrganizationDomain("krishnendu.com")

    # Set application icon if available
    icon_path = Path(__file__).parent / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    try:
        # Check and download tools if needed
        logger.info("Checking required tools...")
        if not check_and_download_tools():
            logger.warning("Continuing without all required tools")

        # Check system dependencies
        logger.info("Checking system dependencies...")
        missing_deps = check_dependencies()

        if missing_deps:
            error_msg = "Missing required dependencies:\n\n"
            error_msg += "\n".join(f"• {dep}" for dep in missing_deps)
            error_msg += "\n\nPlease install the missing dependencies and try again."

            QMessageBox.critical(None, "Missing Dependencies", error_msg)
            return 1

        # Create and show main window
        logger.info("Starting APK Purifier...")
        main_window = MainWindow()
        main_window.show()

        # Start event loop
        return app.exec()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        QMessageBox.critical(
            None, "Fatal Error", f"A fatal error occurred:\n\n{str(e)}\n\nCheck the logs for more details."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
