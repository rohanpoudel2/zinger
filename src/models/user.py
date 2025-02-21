from dataclasses import dataclass
from enum import Enum
from typing import List
from .ticket import Ticket

class UserRole(Enum):
    PASSENGER = "passenger"
    STAFF = "staff"

@dataclass
class User:
    name: str
    role: UserRole = UserRole.PASSENGER
    bookings: List[Ticket] = None

    def __post_init__(self):
        if self.bookings is None:
            self.bookings = []

    def add_booking(self, ticket: Ticket) -> None:
        """Add a booking to user's bookings."""
        self.bookings.append(ticket)

    def get_bookings(self) -> List[Ticket]:
        """Get all bookings for the user."""
        return self.bookings

    def cancel_booking(self, booking_id: str) -> None:
        """Cancel a specific booking."""
        for ticket in self.bookings:
            if ticket.booking_id == booking_id:
                ticket.cancel()
                return
        raise ValueError("Booking not found") 