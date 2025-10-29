"""
Comprehensive Validation Layer

This module provides a comprehensive validation system for the application,
including input validation, data validation, and business rule validation.
"""

import re
import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from core.config import config_manager
from core.logging_system import AppLogger
from core.services import DownloadRequest


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Allow boolean evaluation"""
        return self.is_valid


@dataclass
class ValidationContext:
    """Context for validation operations"""
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    strict_mode: bool = False


class IValidator(ABC):
    """Interface for validators"""
    
    @abstractmethod
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """
        Validate a value
        
        Args:
            value: The value to validate
            context: Optional validation context
            
        Returns:
            ValidationResult indicating success or failure
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the validator name"""
        pass


class BaseValidator(IValidator):
    """Base validator implementation"""
    
    def __init__(self, name: str, error_message: str = "Validation failed"):
        self.name = name
        self.error_message = error_message
        self.logger = AppLogger(f'validator.{name}')
    
    def get_name(self) -> str:
        """Get the validator name"""
        return self.name
    
    def create_result(self, is_valid: bool, level: ValidationLevel = ValidationLevel.ERROR,
                     message: Optional[str] = None, suggestion: Optional[str] = None) -> ValidationResult:
        """Create a validation result"""
        return ValidationResult(
            is_valid=is_valid,
            level=level,
            message=message or self.error_message,
            suggestion=suggestion
        )


class RequiredValidator(BaseValidator):
    """Validator for required fields"""
    
    def __init__(self):
        super().__init__("required", "This field is required")
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate that value is not empty"""
        if value is None:
            return self.create_result(False)
        
        if isinstance(value, str) and not value.strip():
            return self.create_result(False)
        
        if isinstance(value, (list, dict)) and len(value) == 0:
            return self.create_result(False)
        
        return self.create_result(True, ValidationLevel.INFO, "Field is not empty")


class URLValidator(BaseValidator):
    """Validator for URLs"""
    
    def __init__(self):
        super().__init__("url", "Invalid URL format")
        self.supported_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com',
            'soundcloud.com', 'bandcamp.com'
        ]
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate URL format and platform support"""
        if not isinstance(value, str):
            return self.create_result(False, message="URL must be a string")
        
        url = value.strip()
        
        # Basic URL format validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return self.create_result(
                False, 
                message="URL must start with http:// or https://",
                suggestion="Add http:// or https:// to the beginning of the URL"
            )
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return self.create_result(False, message="Invalid URL format")
        except Exception:
            return self.create_result(False, message="Invalid URL format")
        
        # Check for supported platforms
        domain = parsed.netloc.lower()
        if any(supported in domain for supported in self.supported_domains):
            return self.create_result(True, ValidationLevel.INFO, "URL from supported platform")
        else:
            return self.create_result(
                True, 
                ValidationLevel.WARNING, 
                "URL may not be from a supported platform",
                suggestion="Supported platforms include YouTube, Vimeo, TikTok, etc."
            )


class PathValidator(BaseValidator):
    """Validator for file paths"""
    
    def __init__(self):
        super().__init__("path", "Invalid file path")
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate file path"""
        if not isinstance(value, str):
            return self.create_result(False, message="Path must be a string")
        
        path = value.strip()
        
        if not path:
            return self.create_result(False, message="Path cannot be empty")
        
        # Check if path exists or can be created
        try:
            # Try to create directory if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            
            # Test write permissions
            test_file = os.path.join(path, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return self.create_result(True, ValidationLevel.INFO, "Path is writable")
            except (PermissionError, OSError) as e:
                return self.create_result(
                    False, 
                    message=f"Cannot write to directory: {str(e)}",
                    suggestion="Choose a different directory or check permissions"
                )
                
        except (OSError, PermissionError) as e:
            return self.create_result(
                False, 
                message=f"Invalid path: {str(e)}",
                suggestion="Check that the path is valid and accessible"
            )


class ResolutionValidator(BaseValidator):
    """Validator for video resolution"""
    
    def __init__(self):
        super().__init__("resolution", "Invalid video resolution")
        self.valid_resolutions = list(config_manager.config.download.RESOLUTION_MAP.keys())
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate video resolution"""
        if not isinstance(value, str):
            return self.create_result(False, message="Resolution must be a string")
        
        if value not in self.valid_resolutions:
            return self.create_result(
                False,
                message=f"Invalid resolution. Must be one of: {', '.join(self.valid_resolutions)}",
                suggestion=f"Try using {self.valid_resolutions[0]} or {self.valid_resolutions[-1]}"
            )
        
        return self.create_result(True, ValidationLevel.INFO, "Valid resolution")


class AudioQualityValidator(BaseValidator):
    """Validator for audio quality"""
    
    def __init__(self):
        super().__init__("audio_quality", "Invalid audio quality")
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate audio quality"""
        if value is None:
            return self.create_result(True, ValidationLevel.INFO, "No audio quality specified")
        
        if isinstance(value, str):
            try:
                quality = int(value)
            except ValueError:
                return self.create_result(
                    False, 
                    message="Audio quality must be a number",
                    suggestion="Use values like 128, 192, or 320"
                )
        elif isinstance(value, int):
            quality = value
        else:
            return self.create_result(False, message="Audio quality must be a number or string")
        
        if quality < 64 or quality > 320:
            return self.create_result(
                False,
                message="Audio quality must be between 64 and 320 kbps",
                suggestion="Common values are 128, 192, or 320 kbps"
            )
        
        return self.create_result(True, ValidationLevel.INFO, f"Valid audio quality: {quality} kbps")


class ProxyValidator(BaseValidator):
    """Validator for proxy settings"""
    
    def __init__(self):
        super().__init__("proxy", "Invalid proxy format")
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Validate proxy format"""
        if value is None or value == "":
            return self.create_result(True, ValidationLevel.INFO, "No proxy specified")
        
        if not isinstance(value, str):
            return self.create_result(False, message="Proxy must be a string")
        
        proxy = value.strip()
        
        # Basic proxy format validation (protocol://host:port)
        proxy_pattern = r'^(https?|socks[45]?)://[^:]+:\d+$'
        if not re.match(proxy_pattern, proxy):
            return self.create_result(
                False,
                message="Invalid proxy format",
                suggestion="Use format: protocol://host:port (e.g., http://proxy.example.com:8080)"
            )
        
        return self.create_result(True, ValidationLevel.INFO, "Valid proxy format")


class ValidationRule:
    """A validation rule combining multiple validators"""
    
    def __init__(self, field_name: str, validators: List[IValidator], required: bool = True):
        self.field_name = field_name
        self.validators = validators
        self.required = required
    
    def validate(self, data: Dict[str, Any], context: Optional[ValidationContext] = None) -> List[ValidationResult]:
        """Validate field using all validators"""
        results = []
        value = data.get(self.field_name)
        
        # Check required first
        if self.required and (value is None or (isinstance(value, str) and not value.strip())):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"{self.field_name} is required",
                field=self.field_name
            ))
            return results
        
        # Skip validation if not required and empty
        if not self.required and (value is None or (isinstance(value, str) and not value.strip())):
            return results
        
        # Run all validators
        for validator in self.validators:
            result = validator.validate(value, context)
            result.field = self.field_name
            results.append(result)
            
            # Stop on first error if in strict mode
            if context and context.strict_mode and not result.is_valid:
                break
        
        return results


class ValidationSchema:
    """Schema for validating complex data structures"""
    
    def __init__(self, name: str, rules: List[ValidationRule]):
        self.name = name
        self.rules = {rule.field_name: rule for rule in rules}
        self.logger = AppLogger(f'validation_schema.{name}')
    
    def validate(self, data: Dict[str, Any], context: Optional[ValidationContext] = None) -> List[ValidationResult]:
        """Validate data against schema"""
        all_results = []
        
        for field_name, rule in self.rules.items():
            results = rule.validate(data, context)
            all_results.extend(results)
        
        return all_results
    
    def is_valid(self, data: Dict[str, Any], context: Optional[ValidationContext] = None) -> bool:
        """Check if data is valid according to schema"""
        results = self.validate(data, context)
        return all(result.is_valid for result in results if result.level == ValidationLevel.ERROR)
    
    def get_errors(self, data: Dict[str, Any], context: Optional[ValidationContext] = None) -> List[ValidationResult]:
        """Get only error-level validation results"""
        results = self.validate(data, context)
        return [result for result in results if not result.is_valid and result.level == ValidationLevel.ERROR]


class ValidationService:
    """Enhanced validation service"""
    
    def __init__(self):
        self.logger = AppLogger('validation_service')
        self.schemas = self._create_schemas()
    
    def _create_schemas(self) -> Dict[str, ValidationSchema]:
        """Create validation schemas"""
        schemas = {}
        
        # Download request schema
        download_rules = [
            ValidationRule("url", [RequiredValidator(), URLValidator()]),
            ValidationRule("resolution", [RequiredValidator(), ResolutionValidator()]),
            ValidationRule("folder", [RequiredValidator(), PathValidator()]),
            ValidationRule("proxy", [ProxyValidator()], required=False),
            ValidationRule("audio_quality", [AudioQualityValidator()], required=False),
        ]
        schemas["download_request"] = ValidationSchema("download_request", download_rules)
        
        return schemas
    
    def validate_download_request(self, request: DownloadRequest) -> Tuple[bool, List[ValidationResult]]:
        """Validate a download request"""
        data = {
            "url": request.url,
            "resolution": request.resolution,
            "folder": request.folder,
            "proxy": request.proxy,
            "audio_quality": request.audio_quality,
        }
        
        schema = self.schemas["download_request"]
        results = schema.validate(data)
        
        is_valid = schema.is_valid(data)
        return is_valid, results
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate URL (backward compatibility)"""
        validator = URLValidator()
        result = validator.validate(url)
        return result.is_valid, None if result.is_valid else result.message
    
    def validate_file_path(self, path: str) -> Tuple[bool, Optional[str]]:
        """Validate file path (backward compatibility)"""
        validator = PathValidator()
        result = validator.validate(path)
        return result.is_valid, None if result.is_valid else result.message
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of validation results"""
        summary = {
            "total": len(results),
            "errors": len([r for r in results if not r.is_valid and r.level == ValidationLevel.ERROR]),
            "warnings": len([r for r in results if r.level == ValidationLevel.WARNING]),
            "is_valid": all(r.is_valid for r in results if r.level == ValidationLevel.ERROR),
            "messages": [r.message for r in results if not r.is_valid]
        }
        return summary


# Global validation service instance
validation_service = ValidationService()