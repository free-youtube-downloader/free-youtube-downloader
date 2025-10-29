"""
Tests for the configuration management system
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from core.config import (
    ConfigManager, AppConfig, UIConfig, DownloadConfig, PathConfig,
    Resolution, AudioFormat, VideoFormat, config_manager
)


class TestConfigManager:
    """Test the configuration manager"""
    
    def test_singleton_behavior(self):
        """Test that ConfigManager is a singleton"""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        
        assert manager1 is manager2
        assert manager1.config is manager2.config
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = config_manager.config
        
        # UI config
        assert config.ui.DEFAULT_WIDTH == 1280
        assert config.ui.DEFAULT_HEIGHT == 1150
        assert config.ui.MIN_WIDTH == 788
        assert config.ui.MIN_HEIGHT == 600
        
        # Download config
        assert config.download.MAX_CONCURRENT_DOWNLOADS == 3
        assert config.download.DEFAULT_RETRIES == 10
        assert config.download.SOCKET_TIMEOUT == 10
        assert config.download.DEFAULT_RESOLUTION == Resolution.P1080
        
        # Logging config
        assert config.logging.MAX_LOG_SIZE == 10 * 1024 * 1024
        assert config.logging.BACKUP_COUNT == 5
    
    def test_update_config(self):
        """Test updating configuration values"""
        manager = ConfigManager()
        original_width = manager.config.ui.DEFAULT_WIDTH
        
        manager.update_config(ui=UIConfig(DEFAULT_WIDTH=1920))
        
        # Config should be updated
        assert manager.config.ui.DEFAULT_WIDTH == 1920
        
        # Reset for other tests
        manager.update_config(ui=UIConfig(DEFAULT_WIDTH=original_width))
    
    def test_resolution_height_mapping(self):
        """Test resolution height mapping"""
        manager = ConfigManager()
        
        assert manager.get_resolution_height("720p") == 720
        assert manager.get_resolution_height("1080p") == 1080
        assert manager.get_resolution_height("4320p") == 4320
        assert manager.get_resolution_height("invalid") == 1080  # Default
    
    def test_format_string_generation(self):
        """Test yt-dlp format string generation"""
        manager = ConfigManager()
        
        format_720p = manager.get_format_string("720p")
        assert "720" in format_720p
        assert "bestvideo" in format_720p
        assert "bestaudio" in format_720p
        
        format_1080p = manager.get_format_string("1080p")
        assert "1080" in format_1080p


class TestPathConfig:
    """Test path configuration"""
    
    def test_data_directory_creation(self):
        """Test data directory creation"""
        path_config = PathConfig()
        
        data_dir = path_config.get_data_dir()
        assert os.path.exists(data_dir)
        assert "TubeTokDownloader" in data_dir
    
    def test_images_directory_creation(self):
        """Test images directory creation"""
        path_config = PathConfig()
        
        images_dir = path_config.get_images_dir()
        assert os.path.exists(images_dir)
        assert images_dir.endswith("images")
    
    def test_cookie_file_path(self):
        """Test cookie file path generation"""
        path_config = PathConfig()
        
        cookie_file = path_config.get_cookie_file()
        assert cookie_file.endswith("youtube_cookies.txt")
        assert os.path.dirname(cookie_file) == path_config.get_data_dir()
    
    @patch('sys.platform', 'win32')
    def test_windows_paths(self):
        """Test Windows-specific paths"""
        with patch.dict(os.environ, {'APPDATA': 'C:/Users/Test/AppData/Roaming'}):
            path_config = PathConfig()
            data_dir = path_config.get_data_dir()
            assert 'AppData/Roaming' in data_dir.replace('\\', '/')
    
    @patch('sys.platform', 'darwin')
    def test_macos_paths(self):
        """Test macOS-specific paths"""
        path_config = PathConfig()
        data_dir = path_config.get_data_dir()
        assert 'Library/Application Support' in data_dir
    
    @patch('sys.platform', 'linux')
    def test_linux_paths(self):
        """Test Linux-specific paths"""
        path_config = PathConfig()
        data_dir = path_config.get_data_dir()
        assert '.local/share' in data_dir
    
    def test_resource_path_development(self):
        """Test resource path in development mode"""
        path_config = PathConfig()
        
        # In development, should use current directory
        resource = path_config.resource_path("test.txt")
        assert "test.txt" in resource
    
    def test_resource_path_pyinstaller(self):
        """Test resource path with PyInstaller"""
        path_config = PathConfig()
        
        # Mock sys._MEIPASS
        with patch('sys._MEIPASS', '/tmp/pyinstaller_bundle', create=True):
            resource = path_config.resource_path("test.txt")
            assert "/tmp/pyinstaller_bundle" in resource
            assert "test.txt" in resource


class TestEnums:
    """Test configuration enums"""
    
    def test_resolution_enum(self):
        """Test Resolution enum"""
        assert Resolution.P720.value == "720p"
        assert Resolution.P1080.value == "1080p"
        assert Resolution.P4320.value == "4320p"
    
    def test_audio_format_enum(self):
        """Test AudioFormat enum"""
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.FLAC.value == "flac"
        assert AudioFormat.M4A.value == "m4a"
    
    def test_video_format_enum(self):
        """Test VideoFormat enum"""
        assert VideoFormat.MP4.value == "mp4"
        assert VideoFormat.WEBM.value == "webm"
        assert VideoFormat.MKV.value == "mkv"


class TestAppConfig:
    """Test complete application configuration"""
    
    def test_config_structure(self):
        """Test that AppConfig has all required sections"""
        config = AppConfig()
        
        assert hasattr(config, 'ui')
        assert hasattr(config, 'download')
        assert hasattr(config, 'paths')
        assert hasattr(config, 'logging')
        assert hasattr(config, 'network')
        
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.download, DownloadConfig)
        assert isinstance(config.paths, PathConfig)
    
    def test_app_metadata(self):
        """Test application metadata"""
        config = AppConfig()
        
        assert "{version}" in config.APP_ID_TEMPLATE
        assert "{version}" in config.SHARED_MEMORY_TEMPLATE
        assert "{version}" in config.SEMAPHORE_TEMPLATE


class TestDownloadConfig:
    """Test download configuration"""
    
    def test_default_values(self):
        """Test default download configuration values"""
        config = DownloadConfig()
        
        assert config.MAX_CONCURRENT_DOWNLOADS == 3
        assert config.DEFAULT_RETRIES == 10
        assert config.FRAGMENT_RETRIES == 10
        assert config.SOCKET_TIMEOUT == 10
        assert config.DEFAULT_RESOLUTION == Resolution.P1080
        assert config.DEFAULT_AUDIO_QUALITY == "320"
        assert config.GEO_BYPASS_COUNTRY == "US"
        assert config.FORCE_IPV4 == True
    
    def test_resolution_mapping(self):
        """Test resolution mapping"""
        config = DownloadConfig()
        
        assert "144p" in config.RESOLUTION_MAP
        assert "1080p" in config.RESOLUTION_MAP
        assert "4320p" in config.RESOLUTION_MAP
        
        assert config.RESOLUTION_MAP["720p"] == 720
        assert config.RESOLUTION_MAP["1080p"] == 1080


if __name__ == "__main__":
    pytest.main([__file__])