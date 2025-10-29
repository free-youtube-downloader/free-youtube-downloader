"""
Application Factory

This module provides the application factory for creating and initializing
the TokLabs Video Downloader application with proper dependency injection.
"""

import sys
import os
import atexit
import ctypes
from typing import Optional, Tuple
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSharedMemory, QSystemSemaphore, Qt
from PySide6.QtGui import QIcon

from core.config import config_manager
from core.container import service_container
from core.services import ServiceRegistry
from core.logging_system import logger_manager, setup_global_exception_handler, app_logger
from core.ffmpeg_checker import check_ffmpeg
from core.utils import resource_path
from core.version import get_version


class ApplicationFactory:
    """Factory for creating and configuring the application"""
    
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.main_window = None
        self.shared_memory: Optional[QSharedMemory] = None
        self.semaphore: Optional[QSystemSemaphore] = None
        self.service_registry: Optional[ServiceRegistry] = None
    
    def create_application(self, argv: list) -> QApplication:
        """Create and configure the QApplication"""
        # Setup global exception handling
        setup_global_exception_handler()
        
        # Set platform-specific settings
        self._set_platform_specific_settings()
        
        # Setup shared memory for single instance
        self.shared_memory, self.semaphore = self._create_shared_memory()
        
        if self.shared_memory:
            atexit.register(self._cleanup_shared_memory)
            
            # Check if another instance is running
            if not self.shared_memory.create(1):
                existing_app = self._handle_existing_instance()
                if existing_app:
                    return existing_app
        
        # Create new application instance
        self.app = QApplication(argv)
        
        # Setup application icon
        self._setup_application_icon()
        
        # Setup dependency injection
        self._setup_services()
        
        # Check FFmpeg
        ffmpeg_found, ffmpeg_path = check_ffmpeg()
        self._log_ffmpeg_status(ffmpeg_found, ffmpeg_path)
        
        # Create main window
        self._create_main_window(ffmpeg_found, ffmpeg_path)
        
        # Setup cleanup
        if self.shared_memory:
            atexit.register(self._cleanup_on_exit)
        
        app_logger.info("Application created successfully")
        return self.app
    
    def run(self) -> int:
        """Run the application"""
        if not self.app or not self.main_window:
            raise RuntimeError("Application not properly initialized")
        
        self.main_window.show()
        app_logger.info("Application started")
        
        try:
            return self.app.exec()
        except Exception as e:
            app_logger.critical("Application crashed", exception=e)
            return 1
        finally:
            app_logger.info("Application shutting down")
    
    def _set_platform_specific_settings(self):
        """Set platform-specific settings"""
        if sys.platform.startswith("win"):
            try:
                config = config_manager.config
                app_id = config.APP_ID_TEMPLATE.format(version=get_version(short=True))
                ctypes.windll.shell62.SetCurrentProcessExplicitAppUserModelID(app_id)
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                app_logger.debug("Windows-specific settings applied")
            except Exception as e:
                app_logger.warning("Failed to set Windows-specific settings", exception=e)
    
    def _create_shared_memory(self) -> Tuple[Optional[QSharedMemory], Optional[QSystemSemaphore]]:
        """Create shared memory for single instance enforcement"""
        if sys.platform.startswith("win"):
            config = config_manager.config
            version = get_version(short=True)
            
            shared_mem = QSharedMemory(
                config.SHARED_MEMORY_TEMPLATE.format(version=version)
            )
            semaphore = QSystemSemaphore(
                config.SEMAPHORE_TEMPLATE.format(version=version), 1
            )
            
            app_logger.debug("Shared memory created for single instance")
            return shared_mem, semaphore
        
        return None, None
    
    def _handle_existing_instance(self) -> Optional[QApplication]:
        """Handle case where another instance is already running"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Try to activate existing window
        if hasattr(app, 'topLevelWidgets'):
            for widget in app.topLevelWidgets():
                from ui.main_window import MainWindow
                if isinstance(widget, MainWindow):
                    if widget.isMinimized():
                        widget.showNormal()
                    if hasattr(Qt, 'WindowMinimized'):
                        widget.setWindowState(widget.windowState() & ~Qt.WindowMinimized)
                    widget.activateWindow()
                    widget.raise_()
                    widget.show()
                    app_logger.info("Activated existing application instance")
                    return app
        
        # Clean up stale shared memory
        try:
            if not self.shared_memory.detach():
                if hasattr(self.shared_memory, 'forceDetach'):
                    self.shared_memory.forceDetach()
            app_logger.debug("Cleaned up stale shared memory")
        except Exception as e:
            app_logger.warning("Failed to clean up stale shared memory", exception=e)
        
        return None
    
    def _setup_application_icon(self):
        """Setup application icon"""
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
            app_logger.debug(f"Application icon set: {icon_path}")
        else:
            app_logger.warning(f"Application icon not found: {icon_path}")
    
    def _setup_services(self):
        """Setup dependency injection services"""
        self.service_registry = ServiceRegistry(service_container)
        app_logger.debug("Services registered successfully")
    
    def _log_ffmpeg_status(self, ffmpeg_found: bool, ffmpeg_path: str):
        """Log FFmpeg status"""
        if ffmpeg_found:
            app_logger.info(f"FFmpeg found at: {ffmpeg_path}")
        else:
            app_logger.warning("FFmpeg not found. Please ensure it is installed and in PATH.")
    
    def _create_main_window(self, ffmpeg_found: bool, ffmpeg_path: str):
        """Create the main window"""
        from ui.main_window import MainWindow
        
        self.main_window = MainWindow(
            ffmpeg_found=ffmpeg_found,
            ffmpeg_path=ffmpeg_path,
            service_registry=self.service_registry
        )
        
        # Set window icon if available
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.main_window.setWindowIcon(app_icon)
        
        app_logger.debug("Main window created")
    
    def _cleanup_shared_memory(self):
        """Clean up shared memory"""
        if self.shared_memory:
            try:
                if self.shared_memory.isAttached():
                    if not self.shared_memory.detach():
                        if hasattr(self.shared_memory, 'forceDetach'):
                            self.shared_memory.forceDetach()
                app_logger.debug("Shared memory cleaned up")
            except Exception as e:
                app_logger.warning("Error during shared memory cleanup", exception=e)
    
    def _cleanup_on_exit(self):
        """Cleanup on application exit"""
        self._cleanup_shared_memory()
        if self.semaphore and self.semaphore.acquire():
            self.semaphore.release()
        app_logger.debug("Exit cleanup completed")


def create_app(argv: list) -> Tuple[QApplication, ApplicationFactory]:
    """
    Create application using factory pattern
    
    Args:
        argv: Command line arguments
        
    Returns:
        Tuple of (QApplication, ApplicationFactory)
    """
    factory = ApplicationFactory()
    app = factory.create_application(argv)
    return app, factory


def main(argv: Optional[list] = None) -> int:
    """
    Main application entry point
    
    Args:
        argv: Command line arguments (default: sys.argv)
        
    Returns:
        Exit code
    """
    if argv is None:
        argv = sys.argv
    
    try:
        app, factory = create_app(argv)
        return factory.run()
    except Exception as e:
        app_logger.critical("Failed to start application", exception=e)
        return 1