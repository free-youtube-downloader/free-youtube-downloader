"""
MP3/Audio Download Page

Provides interface for downloading audio in various formats.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, 
    QFormLayout, QGroupBox, QLabel
)
from PySide6.QtCore import Qt
from ui.base import BaseDownloadPage
from ui.components.animated_button import AnimatedButton
from ui.components.drag_drop_line_edit import DragDropLineEdit
from core.config import config_manager


class AudioPage(BaseDownloadPage):
    """Page for downloading audio in various formats"""
    
    def __init__(self, parent=None):
        self.format_combo = None
        self.quality_combo = None
        super().__init__(parent)
    
    def get_page_title(self) -> str:
        """Get the page title"""
        return "Download Audio"
    
    def create_url_input(self) -> QWidget:
        """Create URL input widget"""
        self.url_input_widget = DragDropLineEdit("Paste or drag a link here...")
        return self.url_input_widget
    
    def init_ui(self):
        """Initialize UI with audio-specific options"""
        # Call parent init_ui first
        super().init_ui()
        
        # Insert audio options before buttons
        audio_options = self.create_audio_options()
        # Insert at position before the last two items (buttons and stretch)
        self.main_layout.insertWidget(self.main_layout.count() - 2, audio_options)
    
    def create_audio_options(self) -> QWidget:
        """Create audio format and quality options"""
        group_box = QGroupBox("Audio Options")
        form_layout = QFormLayout(group_box)
        
        # Audio format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "m4a", "flac", "ogg", "wav"])
        self.format_combo.setCurrentText("mp3")  # Default
        form_layout.addRow("Format:", self.format_combo)
        
        # Audio quality selection
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["64", "96", "128", "192", "256", "320"])
        self.quality_combo.setCurrentText("320")  # Default
        form_layout.addRow("Quality (kbps):", self.quality_combo)
        
        return group_box
    
    def create_download_buttons(self) -> QWidget:
        """Create download action buttons"""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # Single audio download button
        single_btn = AnimatedButton("Download Single Audio")
        single_btn.clicked.connect(lambda: self.handle_single_download())
        
        # Playlist download button
        playlist_btn = AnimatedButton("Download Playlist Audio")
        playlist_btn.clicked.connect(lambda: self.handle_playlist_download())
        
        # Cancel button
        cancel_btn = AnimatedButton("Cancel All")
        cancel_btn.clicked.connect(self.handle_cancel_all)
        
        layout.addWidget(single_btn)
        layout.addWidget(playlist_btn)
        layout.addWidget(cancel_btn)
        
        return container
    
    def handle_single_download(self):
        """Handle single audio download"""
        self.logger.info("Starting single audio download")
        self.start_download(playlist=False, audio_only=True)
    
    def handle_playlist_download(self):
        """Handle playlist audio download"""
        self.logger.info("Starting playlist audio download")
        self.start_download(playlist=True, audio_only=True)
    
    def handle_cancel_all(self):
        """Handle cancel all downloads"""
        if self.parent and hasattr(self.parent, 'cancel_active'):
            self.parent.cancel_active()
            self.logger.info("Cancelled all active downloads")
        else:
            self.logger.warning("Cancel function not available")
    
    def start_download(self, playlist: bool = False, audio_only: bool = True):
        """Start download with audio-specific settings"""
        if not self.validate_url_input():
            return
        
        url = self.get_url_input_value()
        
        try:
            # Get audio-specific settings
            audio_format = self.format_combo.currentText() if self.format_combo else "mp3"
            audio_quality = self.quality_combo.currentText() if self.quality_combo else "320"
            
            # Get user settings from parent
            resolution = self.get_default_resolution()
            folder = self.get_download_folder()
            proxy = self.get_proxy_settings()
            
            # Create download request with audio settings
            from core.services import DownloadRequest
            request = DownloadRequest(
                url=url,
                resolution=resolution,
                folder=folder,
                proxy=proxy,
                audio_only=audio_only,
                playlist=playlist,
                output_format=audio_format,
                audio_format=audio_format,
                audio_quality=audio_quality
            )
            
            # Start download
            download_service = self.get_download_service()
            if download_service:
                success = download_service.start_download(request)
                if success:
                    self.download_started.emit(url)
                    self.signals.status_changed.emit("Audio download started")
                else:
                    self.show_error("Download Error", "Failed to start audio download")
            else:
                self.show_error("Service Error", "Download service not available")
                
        except Exception as e:
            self.logger.error("Failed to start audio download", exception=e)
            self.show_error("Error", f"Failed to start audio download: {str(e)}")
    
    def get_url_input_value(self) -> str:
        """Get URL from input widget"""
        if hasattr(self.url_input_widget, 'text'):
            return self.url_input_widget.text().strip()
        return "" 