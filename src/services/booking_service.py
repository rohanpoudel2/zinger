from typing import List, Optional, Dict
from models.database_models import BookingModel, BookingStatus, BusModel, UserModel
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from repositories.user_repository import UserRepository
from exceptions import BookingError, ValidationError, SeatError, BusError, UserError
from datetime import datetime
import logging

class BookingService:
    def __init__(self, booking_repo: BookingRepository, bus_repo: BusRepository, user_repo: UserRepository):
        self.booking_repo = booking_repo
        self.bus_repo = bus_repo
        self.user_repo = user_repo
        self.booking_id_counter = 1000

    def get_available_buses(self) -> List:
        """Get all available buses."""
        return [bus for bus in self.bus_repo.get_all() if bus.is_active]

    def get_route_info(self, route: str) -> Dict:
        """Get detailed information about a specific route."""
        # Return empty dict - we'll use real-time data from the API instead of static data
        return {}

    def create_booking(self, user_id: int, bus_id: int, seats: int) -> BookingModel:
        """Create a new booking."""
        try:
            # Verify user exists
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise UserError("User not found")

            # Verify bus exists and is active
            bus = self.bus_repo.get_by_id(bus_id)
            if not bus:
                raise BusError("Bus not found")
            if not bus.is_active:
                raise BusError("Bus is not active")

            # Check seat availability
            if not self.booking_repo.is_seat_available(bus_id, seats, bus.total_seats):
                raise BookingError("Not enough seats available")

            # Create booking
            booking = self.booking_repo.create_booking(
                user_id=user_id,
                bus_id=bus_id,
                seats=seats,
                departure_time=bus.last_updated
            )

            # Update bus available seats
            bus.available_seats -= seats
            self.bus_repo.update(bus)

            return booking

        except (UserError, BusError, BookingError) as e:
            raise e
        except Exception as e:
            raise BookingError(f"Failed to create booking: {str(e)}")

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        """Get a booking by ID."""
        return self.booking_repo.get_booking(booking_id)

    def get_all_bookings(self) -> List[BookingModel]:
        """Get all bookings."""
        return self.booking_repo.get_all()

    def get_user_bookings(self, user_id: int) -> List[BookingModel]:
        """Get all bookings for a user."""
        return self.booking_repo.get_user_bookings(user_id)

    def get_bus_bookings(self, bus_id: int) -> List[BookingModel]:
        """Get all bookings for a bus."""
        return self.booking_repo.get_bus_bookings(bus_id)

    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel a booking."""
        try:
            booking = self.booking_repo.get_booking(booking_id)
            if not booking:
                raise BookingError("Booking not found")

            if booking.status == "cancelled":
                raise BookingError("Booking is already cancelled")

            # Get the bus to update available seats
            bus = self.bus_repo.get_by_id(booking.bus_id)
            if not bus:
                raise BusError("Bus not found")

            # Cancel the booking
            if self.booking_repo.cancel_booking(booking_id):
                # Return seats to available pool
                bus.available_seats += booking.seats
                self.bus_repo.update(bus)
                return True

            return False

        except (BookingError, BusError) as e:
            raise e
        except Exception as e:
            raise BookingError(f"Failed to cancel booking: {str(e)}")

    def get_available_seats(self, bus_number: str) -> int:
        """Get the number of available seats on a bus."""
        try:
            # Get the bus
            bus = self.bus_repo.get_by_bus_number(bus_number)
            if not bus:
                raise ValidationError(f"Bus with number {bus_number} not found")
            
            # Get the total number of seats
            total_seats = bus.total_seats if hasattr(bus, 'total_seats') else 30
            
            # Get the number of confirmed bookings
            confirmed_bookings = self.booking_repo.count_by_bus_status(bus.id, 'confirmed')
            
            # Calculate available seats
            available_seats = total_seats - confirmed_bookings
            
            return available_seats
        except Exception as e:
            logging.error(f"Error getting available seats: {e}")
            raise ValidationError(f"Failed to get available seats: {e}")

    def get_active_bookings(self) -> List[BookingModel]:
        """Get all active bookings."""
        return self.booking_repo.get_active_bookings()

    def book_seat(self, bus_number, passenger_name, phone_number):
        """Book a seat on a bus."""
        try:
            # Get the bus
            bus = self.bus_repo.get_by_bus_number(bus_number)
            if not bus:
                raise ValidationError(f"Bus with number {bus_number} not found")
            
            # Check if bus is active
            if not bus.is_active:
                raise ValidationError(f"Bus {bus_number} is not currently active")
            
            # Check if bus has available seats
            available_seats = self.get_available_seats(bus_number)
            if available_seats <= 0:
                raise ValidationError(f"No available seats on bus {bus_number}")
            
            # Create a new booking
            booking = BookingModel(
                bus_id=bus.id,
                passenger_name=passenger_name,
                phone_number=phone_number,
                booking_time=datetime.utcnow(),
                status='confirmed'
            )
            
            # Save the booking
            return self.booking_repo.add(booking)
        except Exception as e:
            logging.error(f"Error booking seat: {e}")
            raise ValidationError(f"Failed to book seat: {e}") 