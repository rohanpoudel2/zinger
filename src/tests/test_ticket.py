import unittest
from models.ticket import Ticket, TicketStatus
from models.bus import Bus
from models.user import User

class TestTicket(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test"""
        self.bus = Bus(
            bus_number="101",
            route="New Haven -> New York",
            departure="10:00 AM",
            total_seats=30,
            fare=30.0
        )
        self.user = User(name="John Doe")
    
    def test_ticket_creation(self):
        """Test ticket creation"""
        ticket = Ticket("123", self.bus, "John Doe", "1234567890", "1A")
        self.assertEqual(ticket.booking_id, "123")
        self.assertEqual(ticket.passenger_name, "John Doe")
        self.assertEqual(ticket.status, TicketStatus.CONFIRMED)
    
    def test_cancel_ticket(self):
        """Test canceling a ticket"""
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")  # Ensure the seat is booked before canceling
        ticket.cancel()
        available_seats = self.bus.get_available_seats()
        self.assertIn("1A", available_seats)
    
    def test_cancel_already_cancelled_ticket(self):
        """Test canceling an already canceled ticket"""
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")
        ticket.cancel()  # Cancel first time
        with self.assertRaises(ValueError) as context:
            ticket.cancel()
        self.assertEqual(str(context.exception), "Ticket is already cancelled")

if __name__ == "__main__":
    unittest.main()
