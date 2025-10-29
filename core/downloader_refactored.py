"""
Refactored Download Module

This module provides a cleaner, more maintainable download system with
better separation of concerns and improved error handling.
"""

import os
import time
import gc
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

import yt_dlp
from PySide6.QtCore import QRunnable, QObject, Signal

from core.config import config_manager
from core.logging_system import AppLogger, handle_errors
from core.services import DownloadRequest, DownloadProgress, VideoInfo


class DownloadStatus(Enum):
    """Download status enumeration"""
    PENDING = "pending"
    CONNECTING = "connecting"
    FETCHING_INFO = "fetching_info"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadContext:
    """Download context data"""
    request: DownloadRequest
    row_id: Optional[int] = None
    worker_id: Optional[str] = None
    status: DownloadStatus = DownloadStatus.PENDING
    progress: Optional[DownloadProgress] = None
    video_info: Optional[VideoInfo] = None
    error_message: Optional[str] = None


class IDownloadEventHandler(ABC):
    """Interface for download event handling"""
    
    @abstractmethod
    def on_status_changed(self, context: DownloadContext, status: DownloadStatus):
        """Handle status change event"""
        pass
    
    @abstractmethod
    def on_progress_updated(self, context: DownloadContext, progress: DownloadProgress):
        """Handle progress update event"""
        pass
    
    @abstractmethod
    def on_info_extracted(self, context: DownloadContext, info: VideoInfo):
        """Handle video info extraction event"""
        pass
    
    @abstractmethod
    def on_log_message(self, context: DownloadContext, message: str, level: str = "info"):
        """Handle log message event"""
        pass
    
    @abstractmethod
    def on_download_completed(self, context: DownloadContext, success: bool):
        """Handle download completion event"""
        pass


class YTDLPLogger:
    """Custom logger for yt-dlp"""
    
    def __init__(self, event_handler: IDownloadEventHandler, context: DownloadContext):
        self.event_handler = event_handler
        self.context = context
        self.logger = AppLogger('ytdlp')
        self._temp_files = []

    def _log(self, level: str, msg: str):
        """Log message with proper formatting"""
        if msg.strip():
            formatted_msg = f"[yt-dlp {level}] {msg}"
            self.event_handler.on_log_message(self.context, formatted_msg, level.lower())
            
            # Also log to our logger system
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(msg)

    def debug(self, msg):
        self._log("Debug", msg)

    def info(self, msg):
        self._log("Info", msg)

    def warning(self, msg):
        self._log("Warning", msg)

    def error(self, msg):
        self._log("Error", msg)

    def cleanup(self):
        """Cleanup temporary files"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except (OSError, PermissionError) as e:
                self.logger.warning(f"Could not remove temp file {temp_file}: {e}")
        self._temp_files.clear()


class DownloadOptionsBuilder:
    """Builder for yt-dlp download options"""
    
    def __init__(self, config=None):
        self.config = config or config_manager.config
        self.logger = AppLogger('download_options')
    
    def build_base_options(self, context: DownloadContext, logger: YTDLPLogger) -> Dict[str, Any]:
        """Build base yt-dlp options"""
        cookie_file = self.config.paths.get_cookie_file()
        
        return {
            "cookiefile": cookie_file,
            "ignoreerrors": True,
            "quiet": False,
            "no_warnings": False,
            "logger": logger,
            "socket_timeout": self.config.download.SOCKET_TIMEOUT,
            "updatetime": False,
            "geo_bypass": True,
            "geo_bypass_country": self.config.download.GEO_BYPASS_COUNTRY,
            "force_ipv4": self.config.download.FORCE_IPV4,
            "retries": self.config.download.DEFAULT_RETRIES,
            "fragment_retries": self.config.download.FRAGMENT_RETRIES,
            "file_access_retries": 5,
            "retry_sleep": 2,
            "prefer_ffmpeg": True,
        }
    
    def build_info_options(self, context: DownloadContext, logger: YTDLPLogger) -> Dict[str, Any]:
        """Build options for info extraction"""
        options = self.build_base_options(context, logger)
        options.update({
            "skip_download": True
        })
        return options
    
    def build_download_options(self, context: DownloadContext, logger: YTDLPLogger, 
                             progress_hook: Callable) -> Dict[str, Any]:
        """Build options for actual download"""
        options = self.build_base_options(context, logger)
        request = context.request
        
        options.update({
            "outtmpl": os.path.join(request.folder, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "noplaylist": not request.playlist,
            "proxy": request.proxy if request.proxy else None,
            "verbose": True,
        })
        
        # Add format-specific options
        if request.audio_only:
            self._add_audio_options(options, request)
        else:
            self._add_video_options(options, request)
        
        # Add subtitle options
        if request.subtitles:
            options.update({
                "writesubtitles": True,
                "allsubtitles": True
            })
        
        return options
    
    def _add_audio_options(self, options: Dict[str, Any], request: DownloadRequest):
        """Add audio-specific options"""
        audio_format = request.audio_format or "mp3"
        audio_quality = request.audio_quality or "320"
        
        if audio_format in ['m4a', 'aac', 'opus'] and audio_format != 'mp3':
            # Use copy mode for native formats
            options.update({
                "final_ext": audio_format,
                "format": f"ba[acodec^={audio_format}]/ba/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "nopostoverwrites": False,
                    "preferredcodec": "copy",
                    "when": "post_process"
                }]
            })
        else:
            # Re-encode for other formats
            options.update({
                "final_ext": audio_format,
                "format": "ba/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "nopostoverwrites": False,
                    "preferredcodec": audio_format,
                    "preferredquality": audio_quality
                }]
            })
    
    def _add_video_options(self, options: Dict[str, Any], request: DownloadRequest):
        """Add video-specific options"""
        format_string = self.config.get_format_string(request.resolution)
        
        options.update({
            "format": format_string,
            "format_sort": ["res", "ext:mp4:m4a", "size", "br", "asr"],
            "prefer_free_formats": False,
            "merge_output_format": request.output_format.lower(),
            "postprocessors": [{
                "key": "FFmpegVideoRemuxer",
                "preferedformat": request.output_format.lower(),
                "when": "post_process"
            }]
        })


class DownloadEngine:
    """Core download engine using yt-dlp"""
    
    def __init__(self, event_handler: IDownloadEventHandler):
        self.event_handler = event_handler
        self.logger = AppLogger('download_engine')
        self.options_builder = DownloadOptionsBuilder()
    
    @handle_errors("download execution", reraise=True)
    def execute_download(self, context: DownloadContext) -> bool:
        """Execute the download process"""
        self._prepare_environment(context)
        
        # Extract video info first
        info = self._extract_video_info(context)
        if not info:
            return False
        
        # Update context with video info
        context.video_info = info
        self.event_handler.on_info_extracted(context, info)
        
        # Execute actual download
        return self._perform_download(context)
    
    def _prepare_environment(self, context: DownloadContext):
        """Prepare download environment"""
        request = context.request
        
        # Create download directory
        if not os.path.exists(request.folder):
            os.makedirs(request.folder, exist_ok=True)
            self.event_handler.on_log_message(
                context, f"Created download directory: {request.folder}"
            )
        
        # Create cookie file if needed
        self._ensure_cookie_file()
    
    def _ensure_cookie_file(self):
        """Ensure cookie file exists"""
        cookie_file = config_manager.config.paths.get_cookie_file()
        if not os.path.exists(cookie_file):
            try:
                with open(cookie_file, "w") as cf:
                    cf.write("# Netscape HTTP Cookie File\\n"
                           "youtube.com\\tFALSE\\t/\\tFALSE\\t0\\tCONSENT\\tYES+42\\n")
            except Exception as e:
                self.logger.warning(f"Failed to create cookie file: {e}")
    
    def _extract_video_info(self, context: DownloadContext) -> Optional[VideoInfo]:
        """Extract video information"""
        logger = YTDLPLogger(self.event_handler, context)
        
        try:
            self.event_handler.on_status_changed(context, DownloadStatus.FETCHING_INFO)
            
            options = self.options_builder.build_info_options(context, logger)
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(context.request.url, download=False)
                
                if not info:
                    self.event_handler.on_log_message(
                        context, "Failed to extract video information", "error"
                    )
                    return None
                
                # Handle playlist
                if context.request.playlist and "title" in info:
                    self._handle_playlist_info(context, info)
                
                # Handle entries
                if "entries" in info and isinstance(info["entries"], list):
                    if info["entries"] and info["entries"][0]:
                        info = info["entries"][0]
                    else:
                        self.event_handler.on_log_message(
                            context, "Playlist entries not found or empty", "error"
                        )
                        return None
                
                return self._create_video_info(info)
                
        except Exception as e:
            self.logger.error(f"Failed to extract video info", exception=e)
            self.event_handler.on_log_message(
                context, f"Info extraction failed: {str(e)}", "error"
            )
            return None
        finally:
            logger.cleanup()
    
    def _handle_playlist_info(self, context: DownloadContext, info: Dict[str, Any]):
        """Handle playlist-specific information"""
        playlist_title = info.get("title", "Unknown Playlist")
        playlist_folder = os.path.join(context.request.folder, playlist_title)
        os.makedirs(playlist_folder, exist_ok=True)
        
        # Update request folder
        context.request.folder = playlist_folder
        
        self.event_handler.on_log_message(
            context, f"Created playlist directory: {playlist_folder}"
        )
    
    def _create_video_info(self, info: Dict[str, Any]) -> VideoInfo:
        """Create VideoInfo from yt-dlp info"""
        return VideoInfo(
            title=info.get("title", "No Title"),
            channel=info.get("uploader", "Unknown Channel"),
            duration=info.get("duration_string"),
            thumbnail=info.get("thumbnail"),
            description=info.get("description"),
            view_count=info.get("view_count")
        )
    
    def _perform_download(self, context: DownloadContext) -> bool:
        """Perform the actual download"""
        logger = YTDLPLogger(self.event_handler, context)
        
        try:
            self.event_handler.on_status_changed(context, DownloadStatus.DOWNLOADING)
            
            # Create progress hook
            def progress_hook(d):
                self._handle_progress(context, d)
            
            options = self.options_builder.build_download_options(
                context, logger, progress_hook
            )
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([context.request.url])
            
            self.event_handler.on_status_changed(context, DownloadStatus.COMPLETED)
            return True
            
        except yt_dlp.utils.DownloadError as e:
            self.logger.error(f"Download failed", exception=e)
            self.event_handler.on_log_message(
                context, f"Download error: {str(e)}", "error"
            )
            context.error_message = str(e)
            self.event_handler.on_status_changed(context, DownloadStatus.FAILED)
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected download error", exception=e)
            self.event_handler.on_log_message(
                context, f"Unexpected error: {str(e)}", "error"
            )
            context.error_message = str(e)
            self.event_handler.on_status_changed(context, DownloadStatus.FAILED)
            return False
            
        finally:
            logger.cleanup()
    
    def _handle_progress(self, context: DownloadContext, progress_data: Dict[str, Any]):
        """Handle download progress updates"""
        try:
            if progress_data.get('status') == 'downloading':
                downloaded = progress_data.get('downloaded_bytes', 0)
                total = progress_data.get('total_bytes') or progress_data.get('total_bytes_estimate', 0)
                speed = progress_data.get('speed', 0) or 0
                eta = progress_data.get('eta', 0) or 0
                
                percentage = (downloaded / total * 100) if total > 0 else 0
                
                progress = DownloadProgress(
                    row_id=context.row_id,
                    percentage=percentage,
                    speed=speed,
                    eta=eta,
                    downloaded=downloaded,
                    total=total,
                    status="downloading"
                )
                
                context.progress = progress
                self.event_handler.on_progress_updated(context, progress)
                
        except Exception as e:
            self.logger.warning(f"Progress update failed", exception=e)


class DownloadWorker(QRunnable):
    """Qt-compatible download worker"""
    
    def __init__(self, context: DownloadContext, event_handler: IDownloadEventHandler):
        super().__init__()
        self.context = context
        self.event_handler = event_handler
        self.engine = DownloadEngine(event_handler)
        self.cancelled = False
        self.logger = AppLogger('download_worker')
    
    def run(self):
        """Execute the download task"""
        try:
            if self.cancelled:
                self.event_handler.on_status_changed(self.context, DownloadStatus.CANCELLED)
                return
            
            success = self.engine.execute_download(self.context)
            self.event_handler.on_download_completed(self.context, success)
            
        except Exception as e:
            self.logger.error(f"Worker execution failed", exception=e)
            self.context.error_message = str(e)
            self.event_handler.on_status_changed(self.context, DownloadStatus.FAILED)
            self.event_handler.on_download_completed(self.context, False)
        finally:
            # Cleanup
            gc.collect()
    
    def cancel(self):
        """Cancel the download"""
        self.cancelled = True
        self.logger.info(f"Download cancelled: {self.context.request.url}")


# Backward compatibility aliases
DownloadTask = DownloadRequest
DownloadQueueWorker = DownloadWorker