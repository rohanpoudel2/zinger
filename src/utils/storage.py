from typing import Dict, Optional, List
from models.bus import Bus
from models.ticket import Ticket, TicketStatus
from models.user import User, UserRole


class InMemoryStorage:
    def __init__(self):
        # Initialize with sample buses
        self.buses: Dict[str, Bus] = {
            "101": Bus(
                bus_number="101",
                route="New Haven -> New York",
                departure="10:00 AM",
                total_seats=30,
                fare=30.0
            ),
            "102": Bus(
                bus_number="102",
                route="New Haven -> Boston",
                departure="11:00 AM",
                total_seats=30,
                fare=35.0
            ),
            "203": Bus(
                bus_number="203",
                route="West Haven -> Hartford",
                departure="6:00 AM",
                total_seats=30,
                fare=15.0
            ),
            "204": Bus(
                bus_number="204",
                route="West Haven -> Meriden",
                departure="7:00 AM",
                total_seats=30,
                fare=15.0
            ),
            "301": Bus(
                bus_number="301",
                route="West Haven -> Bridgeport",
                departure="9:00 AM",
                total_seats=30,
                fare=15.0
            ),
            "302": Bus(
                bus_number="302",
                route="Orange -> Bridgeport",
                departure="9:00 AM",
                total_seats=30,
                fare=15.0
            ),
            "303": Bus(
                bus_number="303",
                route="West Haven -> Norwalk",
                departure="9:00 AM",
                total_seats=30,
                fare=15.0
            )

        }

        self.bookings: Dict[str, Ticket] = {}
        self.users: Dict[str, User] = {}
        self.current_user = User("Guest")  # Default user
        self.booking_id_counter = 1000

    def get_all_buses(self) -> Dict[str, Bus]:
        return self.buses

    def get_bus(self, bus_number: str) -> Optional[Bus]:
        return self.buses.get(bus_number)

    def get_available_seats(self, bus_number):
        bus = self.get_bus(bus_number)
        if not bus:
            return []
        all_seats = [f"{row}{seat}" for row in range(
            1, 6) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
        return [seat for seat in all_seats if seat not in bus.booked_seats]

    def create_booking(self, bus_number: str, passenger_name: str, phone: str, seat: str) -> str:
        bus = self.get_bus(bus_number)
        if not bus:
            raise ValueError("Invalid bus number")

        try:
            bus.book_seat(seat)
        except ValueError as e:
            raise ValueError(f"Booking failed: {str(e)}")

        booking_id = str(self.booking_id_counter)
        self.booking_id_counter += 1

        ticket = Ticket(
            booking_id=booking_id,
            bus=bus,
            passenger_name=passenger_name,
            phone=phone,
            seat=seat
        )

        self.bookings[booking_id] = ticket
        self.current_user.add_booking(ticket)

        return booking_id

    def get_booking(self, booking_id: str) -> Optional[Ticket]:
        return self.bookings.get(booking_id)

    def get_all_bookings(self) -> List[Ticket]:
        return self.current_user.get_bookings()

    def cancel_booking(self, booking_id: str) -> bool:
        try:
            self.current_user.cancel_booking(booking_id)
            return True
        except ValueError as e:
            raise ValueError(f"Cancellation failed: {str(e)}")

    def add_bus(self, bus):
        self.buses[bus.bus_number] = bus
