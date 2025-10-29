"""
Dependency Injection Container

This module provides a simple dependency injection container for managing
service dependencies throughout the application.
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union
from abc import ABC, abstractmethod
import inspect
from functools import wraps


T = TypeVar('T')


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found in the container."""
    pass


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected."""
    pass


class ServiceContainer:
    """
    Simple dependency injection container that manages service instances
    and their dependencies.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._building: set = set()  # Track services being built to detect circular deps
    
    def register(self, interface: Union[Type[T], str], implementation: Union[Type[T], Callable, Any], 
                 singleton: bool = True) -> 'ServiceContainer':
        """
        Register a service in the container.
        
        Args:
            interface: The interface/key to register under
            implementation: The implementation class, factory function, or instance
            singleton: Whether to treat as singleton (default: True)
        
        Returns:
            Self for method chaining
        """
        key = self._get_key(interface)
        
        if inspect.isclass(implementation):
            # Register as factory for class
            self._factories[key] = implementation
        elif callable(implementation):
            # Register as factory function
            self._factories[key] = implementation
        else:
            # Register as instance
            if singleton:
                self._singletons[key] = implementation
            else:
                self._services[key] = implementation
        
        return self
    
    def register_instance(self, interface: Union[Type[T], str], instance: T) -> 'ServiceContainer':
        """Register a specific instance."""
        key = self._get_key(interface)
        self._singletons[key] = instance
        return self
    
    def register_factory(self, interface: Union[Type[T], str], factory: Callable[[], T], 
                        singleton: bool = True) -> 'ServiceContainer':
        """Register a factory function."""
        key = self._get_key(interface)
        
        if singleton:
            # Wrap factory to ensure singleton behavior
            def singleton_factory():
                if key not in self._singletons:
                    self._singletons[key] = factory()
                return self._singletons[key]
            self._factories[key] = singleton_factory
        else:
            self._factories[key] = factory
        
        return self
    
    def get(self, interface: Union[Type[T], str]) -> T:
        """
        Resolve a service from the container.
        
        Args:
            interface: The interface/key to resolve
            
        Returns:
            The resolved service instance
            
        Raises:
            ServiceNotFoundError: If the service is not registered
            CircularDependencyError: If a circular dependency is detected
        """
        key = self._get_key(interface)
        
        # Check for circular dependency
        if key in self._building:
            raise CircularDependencyError(f"Circular dependency detected for service: {key}")
        
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check direct services
        if key in self._services:
            return self._services[key]
        
        # Check factories
        if key in self._factories:
            self._building.add(key)
            try:
                instance = self._build_from_factory(key)
                return instance
            finally:
                self._building.discard(key)
        
        raise ServiceNotFoundError(f"Service not found: {key}")
    
    def has(self, interface: Union[Type[T], str]) -> bool:
        """Check if a service is registered."""
        key = self._get_key(interface)
        return (key in self._services or 
                key in self._factories or 
                key in self._singletons)
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._building.clear()
    
    def _get_key(self, interface: Union[Type[T], str]) -> str:
        """Get string key for interface."""
        if isinstance(interface, str):
            return interface
        return interface.__name__ if hasattr(interface, '__name__') else str(interface)
    
    def _build_from_factory(self, key: str) -> Any:
        """Build instance from factory."""
        factory = self._factories[key]
        
        # Get constructor parameters for dependency injection
        if inspect.isclass(factory):
            # Handle class constructor
            sig = inspect.signature(factory.__init__)
            params = list(sig.parameters.values())[1:]  # Skip 'self'
        elif callable(factory):
            # Handle factory function
            sig = inspect.signature(factory)
            params = list(sig.parameters.values())
        else:
            # No parameters
            return factory()
        
        # Build arguments for constructor/factory
        args = []
        kwargs = {}
        
        for param in params:
            if param.annotation != inspect.Parameter.empty:
                # Try to resolve dependency by type annotation
                try:
                    dependency = self.get(param.annotation)
                    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                        args.append(dependency)
                    else:
                        kwargs[param.name] = dependency
                except ServiceNotFoundError:
                    # If dependency not found and has default, use default
                    if param.default != inspect.Parameter.empty:
                        kwargs[param.name] = param.default
                    else:
                        # Re-raise the error
                        raise
        
        # Create instance
        if inspect.isclass(factory):
            instance = factory(*args, **kwargs)
        else:
            instance = factory(*args, **kwargs)
        
        # Store as singleton if it's a class factory
        if inspect.isclass(factory):
            self._singletons[key] = instance
        
        return instance


class Injectable(ABC):
    """Base class for services that can be injected."""
    pass


def inject(container: ServiceContainer):
    """
    Decorator for automatic dependency injection.
    
    Args:
        container: The service container to use for injection
    """
    def decorator(cls):
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            # Get constructor signature
            sig = inspect.signature(original_init)
            params = list(sig.parameters.values())[1:]  # Skip 'self'
            
            # Inject dependencies for parameters with type annotations
            injected_kwargs = {}
            for param in params:
                if (param.name not in kwargs and 
                    param.annotation != inspect.Parameter.empty and
                    container.has(param.annotation)):
                    injected_kwargs[param.name] = container.get(param.annotation)
            
            # Merge with provided kwargs
            final_kwargs = {**injected_kwargs, **kwargs}
            original_init(self, *args, **final_kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator


# Global service container instance
service_container = ServiceContainer()