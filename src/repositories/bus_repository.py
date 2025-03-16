from typing import Dict, Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.database_models import BusModel
from .base_repository import BaseRepository

class BusRepository(BaseRepository[BusModel]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, bus: BusModel) -> None:
        """Add a new bus to the database."""
        self.session.merge(bus)
        self.session.commit()

    def get(self, bus_number: str) -> Optional[BusModel]:
        """Get bus details by bus number."""
        return self.session.get(BusModel, bus_number)

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

    def delete(self, bus_number: str) -> bool:
        """Delete a bus by bus number."""
        bus = self.session.get(BusModel, bus_number)
        if bus:
            self.session.delete(bus)
            self.session.commit()
            return True
        return False

    def get_all_as_dict(self) -> Dict[str, BusModel]:
        """Get all buses as a dictionary keyed by bus number."""
        return {bus.bus_number: bus for bus in self.get_all()} 