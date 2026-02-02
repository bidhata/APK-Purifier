"""
JADX Decompiler Integration Module
Handles APK decompilation using JADX as an alternative to APKTool.

Author: Krishnendu Paul
Website: https://krishnendu.com
"""

import logging
import shutil
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .utils import run_command, get_tools_dir, get_temp_dir


class JADXAnalyzer:
    """Handles APK decompilation using JADX."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools_dir = get_tools_dir()
        self.temp_dir = get_temp_dir()
        self.jadx_dir = self.tools_dir / "jadx"
        
        # Determine JADX executable based on OS
        if os.name == 'nt':  # Windows
            self.jadx_cmd = self.jadx_dir / "bin" / "jadx.bat"
        else:  # Linux/macOS
            self.jadx_cmd = self.jadx_dir / "bin" / "jadx"

    def is_available(self) -> bool:
        """Check if JADX is available."""
        return self.jadx_cmd.exists() and self.jadx_cmd.is_file()

    def decompile_apk(self, apk_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Decompile APK using JADX."""
        if not self.is_available():
            self.logger.error("JADX not found or not executable")
            return None

        if output_dir is None:
            output_dir = self.temp_dir / f"{apk_path.stem}_jadx_decompiled"

        # Remove existing output directory
        if output_dir.exists():
            shutil.rmtree(output_dir)

        self.logger.info(f"Decompiling APK with JADX to: {output_dir}")
        
        # Calculate timeout based on file size
        file_size_mb = apk_path.stat().st_size / (1024 * 1024)
        timeout = max(300, min(1800, int(file_size_mb * 45)))  # 45 seconds per MB
        
        self.logger.info(f"Using timeout of {timeout} seconds for {file_size_mb:.1f}MB APK")

        cmd = [
            str(self.jadx_cmd),
            "-d", str(output_dir),  # output directory
            "-r",  # do not decode resources
            "--show-bad-code",  # show inconsistent code
            "--no-imports",  # disable auto import
            "--no-debug-info",  # disable debug info
            str(apk_path)
        ]

        try:
            self.logger.debug(f"Running JADX command: {' '.join(cmd)}")
            result = run_command(cmd, timeout=timeout)

            self.logger.debug(f"JADX stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"JADX stderr: {result.stderr}")

            if result.returncode == 0 and output_dir.exists():
                self.logger.info("APK decompiled successfully with JADX")
                return output_dir
            else:
                self.logger.error(f"JADX decompilation failed with return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                
                # Try with resources enabled if it failed
                self.logger.info("Retrying JADX decompilation with resources...")
                cmd_retry = [
                    str(self.jadx_cmd),
                    "-d", str(output_dir),
                    "--show-bad-code",
                    "--no-imports",
                    str(apk_path)
                ]
                
                result_retry = run_command(cmd_retry, timeout=timeout * 2)
                
                if result_retry.returncode == 0 and output_dir.exists():
                    self.logger.info("APK decompiled successfully with JADX on retry")
                    return output_dir
                else:
                    self.logger.error(f"JADX decompilation failed on retry: {result_retry.stderr}")
                    return None

        except Exception as e:
            self.logger.error(f"Error during JADX decompilation: {e}")
            return None

    def decompile_to_java(self, apk_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Decompile APK to Java source code using JADX."""
        if not self.is_available():
            self.logger.error("JADX not found or not executable")
            return None

        if output_dir is None:
            output_dir = self.temp_dir / f"{apk_path.stem}_jadx_java"

        # Remove existing output directory
        if output_dir.exists():
            shutil.rmtree(output_dir)

        self.logger.info(f"Decompiling APK to Java with JADX: {output_dir}")
        
        # Calculate timeout based on file size
        file_size_mb = apk_path.stat().st_size / (1024 * 1024)
        timeout = max(600, min(3600, int(file_size_mb * 60)))  # 60 seconds per MB for Java
        
        cmd = [
            str(self.jadx_cmd),
            "-d", str(output_dir),
            "--show-bad-code",
            "--no-imports",
            "--no-debug-info",
            "--deobf",  # enable deobfuscation
            str(apk_path)
        ]

        try:
            self.logger.debug(f"Running JADX Java command: {' '.join(cmd)}")
            result = run_command(cmd, timeout=timeout)

            if result.returncode == 0 and output_dir.exists():
                self.logger.info("APK decompiled to Java successfully with JADX")
                return output_dir
            else:
                self.logger.error(f"JADX Java decompilation failed: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error during JADX Java decompilation: {e}")
            return None

    def analyze_decompiled_java(self, java_dir: Path) -> Dict[str, Any]:
        """Analyze decompiled Java code for ad-related patterns."""
        analysis = {
            "total_java_files": 0,
            "ad_related_files": [],
            "suspicious_patterns": [],
            "package_structure": {}
        }

        try:
            # Find all Java files
            java_files = list(java_dir.rglob("*.java"))
            analysis["total_java_files"] = len(java_files)

            # Known ad-related patterns in Java code
            ad_patterns = [
                "google.ads",
                "facebook.ads", 
                "amazon.device.ads",
                "unity3d.ads",
                "chartboost",
                "applovin",
                "ironsource",
                "vungle",
                "tapjoy",
                "inmobi",
                "mopub",
                "admob",
                "adsystem",
                "advertising"
            ]

            suspicious_keywords = [
                "loadAd",
                "showAd",
                "AdRequest",
                "AdView",
                "InterstitialAd",
                "BannerAd",
                "RewardedAd"
            ]

            for java_file in java_files:
                try:
                    relative_path = java_file.relative_to(java_dir)
                    
                    # Check file path for ad patterns
                    for pattern in ad_patterns:
                        if pattern in str(relative_path).lower():
                            analysis["ad_related_files"].append(str(relative_path))
                            break
                    
                    # Read file content and check for suspicious keywords
                    with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for keyword in suspicious_keywords:
                            if keyword in content:
                                analysis["suspicious_patterns"].append({
                                    "file": str(relative_path),
                                    "pattern": keyword,
                                    "type": "ad_keyword"
                                })

                except Exception as e:
                    self.logger.debug(f"Error analyzing Java file {java_file}: {e}")
                    continue

            # Build package structure
            analysis["package_structure"] = self._build_package_structure(java_dir)

        except Exception as e:
            self.logger.error(f"Error analyzing decompiled Java code: {e}")
            analysis["error"] = str(e)

        return analysis

    def _build_package_structure(self, java_dir: Path) -> Dict[str, Any]:
        """Build package structure from Java files."""
        structure = {}
        
        try:
            for java_file in java_dir.rglob("*.java"):
                relative_path = java_file.relative_to(java_dir)
                parts = relative_path.parts[:-1]  # Exclude filename
                
                current = structure
                for part in parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
        except Exception as e:
            self.logger.error(f"Error building package structure: {e}")
            
        return structure

    def extract_strings(self, apk_path: Path) -> Optional[List[str]]:
        """Extract strings from APK using JADX."""
        if not self.is_available():
            self.logger.error("JADX not found")
            return None

        self.logger.info("Extracting strings from APK with JADX")
        
        cmd = [
            str(self.jadx_cmd),
            "--show-bad-code",
            "--no-src",  # don't save sources
            "--no-res",  # don't save resources
            "--export-gradle",  # export gradle project
            str(apk_path)
        ]

        try:
            result = run_command(cmd, timeout=300)
            
            if result.returncode == 0:
                # Parse strings from output
                strings = []
                for line in result.stdout.split('\n'):
                    if 'string' in line.lower() and '"' in line:
                        # Extract string literals
                        parts = line.split('"')
                        if len(parts) >= 2:
                            strings.append(parts[1])
                
                self.logger.info(f"Extracted {len(strings)} strings")
                return strings
            else:
                self.logger.error(f"JADX string extraction failed: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error extracting strings with JADX: {e}")
            return None