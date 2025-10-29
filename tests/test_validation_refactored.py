"""
Tests for the refactored validation system
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from core.validation import (
    ValidationService, URLValidator, PathValidator, ResolutionValidator,
    AudioQualityValidator, ProxyValidator, RequiredValidator,
    ValidationLevel, ValidationContext
)
from core.services import DownloadRequest


class TestValidators:
    """Test individual validators"""
    
    def test_required_validator(self):
        """Test required field validator"""
        validator = RequiredValidator()
        
        # Valid cases
        assert validator.validate("test").is_valid
        assert validator.validate(123).is_valid
        assert validator.validate(["item"]).is_valid
        
        # Invalid cases
        assert not validator.validate(None).is_valid
        assert not validator.validate("").is_valid
        assert not validator.validate("   ").is_valid
        assert not validator.validate([]).is_valid
        assert not validator.validate({}).is_valid
    
    def test_url_validator(self):
        """Test URL validator"""
        validator = URLValidator()
        
        # Valid YouTube URLs
        result = validator.validate("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result.is_valid
        assert result.level == ValidationLevel.INFO
        
        result = validator.validate("https://youtu.be/dQw4w9WgXcQ")
        assert result.is_valid
        
        # Valid but unsupported platform
        result = validator.validate("https://example.com/video")
        assert result.is_valid
        assert result.level == ValidationLevel.WARNING
        
        # Invalid URLs
        assert not validator.validate("not-a-url").is_valid
        assert not validator.validate("ftp://example.com").is_valid
        assert not validator.validate("").is_valid
        assert not validator.validate(None).is_valid
    
    def test_path_validator(self):
        """Test path validator"""
        validator = PathValidator()
        
        # Test with temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate(temp_dir)
            assert result.is_valid
        
        # Test with non-existent but creatable path
        with tempfile.TemporaryDirectory() as temp_dir:
            new_path = os.path.join(temp_dir, "new_folder")
            result = validator.validate(new_path)
            assert result.is_valid
            assert os.path.exists(new_path)
        
        # Invalid cases
        assert not validator.validate("").is_valid
        assert not validator.validate(None).is_valid
        assert not validator.validate(123).is_valid
    
    def test_resolution_validator(self):
        """Test resolution validator"""
        validator = ResolutionValidator()
        
        # Valid resolutions
        assert validator.validate("720p").is_valid
        assert validator.validate("1080p").is_valid
        assert validator.validate("4320p").is_valid
        
        # Invalid resolutions
        assert not validator.validate("999p").is_valid
        assert not validator.validate("HD").is_valid
        assert not validator.validate("").is_valid
        assert not validator.validate(None).is_valid
    
    def test_audio_quality_validator(self):
        """Test audio quality validator"""
        validator = AudioQualityValidator()
        
        # Valid qualities
        assert validator.validate("128").is_valid
        assert validator.validate("320").is_valid
        assert validator.validate(192).is_valid
        assert validator.validate(None).is_valid  # Optional field
        
        # Invalid qualities
        assert not validator.validate("50").is_valid  # Too low
        assert not validator.validate("400").is_valid  # Too high
        assert not validator.validate("abc").is_valid  # Not a number
        assert not validator.validate([]).is_valid  # Wrong type
    
    def test_proxy_validator(self):
        """Test proxy validator"""
        validator = ProxyValidator()
        
        # Valid proxies
        assert validator.validate(None).is_valid  # No proxy
        assert validator.validate("").is_valid  # Empty proxy
        assert validator.validate("http://proxy.example.com:8080").is_valid
        assert validator.validate("https://secure.proxy.com:3128").is_valid
        assert validator.validate("socks5://socks.proxy.net:1080").is_valid
        
        # Invalid proxies
        assert not validator.validate("invalid-proxy").is_valid
        assert not validator.validate("http://proxy").is_valid  # No port
        assert not validator.validate("proxy.com:8080").is_valid  # No protocol


class TestValidationService:
    """Test the validation service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ValidationService()
    
    def test_validate_download_request_valid(self):
        """Test validation of a valid download request"""
        with tempfile.TemporaryDirectory() as temp_dir:
            request = DownloadRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                resolution="1080p",
                folder=temp_dir,
                proxy=None,
                audio_quality="320"
            )
            
            is_valid, results = self.service.validate_download_request(request)
            assert is_valid
            
            # Should have results for all validated fields
            assert len(results) > 0
            
            # No error-level results
            errors = [r for r in results if r.level == ValidationLevel.ERROR and not r.is_valid]
            assert len(errors) == 0
    
    def test_validate_download_request_invalid_url(self):
        """Test validation with invalid URL"""
        with tempfile.TemporaryDirectory() as temp_dir:
            request = DownloadRequest(
                url="not-a-url",
                resolution="1080p",
                folder=temp_dir
            )
            
            is_valid, results = self.service.validate_download_request(request)
            assert not is_valid
            
            # Should have URL validation error
            url_errors = [r for r in results if r.field == "url" and not r.is_valid]
            assert len(url_errors) > 0
    
    def test_validate_download_request_invalid_resolution(self):
        """Test validation with invalid resolution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            request = DownloadRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                resolution="999p",
                folder=temp_dir
            )
            
            is_valid, results = self.service.validate_download_request(request)
            assert not is_valid
            
            # Should have resolution validation error
            resolution_errors = [r for r in results if r.field == "resolution" and not r.is_valid]
            assert len(resolution_errors) > 0
    
    def test_validate_download_request_invalid_path(self):
        """Test validation with invalid path"""
        request = DownloadRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            resolution="1080p",
            folder=""  # Empty path
        )
        
        is_valid, results = self.service.validate_download_request(request)
        assert not is_valid
        
        # Should have path validation error
        path_errors = [r for r in results if r.field == "folder" and not r.is_valid]
        assert len(path_errors) > 0
    
    def test_backward_compatibility_methods(self):
        """Test backward compatibility methods"""
        # URL validation
        is_valid, error = self.service.validate_url("https://www.youtube.com/watch?v=test")
        assert is_valid
        assert error is None
        
        is_valid, error = self.service.validate_url("not-a-url")
        assert not is_valid
        assert error is not None
        
        # Path validation
        with tempfile.TemporaryDirectory() as temp_dir:
            is_valid, error = self.service.validate_file_path(temp_dir)
            assert is_valid
            assert error is None
        
        is_valid, error = self.service.validate_file_path("")
        assert not is_valid
        assert error is not None
    
    def test_validation_summary(self):
        """Test validation summary generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            request = DownloadRequest(
                url="https://example.com/video",  # Will generate warning
                resolution="1080p",
                folder=temp_dir,
                audio_quality="50"  # Will generate error
            )
            
            is_valid, results = self.service.validate_download_request(request)
            summary = self.service.get_validation_summary(results)
            
            assert "total" in summary
            assert "errors" in summary
            assert "warnings" in summary
            assert "is_valid" in summary
            assert "messages" in summary
            
            assert summary["total"] > 0
            assert summary["errors"] > 0  # Audio quality error
            assert not summary["is_valid"]


class TestValidationContext:
    """Test validation context functionality"""
    
    def test_validation_context_strict_mode(self):
        """Test strict mode validation"""
        # This would need to be implemented in the validation rules
        # For now, just test that context can be created
        context = ValidationContext(
            data={"test": "value"},
            strict_mode=True
        )
        
        assert context.strict_mode
        assert context.data["test"] == "value"


if __name__ == "__main__":
    pytest.main([__file__])