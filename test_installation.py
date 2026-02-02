#!/usr/bin/env python3
"""
Installation test script for APK Purifier
Verifies that all dependencies and tools are properly installed.

Author: Krishnendu Paul
Website: https://krishnendu.com
"""

import sys
import subprocess
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version."""
    print("Testing Python version...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def test_python_packages():
    """Test required Python packages."""
    print("\nTesting Python packages...")
    
    required_packages = [
        "PyQt6",
        "requests",
        "lxml",
        "cryptography",
        "pathlib"
    ]
    
    success_count = 0
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
            success_count += 1
        except ImportError:
            print(f"✗ {package} (Missing)")
    
    return success_count == len(required_packages)

def test_java():
    """Test Java installation."""
    print("\nTesting Java installation...")
    
    try:
        result = subprocess.run(
            ["java", "-version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"✓ {version_line}")
            return True
        else:
            print("✗ Java command failed")
            return False
            
    except FileNotFoundError:
        print("✗ Java not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Java command timed out")
        return False

def test_tools():
    """Test external tools."""
    print("\nTesting external tools...")
    
    tools_dir = Path(__file__).parent / "tools"
    required_tools = [
        "apktool.jar",
        "uber-apk-signer.jar"
    ]
    
    # JADX is optional but recommended
    optional_tools = [
        "jadx/bin/jadx.bat" if sys.platform == "win32" else "jadx/bin/jadx"
    ]
    
    success_count = 0
    
    for tool in required_tools:
        tool_path = tools_dir / tool
        if tool_path.exists():
            print(f"✓ {tool} ({tool_path})")
            success_count += 1
        else:
            print(f"✗ {tool} (Not found in {tools_dir})")
    
    # Check optional tools
    for tool in optional_tools:
        tool_path = tools_dir / tool
        if tool_path.exists():
            print(f"✓ {tool} (Optional - Available)")
        else:
            print(f"○ {tool} (Optional - Not found)")
    
    return success_count == len(required_tools)

def test_apktool():
    """Test APKTool functionality."""
    print("\nTesting APKTool...")
    
    tools_dir = Path(__file__).parent / "tools"
    apktool_path = tools_dir / "apktool.jar"
    
    if not apktool_path.exists():
        print("✗ APKTool not found")
        return False
    
    try:
        result = subprocess.run(
            ["java", "-jar", str(apktool_path), "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ APKTool version: {version}")
            return True
        else:
            print(f"✗ APKTool failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ APKTool command timed out")
        return False
    except Exception as e:
        print(f"✗ APKTool test failed: {e}")
        return False

def test_uber_apk_signer():
    """Test uber-apk-signer functionality."""
    print("\nTesting uber-apk-signer...")
    
    tools_dir = Path(__file__).parent / "tools"
    signer_path = tools_dir / "uber-apk-signer.jar"
    
    if not signer_path.exists():
        print("✗ uber-apk-signer not found")
        return False
    
    try:
        result = subprocess.run(
            ["java", "-jar", str(signer_path), "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ uber-apk-signer version: {version}")
            return True
        else:
            print(f"✗ uber-apk-signer failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ uber-apk-signer command timed out")
        return False
    except Exception as e:
        print(f"✗ uber-apk-signer test failed: {e}")
        return False

def test_jadx():
    """Test JADX functionality (optional)."""
    print("\nTesting JADX (optional)...")
    
    tools_dir = Path(__file__).parent / "tools"
    jadx_dir = tools_dir / "jadx"
    
    if not jadx_dir.exists():
        print("○ JADX not found (optional tool)")
        return True  # Not required, so return True
    
    # Determine JADX executable based on OS
    if sys.platform == "win32":
        jadx_cmd = jadx_dir / "bin" / "jadx.bat"
    else:
        jadx_cmd = jadx_dir / "bin" / "jadx"
    
    if not jadx_cmd.exists():
        print(f"✗ JADX executable not found: {jadx_cmd}")
        return True  # Optional tool
    
    try:
        result = subprocess.run(
            [str(jadx_cmd), "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            version_info = result.stdout.strip() or result.stderr.strip()
            print(f"✓ JADX available: {version_info}")
            return True
        else:
            print(f"○ JADX test failed (optional): {result.stderr}")
            return True  # Optional tool
            
    except subprocess.TimeoutExpired:
        print("○ JADX command timed out (optional)")
        return True
    except Exception as e:
        print(f"○ JADX test failed (optional): {e}")
        return True

def test_gui():
    """Test GUI components."""
    print("\nTesting GUI components...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Create a minimal QApplication to test GUI
        app = QApplication([])
        print("✓ PyQt6 GUI components working")
        app.quit()
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def test_core_modules():
    """Test core application modules."""
    print("\nTesting core modules...")
    
    src_dir = Path(__file__).parent / "src"
    if not src_dir.exists():
        print("✗ Source directory not found")
        return False
    
    # Add src to path for imports
    sys.path.insert(0, str(src_dir))
    
    modules_to_test = [
        "core.utils",
        "core.apk_analyzer",
        "core.jadx_analyzer",
        "core.ad_patcher",
        "core.malware_scanner",
        "core.apk_signer"
    ]
    
    success_count = 0
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module} ({e})")
    
    return success_count == len(modules_to_test)

def main():
    """Main test function."""
    print("APK Purifier - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Python Packages", test_python_packages),
        ("Java Installation", test_java),
        ("External Tools", test_tools),
        ("APKTool", test_apktool),
        ("uber-apk-signer", test_uber_apk_signer),
        ("JADX (Optional)", test_jadx),
        ("GUI Components", test_gui),
        ("Core Modules", test_core_modules)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✓ All tests passed! APK Purifier is ready to use.")
        print("\nTo start the application, run:")
        print("python src/main.py")
        return 0
    else:
        print("✗ Some tests failed. Please check the installation.")
        
        if passed_tests < total_tests // 2:
            print("\nRecommended actions:")
            print("1. Install missing Python packages: pip install -r requirements.txt")
            print("2. Download tools: python download_tools.py")
            print("3. Verify Java installation")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        sys.exit(1)