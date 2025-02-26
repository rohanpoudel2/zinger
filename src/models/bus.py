from typing import List, Set
from dataclasses import dataclass, field
from exceptions import SeatError, ValidationError


@dataclass
class Bus:
    bus_number: str
    route: str
    departure: str
    total_seats: int
    fare: float
    booked_seats: Set[str] = field(default_factory=set)

    def is_seat_available(self, seat: str) -> bool:
        """Check if a specific seat is available."""
        return seat not in self.booked_seats

    def book_seat(self, seat: str) -> bool:
        """Book a specific seat if available."""
        if not self.is_valid_seat(seat):
            raise ValidationError(f"Invalid seat number: {seat}")

        if not self.is_seat_available(seat):
            raise SeatError(f"Seat {seat} is already booked")

        self.booked_seats.add(seat)
        return True

    def cancel_seat(self, seat: str) -> bool:
        """Cancel a booked seat."""
        if not isinstance(seat, str):
            raise ValidationError("Seat number must be a string")
            
        if seat not in self.booked_seats:
            raise SeatError(f"Seat {seat} is not booked")

        self.booked_seats.remove(seat)
        return True

    def get_available_seats(self) -> List[str]:
        """Get list of available seats."""
        all_seats = [f"{row}{seat}" for row in range(
            1, 6) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
        return [seat for seat in all_seats if seat not in self.booked_seats]

    def is_valid_seat(self, seat: str) -> bool:
        """Check if seat number is valid."""
        try:
            if not isinstance(seat, str):
                raise ValidationError("Seat number must be a string")
            
            if len(seat) != 2:
                return False
                
            row = int(seat[0])
            column = seat[1].upper()
            return 1 <= row <= 5 and column in ['A', 'B', 'C', 'D', 'E', 'F']
        except ValueError:
            return False

    @staticmethod
    def view_available_buses(buses):
        print("\n--- Available Buses ---")
        for bus in buses.values():
            available_seats = len(bus.get_available_seats())
            print(f"Bus {bus.bus_number}: {bus.route} | "
                  f"{bus.departure} | {available_seats} seats | ${bus.fare}")
