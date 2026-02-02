"""
APK Analysis and Decompilation Module
Handles APK file analysis, decompilation, and recompilation using APKTool and JADX.
"""

import logging
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import xmltodict

from .utils import run_command, get_tools_dir, get_temp_dir
from .jadx_analyzer import JADXAnalyzer


class APKAnalyzer:
    """Handles APK analysis and decompilation operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools_dir = get_tools_dir()
        self.temp_dir = get_temp_dir()
        self.apktool_path = self.tools_dir / "apktool.jar"
        self.jadx_analyzer = JADXAnalyzer()

    def analyze_apk(self, apk_path: Path) -> Dict[str, Any]:
        """Analyze APK file and extract metadata."""
        self.logger.info(f"Analyzing APK: {apk_path}")

        analysis = {
            "file_path": str(apk_path),
            "file_size": apk_path.stat().st_size,
            "manifest": {},
            "permissions": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "dex_files": [],
            "resources": [],
            "certificates": [],
            "ad_related": {"domains": [], "classes": [], "resources": []},
        }

        try:
            # Extract basic info from APK
            with zipfile.ZipFile(apk_path, "r") as zf:
                file_list = zf.namelist()

                # Find DEX files
                analysis["dex_files"] = [f for f in file_list if f.endswith(".dex")]

                # Find resource files
                analysis["resources"] = [f for f in file_list if f.startswith("res/")]

                # Extract AndroidManifest.xml if available
                if "AndroidManifest.xml" in file_list:
                    manifest_data = zf.read("AndroidManifest.xml")
                    # Note: This is binary XML, need to decompile for readable version
                    analysis["manifest"]["binary_size"] = len(manifest_data)

            # Decompile APK for detailed analysis
            decompiled_dir = self.decompile_apk(apk_path)
            if decompiled_dir:
                analysis.update(self._analyze_decompiled_apk(decompiled_dir))
            else:
                # Try JADX as fallback if APKTool fails
                self.logger.info("APKTool decompilation failed, trying JADX as fallback...")
                jadx_dir = self.jadx_analyzer.decompile_apk(apk_path)
                if jadx_dir:
                    analysis["decompiler_used"] = "JADX"
                    analysis.update(self._analyze_jadx_decompiled_apk(jadx_dir))
                else:
                    self.logger.warning("Both APKTool and JADX decompilation failed")

        except Exception as e:
            self.logger.error(f"Error analyzing APK: {e}")
            analysis["error"] = str(e)

        return analysis

    def decompile_apk(self, apk_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Decompile APK using APKTool."""
        if not self.apktool_path.exists():
            self.logger.error("APKTool not found")
            return None

        if output_dir is None:
            output_dir = self.temp_dir / f"{apk_path.stem}_decompiled"

        # Remove existing output directory
        if output_dir.exists():
            shutil.rmtree(output_dir)

        self.logger.info(f"Decompiling APK to: {output_dir}")
        
        # Calculate timeout based on file size (minimum 5 minutes, max 30 minutes)
        file_size_mb = apk_path.stat().st_size / (1024 * 1024)
        timeout = max(300, min(1800, int(file_size_mb * 30)))  # 30 seconds per MB
        
        self.logger.info(f"Using timeout of {timeout} seconds for {file_size_mb:.1f}MB APK")

        cmd = [
            "java",
            "-jar",
            str(self.apktool_path),
            "d",  # decode
            str(apk_path),
            "-o",
            str(output_dir),
            "-f",  # force overwrite
            "--no-src",  # Don't decompile sources (faster, less likely to fail)
        ]

        try:
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            result = run_command(cmd, timeout=timeout)

            self.logger.debug(f"APKTool stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"APKTool stderr: {result.stderr}")

            if result.returncode == 0:
                self.logger.info("APK decompiled successfully")
                return output_dir
            else:
                self.logger.error(f"APKTool decompilation failed with return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                
                # Try again without --no-src if it failed
                self.logger.info("Retrying decompilation with full source decompilation...")
                cmd_retry = [
                    "java",
                    "-jar",
                    str(self.apktool_path),
                    "d",  # decode
                    str(apk_path),
                    "-o",
                    str(output_dir),
                    "-f",  # force overwrite
                ]
                
                result_retry = run_command(cmd_retry, timeout=timeout * 2)  # Double timeout for retry
                
                if result_retry.returncode == 0:
                    self.logger.info("APK decompiled successfully on retry")
                    return output_dir
                else:
                    self.logger.error(f"APKTool decompilation failed on retry: {result_retry.stderr}")
                    return None

        except Exception as e:
            self.logger.error(f"Error during decompilation: {e}")
            return None

    def recompile_apk(self, decompiled_dir: Path, output_apk: Optional[Path] = None) -> Optional[Path]:
        """Recompile APK using APKTool."""
        if not self.apktool_path.exists():
            self.logger.error("APKTool not found")
            return None

        if output_apk is None:
            output_apk = self.temp_dir / f"{decompiled_dir.name}_recompiled.apk"

        self.logger.info(f"Recompiling APK from: {decompiled_dir}")
        self.logger.info(f"Output APK: {output_apk}")

        cmd = [
            "java",
            "-jar",
            str(self.apktool_path),
            "b",  # build
            str(decompiled_dir),
            "-o",
            str(output_apk),
            "-f",  # force overwrite
        ]

        try:
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            result = run_command(cmd, timeout=600)

            self.logger.debug(f"APKTool stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"APKTool stderr: {result.stderr}")

            if result.returncode == 0 and output_apk.exists():
                self.logger.info(f"APK recompiled successfully: {output_apk}")
                return output_apk
            else:
                self.logger.error(f"APKTool recompilation failed with return code: {result.returncode}")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                
                # Check for common issues
                if "aapt" in result.stderr.lower():
                    self.logger.error("AAPT error detected. This might be due to resource conflicts.")
                if "duplicate" in result.stderr.lower():
                    self.logger.error("Duplicate resource error detected.")
                if "invalid" in result.stderr.lower():
                    self.logger.error("Invalid resource or configuration detected.")
                    
                return None

        except Exception as e:
            self.logger.error(f"Error during recompilation: {e}")
            return None
    
    def recompile_apk_simple(self, decompiled_dir: Path, output_apk: Optional[Path] = None) -> Optional[Path]:
        """Simple APK recompilation with minimal processing."""
        if not self.apktool_path.exists():
            self.logger.error("APKTool not found")
            return None

        if output_apk is None:
            output_apk = self.temp_dir / f"{decompiled_dir.name}_simple_recompiled.apk"

        self.logger.info(f"Attempting simple recompilation from: {decompiled_dir}")

        # Try with minimal flags first
        cmd = [
            "java",
            "-jar",
            str(self.apktool_path),
            "b",  # build
            str(decompiled_dir),
            "-o",
            str(output_apk),
            "-f",  # force overwrite
            "--use-aapt2",  # Use AAPT2 for better compatibility
        ]

        try:
            result = run_command(cmd, timeout=900)  # Longer timeout

            if result.returncode == 0 and output_apk.exists():
                self.logger.info(f"Simple APK recompilation successful: {output_apk}")
                return output_apk
            else:
                self.logger.warning("Simple recompilation failed, trying without AAPT2...")
                
                # Try without AAPT2
                cmd_fallback = [
                    "java",
                    "-jar",
                    str(self.apktool_path),
                    "b",
                    str(decompiled_dir),
                    "-o",
                    str(output_apk),
                    "-f",
                ]
                
                result_fallback = run_command(cmd_fallback, timeout=900)
                
                if result_fallback.returncode == 0 and output_apk.exists():
                    self.logger.info(f"Fallback APK recompilation successful: {output_apk}")
                    return output_apk
                else:
                    self.logger.error("All recompilation attempts failed")
                    return None

        except Exception as e:
            self.logger.error(f"Error during simple recompilation: {e}")
            return None

    def _analyze_decompiled_apk(self, decompiled_dir: Path) -> Dict[str, Any]:
        """Analyze decompiled APK directory."""
        analysis = {}

        try:
            # Parse AndroidManifest.xml
            manifest_path = decompiled_dir / "AndroidManifest.xml"
            if manifest_path.exists():
                analysis["manifest"] = self._parse_manifest(manifest_path)

            # Analyze smali code
            smali_dir = decompiled_dir / "smali"
            if smali_dir.exists():
                analysis["smali_analysis"] = self._analyze_smali_code(smali_dir)

            # Analyze resources
            res_dir = decompiled_dir / "res"
            if res_dir.exists():
                analysis["resource_analysis"] = self._analyze_resources(res_dir)

        except Exception as e:
            self.logger.error(f"Error analyzing decompiled APK: {e}")
            analysis["analysis_error"] = str(e)

        return analysis

    def _analyze_jadx_decompiled_apk(self, jadx_dir: Path) -> Dict[str, Any]:
        """Analyze JADX decompiled APK directory."""
        analysis = {}

        try:
            # Analyze Java source code
            sources_dir = jadx_dir / "sources"
            if sources_dir.exists():
                analysis["jadx_java_analysis"] = self.jadx_analyzer.analyze_decompiled_java(sources_dir)

            # Analyze resources if available
            resources_dir = jadx_dir / "resources"
            if resources_dir.exists():
                # Look for AndroidManifest.xml
                manifest_path = resources_dir / "AndroidManifest.xml"
                if manifest_path.exists():
                    analysis["manifest"] = self._parse_manifest(manifest_path)
                
                # Analyze other resources
                res_dir = resources_dir / "res"
                if res_dir.exists():
                    analysis["resource_analysis"] = self._analyze_resources(res_dir)

        except Exception as e:
            self.logger.error(f"Error analyzing JADX decompiled APK: {e}")
            analysis["jadx_analysis_error"] = str(e)

        return analysis

    def decompile_with_jadx(self, apk_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Decompile APK using JADX (public method)."""
        return self.jadx_analyzer.decompile_apk(apk_path, output_dir)

    def decompile_to_java(self, apk_path: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Decompile APK to Java source using JADX."""
        return self.jadx_analyzer.decompile_to_java(apk_path, output_dir)

    def is_jadx_available(self) -> bool:
        """Check if JADX is available."""
        return self.jadx_analyzer.is_available()

    def _parse_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Parse AndroidManifest.xml file."""
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse XML
            root = ET.fromstring(content)

            manifest_info = {
                "package": root.get("package", ""),
                "version_code": root.get("{http://schemas.android.com/apk/res/android}versionCode", ""),
                "version_name": root.get("{http://schemas.android.com/apk/res/android}versionName", ""),
                "permissions": [],
                "activities": [],
                "services": [],
                "receivers": [],
            }

            # Extract permissions
            for perm in root.findall("uses-permission"):
                name = perm.get("{http://schemas.android.com/apk/res/android}name", "")
                if name:
                    manifest_info["permissions"].append(name)

            # Extract application components
            app = root.find("application")
            if app is not None:
                # Activities
                for activity in app.findall("activity"):
                    name = activity.get("{http://schemas.android.com/apk/res/android}name", "")
                    if name:
                        manifest_info["activities"].append(name)

                # Services
                for service in app.findall("service"):
                    name = service.get("{http://schemas.android.com/apk/res/android}name", "")
                    if name:
                        manifest_info["services"].append(name)

                # Receivers
                for receiver in app.findall("receiver"):
                    name = receiver.get("{http://schemas.android.com/apk/res/android}name", "")
                    if name:
                        manifest_info["receivers"].append(name)

            return manifest_info

        except Exception as e:
            self.logger.error(f"Error parsing manifest: {e}")
            return {"error": str(e)}

    def _analyze_smali_code(self, smali_dir: Path) -> Dict[str, Any]:
        """Analyze smali code for ad-related patterns."""
        analysis = {"total_files": 0, "ad_related_files": [], "suspicious_patterns": []}

        try:
            # Known ad-related package patterns
            ad_patterns = [
                "com/google/ads",
                "com/facebook/ads",
                "com/amazon/device/ads",
                "com/unity3d/ads",
                "com/chartboost",
                "com/applovin",
                "com/ironsource",
                "com/vungle",
                "com/tapjoy",
                "com/inmobi",
                "com/mopub",
                "com/admob",
                "com/adsystem",
                "com/advertising",
            ]

            # Recursively find all .smali files
            smali_files = list(smali_dir.rglob("*.smali"))
            analysis["total_files"] = len(smali_files)

            for smali_file in smali_files:
                relative_path = smali_file.relative_to(smali_dir)

                # Check if file path contains ad-related patterns
                for pattern in ad_patterns:
                    if pattern in str(relative_path):
                        analysis["ad_related_files"].append(str(relative_path))
                        break

        except Exception as e:
            self.logger.error(f"Error analyzing smali code: {e}")
            analysis["error"] = str(e)

        return analysis

    def _analyze_resources(self, res_dir: Path) -> Dict[str, Any]:
        """Analyze resources for ad-related content."""
        analysis = {"layouts": [], "drawables": [], "strings": {}, "ad_related_resources": []}

        try:
            # Analyze layout files
            layout_dir = res_dir / "layout"
            if layout_dir.exists():
                analysis["layouts"] = [f.name for f in layout_dir.glob("*.xml")]

            # Analyze drawable resources
            for drawable_dir in res_dir.glob("drawable*"):
                if drawable_dir.is_dir():
                    drawables = [f.name for f in drawable_dir.iterdir()]
                    analysis["drawables"].extend(drawables)

            # Analyze strings.xml for ad-related content
            values_dir = res_dir / "values"
            if values_dir.exists():
                strings_file = values_dir / "strings.xml"
                if strings_file.exists():
                    analysis["strings"] = self._parse_strings_xml(strings_file)

        except Exception as e:
            self.logger.error(f"Error analyzing resources: {e}")
            analysis["error"] = str(e)

        return analysis

    def _parse_strings_xml(self, strings_file: Path) -> Dict[str, str]:
        """Parse strings.xml file."""
        strings = {}

        try:
            tree = ET.parse(strings_file)
            root = tree.getroot()

            for string_elem in root.findall("string"):
                name = string_elem.get("name")
                value = string_elem.text or ""
                if name:
                    strings[name] = value

        except Exception as e:
            self.logger.error(f"Error parsing strings.xml: {e}")

        return strings
