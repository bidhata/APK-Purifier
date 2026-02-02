#!/usr/bin/env python3
"""
Tool downloader script for APK Purifier
Downloads required external tools (APKTool, uber-apk-signer)

Author: Krishnendu Paul
Website: https://krishnendu.com
"""

import os
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urlparse
import zipfile
import tempfile

def download_file(url: str, destination: Path, description: str = ""):
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

def get_latest_github_release(repo: str) -> dict:
    """Get latest release info from GitHub API."""
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to get release info for {repo}: {e}")
        return {}

def download_apktool(tools_dir: Path) -> bool:
    """Download APKTool."""
    print("\n=== Downloading APKTool ===")
    
    # APKTool download URLs (these may need to be updated)
    apktool_jar_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar"
    apktool_script_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
    
    # Download APKTool JAR
    jar_path = tools_dir / "apktool.jar"
    if not download_file(apktool_jar_url, jar_path, "APKTool JAR"):
        return False
    
    # Download APKTool script (for Linux/macOS)
    if os.name != 'nt':  # Not Windows
        script_path = tools_dir / "apktool"
        if download_file(apktool_script_url, script_path, "APKTool script"):
            # Make script executable
            os.chmod(script_path, 0o755)
    
    return True

def download_jadx(tools_dir: Path) -> bool:
    """Download JADX decompiler."""
    print("\n=== Downloading JADX ===")
    
    # Get latest release
    release_info = get_latest_github_release("skylot/jadx")
    
    if not release_info:
        # Fallback to known version
        download_url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
        version = "1.4.7"
    else:
        # Find the ZIP asset
        download_url = None
        version = release_info.get("tag_name", "latest").replace("v", "")
        
        for asset in release_info.get("assets", []):
            if asset["name"].endswith(".zip") and "jadx" in asset["name"].lower():
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print("Could not find ZIP file in latest release")
            return False
    
    # Download JADX
    jadx_zip_path = tools_dir / f"jadx-{version}.zip"
    if not download_file(download_url, jadx_zip_path, f"JADX {version}"):
        return False
    
    # Extract JADX
    try:
        import shutil
        jadx_dir = tools_dir / "jadx"
        
        # Remove existing directory
        if jadx_dir.exists():
            shutil.rmtree(jadx_dir)
        
        with zipfile.ZipFile(jadx_zip_path, 'r') as zip_ref:
            zip_ref.extractall(jadx_dir)
        
        # Make scripts executable on Unix systems
        if os.name != 'nt':
            for script in jadx_dir.glob("bin/*"):
                if script.is_file():
                    os.chmod(script, 0o755)
        
        # Clean up zip file
        jadx_zip_path.unlink()
        
        print(f"✓ JADX extracted to {jadx_dir}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to extract JADX: {e}")
        return False

def download_uber_apk_signer(tools_dir: Path) -> bool:
    print("\n=== Downloading uber-apk-signer ===")
    
    # Get latest release
    release_info = get_latest_github_release("patrickfav/uber-apk-signer")
    
    if not release_info:
        # Fallback to known version
        download_url = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.2.1/uber-apk-signer-1.2.1.jar"
    else:
        # Find the JAR asset
        download_url = None
        for asset in release_info.get("assets", []):
            if asset["name"].endswith(".jar") and "uber-apk-signer" in asset["name"]:
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print("Could not find JAR file in latest release")
            return False
    
    # Download the JAR
    jar_path = tools_dir / "uber-apk-signer.jar"
    return download_file(download_url, jar_path, "uber-apk-signer JAR")

def verify_java():
    """Verify Java installation."""
    print("\n=== Verifying Java Installation ===")
    
    try:
        import subprocess
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]  # Java version is in stderr
            print(f"✓ Java found: {version_line}")
            return True
        else:
            print("✗ Java not found or not working")
            return False
            
    except FileNotFoundError:
        print("✗ Java not found in PATH")
        return False

def main():
    """Main function."""
    print("APK Purifier - Tool Downloader")
    print("=" * 40)
    
    # Create tools directory
    tools_dir = Path(__file__).parent / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    print(f"Tools will be downloaded to: {tools_dir.absolute()}")
    
    # Verify Java first
    if not verify_java():
        print("\nWarning: Java is required but not found.")
        print("Please install Java JDK 8 or higher before using APK Purifier.")
        print("Download from: https://openjdk.org/ or https://www.oracle.com/java/")
    
    success_count = 0
    total_tools = 3  # APKTool, uber-apk-signer, JADX
    
    # Download APKTool
    if download_apktool(tools_dir):
        success_count += 1
    
    # Download uber-apk-signer
    if download_uber_apk_signer(tools_dir):
        success_count += 1
    
    # Download JADX
    if download_jadx(tools_dir):
        success_count += 1
    
    # Summary
    print(f"\n=== Download Summary ===")
    print(f"Successfully downloaded: {success_count}/{total_tools} tools")
    
    if success_count == total_tools:
        print("✓ All tools downloaded successfully!")
        print("\nYou can now run APK Purifier:")
        print("python src/main.py")
    else:
        print("✗ Some tools failed to download.")
        print("Please check your internet connection and try again.")
        print("You can also download the tools manually:")
        print("- APKTool: https://ibotpeaches.github.io/Apktool/")
        print("- uber-apk-signer: https://github.com/patrickfav/uber-apk-signer/releases")
        print("- JADX: https://github.com/skylot/jadx/releases")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)