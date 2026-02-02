#!/usr/bin/env python3
"""
Standalone tool downloader for APK Purifier
Can be run independently or called from the main application
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

def get_tools_directory():
    """Get the tools directory path."""
    if getattr(sys, 'frozen', False):
        # Running as executable
        return Path(sys.executable).parent / "tools"
    else:
        # Running as script
        return Path(__file__).parent / "tools"

def download_file(url, destination, description=""):
    """Download a file with progress indication."""
    print(f"Downloading {description or url}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end="", flush=True)
        
        print(f"\n✓ Downloaded {destination.name}")
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to download {destination.name}: {e}")
        return False

def download_apktool(tools_dir):
    """Download APKTool."""
    print("\n=== Downloading APKTool ===")
    apktool_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar"
    apktool_path = tools_dir / "apktool.jar"
    
    if apktool_path.exists():
        print("✓ APKTool already exists")
        return True
    
    return download_file(apktool_url, apktool_path, "APKTool")

def download_uber_apk_signer(tools_dir):
    """Download uber-apk-signer."""
    print("\n=== Downloading uber-apk-signer ===")
    signer_url = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.2.1/uber-apk-signer-1.2.1.jar"
    signer_path = tools_dir / "uber-apk-signer.jar"
    
    if signer_path.exists():
        print("✓ uber-apk-signer already exists")
        return True
    
    return download_file(signer_url, signer_path, "uber-apk-signer")

def download_jadx(tools_dir):
    """Download JADX."""
    print("\n=== Downloading JADX ===")
    jadx_url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
    jadx_dir = tools_dir / "jadx"
    
    if jadx_dir.exists():
        print("✓ JADX already exists")
        return True
    
    # Download zip file
    jadx_zip = tools_dir / "jadx.zip"
    if not download_file(jadx_url, jadx_zip, "JADX"):
        return False
    
    # Extract JADX
    try:
        print("Extracting JADX...")
        with zipfile.ZipFile(jadx_zip, 'r') as zip_ref:
            zip_ref.extractall(jadx_dir)
        
        # Make scripts executable on Unix
        if os.name != 'nt':
            for script in jadx_dir.glob("bin/*"):
                if script.is_file():
                    os.chmod(script, 0o755)
        
        # Clean up zip file
        jadx_zip.unlink()
        
        print("✓ JADX extracted successfully")
        return True
        
    except Exception as e:
        print(f"✗ Failed to extract JADX: {e}")
        return False

def verify_java():
    """Verify Java installation."""
    print("\n=== Verifying Java ===")
    try:
        import subprocess
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"✓ Java found: {version_line}")
            return True
        else:
            print("✗ Java not working properly")
            return False
            
    except Exception as e:
        print(f"✗ Java not found: {e}")
        print("Please install Java 8+ from: https://openjdk.org/")
        return False

def main():
    """Main download function."""
    print("APK Purifier - Tool Downloader")
    print("=" * 50)
    
    # Get tools directory
    tools_dir = get_tools_directory()
    tools_dir.mkdir(exist_ok=True)
    
    print(f"Tools directory: {tools_dir.absolute()}")
    
    # Verify Java first
    java_ok = verify_java()
    
    # Download tools
    success_count = 0
    total_tools = 3
    
    if download_apktool(tools_dir):
        success_count += 1
    
    if download_uber_apk_signer(tools_dir):
        success_count += 1
    
    if download_jadx(tools_dir):
        success_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Download Summary: {success_count}/{total_tools} tools")
    
    if success_count == total_tools:
        print("✅ All tools downloaded successfully!")
        if not java_ok:
            print("⚠️  Warning: Java not found. Please install Java 8+ for APK Purifier to work.")
        return True
    else:
        print("❌ Some tools failed to download.")
        print("Please check your internet connection and try again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)