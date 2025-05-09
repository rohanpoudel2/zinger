from typing import Dict, Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.database_models import BusModel
from .base_repository import BaseRepository
import logging

class BusRepository(BaseRepository[BusModel]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, bus: BusModel) -> None:
        """Add a new bus to the database."""
        self.session.merge(bus)
        self.session.commit()

    def get(self, id: str) -> Optional[BusModel]:
        """Get bus details by ID."""
        try:
            return self.session.query(BusModel).filter(BusModel.id == id).first()
        except Exception as e:
            logging.error(f"Error getting bus by ID: {e}")
            return None

    def get_all(self) -> List[BusModel]:
        """Get all buses from the database."""
        stmt = select(BusModel)
        return list(self.session.scalars(stmt))

    def update(self, bus: BusModel) -> None:
        """Update a bus in the database."""
        try:
            self.session.merge(bus)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, id: str) -> bool:
        """Delete a bus by ID."""
        try:
            bus = self.get(id)
            if bus:
                self.session.delete(bus)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error deleting bus: {e}")
            return False

    def get_all_as_dict(self) -> Dict[str, BusModel]:
        """Get all buses as a dictionary keyed by bus number."""
        return {bus.bus_number: bus for bus in self.get_all()}

    def get_by_id(self, bus_id):
        """Get bus by ID."""
        try:
            return self.session.query(BusModel).filter(BusModel.id == bus_id).first()
        except Exception as e:
            logging.error(f"Error getting bus by ID: {e}")
            return None

    def get_by_bus_number(self, bus_number):
        """Get bus by bus number."""
        try:
            return self.session.query(BusModel).filter(BusModel.bus_number == bus_number).first()
        except Exception as e:
            logging.error(f"Error getting bus by number: {e}")
            return None

    def get_active_buses(self) -> List[BusModel]:
        """Get all active buses."""
        try:
            return self.session.query(BusModel).filter(BusModel.is_active == True).all()
        except Exception as e:
            logging.error(f"Error retrieving active buses: {e}")
            return []

    def update_bulk(self, buses: List[BusModel]) -> bool:
        """Update multiple buses at once."""
        try:
            for bus in buses:
                self.session.merge(bus)
            return True
        except Exception as e:
            logging.error(f"Error bulk updating buses: {e}")
            return False

    def search_buses(self, search_term: str) -> List[BusModel]:
        """Search for buses by bus number or route.
        
        Args:
            search_term: Text to search for in bus_number or route fields
            
        Returns:
            List of buses matching the search criteria
        """
        try:
            if not search_term or search_term.strip() == "":
                return self.get_active_buses()
                
            # Convert search term to lowercase for case-insensitive search
            # and add wildcards for partial matching
            search_pattern = f"%{search_term.lower()}%"
            
            return self.session.query(BusModel).filter(
                (BusModel.is_active == True) &
                (
                    BusModel.bus_number.ilike(search_pattern) | 
                    BusModel.route.ilike(search_pattern)
                )
            ).all()
        except Exception as e:
            logging.error(f"Error searching buses: {e}")
            return [] 