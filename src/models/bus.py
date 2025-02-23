from typing import List, Set
from dataclasses import dataclass, field


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
            raise ValueError("Invalid seat number")

        if not self.is_seat_available(seat):
            raise ValueError("Seat already booked")

        self.booked_seats.add(seat)
        return True

    def cancel_seat(self, seat: str) -> bool:
        """Cancel a booked seat."""
        if seat not in self.booked_seats:
            raise ValueError("Seat not booked")

        self.booked_seats.remove(seat)
        return True

    def get_available_seats(self) -> List[str]:
        """Get list of available seats."""
        all_seats = [f"{row}{seat}" for row in range(
            1, 6) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
        return [seat for seat in all_seats if seat not in self.booked_seats]

    def is_valid_seat(self, seat: str) -> bool:
        """Check if seat number is valid."""
        if len(seat) != 2:
            return False
        try:
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
