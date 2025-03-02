import unittest
from models.ticket import Ticket, TicketStatus
from models.bus import Bus
from models.user import User
from exceptions import ValidationError, SeatError

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
        ticket = Ticket("123", self.bus, "John Doe", "1234567890", "1A")
        self.bus.book_seat("1A")
        ticket.cancel()
        self.assertEqual(ticket.status, TicketStatus.CANCELLED)
        self.assertNotIn("1A", self.bus.booked_seats)
    
    def test_cancel_already_cancelled_ticket(self):
        """Test canceling an already canceled ticket"""
        ticket = Ticket("123", self.bus, "John Doe", "1234567890", "1A")
        self.bus.book_seat("1A")
        ticket.cancel()
        with self.assertRaises(ValueError):
            ticket.cancel()

if __name__ == "__main__":
    unittest.main()
