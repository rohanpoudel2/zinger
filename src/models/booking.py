from typing import Optional
from models.ticket import Ticket, TicketStatus
from models.bus import Bus
from exceptions import BookingError, ValidationError, StorageError
from utils.storage import InMemoryStorage
from utils.logger import setup_logger

class Booking:
    def __init__(self):
        self.storage = InMemoryStorage()
        self.logger = setup_logger()

    def view_available_buses(self):
        """Handle viewing available buses."""
        buses = self.storage.get_all_buses()
        Bus.view_available_buses(buses)
        return buses

    def view_bookings(self) -> list[Ticket]:
        """Handle viewing user's bookings."""
        return self.storage.get_all_bookings()

    def create_booking(self, bus_number: str, passenger_name: str, phone: str, seat: str) -> str:
        """Handle ticket booking."""
        try:
            booking_id = self.storage.create_booking(
                bus_number=bus_number,
                passenger_name=passenger_name,
                phone=phone,
                seat=seat
            )
            self.logger.info(f"Created booking {booking_id} for {passenger_name}")
            return booking_id
        except (BookingError, ValidationError, StorageError) as e:
            self.logger.error(f"Booking failed: {str(e)}")
            raise

    def cancel_booking(self, booking_id: str) -> bool:
        """Handle booking cancellation."""
        try:
            success = self.storage.cancel_booking(booking_id)
            if success:
                self.logger.info(f"Cancelled booking {booking_id}")
            return success
        except ValueError as e:
            self.logger.error(f"Cancellation failed: {str(e)}")
            raise

    def track_bus(self, booking_id: str) -> Optional[Bus]:
        """Get bus details for tracking."""
        booking = self.storage.get_booking(booking_id)
        if not booking:
            raise BookingError("Invalid booking ID!")
        if booking.status == TicketStatus.CANCELLED:
            raise BookingError("This booking has been cancelled!")
        return booking.bus 