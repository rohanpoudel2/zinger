import unittest
from models.user import User, UserRole
from models.ticket import Ticket
from models.bus import Bus

class TestUser(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test"""
        self.user = User(name="John Doe")
        self.bus = Bus(
            bus_number="101",
            route="New Haven -> New York",
            departure="10:00 AM",
            total_seats=30,
            fare=30.0
        )
    
    def test_user_initialization(self):
        """Test if user is initialized correctly"""
        self.assertEqual(self.user.name, "John Doe")
        self.assertEqual(self.user.role, UserRole.PASSENGER)
        self.assertEqual(len(self.user.bookings), 0)
    
    def test_add_booking(self):
        """Test adding a booking to user"""
        ticket = Ticket("123", self.bus, "John Doe", "1234567890", "1A")
        self.user.add_booking(ticket)
        self.assertIn(ticket, self.user.bookings)

    def test_cancel_user_booking(self):
        """Test canceling a user booking"""
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")
        self.user.cancel_booking("123")
        available_seats = self.bus.get_available_seats()
        self.assertIn("1A", available_seats)
    
    def test_cancel_nonexistent_booking(self):
        """Test canceling a booking that doesn't exist"""
        with self.assertRaises(ValueError):
            self.user.cancel_booking("999")

if __name__ == "__main__":
    unittest.main()
