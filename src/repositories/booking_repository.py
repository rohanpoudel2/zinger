from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from models.database_models import BookingModel, BookingStatus
from .base_repository import BaseRepository
from exceptions import BookingError
from datetime import datetime
import logging
import pytz

class BookingRepository(BaseRepository[BookingModel]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, booking: BookingModel) -> None:
        """Add a new booking to the database."""
        try:
            self.session.add(booking)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error adding booking: {e}")
            raise BookingError(f"Failed to add booking: {str(e)}")

    def get(self, id: str) -> Optional[BookingModel]:
        """Get a booking by ID."""
        try:
            return self.session.query(BookingModel).filter(BookingModel.id == id).first()
        except Exception as e:
            logging.error(f"Error getting booking by ID: {e}")
            return None

    def get_all(self) -> List[BookingModel]:
        """Get all bookings."""
        return self.session.query(BookingModel).order_by(BookingModel.booking_time.desc()).all()

    def update(self, booking: BookingModel) -> None:
        """Update a booking."""
        self.session.merge(booking)
        self.session.commit()

    def delete(self, id: str) -> bool:
        """Delete a booking by ID."""
        try:
            booking = self.get(id)
            if booking:
                self.session.delete(booking)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error deleting booking: {e}")
            return False
    
    def create_booking(self, user_id: int, bus_id: int, seats: int, departure_time: datetime) -> BookingModel:
        """Create a new booking."""
        try:
            booking = BookingModel(
                user_id=user_id,
                bus_id=bus_id,
                seats=seats,
                departure_time=departure_time,
                status="confirmed"
            )
            self.session.add(booking)
            self.session.commit()
            return booking
        except Exception as e:
            self.session.rollback()
            raise BookingError(f"Failed to create booking: {str(e)}")

    def get_booking(self, booking_id: int) -> BookingModel:
        """Get a booking by ID."""
        return self.session.query(BookingModel).filter_by(id=booking_id).first()

    def get_user_bookings(self, user_id: int) -> list[BookingModel]:
        """Get all bookings for a user."""
        return self.session.query(BookingModel).filter_by(user_id=user_id).all()

    def get_bus_bookings(self, bus_id: int) -> list[BookingModel]:
        """Get all bookings for a bus."""
        return self.session.query(BookingModel).filter_by(bus_id=bus_id).all()

    def get_active_bookings(self) -> list[BookingModel]:
        """Get all active (confirmed) bookings."""
        return self.session.query(BookingModel).filter_by(status="confirmed").all()

    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel a booking."""
        try:
            booking = self.get_booking(booking_id)
            if booking:
                booking.status = "cancelled"
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise BookingError(f"Failed to cancel booking: {str(e)}")

    def get_seats_booked(self, bus_id: int) -> int:
        """Get total number of seats booked for a bus."""
        bookings = self.session.query(BookingModel).filter(
            and_(
                BookingModel.bus_id == bus_id,
                BookingModel.status == "confirmed"
            )
        ).all()
        return sum(booking.seats for booking in bookings)

    def is_seat_available(self, bus_id: int, seats_requested: int, total_seats: int) -> bool:
        """Check if requested number of seats are available on the bus."""
        seats_booked = self.get_seats_booked(bus_id)
        return (total_seats - seats_booked) >= seats_requested

    def book_seat(self, bus_id: int, passenger_name: str, phone_number: str, user_id: Optional[int] = None) -> int:
        """Create a booking and return the booking ID."""
        try:
            # Use pytz to get proper timezone for New York
            eastern = pytz.timezone('America/New_York')
            now = datetime.now(eastern)
            
            booking = BookingModel(
                bus_id=bus_id,
                passenger_name=passenger_name,
                phone_number=phone_number,
                booking_time=now,
                status='confirmed',
                seats=1,
                user_id=user_id
            )
            self.session.add(booking)
            self.session.commit()
            return booking.id
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error booking seat: {e}")
            raise BookingError(f"Failed to book seat: {str(e)}")

    def count_by_bus_status(self, bus_id, status):
        """Count bookings for a specific bus with a given status."""
        try:
            return self.session.query(BookingModel).filter(
                BookingModel.bus_id == bus_id,
                BookingModel.status == status
            ).count()
        except Exception as e:
            logging.error(f"Error counting bookings by bus status: {e}")
            return 0 