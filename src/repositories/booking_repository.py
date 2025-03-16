from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.database_models import BookingModel, BookedSeatModel, BookingStatus
from .base_repository import BaseRepository

class BookingRepository(BaseRepository[BookingModel]):
    def __init__(self, session: Session):
        self.session = session

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