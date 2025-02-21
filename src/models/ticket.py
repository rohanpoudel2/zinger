from dataclasses import dataclass
from enum import Enum
from .bus import Bus

class TicketStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"

@dataclass
class Ticket:
    booking_id: str
    bus: Bus
    passenger_name: str
    phone: str
    seat: str
    status: TicketStatus = TicketStatus.CONFIRMED

    def cancel(self) -> None:
        """Cancel the ticket."""
        if self.status == TicketStatus.CANCELLED:
            raise ValueError("Ticket is already cancelled")
        
        self.bus.cancel_seat(self.seat)
        self.status = TicketStatus.CANCELLED

    def get_details(self) -> str:
        """Get formatted ticket details."""
        return (f"Booking #{self.booking_id} | Bus {self.bus.bus_number} | "
                f"{self.bus.route} | {self.bus.departure} | "
                f"Seat {self.seat} | {self.status.value}") 