"""
Ad Removal Patcher Module
Implements various methods to remove advertisements from APK files.
"""

import logging
import re
import shutil
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import xml.etree.ElementTree as ET

from .utils import get_data_dir


class AdPatcher:
    """Handles advertisement removal from decompiled APK files."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = get_data_dir()
        self.ad_domains = self._load_ad_domains()
        self.ad_classes = self._load_ad_classes()

    def patch_apk(self, decompiled_dir: Path, methods: List[str] = None) -> Dict[str, any]:
        """
        Apply ad removal patches to decompiled APK.

        Args:
            decompiled_dir: Path to decompiled APK directory
            methods: List of patching methods to apply

        Returns:
            Dictionary with patching results
        """
        if methods is None:
            methods = ["domain_replacement", "class_removal", "manifest_cleanup", "resource_cleanup"]

        results = {
            "methods_applied": [],
            "domains_replaced": 0,
            "classes_removed": 0,
            "permissions_removed": 0,
            "resources_removed": 0,
            "errors": [],
        }

        self.logger.info(f"Starting ad patching with methods: {methods}")

        try:
            # Create backup of critical files before patching
            self._backup_critical_files(decompiled_dir)

            if "domain_replacement" in methods:
                domain_result = self._patch_ad_domains(decompiled_dir)
                results["domains_replaced"] = domain_result
                results["methods_applied"].append("domain_replacement")

            if "class_removal" in methods:
                class_result = self._remove_ad_classes(decompiled_dir)
                results["classes_removed"] = class_result
                results["methods_applied"].append("class_removal")

            if "manifest_cleanup" in methods:
                manifest_result = self._clean_manifest(decompiled_dir)
                results["permissions_removed"] = manifest_result
                results["methods_applied"].append("manifest_cleanup")

            if "resource_cleanup" in methods:
                resource_result = self._clean_resources(decompiled_dir)
                results["resources_removed"] = resource_result
                results["methods_applied"].append("resource_cleanup")

        except Exception as e:
            error_msg = f"Error during ad patching: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            
            # Attempt to restore from backup on critical errors
            try:
                self._restore_critical_files(decompiled_dir)
                self.logger.info("Restored critical files from backup due to patching error")
            except Exception as restore_error:
                self.logger.error(f"Failed to restore backup: {restore_error}")

        return results

    def _backup_critical_files(self, decompiled_dir: Path) -> None:
        """Create backup of critical files before patching."""
        try:
            backup_dir = decompiled_dir / ".backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup AndroidManifest.xml
            manifest_path = decompiled_dir / "AndroidManifest.xml"
            if manifest_path.exists():
                shutil.copy2(manifest_path, backup_dir / "AndroidManifest.xml")
            
            # Backup public.xml files
            res_dir = decompiled_dir / "res"
            if res_dir.exists():
                values_dirs = [d for d in res_dir.iterdir() if d.is_dir() and d.name.startswith("values")]
                for values_dir in values_dirs:
                    public_xml = values_dir / "public.xml"
                    if public_xml.exists():
                        backup_values_dir = backup_dir / values_dir.name
                        backup_values_dir.mkdir(exist_ok=True)
                        shutil.copy2(public_xml, backup_values_dir / "public.xml")
            
            self.logger.debug("Created backup of critical files")
            
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")

    def _restore_critical_files(self, decompiled_dir: Path) -> None:
        """Restore critical files from backup."""
        try:
            backup_dir = decompiled_dir / ".backup"
            if not backup_dir.exists():
                return
            
            # Restore AndroidManifest.xml
            backup_manifest = backup_dir / "AndroidManifest.xml"
            if backup_manifest.exists():
                shutil.copy2(backup_manifest, decompiled_dir / "AndroidManifest.xml")
            
            # Restore public.xml files
            for backup_values_dir in backup_dir.iterdir():
                if backup_values_dir.is_dir() and backup_values_dir.name.startswith("values"):
                    backup_public_xml = backup_values_dir / "public.xml"
                    if backup_public_xml.exists():
                        target_values_dir = decompiled_dir / "res" / backup_values_dir.name
                        if target_values_dir.exists():
                            shutil.copy2(backup_public_xml, target_values_dir / "public.xml")
            
            self.logger.debug("Restored critical files from backup")
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")

    def _load_ad_domains(self) -> Set[str]:
        """Load known ad domains from data file."""
        domains = set()

        try:
            domains_file = self.data_dir / "ad_domains.txt"
            if domains_file.exists():
                with open(domains_file, "r", encoding="utf-8") as f:
                    for line in f:
                        domain = line.strip()
                        if domain and not domain.startswith("#"):
                            domains.add(domain)
            else:
                # Default ad domains if file doesn't exist
                domains.update(
                    [
                        "googleads.g.doubleclick.net",
                        "googlesyndication.com",
                        "googleadservices.com",
                        "facebook.com/tr",
                        "amazon-adsystem.com",
                        "unity3d.com/ads",
                        "chartboost.com",
                        "applovin.com",
                        "ironsrc.com",
                        "vungle.com",
                        "tapjoy.com",
                        "inmobi.com",
                        "mopub.com",
                        "admob.com",
                        "adsystem.com",
                        "advertising.com",
                    ]
                )

        except Exception as e:
            self.logger.error(f"Error loading ad domains: {e}")

        self.logger.info(f"Loaded {len(domains)} ad domains")
        return domains

    def _load_ad_classes(self) -> Set[str]:
        """Load known ad-related class patterns."""
        classes = set()

        try:
            classes_file = self.data_dir / "ad_classes.txt"
            if classes_file.exists():
                with open(classes_file, "r", encoding="utf-8") as f:
                    for line in f:
                        class_pattern = line.strip()
                        if class_pattern and not class_pattern.startswith("#"):
                            classes.add(class_pattern)
            else:
                # Default ad class patterns
                classes.update(
                    [
                        "com/google/ads",
                        "com/google/android/gms/ads",
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
                )

        except Exception as e:
            self.logger.error(f"Error loading ad classes: {e}")

        self.logger.info(f"Loaded {len(classes)} ad class patterns")
        return classes

    def _patch_ad_domains(self, decompiled_dir: Path) -> int:
        """Replace ad domains in smali files with invalid domains."""
        domains_replaced = 0

        try:
            smali_dir = decompiled_dir / "smali"
            if not smali_dir.exists():
                return 0

            # Find all smali files
            smali_files = list(smali_dir.rglob("*.smali"))

            for smali_file in smali_files:
                try:
                    with open(smali_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content

                    # Replace each known ad domain
                    for domain in self.ad_domains:
                        if domain in content:
                            # Replace with invalid domain of same length
                            invalid_domain = "x" * len(domain)
                            content = content.replace(domain, invalid_domain)
                            domains_replaced += 1
                            self.logger.debug(f"Replaced {domain} in {smali_file.name}")

                    # Write back if changes were made
                    if content != original_content:
                        with open(smali_file, "w", encoding="utf-8") as f:
                            f.write(content)

                except Exception as e:
                    self.logger.error(f"Error processing {smali_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error in domain replacement: {e}")

        self.logger.info(f"Replaced {domains_replaced} ad domain references")
        return domains_replaced

    def _remove_ad_classes(self, decompiled_dir: Path) -> int:
        """Remove ad-related class files."""
        classes_removed = 0

        try:
            smali_dir = decompiled_dir / "smali"
            if not smali_dir.exists():
                return 0

            # Find directories matching ad class patterns
            for class_pattern in self.ad_classes:
                class_path = smali_dir / class_pattern
                if class_path.exists() and class_path.is_dir():
                    try:
                        shutil.rmtree(class_path)
                        classes_removed += 1
                        self.logger.info(f"Removed ad class directory: {class_pattern}")
                    except Exception as e:
                        self.logger.error(f"Error removing {class_path}: {e}")

                # Also check for individual class files
                class_file = smali_dir / f"{class_pattern}.smali"
                if class_file.exists():
                    try:
                        class_file.unlink()
                        classes_removed += 1
                        self.logger.info(f"Removed ad class file: {class_pattern}.smali")
                    except Exception as e:
                        self.logger.error(f"Error removing {class_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error in class removal: {e}")

        self.logger.info(f"Removed {classes_removed} ad-related classes")
        return classes_removed

    def _clean_manifest(self, decompiled_dir: Path) -> int:
        """Remove ad-related permissions and components from AndroidManifest.xml."""
        permissions_removed = 0

        try:
            manifest_path = decompiled_dir / "AndroidManifest.xml"
            if not manifest_path.exists():
                return 0

            # Parse manifest
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Ad-related permissions to remove
            ad_permissions = [
                "com.google.android.gms.permission.AD_ID",
                "android.permission.ACCESS_NETWORK_STATE",  # Often used by ads (but be careful)
                "com.android.vending.BILLING",  # In-app purchases (be careful)
            ]

            # Remove ad-related permissions (be conservative)
            for perm_elem in root.findall("uses-permission"):
                perm_name = perm_elem.get("{http://schemas.android.com/apk/res/android}name", "")
                if any(ad_perm in perm_name for ad_perm in ["AD_ID"]):  # Only remove clearly ad-related
                    root.remove(perm_elem)
                    permissions_removed += 1
                    self.logger.info(f"Removed permission: {perm_name}")

            # Remove ad-related activities, services, receivers
            app_elem = root.find("application")
            if app_elem is not None:
                for component_type in ["activity", "service", "receiver"]:
                    for component in app_elem.findall(component_type):
                        name = component.get("{http://schemas.android.com/apk/res/android}name", "")
                        if any(ad_class in name.lower() for ad_class in ["ads", "admob", "doubleclick"]):
                            app_elem.remove(component)
                            self.logger.info(f"Removed {component_type}: {name}")

            # Write back the modified manifest
            tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

        except Exception as e:
            self.logger.error(f"Error cleaning manifest: {e}")

        self.logger.info(f"Removed {permissions_removed} ad-related manifest entries")
        return permissions_removed

    def _clean_resources(self, decompiled_dir: Path) -> int:
        """Remove ad-related resources and update public.xml."""
        resources_removed = 0

        try:
            res_dir = decompiled_dir / "res"
            if not res_dir.exists():
                return 0

            # Track removed resources for public.xml cleanup
            removed_resources = []

            # Ad-related resource patterns (more conservative)
            ad_resource_patterns = [
                "*native_ad*", "*banner_ad*", "*interstitial_ad*", 
                "*admob*", "*doubleclick*", "*google_ads*",
                "*unity_ads*", "*facebook_ads*", "*ad_unit*"
            ]

            # Remove ad-related layout files
            layout_dirs = [d for d in res_dir.iterdir() if d.is_dir() and d.name.startswith("layout")]
            for layout_dir in layout_dirs:
                for pattern in ad_resource_patterns:
                    for layout_file in layout_dir.glob(f"{pattern}.xml"):
                        try:
                            # Track the resource name for public.xml cleanup
                            resource_name = layout_file.stem
                            removed_resources.append(("layout", resource_name))
                            
                            layout_file.unlink()
                            resources_removed += 1
                            self.logger.info(f"Removed layout: {layout_file.name}")
                        except Exception as e:
                            self.logger.error(f"Error removing {layout_file}: {e}")

            # Remove ad-related drawable resources
            drawable_dirs = [d for d in res_dir.iterdir() if d.is_dir() and d.name.startswith("drawable")]
            for drawable_dir in drawable_dirs:
                for pattern in ad_resource_patterns:
                    for drawable_file in drawable_dir.glob(f"{pattern}.*"):
                        try:
                            # Track the resource name for public.xml cleanup
                            resource_name = drawable_file.stem
                            removed_resources.append(("drawable", resource_name))
                            
                            drawable_file.unlink()
                            resources_removed += 1
                            self.logger.info(f"Removed drawable: {drawable_file.name}")
                        except Exception as e:
                            self.logger.error(f"Error removing {drawable_file}: {e}")

            # Clean up public.xml references
            if removed_resources:
                self._clean_public_xml(res_dir, removed_resources)

        except Exception as e:
            self.logger.error(f"Error cleaning resources: {e}")

        self.logger.info(f"Removed {resources_removed} ad-related resources")
        return resources_removed

    def _clean_public_xml(self, res_dir: Path, removed_resources: List[Tuple[str, str]]) -> None:
        """Remove references to deleted resources from public.xml files."""
        try:
            # Find all public.xml files (can be in values, values-v21, etc.)
            values_dirs = [d for d in res_dir.iterdir() if d.is_dir() and d.name.startswith("values")]
            
            for values_dir in values_dirs:
                public_xml = values_dir / "public.xml"
                if not public_xml.exists():
                    continue
                
                try:
                    # Read the public.xml file
                    with open(public_xml, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    lines_removed = 0
                    
                    # Remove lines that reference deleted resources
                    lines = content.split('\n')
                    filtered_lines = []
                    
                    for line in lines:
                        should_remove = False
                        
                        for resource_type, resource_name in removed_resources:
                            # Check if this line declares a removed resource
                            if (f'type="{resource_type}"' in line and 
                                f'name="{resource_name}"' in line):
                                should_remove = True
                                lines_removed += 1
                                self.logger.info(f"Removed public.xml entry: {resource_type}/{resource_name}")
                                break
                        
                        if not should_remove:
                            filtered_lines.append(line)
                    
                    # Write back if changes were made
                    if lines_removed > 0:
                        new_content = '\n'.join(filtered_lines)
                        with open(public_xml, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        self.logger.info(f"Updated {public_xml} - removed {lines_removed} entries")
                
                except Exception as e:
                    self.logger.error(f"Error processing {public_xml}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning public.xml files: {e}")

    def add_custom_domain(self, domain: str) -> None:
        """Add a custom ad domain to the list."""
        self.ad_domains.add(domain)
        self.logger.info(f"Added custom ad domain: {domain}")

    def add_custom_class_pattern(self, pattern: str) -> None:
        """Add a custom ad class pattern to the list."""
        self.ad_classes.add(pattern)
        self.logger.info(f"Added custom ad class pattern: {pattern}")

    def get_ad_domains(self) -> Set[str]:
        """Get the current list of ad domains."""
        return self.ad_domains.copy()

    def get_ad_classes(self) -> Set[str]:
        """Get the current list of ad class patterns."""
        return self.ad_classes.copy()
