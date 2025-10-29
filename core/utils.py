"""
Utility Functions

This module provides utility functions for the TokLabs Video Downloader.
Most path and configuration-related functions have been moved to the config module.
"""

from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor
from PySide6.QtCore import Qt
from core.config import config_manager


def set_circular_pixmap(label, image_path):
    """
    Set a circular pixmap on a QLabel
    
    Args:
        label: QLabel to set pixmap on
        image_path: Path to the image file
    """
    if not image_path:
        label.setPixmap(QPixmap())
        return

    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        label.setPixmap(QPixmap())
        return

    scaled_pixmap = pixmap.scaled(
        50, 50, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    )
    mask = QPixmap(scaled_pixmap.size())
    mask.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(mask)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(Qt.GlobalColor.white))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
    painter.end()
    
    scaled_pixmap.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))
    label.setPixmap(scaled_pixmap)


def format_speed(speed):
    """
    Format download speed for display
    
    Args:
        speed: Speed in bytes per second
        
    Returns:
        Formatted speed string
    """
    if speed > 1000000:
        return f"{speed / 1000000:.2f} MB/s"
    elif speed > 1000:
        return f"{speed / 1000:.2f} KB/s"
    else:
        return f"{speed} B/s"


def format_time(seconds):
    """
    Format time duration for display
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{int(h)}h {int(m)}m {int(s)}s"
    elif m:
        return f"{int(m)}m {int(s)}s"
    else:
        return f"{int(s)}s"


def format_file_size(size_bytes):
    """
    Format file size for display
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def sanitize_filename(filename):
    """
    Sanitize filename for safe file system use
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized or 'untitled'


# Deprecated functions - use config_manager instead
def get_data_dir():
    """
    DEPRECATED: Use config_manager.config.paths.get_data_dir() instead
    """
    import warnings
    warnings.warn(
        "get_data_dir() is deprecated. Use config_manager.config.paths.get_data_dir() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.config.paths.get_data_dir()


def get_images_dir():
    """
    DEPRECATED: Use config_manager.config.paths.get_images_dir() instead
    """
    import warnings
    warnings.warn(
        "get_images_dir() is deprecated. Use config_manager.config.paths.get_images_dir() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.config.paths.get_images_dir()


def resource_path(relative_path: str) -> str:
    """
    DEPRECATED: Use config_manager.config.paths.resource_path() instead
    """
    import warnings
    warnings.warn(
        "resource_path() is deprecated. Use config_manager.config.paths.resource_path() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.config.paths.resource_path(relative_path)