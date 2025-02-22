import unittest
from models.bus import Bus
from models.ticket import Ticket
from models.user import User

class TestBus(unittest.TestCase):
    
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
    
    def test_bus_initialization(self):
        """Test if bus is initialized correctly"""
        self.assertEqual(self.bus.bus_number, "101")
        self.assertEqual(self.bus.route, "New Haven -> New York")
        self.assertEqual(self.bus.departure, "10:00 AM")
        self.assertEqual(self.bus.total_seats, 30)
        self.assertEqual(self.bus.fare, 30.0)
        self.assertEqual(len(self.bus.booked_seats), 0)
    
    def test_book_seat(self):
        """Test booking a seat"""
        self.assertTrue(self.bus.book_seat("1A"))
        self.assertIn("1A", self.bus.booked_seats)
    
    def test_book_already_taken_seat(self):
        """Test booking an already booked seat"""
        self.bus.book_seat("1A")
        with self.assertRaises(ValueError):
            self.bus.book_seat("1A")
    
    def test_cancel_seat(self):
        """Test canceling a booked seat"""
        self.bus.book_seat("1A")
        self.assertTrue(self.bus.cancel_seat("1A"))
        self.assertNotIn("1A", self.bus.booked_seats)
    
    def test_cancel_unbooked_seat(self):
        """Test canceling a seat that hasn't been booked"""
        with self.assertRaises(ValueError):
            self.bus.cancel_seat("2B")

    def test_get_available_seats(self):
        """Test getting available seats"""
        self.bus.book_seat("1A")
        available_seats = self.bus.get_available_seats()
        self.assertNotIn("1A", available_seats)

if __name__ == "__main__":
    unittest.main()
