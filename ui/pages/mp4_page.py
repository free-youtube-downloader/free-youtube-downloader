"""
MP4/Video Download Page

Provides interface for downloading videos in MP4 format.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from ui.base import BaseDownloadPage
from ui.components.animated_button import AnimatedButton
from ui.components.drag_drop_line_edit import DragDropLineEdit


class VideoPage(BaseDownloadPage):
    """Page for downloading videos in MP4 format"""
    
    def get_page_title(self) -> str:
        """Get the page title"""
        return "Download Video"
    
    def create_url_input(self) -> QWidget:
        """Create URL input widget"""
        self.url_input_widget = DragDropLineEdit("Paste or drag a link here...")
        return self.url_input_widget
    
    def create_download_buttons(self) -> QWidget:
        """Create download action buttons"""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # Single video download button
        single_btn = AnimatedButton("Download Single MP4")
        single_btn.clicked.connect(lambda: self.handle_single_download())
        
        # Playlist download button
        playlist_btn = AnimatedButton("Download Playlist MP4")
        playlist_btn.clicked.connect(lambda: self.handle_playlist_download())
        
        # Cancel button
        cancel_btn = AnimatedButton("Cancel All")
        cancel_btn.clicked.connect(self.handle_cancel_all)
        
        layout.addWidget(single_btn)
        layout.addWidget(playlist_btn)
        layout.addWidget(cancel_btn)
        
        return container
    
    def handle_single_download(self):
        """Handle single video download"""
        self.logger.info("Starting single MP4 download")
        self.start_download(playlist=False, audio_only=False)
    
    def handle_playlist_download(self):
        """Handle playlist download"""
        self.logger.info("Starting playlist MP4 download")
        self.start_download(playlist=True, audio_only=False)
    
    def handle_cancel_all(self):
        """Handle cancel all downloads"""
        if self.parent and hasattr(self.parent, 'cancel_active'):
            self.parent.cancel_active()
            self.logger.info("Cancelled all active downloads")
        else:
            self.logger.warning("Cancel function not available")
    
    def get_url_input_value(self) -> str:
        """Get URL from input widget"""
        if hasattr(self.url_input_widget, 'text'):
            return self.url_input_widget.text().strip()
        return "" 