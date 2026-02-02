#!/usr/bin/env python3
"""
APK Purifier - Command Line Interface
Provides CLI access to APK purification functionality.

Author: Krishnendu Paul
Website: https://krishnendu.com
GitHub: https://github.com/bidhata/APK-Purifier
Email: me@krishnendu.com
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.apk_analyzer import APKAnalyzer
from core.ad_patcher import AdPatcher
from core.malware_scanner import MalwareScanner
from core.apk_signer import APKSigner
from core.utils import validate_apk_file, create_backup, setup_logging


def setup_cli_logging(verbose: bool = False):
    """Setup logging for CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def analyze_command(args):
    """Handle analyze command."""
    apk_path = Path(args.apk)

    if not validate_apk_file(apk_path):
        print(f"Error: {apk_path} is not a valid APK file")
        return 1

    print(f"Analyzing APK: {apk_path}")

    analyzer = APKAnalyzer()
    analysis = analyzer.analyze_apk(apk_path)

    if "error" in analysis:
        print(f"Analysis failed: {analysis['error']}")
        return 1

    # Display analysis results
    print(f"\nAPK Analysis Results:")
    print(f"File size: {analysis['file_size']:,} bytes")
    print(f"DEX files: {len(analysis.get('dex_files', []))}")
    print(f"Resources: {len(analysis.get('resources', []))}")

    manifest = analysis.get("manifest", {})
    if manifest:
        print(f"Package: {manifest.get('package', 'Unknown')}")
        print(f"Version: {manifest.get('version_name', 'Unknown')}")
        print(f"Permissions: {len(manifest.get('permissions', []))}")
        print(f"Activities: {len(manifest.get('activities', []))}")

    return 0


def scan_command(args):
    """Handle scan command."""
    apk_path = Path(args.apk)

    if not validate_apk_file(apk_path):
        print(f"Error: {apk_path} is not a valid APK file")
        return 1

    print(f"Scanning APK for malware: {apk_path}")

    analyzer = APKAnalyzer()
    scanner = MalwareScanner()

    # Decompile APK
    decompiled_dir = analyzer.decompile_apk(apk_path)
    if not decompiled_dir:
        print("Error: Failed to decompile APK")
        return 1

    # Scan for malware
    scan_results = scanner.scan_apk(decompiled_dir)

    print(f"\nMalware Scan Results:")
    print(f"Risk Level: {scan_results.get('risk_level', 'UNKNOWN')}")
    print(f"Threats Found: {len(scan_results.get('threats_found', []))}")
    print(f"Suspicious Permissions: {len(scan_results.get('suspicious_permissions', []))}")
    print(f"Obfuscation Detected: {scan_results.get('obfuscation_detected', False)}")

    # Display threats
    threats = scan_results.get("threats_found", [])
    if threats:
        print(f"\nDetected Threats:")
        for threat in threats[:10]:  # Show first 10
            print(f"  - {threat.get('type', 'Unknown')}: {threat.get('description', 'No description')}")

    # Display recommendations
    recommendations = scan_results.get("recommendations", [])
    if recommendations:
        print(f"\nRecommendations:")
        for rec in recommendations:
            print(f"  - {rec}")

    return 0


def purify_command(args):
    """Handle purify command."""
    apk_path = Path(args.apk)
    output_path = Path(args.output) if args.output else apk_path.parent / f"{apk_path.stem}_purified.apk"

    if not validate_apk_file(apk_path):
        print(f"Error: {apk_path} is not a valid APK file")
        return 1

    print(f"Purifying APK: {apk_path}")

    # Create backup if requested
    if args.backup:
        backup_path = create_backup(apk_path)
        print(f"Backup created: {backup_path}")

    analyzer = APKAnalyzer()
    ad_patcher = AdPatcher()
    scanner = MalwareScanner()
    signer = APKSigner()

    try:
        # Decompile APK
        print("Decompiling APK...")
        decompiled_dir = analyzer.decompile_apk(apk_path)
        if not decompiled_dir:
            print("Error: Failed to decompile APK")
            return 1

        # Scan for malware if requested
        if args.scan_malware:
            print("Scanning for malware...")
            scan_results = scanner.scan_apk(decompiled_dir)
            risk_level = scan_results.get("risk_level", "LOW")

            if risk_level in ["CRITICAL", "HIGH"] and not args.force:
                print(f"Error: High risk malware detected ({risk_level}). Use --force to continue.")
                return 1

        # Apply ad removal patches
        print("Removing advertisements...")
        patch_methods = []
        if args.domain_replacement:
            patch_methods.append("domain_replacement")
        if args.class_removal:
            patch_methods.append("class_removal")
        if args.manifest_cleanup:
            patch_methods.append("manifest_cleanup")
        if args.resource_cleanup:
            patch_methods.append("resource_cleanup")

        if not patch_methods:
            patch_methods = ["domain_replacement", "class_removal", "manifest_cleanup", "resource_cleanup"]

        patch_results = ad_patcher.patch_apk(decompiled_dir, patch_methods)

        print(f"Purification results:")
        print(f"  - Domains replaced: {patch_results.get('domains_replaced', 0)}")
        print(f"  - Classes removed: {patch_results.get('classes_removed', 0)}")
        print(f"  - Permissions removed: {patch_results.get('permissions_removed', 0)}")
        print(f"  - Resources removed: {patch_results.get('resources_removed', 0)}")

        # Recompile APK
        print("Recompiling APK...")
        recompiled_apk = analyzer.recompile_apk(decompiled_dir, output_path)
        if not recompiled_apk:
            print("Error: Failed to recompile APK")
            return 1

        # Sign APK if requested
        if args.sign:
            print("Signing APK...")
            signed_path = output_path.parent / f"{output_path.stem}_signed.apk"
            signed_apk = signer.sign_apk(recompiled_apk, signed_path)

            if signed_apk:
                # Remove unsigned version
                if recompiled_apk.exists():
                    recompiled_apk.unlink()
                output_path = signed_apk
                print(f"APK signed successfully")
            else:
                print("Warning: Failed to sign APK, keeping unsigned version")

        print(f"\nPurification completed successfully!")
        print(f"Output APK: {output_path}")

        return 0

    except Exception as e:
        print(f"Error during purification: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="APK Purifier - Remove ads and malware from Android APK files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze app.apk                    # Analyze APK file
  %(prog)s scan app.apk                       # Scan for malware
  %(prog)s purify app.apk                     # Purify APK (remove ads)
  %(prog)s purify app.apk -o clean_app.apk    # Purify with custom output
  %(prog)s purify app.apk --sign --backup     # Purify, sign, and backup

Author: Krishnendu Paul (https://krishnendu.com)
GitHub: https://github.com/bidhata/APK-Purifier
        """,
    )

    parser.add_argument("--version", action="version", version="APK Purifier 1.0.0")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze APK file")
    analyze_parser.add_argument("apk", help="Path to APK file")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan APK for malware")
    scan_parser.add_argument("apk", help="Path to APK file")

    # Purify command
    purify_parser = subparsers.add_parser("purify", help="Purify APK (remove ads and malware)")
    purify_parser.add_argument("apk", help="Path to APK file")
    purify_parser.add_argument("-o", "--output", help="Output APK path")
    purify_parser.add_argument("--backup", action="store_true", help="Create backup of original APK")
    purify_parser.add_argument("--sign", action="store_true", help="Sign the purified APK")
    purify_parser.add_argument("--scan-malware", action="store_true", help="Scan for malware before purifying")
    purify_parser.add_argument("--force", action="store_true", help="Force purification even if malware detected")

    # Purification method options
    purify_parser.add_argument("--domain-replacement", action="store_true", help="Replace ad domains")
    purify_parser.add_argument("--class-removal", action="store_true", help="Remove ad classes")
    purify_parser.add_argument("--manifest-cleanup", action="store_true", help="Clean manifest")
    purify_parser.add_argument("--resource-cleanup", action="store_true", help="Clean resources")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logging
    setup_cli_logging(args.verbose)

    # Execute command
    if args.command == "analyze":
        return analyze_command(args)
    elif args.command == "scan":
        return scan_command(args)
    elif args.command == "purify":
        return purify_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())