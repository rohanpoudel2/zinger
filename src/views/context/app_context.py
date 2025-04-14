from typing import Dict, Any, List, Callable, Optional, TypeVar, Generic
import uuid

T = TypeVar('T')

class Observer:
    """Base observer class for the observer pattern."""
    def update(self, subject: 'Subject', data: Any) -> None:
        """Called when the subject changes state."""
        pass

class Subject:
    """Base subject class for the observer pattern."""
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, data: Any = None) -> None:
        """Notify all observers of a state change."""
        for observer in self._observers:
            observer.update(self, data)

class Store(Subject):
    """A global state store (similar to Redux store or React Context)."""
    
    def __init__(self, initial_state: Dict[str, Any] = None):
        """
        Initialize a new store with the provided initial state.
        
        Args:
            initial_state: Initial state values
        """
        super().__init__()
        self._state = initial_state or {}
        
    def get_state(self) -> Dict[str, Any]:
        """Get the entire current state."""
        return self._state.copy()
    
    def get(self, key: str, default: T = None) -> T:
        """
        Get a value from the state by key.
        
        Args:
            key: The state key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The state value or default
        """
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the state.
        
        Args:
            key: The state key to update
            value: The new value
        """
        self._state[key] = value
        self.notify({key: value})
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple state values at once.
        
        Args:
            updates: Dictionary of state updates
        """
        self._state.update(updates)
        self.notify(updates)

class AppContext:
    """
    Application context singleton to manage global state.
    
    This provides a way to access global state from anywhere
    in the application, similar to React Context.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            # Create the instance first
            instance = super(AppContext, cls).__new__(cls)

            # Initialize attributes directly on the instance
            instance._stores: Dict[str, Store] = {} # type: ignore
            instance._services: Dict[str, Any] = {} # type: ignore

            # Initialize default stores and add them to the _stores dictionary
            instance._auth_store = Store({
                'current_user': None,
                'is_authenticated': False,
                'role': None
            })
            instance._stores['auth'] = instance._auth_store
            
            instance._location_store = Store({
                'current_location': None,
                'location_name': None,
                'latitude': None,
                'longitude': None
            })
            instance._stores['location'] = instance._location_store
            
            instance._app_store = Store({
                'is_loading': False,
                'error': None,
                'theme': 'light',
                'is_ready': False
            })
            instance._stores['app'] = instance._app_store

            # Assign the fully initialized instance to the class variable
            cls._instance = instance
        return cls._instance
    
    def get_store(self, name: str) -> Optional[Store]:
        """
        Get a named state store.
        
        Args:
            name: Name of the store to retrieve
            
        Returns:
            The requested store or None if it doesn't exist
        """
        return self._stores.get(name)
    
    def create_store(self, name: str, initial_state: Dict[str, Any] = None) -> Store:
        """
        Create a new named state store.
        
        Args:
            name: Name for the new store
            initial_state: Initial state for the store
            
        Returns:
            The newly created store
        """
        if name in self._stores:
            return self._stores[name]
        
        store = Store(initial_state or {})
        self._stores[name] = store
        return store
    
    def register_service(self, name: str, service_instance: Any) -> None:
        """
        Register a service with the application context.
        
        Args:
            name: Name to register the service under
            service_instance: The service to register
        """
        self._services[name] = service_instance
    
    def get_service(self, name: str) -> Any:
        """
        Get a registered service.
        
        Args:
            name: Name of the service to retrieve
            
        Returns:
            The requested service or None if it doesn't exist
        """
        return self._services.get(name)
    
    # Convenience methods for auth
    def set_current_user(self, user: Any) -> None:
        """Set the current authenticated user."""
        auth_store = self.get_store('auth')
        if auth_store:
            auth_store.update({
                'current_user': user,
                'is_authenticated': user is not None,
                'role': getattr(user, 'role', None) if user else None
            })
    
    def get_current_user(self) -> Any:
        """Get the current authenticated user."""
        auth_store = self.get_store('auth')
        return auth_store.get('current_user') if auth_store else None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        auth_store = self.get_store('auth')
        return auth_store.get('is_authenticated', False) if auth_store else False 