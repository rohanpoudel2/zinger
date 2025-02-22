import unittest
from utils.storage import InMemoryStorage
from models.bus import Bus

class TestStorage(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test"""
        self.storage = InMemoryStorage()
        self.bus = Bus(
            bus_number="101",
            route="New Haven -> New York",
            departure="10:00 AM",
            total_seats=30,
            fare=30.0
        )
        # Add the bus to storage
        self.storage.add_bus(self.bus)

    def test_get_all_buses(self):
        """Test getting all available buses"""
        buses = self.storage.get_all_buses()
        self.assertIn("101", buses)
    
    def test_get_bus(self):
        """Test fetching a specific bus"""
        bus = self.storage.get_bus("101")
        self.assertIsNotNone(bus)
        self.assertEqual(bus.bus_number, "101")
    
    def test_create_booking(self):
        """Test booking a ticket through storage"""
        booking_id = self.storage.create_booking("101", "John Doe", "1234567890", "1A")
        self.assertTrue(booking_id)
        self.assertIn(booking_id, self.storage.bookings)

    def test_cancel_booking_in_storage(self):
        """Test canceling a booking in storage"""
        booking_id = self.storage.create_booking("101", "John Doe", "1234567890", "1A")
        self.assertTrue(self.storage.cancel_booking(booking_id))

if __name__ == "__main__":
    unittest.main()
