"""
Simple tests for the validation system (without services dependency)
"""

import pytest
import tempfile
import os

from core.validation import (
    URLValidator, PathValidator, ResolutionValidator,
    AudioQualityValidator, ProxyValidator, RequiredValidator,
    ValidationLevel
)


class TestBasicValidators:
    """Test individual validators without complex dependencies"""
    
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


if __name__ == "__main__":
    pytest.main([__file__])