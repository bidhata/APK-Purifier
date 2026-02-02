"""
Settings Dialog for APK Patcher Desktop
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt
from pathlib import Path
import json

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import get_data_dir


class SettingsDialog(QDialog):
    """Settings configuration dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_dir = get_data_dir()
        self.settings_file = self.data_dir / "settings.json"
        self.settings = self.load_settings()

        self.init_ui()
        self.load_ui_values()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_general_tab()
        self.create_patching_tab()
        self.create_signing_tab()
        self.create_advanced_tab()

        # Buttons
        button_layout = QHBoxLayout()

        self.restore_defaults_btn = QPushButton("Restore Defaults")
        self.restore_defaults_btn.clicked.connect(self.restore_defaults)
        button_layout.addWidget(self.restore_defaults_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_settings)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def create_general_tab(self):
        """Create general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Paths group
        paths_group = QGroupBox("Paths")
        paths_layout = QFormLayout(paths_group)

        # Temp directory
        self.temp_dir_edit = QLineEdit()
        temp_browse_btn = QPushButton("Browse")
        temp_browse_btn.clicked.connect(lambda: self.browse_directory(self.temp_dir_edit))

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temp_dir_edit)
        temp_layout.addWidget(temp_browse_btn)

        paths_layout.addRow("Temporary Directory:", temp_layout)

        # Backup directory
        self.backup_dir_edit = QLineEdit()
        backup_browse_btn = QPushButton("Browse")
        backup_browse_btn.clicked.connect(lambda: self.browse_directory(self.backup_dir_edit))

        backup_layout = QHBoxLayout()
        backup_layout.addWidget(self.backup_dir_edit)
        backup_layout.addWidget(backup_browse_btn)

        paths_layout.addRow("Backup Directory:", backup_layout)

        layout.addWidget(paths_group)

        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        self.auto_backup_cb = QCheckBox("Automatically create backups")
        behavior_layout.addWidget(self.auto_backup_cb)

        self.auto_sign_cb = QCheckBox("Automatically sign patched APKs")
        behavior_layout.addWidget(self.auto_sign_cb)

        self.clean_temp_cb = QCheckBox("Clean temporary files after patching")
        behavior_layout.addWidget(self.clean_temp_cb)

        layout.addWidget(behavior_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "General")

    def create_patching_tab(self):
        """Create patching settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Ad domains group
        domains_group = QGroupBox("Ad Domains")
        domains_layout = QVBoxLayout(domains_group)

        domains_label = QLabel("Custom ad domains to block (one per line):")
        domains_layout.addWidget(domains_label)

        self.ad_domains_text = QTextEdit()
        self.ad_domains_text.setMaximumHeight(150)
        domains_layout.addWidget(self.ad_domains_text)

        domains_buttons = QHBoxLayout()

        load_domains_btn = QPushButton("Load from File")
        load_domains_btn.clicked.connect(self.load_ad_domains_file)
        domains_buttons.addWidget(load_domains_btn)

        save_domains_btn = QPushButton("Save to File")
        save_domains_btn.clicked.connect(self.save_ad_domains_file)
        domains_buttons.addWidget(save_domains_btn)

        domains_buttons.addStretch()
        domains_layout.addLayout(domains_buttons)

        layout.addWidget(domains_group)

        # Ad classes group
        classes_group = QGroupBox("Ad Class Patterns")
        classes_layout = QVBoxLayout(classes_group)

        classes_label = QLabel("Custom ad class patterns to remove (one per line):")
        classes_layout.addWidget(classes_label)

        self.ad_classes_text = QTextEdit()
        self.ad_classes_text.setMaximumHeight(150)
        classes_layout.addWidget(self.ad_classes_text)

        layout.addWidget(classes_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Patching")

    def create_signing_tab(self):
        """Create signing settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Keystore group
        keystore_group = QGroupBox("Keystore Settings")
        keystore_layout = QFormLayout(keystore_group)

        # Use custom keystore
        self.use_custom_keystore_cb = QCheckBox("Use custom keystore")
        keystore_layout.addRow(self.use_custom_keystore_cb)

        # Keystore path
        self.keystore_path_edit = QLineEdit()
        keystore_browse_btn = QPushButton("Browse")
        keystore_browse_btn.clicked.connect(
            lambda: self.browse_file(self.keystore_path_edit, "Keystore Files (*.jks *.keystore)")
        )

        keystore_path_layout = QHBoxLayout()
        keystore_path_layout.addWidget(self.keystore_path_edit)
        keystore_path_layout.addWidget(keystore_browse_btn)

        keystore_layout.addRow("Keystore Path:", keystore_path_layout)

        # Keystore password
        self.keystore_password_edit = QLineEdit()
        self.keystore_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        keystore_layout.addRow("Keystore Password:", self.keystore_password_edit)

        # Key alias
        self.key_alias_edit = QLineEdit()
        keystore_layout.addRow("Key Alias:", self.key_alias_edit)

        # Key password
        self.key_password_edit = QLineEdit()
        self.key_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        keystore_layout.addRow("Key Password:", self.key_password_edit)

        layout.addWidget(keystore_group)

        # Signing options group
        signing_group = QGroupBox("Signing Options")
        signing_layout = QVBoxLayout(signing_group)

        self.v1_signature_cb = QCheckBox("Enable v1 signature (JAR signing)")
        signing_layout.addWidget(self.v1_signature_cb)

        self.v2_signature_cb = QCheckBox("Enable v2 signature (APK Signature Scheme v2)")
        signing_layout.addWidget(self.v2_signature_cb)

        self.v3_signature_cb = QCheckBox("Enable v3 signature (APK Signature Scheme v3)")
        signing_layout.addWidget(self.v3_signature_cb)

        layout.addWidget(signing_group)

        # Connect custom keystore checkbox
        self.use_custom_keystore_cb.toggled.connect(self.toggle_custom_keystore)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Signing")

    def create_advanced_tab(self):
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Performance group
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)

        # Timeout settings
        self.decompile_timeout_spin = QSpinBox()
        self.decompile_timeout_spin.setRange(60, 1800)  # 1 minute to 30 minutes
        self.decompile_timeout_spin.setSuffix(" seconds")
        performance_layout.addRow("Decompile Timeout:", self.decompile_timeout_spin)

        self.recompile_timeout_spin = QSpinBox()
        self.recompile_timeout_spin.setRange(60, 1800)
        self.recompile_timeout_spin.setSuffix(" seconds")
        performance_layout.addRow("Recompile Timeout:", self.recompile_timeout_spin)

        self.signing_timeout_spin = QSpinBox()
        self.signing_timeout_spin.setRange(30, 600)  # 30 seconds to 10 minutes
        self.signing_timeout_spin.setSuffix(" seconds")
        performance_layout.addRow("Signing Timeout:", self.signing_timeout_spin)

        layout.addWidget(performance_group)

        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QVBoxLayout(logging_group)

        self.verbose_logging_cb = QCheckBox("Enable verbose logging")
        logging_layout.addWidget(self.verbose_logging_cb)

        self.log_to_file_cb = QCheckBox("Log to file")
        logging_layout.addWidget(self.log_to_file_cb)

        layout.addWidget(logging_group)

        # Tools group
        tools_group = QGroupBox("External Tools")
        tools_layout = QFormLayout(tools_group)

        # Java path
        self.java_path_edit = QLineEdit()
        java_browse_btn = QPushButton("Browse")
        java_browse_btn.clicked.connect(lambda: self.browse_file(self.java_path_edit, "Executable Files (*.exe)"))

        java_layout = QHBoxLayout()
        java_layout.addWidget(self.java_path_edit)
        java_layout.addWidget(java_browse_btn)

        tools_layout.addRow("Java Path (optional):", java_layout)

        layout.addWidget(tools_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Advanced")

    def toggle_custom_keystore(self, enabled: bool):
        """Enable/disable custom keystore fields."""
        self.keystore_path_edit.setEnabled(enabled)
        self.keystore_password_edit.setEnabled(enabled)
        self.key_alias_edit.setEnabled(enabled)
        self.key_password_edit.setEnabled(enabled)

    def browse_directory(self, line_edit: QLineEdit):
        """Browse for directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)

    def browse_file(self, line_edit: QLineEdit, file_filter: str = "All Files (*)"):
        """Browse for file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file_path:
            line_edit.setText(file_path)

    def load_ad_domains_file(self):
        """Load ad domains from file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Ad Domains", "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.ad_domains_text.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file:\n{str(e)}")

    def save_ad_domains_file(self):
        """Save ad domains to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Ad Domains", "ad_domains.txt", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.ad_domains_text.toPlainText())
                QMessageBox.information(self, "Success", "Ad domains saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file:\n{str(e)}")

    def load_settings(self) -> dict:
        """Load settings from file."""
        default_settings = {
            "temp_dir": "",
            "backup_dir": "",
            "auto_backup": True,
            "auto_sign": True,
            "clean_temp": True,
            "ad_domains": [],
            "ad_classes": [],
            "use_custom_keystore": False,
            "keystore_path": "",
            "keystore_password": "",
            "key_alias": "",
            "key_password": "",
            "v1_signature": True,
            "v2_signature": True,
            "v3_signature": False,
            "decompile_timeout": 300,
            "recompile_timeout": 600,
            "signing_timeout": 300,
            "verbose_logging": False,
            "log_to_file": True,
            "java_path": "",
        }

        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self):
        """Save settings to file."""
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings:\n{str(e)}")

    def load_ui_values(self):
        """Load settings values into UI."""
        # General tab
        self.temp_dir_edit.setText(self.settings.get("temp_dir", ""))
        self.backup_dir_edit.setText(self.settings.get("backup_dir", ""))
        self.auto_backup_cb.setChecked(self.settings.get("auto_backup", True))
        self.auto_sign_cb.setChecked(self.settings.get("auto_sign", True))
        self.clean_temp_cb.setChecked(self.settings.get("clean_temp", True))

        # Patching tab
        ad_domains = self.settings.get("ad_domains", [])
        self.ad_domains_text.setPlainText("\n".join(ad_domains))

        ad_classes = self.settings.get("ad_classes", [])
        self.ad_classes_text.setPlainText("\n".join(ad_classes))

        # Signing tab
        self.use_custom_keystore_cb.setChecked(self.settings.get("use_custom_keystore", False))
        self.keystore_path_edit.setText(self.settings.get("keystore_path", ""))
        self.keystore_password_edit.setText(self.settings.get("keystore_password", ""))
        self.key_alias_edit.setText(self.settings.get("key_alias", ""))
        self.key_password_edit.setText(self.settings.get("key_password", ""))
        self.v1_signature_cb.setChecked(self.settings.get("v1_signature", True))
        self.v2_signature_cb.setChecked(self.settings.get("v2_signature", True))
        self.v3_signature_cb.setChecked(self.settings.get("v3_signature", False))

        # Advanced tab
        self.decompile_timeout_spin.setValue(self.settings.get("decompile_timeout", 300))
        self.recompile_timeout_spin.setValue(self.settings.get("recompile_timeout", 600))
        self.signing_timeout_spin.setValue(self.settings.get("signing_timeout", 300))
        self.verbose_logging_cb.setChecked(self.settings.get("verbose_logging", False))
        self.log_to_file_cb.setChecked(self.settings.get("log_to_file", True))
        self.java_path_edit.setText(self.settings.get("java_path", ""))

        # Update UI state
        self.toggle_custom_keystore(self.use_custom_keystore_cb.isChecked())

    def save_ui_values(self):
        """Save UI values to settings."""
        # General tab
        self.settings["temp_dir"] = self.temp_dir_edit.text()
        self.settings["backup_dir"] = self.backup_dir_edit.text()
        self.settings["auto_backup"] = self.auto_backup_cb.isChecked()
        self.settings["auto_sign"] = self.auto_sign_cb.isChecked()
        self.settings["clean_temp"] = self.clean_temp_cb.isChecked()

        # Patching tab
        ad_domains_text = self.ad_domains_text.toPlainText().strip()
        self.settings["ad_domains"] = [line.strip() for line in ad_domains_text.split("\n") if line.strip()]

        ad_classes_text = self.ad_classes_text.toPlainText().strip()
        self.settings["ad_classes"] = [line.strip() for line in ad_classes_text.split("\n") if line.strip()]

        # Signing tab
        self.settings["use_custom_keystore"] = self.use_custom_keystore_cb.isChecked()
        self.settings["keystore_path"] = self.keystore_path_edit.text()
        self.settings["keystore_password"] = self.keystore_password_edit.text()
        self.settings["key_alias"] = self.key_alias_edit.text()
        self.settings["key_password"] = self.key_password_edit.text()
        self.settings["v1_signature"] = self.v1_signature_cb.isChecked()
        self.settings["v2_signature"] = self.v2_signature_cb.isChecked()
        self.settings["v3_signature"] = self.v3_signature_cb.isChecked()

        # Advanced tab
        self.settings["decompile_timeout"] = self.decompile_timeout_spin.value()
        self.settings["recompile_timeout"] = self.recompile_timeout_spin.value()
        self.settings["signing_timeout"] = self.signing_timeout_spin.value()
        self.settings["verbose_logging"] = self.verbose_logging_cb.isChecked()
        self.settings["log_to_file"] = self.log_to_file_cb.isChecked()
        self.settings["java_path"] = self.java_path_edit.text()

    def restore_defaults(self):
        """Restore default settings."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self.load_settings()  # This will load defaults
            self.load_ui_values()

    def accept_settings(self):
        """Accept and save settings."""
        self.save_ui_values()
        self.save_settings()
        self.accept()
