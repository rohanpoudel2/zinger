from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from models.database_models import BookingModel, BookingStatus
from .base_repository import BaseRepository
from exceptions import BookingError
from datetime import datetime
import logging

class BookingRepository(BaseRepository[BookingModel]):
    def __init__(self, session: Session):
        self.session = session

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

    def add(self, booking: BookingModel) -> None:
        """Create a new booking."""
        # First add and commit the booking to get a valid booking_id
        self.session.add(booking)
        self.session.flush()  # This assigns the primary key but doesn't commit
        
        # Now create the booked seat with the valid booking_id
        booked_seat = BookedSeatModel(
            bus_number=booking.bus_number,
            seat=booking.seat,
            booking_id=booking.booking_id
        )
        self.session.add(booked_seat)
        self.session.commit()  # Commit both in a single transaction

    def get(self, booking_id: str) -> Optional[BookingModel]:
        """Get booking details by booking ID."""
        stmt = select(BookingModel).where(BookingModel.booking_id == booking_id)
        return self.session.scalar(stmt)

    def get_all(self) -> List[BookingModel]:
        """Get all bookings."""
        stmt = select(BookingModel).order_by(BookingModel.booking_time.desc())
        return list(self.session.scalars(stmt))

    def update(self, booking: BookingModel) -> None:
        """Update a booking."""
        self.session.merge(booking)
        self.session.commit()

    def delete(self, booking_id: str) -> bool:
        """Cancel a booking."""
        booking = self.get(booking_id)
        if booking:
            booking.status = BookingStatus.CANCELLED
            self.session.query(BookedSeatModel).filter_by(
                bus_number=booking.bus_number,
                seat=booking.seat
            ).delete()
            self.session.commit()
            return True
        return False

    def get_booked_seats(self, bus_number: str) -> List[str]:
        """Get all booked seats for a bus."""
        stmt = select(BookedSeatModel.seat).where(
            BookedSeatModel.bus_number == bus_number
        )
        return [row[0] for row in self.session.execute(stmt)]

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