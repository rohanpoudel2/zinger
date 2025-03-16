from typing import List, Optional, Dict
from models.database_models import BookingModel, BookingStatus
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from exceptions import BookingError, ValidationError, SeatError

class BookingService:
    def __init__(self, booking_repository: BookingRepository, bus_repository: BusRepository):
        self.booking_repository = booking_repository
        self.bus_repository = bus_repository
        self.booking_id_counter = 1000

    def get_available_buses(self) -> List:
        """Get all available buses."""
        return [bus for bus in self.bus_repository.get_all() if bus.is_active]

    def get_route_info(self, route: str) -> Dict:
        """Get detailed information about a specific route."""
        route_info = {
            "Downtown Shuttle": {
                "frequency": "Every 10 minutes",
                "operating_hours": "6:00 AM - 10:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Yale Shuttle": {
                "frequency": "Every 15 minutes",
                "operating_hours": "7:00 AM - 6:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Whitney Avenue": {
                "frequency": "Every 20 minutes",
                "operating_hours": "5:30 AM - 11:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Dixwell Avenue": {
                "frequency": "Every 20 minutes",
                "operating_hours": "5:30 AM - 11:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            }
        }
        return route_info.get(route, {})

    def create_booking(self, bus_number: str, passenger_name: str, phone: str, seat: str, user_id: int) -> str:
        """Create a new booking."""
        if not all([bus_number, passenger_name, phone, seat]):
            raise ValidationError("All booking fields are required")

        bus = self.bus_repository.get(bus_number)
        if not bus:
            raise BookingError(f"Bus {bus_number} not found")

        booked_seats = self.booking_repository.get_booked_seats(bus_number)
        if seat in booked_seats:
            raise SeatError(f"Seat {seat} is not available")

        booking_id = str(self.booking_id_counter)
        self.booking_id_counter += 1

        booking = BookingModel(
            booking_id=booking_id,
            bus_number=bus_number,
            user_id=user_id,
            passenger_name=passenger_name,
            phone=phone,
            seat=seat,
            status=BookingStatus.CONFIRMED
        )

        try:
            self.booking_repository.add(booking)
            return booking_id
        except Exception as e:
            raise BookingError(f"Failed to create booking: {str(e)}")

    def get_booking(self, booking_id: str) -> Optional[BookingModel]:
        """Get booking details."""
        return self.booking_repository.get(booking_id)

    def get_all_bookings(self) -> List[BookingModel]:
        """Get all bookings."""
        return self.booking_repository.get_all()

    def get_user_bookings(self, user_id: int) -> List[BookingModel]:
        """Get bookings for a specific user."""
        return [b for b in self.get_all_bookings() if b.user_id == user_id]

    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking."""
        if not self.booking_repository.delete(booking_id):
            raise BookingError(f"Booking {booking_id} not found")
        return True

    def get_available_seats(self, bus_number: str) -> List[str]:
        """Get available seats for a bus."""
        bus = self.bus_repository.get(bus_number)
        if not bus:
            return []

        booked_seats = self.booking_repository.get_booked_seats(bus_number)
        all_seats = [f"{row}{seat}" for row in range(1, 6) 
                    for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
        
        return [seat for seat in all_seats if seat not in booked_seats] 