"""
Service Layer for Business Logic

This module provides service classes that encapsulate business logic
and provide clean interfaces for the UI layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from core.config import config_manager
from core.logging_system import AppLogger
from core.container import Injectable


@dataclass
class DownloadRequest:
    """Download request data structure"""
    url: str
    resolution: str
    folder: str
    proxy: Optional[str] = None
    audio_only: bool = False
    playlist: bool = False
    subtitles: bool = False
    output_format: str = "mp4"
    audio_format: Optional[str] = None
    audio_quality: str = "320"


@dataclass
class DownloadProgress:
    """Download progress data structure"""
    row_id: Optional[int]
    percentage: float
    speed: float
    eta: float
    downloaded: int
    total: int
    status: str


@dataclass
class VideoInfo:
    """Video information data structure"""
    title: str
    channel: str
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    view_count: Optional[int] = None


class IDownloadService(ABC):
    """Interface for download service"""
    
    @abstractmethod
    def start_download(self, request: DownloadRequest) -> bool:
        """Start a download task"""
        pass
    
    @abstractmethod
    def cancel_download(self, download_id: str) -> bool:
        """Cancel a download task"""
        pass
    
    @abstractmethod
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information"""
        pass
    
    @abstractmethod
    def get_active_downloads(self) -> List[str]:
        """Get list of active download IDs"""
        pass


class IHistoryService(ABC):
    """Interface for history service"""
    
    @abstractmethod
    def add_entry(self, title: str, channel: str, url: str) -> bool:
        """Add history entry"""
        pass
    
    @abstractmethod
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get history entries"""
        pass
    
    @abstractmethod
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Search history entries"""
        pass
    
    @abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        """Delete history entry"""
        pass
    
    @abstractmethod
    def clear_history(self) -> bool:
        """Clear all history"""
        pass


class IProfileService(ABC):
    """Interface for profile service"""
    
    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        pass
    
    @abstractmethod
    def update_profile(self, data: Dict[str, Any]) -> bool:
        """Update user profile"""
        pass
    
    @abstractmethod
    def export_profile(self, file_path: str) -> bool:
        """Export profile to file"""
        pass
    
    @abstractmethod
    def import_profile(self, file_path: str) -> bool:
        """Import profile from file"""
        pass


class IValidationService(ABC):
    """Interface for validation service"""
    
    @abstractmethod
    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Validate URL and return (is_valid, error_message)"""
        pass
    
    @abstractmethod
    def validate_download_request(self, request: DownloadRequest) -> tuple[bool, Optional[str]]:
        """Validate download request"""
        pass
    
    @abstractmethod
    def validate_file_path(self, path: str) -> tuple[bool, Optional[str]]:
        """Validate file path"""
        pass


class ValidationService(IValidationService):
    """Validation service implementation"""
    
    def __init__(self):
        self.logger = AppLogger('validation')
    
    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Validate URL format and supported platforms"""
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        url = url.strip()
        
        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return False, "URL must start with http:// or https://"
        
        # Check for supported platforms (basic check)
        supported_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com'
        ]
        
        if not any(domain in url.lower() for domain in supported_domains):
            self.logger.warning(f"URL may not be from a supported platform: {url}")
        
        return True, None
    
    def validate_download_request(self, request: DownloadRequest) -> tuple[bool, Optional[str]]:
        """Validate complete download request"""
        # Validate URL
        url_valid, url_error = self.validate_url(request.url)
        if not url_valid:
            return False, url_error
        
        # Validate folder path
        path_valid, path_error = self.validate_file_path(request.folder)
        if not path_valid:
            return False, path_error
        
        # Validate resolution
        valid_resolutions = list(config_manager.config.download.RESOLUTION_MAP.keys())
        if request.resolution not in valid_resolutions:
            return False, f"Invalid resolution. Must be one of: {', '.join(valid_resolutions)}"
        
        # Validate audio quality
        if request.audio_only and request.audio_quality:
            try:
                quality = int(request.audio_quality)
                if quality < 64 or quality > 320:
                    return False, "Audio quality must be between 64 and 320 kbps"
            except ValueError:
                return False, "Audio quality must be a number"
        
        return True, None
    
    def validate_file_path(self, path: str) -> tuple[bool, Optional[str]]:
        """Validate file path"""
        if not path or not path.strip():
            return False, "Path cannot be empty"
        
        import os
        try:
            # Check if path is valid and writable
            if not os.path.exists(path):
                # Try to create the directory
                os.makedirs(path, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = os.path.join(path, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except (PermissionError, OSError) as e:
                return False, f"Cannot write to directory: {str(e)}"
            
        except (OSError, PermissionError) as e:
            return False, f"Invalid path: {str(e)}"
        
        return True, None


class DownloadService(QObject):
    """Download service implementation"""
    
    # Signals for UI updates
    progress_updated = Signal(int, DownloadProgress)  # row_id, progress
    status_updated = Signal(int, str)  # row_id, status
    info_updated = Signal(int, VideoInfo)  # row_id, video_info
    download_completed = Signal(int, bool)  # row_id, success
    
    def __init__(self, validation_service: IValidationService):
        super().__init__()
        self.validation_service = validation_service
        self.logger = AppLogger('download')
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(
            config_manager.config.download.MAX_CONCURRENT_DOWNLOADS
        )
        self.active_downloads: Dict[str, Any] = {}
    
    def start_download(self, request: DownloadRequest) -> bool:
        """Start a download task"""
        # Validate request
        is_valid, error = self.validation_service.validate_download_request(request)
        if not is_valid:
            self.logger.error(f"Download request validation failed: {error}")
            return False
        
        try:
            # Import here to avoid circular imports
            from core.downloader import DownloadTask, DownloadQueueWorker
            
            # Create download task
            task = DownloadTask(
                url=request.url,
                resolution=request.resolution,
                folder=request.folder,
                proxy=request.proxy,
                audio_only=request.audio_only,
                playlist=request.playlist,
                subtitles=request.subtitles,
                output_format=request.output_format,
                audio_format=request.audio_format,
                audio_quality=request.audio_quality
            )
            
            # Create worker with signal connections
            worker = DownloadQueueWorker(
                task=task,
                row=None,  # Will be set by caller if needed
                progress_signal=None,  # Will connect to our signals
                status_signal=None,
                log_signal=None,
                info_signal=None
            )
            
            # Generate download ID
            download_id = f"{request.url}_{len(self.active_downloads)}"
            self.active_downloads[download_id] = {
                'worker': worker,
                'request': request,
                'status': 'queued'
            }
            
            # Start the download
            self.thread_pool.start(worker)
            
            self.logger.info(f"Started download: {request.url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start download", exception=e, request=request)
            return False
    
    def cancel_download(self, download_id: str) -> bool:
        """Cancel a download task"""
        if download_id not in self.active_downloads:
            return False
        
        try:
            download_info = self.active_downloads[download_id]
            worker = download_info['worker']
            worker.cancel = True
            download_info['status'] = 'cancelled'
            
            self.logger.info(f"Cancelled download: {download_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel download", exception=e, download_id=download_id)
            return False
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information"""
        try:
            # This would typically use yt-dlp to extract info
            # For now, return placeholder implementation
            return VideoInfo(
                title="Video Title",
                channel="Channel Name",
                duration="00:05:30"
            )
        except Exception as e:
            self.logger.error(f"Failed to get video info", exception=e, url=url)
            return None
    
    def get_active_downloads(self) -> List[str]:
        """Get list of active download IDs"""
        return [
            download_id for download_id, info in self.active_downloads.items()
            if info['status'] in ['queued', 'downloading']
        ]


class ServiceRegistry:
    """Registry for all application services"""
    
    def __init__(self, container):
        self.container = container
        self._setup_services()
    
    def _setup_services(self):
        """Setup and register all services"""
        # Register validation service
        self.container.register(
            IValidationService,
            ValidationService,
            singleton=True
        )
        
        # Register download service (requires validation service)
        self.container.register_factory(
            IDownloadService,
            lambda: DownloadService(
                validation_service=self.container.get(IValidationService)
            ),
            singleton=True
        )
    
    def get_validation_service(self) -> IValidationService:
        """Get validation service"""
        return self.container.get(IValidationService)
    
    def get_download_service(self) -> IDownloadService:
        """Get download service"""
        return self.container.get(IDownloadService)