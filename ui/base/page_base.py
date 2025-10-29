"""
Base Classes for UI Pages

This module provides abstract base classes for UI pages to ensure
consistent structure and reduce code duplication.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont
from core.logging_system import AppLogger
from core.services import IValidationService, IDownloadService
from core.config import config_manager


class BasePageSignals(QObject):
    """Common signals for all pages"""
    page_action = Signal(str, dict)  # action_name, data
    validation_error = Signal(str)  # error_message
    status_changed = Signal(str)  # status_message


# Create a metaclass that combines QWidget and ABC metaclasses
class PageMeta(type(QWidget), type(ABC)):
    """Metaclass that combines QWidget and ABC metaclasses"""
    pass


class BasePage(QWidget, ABC, metaclass=PageMeta):
    """
    Abstract base class for all application pages.
    Provides common functionality and enforces consistent structure.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = AppLogger(f'ui.{self.__class__.__name__}')
        self.signals = BasePageSignals()
        self._validation_service: Optional[IValidationService] = None
        self._download_service: Optional[IDownloadService] = None
        
        # Setup page
        self.setup_page()
        self.init_ui()
        self.connect_signals()
        
        self.logger.debug(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def init_ui(self):
        """Initialize the UI components. Must be implemented by subclasses."""
        pass
    
    def setup_page(self):
        """Setup basic page configuration"""
        # Set up layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
    
    def connect_signals(self):
        """Connect page signals. Override in subclasses for custom connections."""
        self.signals.validation_error.connect(self.show_validation_error)
        self.signals.status_changed.connect(self.update_status_message)
    
    def create_title_label(self, title: str) -> QLabel:
        """Create a standardized title label"""
        label = QLabel(title)
        label.setFont(QFont(
            config_manager.config.ui.DEFAULT_FONT_FAMILY,
            config_manager.config.ui.TITLE_FONT_SIZE,
            QFont.Bold
        ))
        label.setAlignment(Qt.AlignCenter)
        return label
    
    def create_section_layout(self) -> QHBoxLayout:
        """Create a standardized section layout"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        return layout
    
    def show_validation_error(self, message: str):
        """Show validation error to user"""
        self.show_error("Validation Error", message)
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        if self.parent and hasattr(self.parent, 'show_warning'):
            self.parent.show_warning(title, message)
        else:
            QMessageBox.warning(self, title, message)
        self.logger.warning(f"Error dialog shown: {title} - {message}")
    
    def show_info(self, title: str, message: str):
        """Show info dialog"""
        QMessageBox.information(self, title, message)
        self.logger.info(f"Info dialog shown: {title} - {message}")
    
    def update_status_message(self, message: str):
        """Update status message. Override in subclasses for custom behavior."""
        self.logger.info(f"Status: {message}")
    
    def get_validation_service(self) -> Optional[IValidationService]:
        """Get validation service from parent or container"""
        if self._validation_service is None and self.parent:
            if hasattr(self.parent, 'get_service'):
                self._validation_service = self.parent.get_service(IValidationService)
        return self._validation_service
    
    def get_download_service(self) -> Optional[IDownloadService]:
        """Get download service from parent or container"""
        if self._download_service is None and self.parent:
            if hasattr(self.parent, 'get_service'):
                self._download_service = self.parent.get_service(IDownloadService)
        return self._download_service
    
    def validate_and_execute(self, action: callable, *args, **kwargs):
        """
        Validate inputs and execute action with error handling
        
        Args:
            action: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        """
        try:
            return action(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing action {action.__name__}", exception=e)
            self.show_error("Error", f"An error occurred: {str(e)}")
            return None


class BaseDownloadPage(BasePage):
    """
    Base class for download pages (MP4, MP3, etc.)
    Provides common download functionality.
    """
    
    # Additional signals specific to download pages
    download_started = Signal(str)  # url
    download_completed = Signal(str, bool)  # url, success
    
    def __init__(self, parent=None):
        self.url_input = None
        super().__init__(parent)
    
    @abstractmethod
    def create_url_input(self) -> QWidget:
        """Create URL input widget. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def create_download_buttons(self) -> QWidget:
        """Create download action buttons. Must be implemented by subclasses."""
        pass
    
    def init_ui(self):
        """Initialize UI for download pages"""
        # Title
        title = self.get_page_title()
        title_label = self.create_title_label(title)
        self.main_layout.addWidget(title_label)
        
        # URL input
        self.url_input = self.create_url_input()
        self.main_layout.addWidget(self.url_input)
        
        # Download buttons
        buttons_widget = self.create_download_buttons()
        self.main_layout.addWidget(buttons_widget)
        
        # Stretch to push content to top
        self.main_layout.addStretch()
    
    @abstractmethod
    def get_page_title(self) -> str:
        """Get the page title. Must be implemented by subclasses."""
        pass
    
    def get_url_input_value(self) -> str:
        """Get URL from input widget"""
        if hasattr(self.url_input, 'text'):
            return self.url_input.text().strip()
        return ""
    
    def validate_url_input(self) -> bool:
        """Validate URL input"""
        url = self.get_url_input_value()
        if not url:
            self.signals.validation_error.emit("Please enter a URL")
            return False
        
        validation_service = self.get_validation_service()
        if validation_service:
            is_valid, error = validation_service.validate_url(url)
            if not is_valid:
                self.signals.validation_error.emit(error)
                return False
        
        return True
    
    def start_download(self, playlist: bool = False, audio_only: bool = False):
        """
        Start download with common validation and setup
        
        Args:
            playlist: Whether this is a playlist download
            audio_only: Whether this is audio-only download
        """
        if not self.validate_url_input():
            return
        
        url = self.get_url_input_value()
        
        try:
            # Get user settings from parent
            resolution = self.get_default_resolution()
            folder = self.get_download_folder()
            proxy = self.get_proxy_settings()
            
            # Create download request
            from core.services import DownloadRequest
            request = DownloadRequest(
                url=url,
                resolution=resolution,
                folder=folder,
                proxy=proxy,
                audio_only=audio_only,
                playlist=playlist,
                output_format="mp3" if audio_only else "mp4"
            )
            
            # Start download
            download_service = self.get_download_service()
            if download_service:
                success = download_service.start_download(request)
                if success:
                    self.download_started.emit(url)
                    self.signals.status_changed.emit("Download started")
                else:
                    self.show_error("Download Error", "Failed to start download")
            else:
                self.show_error("Service Error", "Download service not available")
                
        except Exception as e:
            self.logger.error("Failed to start download", exception=e)
            self.show_error("Error", f"Failed to start download: {str(e)}")
    
    def get_default_resolution(self) -> str:
        """Get default resolution from parent or config"""
        if self.parent and hasattr(self.parent, 'user_profile'):
            return self.parent.user_profile.get_default_resolution()
        return config_manager.config.download.DEFAULT_RESOLUTION.value
    
    def get_download_folder(self) -> str:
        """Get download folder from parent or config"""
        if self.parent and hasattr(self.parent, 'user_profile'):
            return self.parent.user_profile.get_download_path()
        return config_manager.config.paths.get_data_dir()
    
    def get_proxy_settings(self) -> Optional[str]:
        """Get proxy settings from parent or config"""
        if self.parent and hasattr(self.parent, 'user_profile'):
            return self.parent.user_profile.get_proxy()
        return None


class BaseListPage(BasePage):
    """
    Base class for list-based pages (History, Queue, etc.)
    Provides common list functionality.
    """
    
    def __init__(self, parent=None):
        self.list_widget = None
        super().__init__(parent)
    
    @abstractmethod
    def create_list_widget(self) -> QWidget:
        """Create the main list widget. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def create_action_buttons(self) -> QWidget:
        """Create action buttons for the list. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def load_data(self):
        """Load data into the list. Must be implemented by subclasses."""
        pass
    
    def init_ui(self):
        """Initialize UI for list pages"""
        # Title
        title = self.get_page_title()
        title_label = self.create_title_label(title)
        self.main_layout.addWidget(title_label)
        
        # Action buttons
        buttons_widget = self.create_action_buttons()
        self.main_layout.addWidget(buttons_widget)
        
        # List widget
        self.list_widget = self.create_list_widget()
        self.main_layout.addWidget(self.list_widget)
        
        # Load initial data
        self.load_data()
    
    @abstractmethod
    def get_page_title(self) -> str:
        """Get the page title. Must be implemented by subclasses."""
        pass
    
    def refresh_data(self):
        """Refresh the list data"""
        self.load_data()
        self.signals.status_changed.emit("Data refreshed")


class BaseSettingsPage(BasePage):
    """
    Base class for settings pages
    Provides common settings functionality.
    """
    
    @abstractmethod
    def create_settings_sections(self) -> List[QWidget]:
        """Create settings sections. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def save_settings(self) -> bool:
        """Save settings. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def load_settings(self):
        """Load settings. Must be implemented by subclasses."""
        pass
    
    def init_ui(self):
        """Initialize UI for settings pages"""
        # Title
        title = self.get_page_title()
        title_label = self.create_title_label(title)
        self.main_layout.addWidget(title_label)
        
        # Settings sections
        sections = self.create_settings_sections()
        for section in sections:
            self.main_layout.addWidget(section)
        
        # Save/Reset buttons
        self.create_action_buttons()
        
        # Load initial settings
        self.load_settings()
    
    def create_action_buttons(self):
        """Create save/reset action buttons"""
        from ui.components.animated_button import AnimatedButton
        
        button_layout = self.create_section_layout()
        
        save_btn = AnimatedButton("Save Settings")
        save_btn.clicked.connect(self.handle_save_settings)
        
        reset_btn = AnimatedButton("Reset to Defaults")
        reset_btn.clicked.connect(self.handle_reset_settings)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        self.main_layout.addLayout(button_layout)
    
    def handle_save_settings(self):
        """Handle save settings action"""
        if self.save_settings():
            self.show_info("Settings", "Settings saved successfully")
        else:
            self.show_error("Settings", "Failed to save settings")
    
    def handle_reset_settings(self):
        """Handle reset settings action"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_default_settings()
            self.show_info("Settings", "Settings reset to defaults")
    
    @abstractmethod
    def load_default_settings(self):
        """Load default settings. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_page_title(self) -> str:
        """Get the page title. Must be implemented by subclasses."""
        pass