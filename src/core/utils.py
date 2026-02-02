"""
Utility functions for APK Patcher Desktop
"""

import os
import sys
import logging
import shutil
import subprocess
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any


def setup_logging(level: int = logging.INFO) -> None:
    """Setup application logging."""
    log_dir = Path.home() / ".apk_purifier" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "apk_purifier.log"

    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Setup logging with both file and console output
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )


def check_dependencies() -> List[str]:
    """Check for required system dependencies."""
    missing = []

    # Check Java
    if not check_java():
        missing.append("Java 8 or higher (required for APKTool and signing)")

    # Check tools directory
    tools_dir = get_tools_dir()
    required_tools = ["apktool.jar", "uber-apk-signer.jar"]

    for tool in required_tools:
        if not (tools_dir / tool).exists():
            missing.append(f"{tool} (should be in tools/ directory)")

    return missing


def check_java() -> bool:
    """Check if Java is available and get version."""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_java_version() -> Optional[str]:
    """Get Java version string."""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Java version is typically in stderr
            version_line = result.stderr.split("\n")[0]
            return version_line
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_tools_dir() -> Path:
    """Get the tools directory path."""
    # Check if we're running as a PyInstaller executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        # Tools should be in the same directory as the executable
        executable_dir = Path(sys.executable).parent
        tools_dir = executable_dir / "tools"
        
        # If tools directory doesn't exist next to executable, 
        # check if it's bundled in the executable
        if not tools_dir.exists():
            # Check if tools are bundled in the executable
            bundled_tools = Path(sys._MEIPASS) / "tools"
            if bundled_tools.exists():
                return bundled_tools
            else:
                # Create tools directory next to executable if it doesn't exist
                tools_dir.mkdir(exist_ok=True)
        
        return tools_dir
    else:
        # Running from source code
        return Path(__file__).parent.parent.parent / "tools"


def get_data_dir() -> Path:
    """Get the data directory path."""
    # Check if we're running as a PyInstaller executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable - data is bundled
        return Path(sys._MEIPASS) / "data"
    else:
        # Running from source code
        return Path(__file__).parent.parent / "data"


def get_temp_dir() -> Path:
    """Get or create temporary directory for processing."""
    temp_dir = Path.home() / ".apk_purifier" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def clean_temp_dir() -> None:
    """Clean up temporary directory."""
    temp_dir = get_temp_dir()
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)


def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a system command with proper error handling and timeout."""
    logger = logging.getLogger(__name__)

    logger.debug(f"Running command: {' '.join(cmd)}")
    if cwd:
        logger.debug(f"Working directory: {cwd}")

    try:
        # Use Popen for better control
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait with timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            process.kill()
            stdout, stderr = process.communicate()
            returncode = -1
        
        # Create result object
        result = subprocess.CompletedProcess(cmd, returncode, stdout, stderr)

        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
        else:
            logger.debug(f"Command succeeded")
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout}")

        return result

    except Exception as e:
        logger.error(f"Error running command: {e}")
        # Return a failed result instead of raising
        return subprocess.CompletedProcess(cmd, -1, "", str(e))


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "java_version": get_java_version(),
    }


def validate_apk_file(file_path: Path) -> bool:
    """Basic validation of APK file."""
    if not file_path.exists():
        return False

    if not file_path.suffix.lower() == ".apk":
        return False

    # Check if it's a valid ZIP file (APKs are ZIP archives)
    try:
        import zipfile

        with zipfile.ZipFile(file_path, "r") as zf:
            # Check for AndroidManifest.xml
            if "AndroidManifest.xml" not in zf.namelist():
                return False
            # Check for classes.dex
            dex_files = [f for f in zf.namelist() if f.endswith(".dex")]
            if not dex_files:
                return False
        return True
    except (zipfile.BadZipFile, Exception):
        return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def create_backup(file_path: Path) -> Path:
    """Create a backup of the original APK file."""
    backup_dir = Path.home() / ".apk_purifier" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_name = f"{file_path.stem}_backup{file_path.suffix}"
    backup_path = backup_dir / backup_name

    # If backup already exists, add a number
    counter = 1
    while backup_path.exists():
        backup_name = f"{file_path.stem}_backup_{counter}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        counter += 1

    shutil.copy2(file_path, backup_path)
    return backup_path
