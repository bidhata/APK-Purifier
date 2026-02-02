"""
APK Signing Module
Handles APK signing and alignment using uber-apk-signer and zipalign.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from .utils import run_command, get_tools_dir, get_temp_dir


class APKSigner:
    """Handles APK signing and alignment operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools_dir = get_tools_dir()
        self.temp_dir = get_temp_dir()
        self.uber_signer_path = self.tools_dir / "uber-apk-signer.jar"

    def sign_apk(
        self,
        input_apk: Path,
        output_apk: Optional[Path] = None,
        keystore_path: Optional[Path] = None,
        keystore_password: Optional[str] = None,
        key_alias: Optional[str] = None,
        key_password: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Sign APK file using uber-apk-signer.

        Args:
            input_apk: Path to input APK file
            output_apk: Path for output signed APK (optional)
            keystore_path: Path to custom keystore (optional, uses debug keystore if not provided)
            keystore_password: Keystore password (optional)
            key_alias: Key alias (optional)
            key_password: Key password (optional)

        Returns:
            Path to signed APK file or None if failed
        """
        if not self.uber_signer_path.exists():
            self.logger.error("uber-apk-signer.jar not found")
            return None

        if output_apk is None:
            output_apk = self.temp_dir / f"{input_apk.stem}_signed.apk"

        self.logger.info(f"Signing APK: {input_apk}")

        # Build command
        cmd = ["java", "-jar", str(self.uber_signer_path), "--apks", str(input_apk), "--out", str(output_apk.parent)]

        # Add custom keystore if provided
        if keystore_path and keystore_path.exists():
            cmd.extend(["--ks", str(keystore_path)])

            if keystore_password:
                cmd.extend(["--ksPass", keystore_password])

            if key_alias:
                cmd.extend(["--ksAlias", key_alias])

            if key_password:
                cmd.extend(["--ksKeyPass", key_password])
        else:
            # Use debug keystore
            cmd.append("--debug")

        # Additional options
        cmd.extend(["--allowResign", "--overwrite"])  # Allow resigning already signed APKs  # Overwrite existing files

        try:
            result = run_command(cmd, timeout=300)

            if result.returncode == 0:
                # uber-apk-signer creates files with specific naming
                # Find the signed APK
                signed_apk = self._find_signed_apk(output_apk.parent, input_apk.stem)

                if signed_apk and signed_apk.exists():
                    # Move to desired output location
                    if signed_apk != output_apk:
                        shutil.move(signed_apk, output_apk)

                    self.logger.info(f"APK signed successfully: {output_apk}")
                    return output_apk
                else:
                    self.logger.error("Signed APK not found after signing")
                    return None
            else:
                self.logger.error(f"APK signing failed: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error during APK signing: {e}")
            return None

    def _find_signed_apk(self, output_dir: Path, base_name: str) -> Optional[Path]:
        """Find the signed APK file created by uber-apk-signer."""
        # uber-apk-signer typically creates files with suffixes like:
        # - filename-aligned-debugSigned.apk
        # - filename-aligned-signed.apk

        possible_patterns = [
            f"{base_name}-aligned-debugSigned.apk",
            f"{base_name}-aligned-signed.apk",
            f"{base_name}-debugSigned.apk",
            f"{base_name}-signed.apk",
        ]

        for pattern in possible_patterns:
            signed_apk = output_dir / pattern
            if signed_apk.exists():
                return signed_apk

        # If not found, look for any APK file in the output directory
        apk_files = list(output_dir.glob("*.apk"))
        if apk_files:
            return apk_files[0]  # Return the first one found

        return None

    def verify_apk_signature(self, apk_path: Path) -> Dict[str, Any]:
        """
        Verify APK signature using uber-apk-signer.

        Args:
            apk_path: Path to APK file to verify

        Returns:
            Dictionary with verification results
        """
        if not self.uber_signer_path.exists():
            self.logger.error("uber-apk-signer.jar not found")
            return {"error": "uber-apk-signer not found"}

        self.logger.info(f"Verifying APK signature: {apk_path}")

        cmd = ["java", "-jar", str(self.uber_signer_path), "--verify", "--apks", str(apk_path)]

        try:
            result = run_command(cmd, timeout=60)

            verification_result = {
                "is_signed": False,
                "signature_valid": False,
                "signature_schemes": [],
                "certificate_info": {},
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

            if result.returncode == 0:
                verification_result["is_signed"] = True
                verification_result["signature_valid"] = True

                # Parse output for signature scheme information
                output = result.stdout.lower()
                if "v1 signature" in output:
                    verification_result["signature_schemes"].append("v1")
                if "v2 signature" in output:
                    verification_result["signature_schemes"].append("v2")
                if "v3 signature" in output:
                    verification_result["signature_schemes"].append("v3")

                self.logger.info("APK signature verification passed")
            else:
                self.logger.warning(f"APK signature verification failed: {result.stderr}")

            return verification_result

        except Exception as e:
            self.logger.error(f"Error during signature verification: {e}")
            return {"error": str(e)}

    def create_debug_keystore(self, keystore_path: Path, password: str = "android") -> bool:
        """
        Create a debug keystore for signing APKs.

        Args:
            keystore_path: Path where to create the keystore
            password: Keystore password (default: "android")

        Returns:
            True if keystore created successfully, False otherwise
        """
        self.logger.info(f"Creating debug keystore: {keystore_path}")

        cmd = [
            "keytool",
            "-genkey",
            "-v",
            "-keystore",
            str(keystore_path),
            "-alias",
            "androiddebugkey",
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "10000",
            "-storepass",
            password,
            "-keypass",
            password,
            "-dname",
            "CN=Android Debug,O=Android,C=US",
        ]

        try:
            result = run_command(cmd, timeout=60)

            if result.returncode == 0 and keystore_path.exists():
                self.logger.info("Debug keystore created successfully")
                return True
            else:
                self.logger.error(f"Failed to create debug keystore: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error creating debug keystore: {e}")
            return False

    def get_apk_info(self, apk_path: Path) -> Dict[str, Any]:
        """
        Get APK information using uber-apk-signer.

        Args:
            apk_path: Path to APK file

        Returns:
            Dictionary with APK information
        """
        if not self.uber_signer_path.exists():
            return {"error": "uber-apk-signer not found"}

        cmd = ["java", "-jar", str(self.uber_signer_path), "--info", "--apks", str(apk_path)]

        try:
            result = run_command(cmd, timeout=60)

            info = {
                "file_path": str(apk_path),
                "file_size": apk_path.stat().st_size,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

            if result.returncode == 0:
                # Parse output for useful information
                output = result.stdout

                # Extract package name, version, etc. from output
                # This would need to be implemented based on uber-apk-signer output format

                self.logger.info("APK info retrieved successfully")
            else:
                self.logger.error(f"Failed to get APK info: {result.stderr}")

            return info

        except Exception as e:
            self.logger.error(f"Error getting APK info: {e}")
            return {"error": str(e)}

    def is_apk_signed(self, apk_path: Path) -> bool:
        """
        Quick check if APK is signed.

        Args:
            apk_path: Path to APK file

        Returns:
            True if APK appears to be signed, False otherwise
        """
        try:
            import zipfile

            with zipfile.ZipFile(apk_path, "r") as zf:
                file_list = zf.namelist()

                # Check for signature files
                has_manifest = any(f.startswith("META-INF/MANIFEST.MF") for f in file_list)
                has_cert = any(f.startswith("META-INF/") and f.endswith(".RSA") for f in file_list)
                has_sf = any(f.startswith("META-INF/") and f.endswith(".SF") for f in file_list)

                return has_manifest and (has_cert or has_sf)

        except Exception as e:
            self.logger.error(f"Error checking if APK is signed: {e}")
            return False
