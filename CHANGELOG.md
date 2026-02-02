# Changelog - APK Purifier

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-02-01

### Added
- **JADX Integration**: Added JADX decompiler as alternative/fallback to APKTool
  - Dual decompiler support for better APK compatibility
  - Smart decompiler selection based on operation type
  - Enhanced Java source code analysis capabilities
  - Automatic fallback when primary decompiler fails

- **Enhanced GUI Options**:
  - "Use JADX as fallback decompiler" option (enabled by default)
  - "Prefer JADX for analysis-only operations" option
  - Tool availability detection with UI feedback
  - Improved tooltips explaining decompiler limitations

- **Resource Conflict Resolution**:
  - Automatic public.xml cleanup when removing ad resources
  - Backup and recovery system for critical files
  - Conservative resource pattern matching to avoid false positives
  - Enhanced error handling with automatic recovery

### Fixed
- **Recompilation Issues**: Fixed APK recompilation failures when JADX was used
  - Smart tool selection ensures APKTool is used when recompilation is needed
  - JADX used only for analysis-only operations
  - Clear user feedback about decompiler selection

- **Resource Conflicts**: Resolved "Public symbol declared here is not defined" errors
  - Enhanced ad patcher now updates public.xml when removing resources
  - Maintains resource consistency across all values directories
  - Prevents orphaned resource declarations

- **Application Stability**: Improved error handling and crash prevention
  - Enhanced exception handling in worker threads
  - Automatic cleanup of temporary files on errors
  - Better memory management with garbage collection
  - Comprehensive logging for debugging

### Improved
- **Ad Removal Accuracy**: More precise ad detection and removal
  - Conservative resource patterns to avoid breaking essential components
  - Better manifest cleanup with safer permission removal
  - Enhanced smali code analysis for ad domain replacement

- **User Experience**: Better feedback and error reporting
  - Detailed progress messages during processing
  - Clear error messages with actionable information
  - Status bar updates showing tool availability
  - Improved logging with GUI integration

- **Performance**: Optimized processing for large APKs
  - Dynamic timeout calculation based on APK size
  - Better resource management during processing
  - Efficient temporary file handling

### Technical Details
- **New Components**:
  - `src/core/jadx_analyzer.py`: Complete JADX integration module
  - Enhanced `src/core/apk_analyzer.py` with dual decompiler support
  - Improved `src/core/ad_patcher.py` with resource conflict resolution

- **Enhanced Features**:
  - Cross-platform JADX executable detection
  - Automatic tool availability checking
  - Backup/recovery system for critical files
  - Public.xml management for resource consistency

## [1.0.0] - 2026-01-31

### Initial Release
- **Core Functionality**:
  - APK decompilation using APKTool
  - Advertisement removal with multiple methods
  - Basic malware pattern detection
  - APK signing with uber-apk-signer
  - Cross-platform support (Windows/Linux)

- **GUI Features**:
  - User-friendly desktop interface using PyQt6
  - Batch processing support
  - Progress tracking with detailed feedback
  - Configurable patching options

- **Ad Removal Methods**:
  - Domain replacement in smali code
  - Ad class removal
  - Manifest cleanup (permissions and components)
  - Resource cleanup (layouts and drawables)

- **Security Features**:
  - Basic malware pattern detection
  - Suspicious permission analysis
  - Automatic backup creation
  - Safe APK signing process

### Dependencies
- Python 3.8+
- PyQt6 for GUI
- Java 8+ for external tools
- APKTool for decompilation/recompilation
- uber-apk-signer for APK signing
- JADX for enhanced decompilation (optional)

### Installation
- Automated tool download script
- Comprehensive installation testing
- Cross-platform compatibility
- Detailed setup documentation