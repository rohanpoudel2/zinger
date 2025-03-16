from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface defining common operations."""
    
    @abstractmethod
    def add(self, entity: T) -> None:
        """Add a new entity."""
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        """Get an entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> None:
        """Update an entity."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        pass 