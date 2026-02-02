"""
Progress Dialog for APK Patcher Desktop
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Dialog for showing detailed progress information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Purification Progress")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Main progress
        self.main_label = QLabel("Initializing...")
        layout.addWidget(self.main_label)

        self.main_progress = QProgressBar()
        layout.addWidget(self.main_progress)

        # Current file progress
        self.file_label = QLabel("")
        layout.addWidget(self.file_label)

        self.file_progress = QProgressBar()
        layout.addWidget(self.file_progress)

        # Detailed log
        log_label = QLabel("Detailed Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def update_main_progress(self, value: int, text: str = ""):
        """Update main progress bar."""
        self.main_progress.setValue(value)
        if text:
            self.main_label.setText(text)

    def update_file_progress(self, value: int, text: str = ""):
        """Update file progress bar."""
        self.file_progress.setValue(value)
        if text:
            self.file_label.setText(text)

    def add_log_message(self, message: str):
        """Add a message to the log."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_completed(self):
        """Mark the operation as completed."""
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.main_label.setText("Operation completed!")

    def set_error(self, error_message: str):
        """Mark the operation as failed."""
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.main_label.setText(f"Operation failed: {error_message}")
        self.add_log_message(f"ERROR: {error_message}")
