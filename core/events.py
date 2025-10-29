"""
Event-Driven Architecture

This module provides an event system for decoupling components
and enabling reactive programming patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional, Type, TypeVar
from dataclasses import dataclass
from enum import Enum
import weakref
import threading
from PySide6.QtCore import QObject, Signal, QTimer
from core.logging_system import AppLogger


T = TypeVar('T')


class EventType(Enum):
    """Standard application event types"""
    
    # Download events
    DOWNLOAD_STARTED = "download_started"
    DOWNLOAD_PROGRESS = "download_progress"
    DOWNLOAD_COMPLETED = "download_completed"
    DOWNLOAD_FAILED = "download_failed"
    DOWNLOAD_CANCELLED = "download_cancelled"
    
    # UI events
    PAGE_CHANGED = "page_changed"
    THEME_CHANGED = "theme_changed"
    SETTINGS_UPDATED = "settings_updated"
    
    # Application events
    APP_STARTED = "app_started"
    APP_CLOSING = "app_closing"
    ERROR_OCCURRED = "error_occurred"
    
    # User events
    USER_PROFILE_UPDATED = "user_profile_updated"
    
    # History events
    HISTORY_ADDED = "history_added"
    HISTORY_CLEARED = "history_cleared"
    
    # Queue events
    QUEUE_ITEM_ADDED = "queue_item_added"
    QUEUE_ITEM_REMOVED = "queue_item_removed"
    QUEUE_STARTED = "queue_started"
    QUEUE_STOPPED = "queue_stopped"


@dataclass
class Event:
    """Base event data structure"""
    event_type: EventType
    data: Dict[str, Any]
    source: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class IEventHandler(ABC):
    """Interface for event handlers"""
    
    @abstractmethod
    def handle_event(self, event: Event) -> bool:
        """
        Handle an event
        
        Args:
            event: The event to handle
            
        Returns:
            True if event was handled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def can_handle(self, event_type: EventType) -> bool:
        """
        Check if this handler can handle a specific event type
        
        Args:
            event_type: The event type to check
            
        Returns:
            True if this handler can handle the event type
        """
        pass


class EventHandlerBase(IEventHandler):
    """Base implementation of event handler"""
    
    def __init__(self, handled_events: List[EventType]):
        self.handled_events = set(handled_events)
        self.logger = AppLogger(f'event_handler.{self.__class__.__name__}')
    
    def can_handle(self, event_type: EventType) -> bool:
        """Check if this handler can handle the event type"""
        return event_type in self.handled_events
    
    def handle_event(self, event: Event) -> bool:
        """Handle the event by dispatching to specific methods"""
        if not self.can_handle(event.event_type):
            return False
        
        try:
            # Try to find a specific handler method
            method_name = f"handle_{event.event_type.value}"
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                return method(event)
            else:
                # Fall back to generic handler
                return self.handle_generic(event)
                
        except Exception as e:
            self.logger.error(f"Error handling event {event.event_type}", exception=e)
            return False
    
    def handle_generic(self, event: Event) -> bool:
        """Generic event handler - override in subclasses"""
        self.logger.debug(f"Handling event: {event.event_type}")
        return True


class EventBus(QObject):
    """Central event bus for application-wide communication"""
    
    # Qt signals for cross-thread communication
    event_emitted = Signal(object)  # Event object
    
    def __init__(self):
        super().__init__()
        self._handlers: Dict[EventType, List[weakref.ref]] = {}
        self._global_handlers: List[weakref.ref] = []
        self._lock = threading.RLock()
        self.logger = AppLogger('event_bus')
        
        # Connect Qt signal to internal handler
        self.event_emitted.connect(self._handle_qt_event)
    
    def subscribe(self, event_type: EventType, handler: IEventHandler) -> bool:
        """
        Subscribe a handler to a specific event type
        
        Args:
            event_type: The event type to subscribe to
            handler: The handler to subscribe
            
        Returns:
            True if subscription was successful
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            
            # Use weak reference to avoid memory leaks
            handler_ref = weakref.ref(handler, self._cleanup_handler)
            self._handlers[event_type].append(handler_ref)
            
            self.logger.debug(f"Subscribed {handler.__class__.__name__} to {event_type}")
            return True
    
    def subscribe_global(self, handler: IEventHandler) -> bool:
        """
        Subscribe a handler to all events
        
        Args:
            handler: The handler to subscribe globally
            
        Returns:
            True if subscription was successful
        """
        with self._lock:
            handler_ref = weakref.ref(handler, self._cleanup_global_handler)
            self._global_handlers.append(handler_ref)
            
            self.logger.debug(f"Subscribed {handler.__class__.__name__} globally")
            return True
    
    def unsubscribe(self, event_type: EventType, handler: IEventHandler) -> bool:
        """
        Unsubscribe a handler from a specific event type
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The handler to unsubscribe
            
        Returns:
            True if unsubscription was successful
        """
        with self._lock:
            if event_type not in self._handlers:
                return False
            
            # Find and remove the handler
            handlers = self._handlers[event_type]
            for i, handler_ref in enumerate(handlers):
                if handler_ref() is handler:
                    handlers.pop(i)
                    self.logger.debug(f"Unsubscribed {handler.__class__.__name__} from {event_type}")
                    return True
            
            return False
    
    def publish(self, event: Event) -> int:
        """
        Publish an event to all subscribed handlers
        
        Args:
            event: The event to publish
            
        Returns:
            Number of handlers that processed the event
        """
        # Use Qt signal for thread-safe event handling
        self.event_emitted.emit(event)
        return 0  # Actual count will be determined in _handle_qt_event
    
    def _handle_qt_event(self, event: Event) -> int:
        """Handle event through Qt signal system"""
        handled_count = 0
        
        with self._lock:
            # Handle specific event type handlers
            if event.event_type in self._handlers:
                handlers = self._handlers[event.event_type][:]  # Copy to avoid modification during iteration
                
                for handler_ref in handlers:
                    handler = handler_ref()
                    if handler is not None:
                        try:
                            if handler.handle_event(event):
                                handled_count += 1
                        except Exception as e:
                            self.logger.error(f"Handler {handler.__class__.__name__} failed", exception=e)
                    else:
                        # Clean up dead reference
                        self._handlers[event.event_type].remove(handler_ref)
            
            # Handle global handlers
            global_handlers = self._global_handlers[:]  # Copy to avoid modification during iteration
            
            for handler_ref in global_handlers:
                handler = handler_ref()
                if handler is not None:
                    try:
                        if handler.can_handle(event.event_type) and handler.handle_event(event):
                            handled_count += 1
                    except Exception as e:
                        self.logger.error(f"Global handler {handler.__class__.__name__} failed", exception=e)
                else:
                    # Clean up dead reference
                    self._global_handlers.remove(handler_ref)
        
        self.logger.debug(f"Event {event.event_type} handled by {handled_count} handlers")
        return handled_count
    
    def _cleanup_handler(self, handler_ref):
        """Cleanup handler reference when object is garbage collected"""
        with self._lock:
            for event_type, handlers in self._handlers.items():
                if handler_ref in handlers:
                    handlers.remove(handler_ref)
    
    def _cleanup_global_handler(self, handler_ref):
        """Cleanup global handler reference when object is garbage collected"""
        with self._lock:
            if handler_ref in self._global_handlers:
                self._global_handlers.remove(handler_ref)
    
    def clear(self):
        """Clear all handlers"""
        with self._lock:
            self._handlers.clear()
            self._global_handlers.clear()
            self.logger.debug("Event bus cleared")
    
    def get_handler_count(self, event_type: Optional[EventType] = None) -> int:
        """Get the number of handlers for a specific event type or total"""
        with self._lock:
            if event_type is None:
                # Total handlers
                total = len(self._global_handlers)
                for handlers in self._handlers.values():
                    total += len(handlers)
                return total
            else:
                return len(self._handlers.get(event_type, []))


class EventPublisher:
    """Helper class for publishing events"""
    
    def __init__(self, event_bus: EventBus, source_name: str):
        self.event_bus = event_bus
        self.source_name = source_name
        self.logger = AppLogger(f'event_publisher.{source_name}')
    
    def publish(self, event_type: EventType, data: Dict[str, Any]) -> int:
        """
        Publish an event
        
        Args:
            event_type: The type of event to publish
            data: Event data
            
        Returns:
            Number of handlers that processed the event
        """
        event = Event(
            event_type=event_type,
            data=data,
            source=self.source_name
        )
        
        return self.event_bus.publish(event)
    
    def publish_download_started(self, url: str, request_data: Dict[str, Any]) -> int:
        """Publish download started event"""
        return self.publish(EventType.DOWNLOAD_STARTED, {
            'url': url,
            'request': request_data
        })
    
    def publish_download_progress(self, url: str, progress_data: Dict[str, Any]) -> int:
        """Publish download progress event"""
        return self.publish(EventType.DOWNLOAD_PROGRESS, {
            'url': url,
            'progress': progress_data
        })
    
    def publish_download_completed(self, url: str, success: bool, file_path: Optional[str] = None) -> int:
        """Publish download completed event"""
        return self.publish(EventType.DOWNLOAD_COMPLETED, {
            'url': url,
            'success': success,
            'file_path': file_path
        })
    
    def publish_error(self, error_message: str, error_data: Optional[Dict[str, Any]] = None) -> int:
        """Publish error event"""
        data = {'message': error_message}
        if error_data:
            data.update(error_data)
        return self.publish(EventType.ERROR_OCCURRED, data)


# Global event bus instance
event_bus = EventBus()


def create_publisher(source_name: str) -> EventPublisher:
    """Create an event publisher for a specific source"""
    return EventPublisher(event_bus, source_name)


def subscribe_to_event(event_type: EventType, handler: IEventHandler) -> bool:
    """Convenience function to subscribe to an event"""
    return event_bus.subscribe(event_type, handler)


def publish_event(event_type: EventType, data: Dict[str, Any], source: str = "unknown") -> int:
    """Convenience function to publish an event"""
    publisher = create_publisher(source)
    return publisher.publish(event_type, data)