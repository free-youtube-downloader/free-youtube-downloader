"""
Centralized Logging and Error Handling

This module provides centralized logging and error handling capabilities
for the TokLabs Video Downloader application.
"""

import logging
import sys
import traceback
import functools
from typing import Optional, Callable, Any, Type, Union
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PySide6.QtCore import QObject, Signal
from core.config import config_manager


class LogLevel:
    """Log level constants"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class QtLogHandler(logging.Handler, QObject):
    """Custom logging handler that emits Qt signals for UI integration"""
    
    log_signal = Signal(str, int)  # message, level
    
    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        
    def emit(self, record):
        """Emit log record as Qt signal"""
        try:
            msg = self.format(record)
            self.log_signal.emit(msg, record.levelno)
        except Exception:
            self.handleError(record)


class LoggerManager:
    """Centralized logger management"""
    
    _instance: Optional['LoggerManager'] = None
    _loggers: dict = {}
    _qt_handler: Optional[QtLogHandler] = None
    
    def __new__(cls) -> 'LoggerManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """Setup logging configuration"""
        config = config_manager.config.logging
        
        # Create logs directory
        log_dir = Path(config_manager.config.paths.get_data_dir()) / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Main log file
        log_file = log_dir / 'toklab_downloader.log'
        
        # Create formatters
        file_formatter = logging.Formatter(
            config.LOG_FORMAT,
            datefmt=config.DATE_FORMAT
        )
        
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.MAX_LOG_SIZE,
            backupCount=config.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Create Qt handler for UI integration
        self._qt_handler = QtLogHandler()
        self._qt_handler.setFormatter(console_formatter)
        self._qt_handler.setLevel(logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(self._qt_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger instance"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def get_qt_handler(self) -> Optional[QtLogHandler]:
        """Get the Qt log handler for UI integration"""
        return self._qt_handler
    
    def set_level(self, level: int):
        """Set logging level for all handlers"""
        for handler in logging.getLogger().handlers:
            if not isinstance(handler, RotatingFileHandler):  # Keep file logging at DEBUG
                handler.setLevel(level)


class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def handle_exception(self, exc_type: Type[Exception], exc_value: Exception, 
                        exc_traceback, context: str = ""):
        """Handle unhandled exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Let keyboard interrupts through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Unhandled exception"
        if context:
            error_msg += f" in {context}"
        error_msg += f": {exc_value}"
        
        self.logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log an error with context"""
        error_msg = f"Error"
        if context:
            error_msg += f" in {context}"
        error_msg += f": {str(error)}"
        
        if kwargs:
            error_msg += f" | Context: {kwargs}"
        
        self.logger.error(error_msg, exc_info=True)
    
    def log_warning(self, message: str, **kwargs):
        """Log a warning with context"""
        if kwargs:
            message += f" | Context: {kwargs}"
        self.logger.warning(message)


def handle_errors(context: str = "", reraise: bool = False, default_return=None):
    """
    Decorator for automatic error handling
    
    Args:
        context: Context description for error logging
        reraise: Whether to reraise the exception after logging
        default_return: Default value to return if exception occurs and not reraising
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = LoggerManager().get_logger(func.__module__)
                error_handler = ErrorHandler(logger)
                
                func_context = context or f"{func.__name__}"
                error_handler.log_error(e, func_context, args=args, kwargs=kwargs)
                
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def log_performance(func: Callable) -> Callable:
    """Decorator to log function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        logger = LoggerManager().get_logger(func.__module__)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper


class AppLogger:
    """Application-specific logger with common methods"""
    
    def __init__(self, name: str):
        self.logger = LoggerManager().get_logger(name)
        self.error_handler = ErrorHandler(self.logger)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if kwargs:
            message += f" | {kwargs}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        if kwargs:
            message += f" | {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.error_handler.log_warning(message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if exception:
            self.error_handler.log_error(exception, message, **kwargs)
        else:
            if kwargs:
                message += f" | Context: {kwargs}"
            self.logger.error(message)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical error message"""
        if exception:
            self.error_handler.log_error(exception, message, **kwargs)
        else:
            if kwargs:
                message += f" | Context: {kwargs}"
        self.logger.critical(message)


# Global logger manager instance
logger_manager = LoggerManager()

# Setup global exception handler
def setup_global_exception_handler():
    """Setup global exception handler"""
    logger = logger_manager.get_logger('global')
    error_handler = ErrorHandler(logger)
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        error_handler.handle_exception(exc_type, exc_value, exc_traceback, "global")
    
    sys.excepthook = exception_handler

# Common logger instances
app_logger = AppLogger('app')
ui_logger = AppLogger('ui')
core_logger = AppLogger('core')
download_logger = AppLogger('download')