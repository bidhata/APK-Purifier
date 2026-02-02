"""
Main GUI Window for APK Patcher Desktop
"""

import logging
import sys
import shutil
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QProgressBar,
    QFileDialog,
    QCheckBox,
    QGroupBox,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QStatusBar,
    QMenuBar,
    QMenu,
    QSplitter,
    QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.progress_dialog import ProgressDialog
from gui.settings_dialog import SettingsDialog
from core.apk_analyzer import APKAnalyzer
from core.ad_patcher import AdPatcher
from core.malware_scanner import MalwareScanner
from core.apk_signer import APKSigner
from core.utils import validate_apk_file, format_file_size, create_backup


class GuiLogHandler(logging.Handler):
    """Custom logging handler to display logs in GUI."""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        """Emit log record to text widget."""
        try:
            msg = self.format(record)
            # Use Qt's thread-safe method to append text
            self.text_widget.append(msg)
        except Exception:
            pass  # Ignore errors in logging


class PatchingWorker(QThread):
    """Worker thread for APK patching operations."""

    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, apk_files: List[Path], patch_options: dict):
        super().__init__()
        self.apk_files = apk_files
        self.patch_options = patch_options
        self.logger = logging.getLogger(__name__)
        self._is_cancelled = False

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        self.log_message.emit("Cancellation requested...")

    def run(self):
        """Run the patching process."""
        try:
            # Initialize components with error handling
            try:
                analyzer = APKAnalyzer()
                ad_patcher = AdPatcher()
                malware_scanner = MalwareScanner()
                signer = APKSigner()
            except Exception as e:
                self.error_occurred.emit(f"Failed to initialize components: {e}")
                return

            results = {"processed_files": [], "total_files": len(self.apk_files), "successful": 0, "failed": 0}

            for i, apk_file in enumerate(self.apk_files):
                if self._is_cancelled:
                    self.log_message.emit("Operation cancelled by user")
                    break
                    
                try:
                    self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Processing {apk_file.name}...")
                    self.log_message.emit(f"Starting processing of {apk_file.name}")

                    file_result = {
                        "file": str(apk_file),
                        "success": False,
                        "output_file": None,
                        "backup_file": None,
                        "analysis": {},
                        "patches_applied": {},
                        "malware_scan": {},
                        "error": None,
                    }

                    # Create backup if requested
                    if self.patch_options.get("create_backup", True):
                        if self._is_cancelled:
                            break
                        self.progress_updated.emit(
                            int((i / len(self.apk_files)) * 100), f"Creating backup of {apk_file.name}..."
                        )
                        self.log_message.emit(f"Creating backup of {apk_file.name}")
                        backup_file = create_backup(apk_file)
                        file_result["backup_file"] = str(backup_file)

                    # Analyze APK
                    self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Analyzing {apk_file.name}...")
                    analysis = analyzer.analyze_apk(apk_file)
                    file_result["analysis"] = analysis

                    # Decompile APK
                    self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Decompiling {apk_file.name}...")
                    
                    decompiled_dir = None
                    decompiler_used = "APKTool"
                    
                    # For patching operations, we need APKTool for recompilation
                    # JADX is only used for analysis when no patching is required
                    needs_recompilation = self.patch_options.get("remove_ads", False)
                    
                    if needs_recompilation:
                        # Always use APKTool when recompilation is needed
                        self.log_message.emit(f"Using APKTool for {apk_file.name} (recompilation required)")
                        decompiled_dir = analyzer.decompile_apk(apk_file)
                        decompiler_used = "APKTool"
                        
                        # Fallback to JADX only for analysis if APKTool fails
                        if not decompiled_dir and self.patch_options.get("use_jadx_fallback", True) and analyzer.is_jadx_available():
                            self.log_message.emit(f"APKTool failed, using JADX for analysis only (no patching) for {apk_file.name}")
                            decompiled_dir = analyzer.decompile_with_jadx(apk_file)
                            decompiler_used = "JADX"
                            # Disable patching since JADX can't recompile
                            self.log_message.emit(f"Patching disabled for {apk_file.name} - JADX cannot recompile")
                            needs_recompilation = False
                    else:
                        # For analysis-only, can use preferred decompiler
                        if self.patch_options.get("prefer_jadx", False) and analyzer.is_jadx_available():
                            self.log_message.emit(f"Using JADX for analysis of {apk_file.name}")
                            decompiled_dir = analyzer.decompile_with_jadx(apk_file)
                            decompiler_used = "JADX"
                            
                            # Fallback to APKTool if JADX fails
                            if not decompiled_dir:
                                self.log_message.emit(f"JADX failed, falling back to APKTool for {apk_file.name}")
                                decompiled_dir = analyzer.decompile_apk(apk_file)
                                decompiler_used = "APKTool"
                        else:
                            # Use APKTool as primary
                            decompiled_dir = analyzer.decompile_apk(apk_file)
                            
                            # Fallback to JADX if enabled and APKTool fails
                            if not decompiled_dir and self.patch_options.get("use_jadx_fallback", True) and analyzer.is_jadx_available():
                                self.log_message.emit(f"APKTool failed, trying JADX fallback for {apk_file.name}")
                                decompiled_dir = analyzer.decompile_with_jadx(apk_file)
                                decompiler_used = "JADX"

                    if not decompiled_dir:
                        available_decompilers = ["APKTool"]
                        if analyzer.is_jadx_available():
                            available_decompilers.append("JADX")
                        
                        error_msg = f"Failed to decompile APK with available decompilers: {', '.join(available_decompilers)}"
                        raise Exception(error_msg)
                    
                    self.log_message.emit(f"Successfully decompiled {apk_file.name} using {decompiler_used}")
                    file_result["decompiler_used"] = decompiler_used

                    # Malware scan if requested
                    if self.patch_options.get("scan_malware", False):
                        self.progress_updated.emit(
                            int((i / len(self.apk_files)) * 100), f"Scanning for malware in {apk_file.name}..."
                        )
                        malware_results = malware_scanner.scan_apk(decompiled_dir)
                        file_result["malware_scan"] = malware_results

                        # Check if we should continue based on risk level
                        risk_level = malware_results.get("risk_level", "LOW")
                        if risk_level in ["CRITICAL", "HIGH"] and not self.patch_options.get("force_patch", False):
                            raise Exception(f"High risk malware detected ({risk_level}). Skipping patch.")

                    # Apply patches if requested and possible
                    if needs_recompilation and self.patch_options.get("remove_ads", False):
                        self.progress_updated.emit(
                            int((i / len(self.apk_files)) * 100), f"Removing ads from {apk_file.name}..."
                        )

                        patch_methods = []
                        if self.patch_options.get("domain_replacement", True):
                            patch_methods.append("domain_replacement")
                        if self.patch_options.get("class_removal", True):
                            patch_methods.append("class_removal")
                        if self.patch_options.get("manifest_cleanup", True):
                            patch_methods.append("manifest_cleanup")
                        if self.patch_options.get("resource_cleanup", True):
                            patch_methods.append("resource_cleanup")

                        patch_results = ad_patcher.patch_apk(decompiled_dir, patch_methods)
                        file_result["patches_applied"] = patch_results
                    elif self.patch_options.get("remove_ads", False) and not needs_recompilation:
                        self.log_message.emit(f"Skipping patching for {apk_file.name} - JADX decompilation cannot be recompiled")
                        file_result["patches_applied"] = {"skipped": "JADX decompilation cannot be recompiled"}

                    # Recompile APK if patching was done
                    if needs_recompilation:
                        self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Recompiling {apk_file.name}...")

                        output_name = f"{apk_file.stem}_patched.apk"
                        output_path = apk_file.parent / output_name

                        # Since we ensured APKTool was used for patching, we can recompile directly
                        recompiled_apk = analyzer.recompile_apk(decompiled_dir, output_path)

                        if not recompiled_apk:
                            # Try simple recompilation as fallback
                            self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Retrying recompilation for {apk_file.name}...")
                            recompiled_apk = analyzer.recompile_apk_simple(decompiled_dir, output_path)
                            
                            if not recompiled_apk:
                                error_details = f"APK recompilation failed for {apk_file.name}. "
                                error_details += "This could be due to:\n"
                                error_details += "• Complex APK structure or obfuscation\n"
                                error_details += "• Resource conflicts or invalid resources\n"
                                error_details += "• AAPT compilation errors\n"
                                error_details += "• Insufficient system resources\n\n"
                                error_details += "Try using a simpler APK or check the logs for detailed error information."
                                raise Exception(error_details)
                    else:
                        # No recompilation needed (analysis only)
                        self.log_message.emit(f"Analysis completed for {apk_file.name} - no recompilation performed")
                        recompiled_apk = None

                    # Sign APK if requested and recompilation was done
                    if recompiled_apk and self.patch_options.get("sign_apk", True):
                        self.progress_updated.emit(int((i / len(self.apk_files)) * 100), f"Signing {apk_file.name}...")

                        signed_name = f"{apk_file.stem}_patched_signed.apk"
                        signed_path = apk_file.parent / signed_name

                        signed_apk = signer.sign_apk(recompiled_apk, signed_path)

                        if signed_apk:
                            file_result["output_file"] = str(signed_apk)
                            self.log_message.emit(f"Successfully created signed APK: {signed_apk.name}")
                        else:
                            file_result["output_file"] = str(recompiled_apk)
                            self.log_message.emit(f"Signing failed, using unsigned APK: {recompiled_apk.name}")
                    elif recompiled_apk:
                        # No signing requested
                        file_result["output_file"] = str(recompiled_apk)
                        self.log_message.emit(f"Successfully created patched APK: {recompiled_apk.name}")
                    else:
                        # Analysis only, no output APK
                        file_result["output_file"] = None
                        self.log_message.emit(f"Analysis completed for {apk_file.name} - no output APK generated")

                    file_result["success"] = True
                    results["successful"] += 1

                except Exception as e:
                    error_msg = str(e)
                    self.logger.error(f"Error processing {apk_file}: {error_msg}")
                    self.log_message.emit(f"Error processing {apk_file.name}: {error_msg}")
                    
                    file_result["success"] = False
                    file_result["error"] = error_msg
                    results["failed"] += 1
                    
                    # Clean up any temporary files on error
                    try:
                        if 'decompiled_dir' in locals() and decompiled_dir and decompiled_dir.exists():
                            shutil.rmtree(decompiled_dir, ignore_errors=True)
                    except Exception as cleanup_error:
                        self.logger.warning(f"Error cleaning up temporary files: {cleanup_error}")

                results["processed_files"].append(file_result)

            self.progress_updated.emit(100, "Patching completed!")
            self.finished.emit(results)

        except Exception as e:
            self.logger.error(f"Fatal error in patching worker: {e}")
            self.error_occurred.emit(f"Fatal error: {str(e)}")
            
            # Emergency cleanup
            try:
                import gc
                gc.collect()  # Force garbage collection
            except Exception:
                pass


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.apk_files = []
        self.patching_worker = None

        self.init_ui()
        self.setup_connections()
        self.check_tool_availability()
        
    def setup_logging_handler(self):
        """Setup logging handler to display logs in GUI."""
        # Create custom handler for GUI
        gui_handler = GuiLogHandler(self.logs_text)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(gui_handler)
        
        # Also add to specific loggers
        for logger_name in ['__main__', 'core.apk_analyzer', 'core.ad_patcher', 'core.malware_scanner', 'core.apk_signer']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(gui_handler)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("APK Purifier v1.0.0")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - File selection and options
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Results and logs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([400, 800])

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_left_panel(self) -> QWidget:
        """Create the left panel with file selection and options."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File selection group
        file_group = QGroupBox("APK Files")
        file_layout = QVBoxLayout(file_group)

        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        file_layout.addWidget(self.file_list)

        # File buttons
        file_buttons = QHBoxLayout()

        self.add_files_btn = QPushButton("Add APK Files")
        self.add_files_btn.clicked.connect(self.add_apk_files)
        file_buttons.addWidget(self.add_files_btn)

        self.remove_files_btn = QPushButton("Remove Selected")
        self.remove_files_btn.clicked.connect(self.remove_selected_files)
        file_buttons.addWidget(self.remove_files_btn)

        self.clear_files_btn = QPushButton("Clear All")
        self.clear_files_btn.clicked.connect(self.clear_all_files)
        file_buttons.addWidget(self.clear_files_btn)

        file_layout.addLayout(file_buttons)
        layout.addWidget(file_group)

        # Patching options group
        options_group = QGroupBox("Patching Options")
        options_layout = QVBoxLayout(options_group)

        # Ad removal options
        self.remove_ads_cb = QCheckBox("Remove Advertisements")
        self.remove_ads_cb.setChecked(True)
        options_layout.addWidget(self.remove_ads_cb)

        # Ad removal methods (indented)
        ad_methods_layout = QVBoxLayout()
        ad_methods_layout.setContentsMargins(20, 0, 0, 0)

        self.domain_replacement_cb = QCheckBox("Domain Replacement")
        self.domain_replacement_cb.setChecked(True)
        ad_methods_layout.addWidget(self.domain_replacement_cb)

        self.class_removal_cb = QCheckBox("Ad Class Removal")
        self.class_removal_cb.setChecked(True)
        ad_methods_layout.addWidget(self.class_removal_cb)

        self.manifest_cleanup_cb = QCheckBox("Manifest Cleanup")
        self.manifest_cleanup_cb.setChecked(True)
        ad_methods_layout.addWidget(self.manifest_cleanup_cb)

        self.resource_cleanup_cb = QCheckBox("Resource Cleanup")
        self.resource_cleanup_cb.setChecked(True)
        ad_methods_layout.addWidget(self.resource_cleanup_cb)

        options_layout.addLayout(ad_methods_layout)

        # Malware scanning
        self.scan_malware_cb = QCheckBox("Scan for Malware")
        self.scan_malware_cb.setChecked(True)
        options_layout.addWidget(self.scan_malware_cb)

        # APK signing
        self.sign_apk_cb = QCheckBox("Sign Patched APK")
        self.sign_apk_cb.setChecked(True)
        options_layout.addWidget(self.sign_apk_cb)

        # Backup option
        self.create_backup_cb = QCheckBox("Create Backup")
        self.create_backup_cb.setChecked(True)
        options_layout.addWidget(self.create_backup_cb)

        # Force patch option
        self.force_patch_cb = QCheckBox("Force Patch (ignore malware warnings)")
        self.force_patch_cb.setChecked(False)
        options_layout.addWidget(self.force_patch_cb)

        # Decompiler options
        decompiler_group = QGroupBox("Decompiler Options")
        decompiler_layout = QVBoxLayout(decompiler_group)
        
        self.use_jadx_fallback_cb = QCheckBox("Use JADX as fallback decompiler")
        self.use_jadx_fallback_cb.setChecked(True)
        self.use_jadx_fallback_cb.setToolTip("Use JADX decompiler if APKTool fails (analysis only if patching enabled)")
        decompiler_layout.addWidget(self.use_jadx_fallback_cb)
        
        self.prefer_jadx_cb = QCheckBox("Prefer JADX for analysis-only operations")
        self.prefer_jadx_cb.setChecked(False)
        self.prefer_jadx_cb.setToolTip("Use JADX as primary decompiler for analysis when no patching is needed")
        decompiler_layout.addWidget(self.prefer_jadx_cb)
        
        options_layout.addWidget(decompiler_group)

        layout.addWidget(options_group)

        # Action buttons
        action_layout = QVBoxLayout()

        self.start_patching_btn = QPushButton("Start Patching")
        self.start_patching_btn.clicked.connect(self.start_patching)
        self.start_patching_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        action_layout.addWidget(self.start_patching_btn)

        self.stop_patching_btn = QPushButton("Stop Patching")
        self.stop_patching_btn.clicked.connect(self.stop_patching)
        self.stop_patching_btn.setEnabled(False)
        self.stop_patching_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        action_layout.addWidget(self.stop_patching_btn)

        layout.addLayout(action_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        layout.addStretch()

        return panel

    def check_tool_availability(self):
        """Check availability of tools and update UI accordingly."""
        try:
            from core.apk_analyzer import APKAnalyzer
            analyzer = APKAnalyzer()
            
            # Check JADX availability
            if not analyzer.is_jadx_available():
                self.use_jadx_fallback_cb.setEnabled(False)
                self.use_jadx_fallback_cb.setToolTip("JADX not available - download tools first")
                self.prefer_jadx_cb.setEnabled(False)
                self.prefer_jadx_cb.setToolTip("JADX not available - download tools first")
                self.status_bar.showMessage("JADX not available - some features disabled")
            else:
                self.status_bar.showMessage("All tools available - Ready")
                
        except Exception as e:
            self.logger.error(f"Error checking tool availability: {e}")

    def create_right_panel(self) -> QWidget:
        """Create the right panel with results and logs."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Results tab
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.results_text, "Results")

        # Logs tab
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Consolas", 9))
        self.tab_widget.addTab(self.logs_text, "Logs")
        
        # Setup logging handler to display logs in GUI
        self.setup_logging_handler()

        return panel

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        add_files_action = QAction("Add APK Files", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self.add_apk_files)
        file_menu.addAction(add_files_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_connections(self):
        """Setup signal connections."""
        # Connect remove ads checkbox to enable/disable sub-options
        self.remove_ads_cb.toggled.connect(self.toggle_ad_removal_options)

    def toggle_ad_removal_options(self, enabled: bool):
        """Enable/disable ad removal sub-options."""
        self.domain_replacement_cb.setEnabled(enabled)
        self.class_removal_cb.setEnabled(enabled)
        self.manifest_cleanup_cb.setEnabled(enabled)
        self.resource_cleanup_cb.setEnabled(enabled)

    def add_apk_files(self):
        """Add APK files to the list."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select APK Files", "", "APK Files (*.apk);;All Files (*)")

        for file_path in files:
            apk_path = Path(file_path)

            # Validate APK file
            if not validate_apk_file(apk_path):
                QMessageBox.warning(self, "Invalid APK", f"The file {apk_path.name} is not a valid APK file.")
                continue

            # Check if already added
            if apk_path not in self.apk_files:
                self.apk_files.append(apk_path)

                # Add to list widget
                item = QListWidgetItem()
                item.setText(f"{apk_path.name} ({format_file_size(apk_path.stat().st_size)})")
                item.setData(Qt.ItemDataRole.UserRole, str(apk_path))
                self.file_list.addItem(item)

        self.update_ui_state()

    def remove_selected_files(self):
        """Remove selected files from the list."""
        for item in self.file_list.selectedItems():
            file_path = Path(item.data(Qt.ItemDataRole.UserRole))
            if file_path in self.apk_files:
                self.apk_files.remove(file_path)

            row = self.file_list.row(item)
            self.file_list.takeItem(row)

        self.update_ui_state()

    def clear_all_files(self):
        """Clear all files from the list."""
        self.apk_files.clear()
        self.file_list.clear()
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI state based on current conditions."""
        has_files = len(self.apk_files) > 0
        is_patching = self.patching_worker is not None and self.patching_worker.isRunning()

        self.start_patching_btn.setEnabled(has_files and not is_patching)
        self.stop_patching_btn.setEnabled(is_patching)
        self.remove_files_btn.setEnabled(has_files and not is_patching)
        self.clear_files_btn.setEnabled(has_files and not is_patching)

        # Update status bar
        if has_files:
            self.status_bar.showMessage(f"{len(self.apk_files)} APK file(s) selected")
        else:
            self.status_bar.showMessage("Ready")

    def get_patch_options(self) -> dict:
        """Get current patch options from UI."""
        return {
            "remove_ads": self.remove_ads_cb.isChecked(),
            "domain_replacement": self.domain_replacement_cb.isChecked(),
            "class_removal": self.class_removal_cb.isChecked(),
            "manifest_cleanup": self.manifest_cleanup_cb.isChecked(),
            "resource_cleanup": self.resource_cleanup_cb.isChecked(),
            "scan_malware": self.scan_malware_cb.isChecked(),
            "sign_apk": self.sign_apk_cb.isChecked(),
            "create_backup": self.create_backup_cb.isChecked(),
            "force_patch": self.force_patch_cb.isChecked(),
            "use_jadx_fallback": self.use_jadx_fallback_cb.isChecked(),
            "prefer_jadx": self.prefer_jadx_cb.isChecked(),
        }

    def start_patching(self):
        """Start the patching process."""
        if not self.apk_files:
            QMessageBox.warning(self, "No Files", "Please select APK files to patch.")
            return

        # Get patch options
        patch_options = self.get_patch_options()

        # Clear previous results
        self.results_text.clear()
        self.logs_text.clear()
        
        # Add initial log message
        self.logger.info("=== Starting APK Purification Process ===")
        self.logger.info(f"Processing {len(self.apk_files)} APK file(s)")
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start worker thread
        self.patching_worker = PatchingWorker(self.apk_files.copy(), patch_options)
        self.patching_worker.progress_updated.connect(self.update_progress)
        self.patching_worker.finished.connect(self.patching_finished)
        self.patching_worker.error_occurred.connect(self.patching_error)
        self.patching_worker.log_message.connect(self.add_log_message)
        self.patching_worker.start()

        self.update_ui_state()
        self.status_bar.showMessage("Patching in progress...")

    def stop_patching(self):
        """Stop the patching process."""
        if self.patching_worker and self.patching_worker.isRunning():
            self.add_log_message("Stopping patching process...")
            self.patching_worker.cancel()
            
            # Give the worker some time to stop gracefully
            if not self.patching_worker.wait(5000):  # Wait 5 seconds
                self.add_log_message("Force terminating patching process...")
                self.patching_worker.terminate()
                self.patching_worker.wait()

            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)

            self.update_ui_state()
            self.status_bar.showMessage("Patching stopped")
            
    def add_log_message(self, message: str):
        """Add a log message to the logs tab."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.logs_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_progress(self, value: int, message: str):
        """Update progress bar and message."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_bar.showMessage(message)

    def patching_finished(self, results: dict):
        """Handle patching completion."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        # Display results
        self.display_results(results)

        self.update_ui_state()

        # Show completion message
        successful = results.get("successful", 0)
        failed = results.get("failed", 0)
        total = results.get("total_files", 0)

        message = f"Purification completed: {successful} successful, {failed} failed out of {total} files"
        self.status_bar.showMessage(message)

        QMessageBox.information(self, "Purification Complete", message)

    def patching_error(self, error_message: str):
        """Handle patching error."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        self.update_ui_state()
        self.status_bar.showMessage("Patching failed")

        QMessageBox.critical(self, "Purification Error", f"An error occurred during purification:\n\n{error_message}")

    def display_results(self, results: dict):
        """Display patching results."""
        output = []
        output.append("=== APK PURIFICATION RESULTS ===\n")

        successful = results.get("successful", 0)
        failed = results.get("failed", 0)
        total = results.get("total_files", 0)

        output.append(f"Total files processed: {total}")
        output.append(f"Successful: {successful}")
        output.append(f"Failed: {failed}")
        output.append("")

        for file_result in results.get("processed_files", []):
            file_path = file_result.get("file", "Unknown")
            file_name = Path(file_path).name
            success = file_result.get("success", False)

            output.append(f"{'✓' if success else '✗'} {file_name}")

            if success:
                output_file = file_result.get("output_file")
                if output_file:
                    output.append(f"  → Output: {Path(output_file).name}")

                backup_file = file_result.get("backup_file")
                if backup_file:
                    output.append(f"  → Backup: {Path(backup_file).name}")

                # Patch results
                patches = file_result.get("patches_applied", {})
                if patches:
                    output.append("  → Purification applied:")
                    for method in patches.get("methods_applied", []):
                        output.append(f"    • {method}")

                    domains = patches.get("domains_replaced", 0)
                    classes = patches.get("classes_removed", 0)
                    permissions = patches.get("permissions_removed", 0)
                    resources = patches.get("resources_removed", 0)

                    if domains > 0:
                        output.append(f"    • {domains} ad domains replaced")
                    if classes > 0:
                        output.append(f"    • {classes} ad classes removed")
                    if permissions > 0:
                        output.append(f"    • {permissions} permissions removed")
                    if resources > 0:
                        output.append(f"    • {resources} resources removed")

                # Malware scan results
                malware = file_result.get("malware_scan", {})
                if malware:
                    risk_level = malware.get("risk_level", "UNKNOWN")
                    threats = len(malware.get("threats_found", []))
                    output.append(f"  → Malware scan: {risk_level} risk ({threats} threats found)")

            else:
                error = file_result.get("error", "Unknown error")
                output.append(f"  → Error: {error}")

            output.append("")

        self.results_text.setPlainText("\n".join(output))
        self.tab_widget.setCurrentIndex(0)  # Switch to results tab

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>APK Purifier v1.0.0</h2>
        <p>A cross-platform desktop application for purifying Android APK files by removing advertisements and basic malware.</p>
        
        <h3>Features:</h3>
        <ul>
        <li>Remove advertisements from APK files</li>
        <li>Basic malware detection and removal</li>
        <li>APK signing and alignment</li>
        <li>Cross-platform support (Windows & Linux)</li>
        <li>Batch processing</li>
        </ul>
        
        <h3>Technology:</h3>
        <p>Built with Python, PyQt6, APKTool, and uber-apk-signer</p>
        
        <h3>Author:</h3>
        <p><b>Krishnendu Paul</b><br>
        Website: <a href="https://krishnendu.com">https://krishnendu.com</a><br>
        GitHub: <a href="https://github.com/bidhata/APK-Purifier">https://github.com/bidhata/APK-Purifier</a><br>
        Email: <a href="mailto:me@krishnendu.com">me@krishnendu.com</a></p>
        
        <p><b>Legal Notice:</b> This tool is for educational and legitimate security research purposes only. Users are responsible for ensuring they have rights to modify the APKs and complying with applicable laws.</p>
        """

        QMessageBox.about(self, "About APK Purifier", about_text)
