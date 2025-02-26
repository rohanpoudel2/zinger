import unittest
from models.booking import Booking
from models.ticket import Ticket, TicketStatus
from models.bus import Bus
from exceptions import BookingError, ValidationError, StorageError

class TestBooking(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.booking_system = Booking()
        # The storage is already initialized with sample buses in InMemoryStorage

    def test_view_available_buses(self):
        """Test viewing available buses"""
        buses = self.booking_system.view_available_buses()
        self.assertIsNotNone(buses)
        self.assertIn("101", buses)  # Check if sample bus exists
        self.assertIsInstance(buses["101"], Bus)

    def test_view_bookings_empty(self):
        """Test viewing bookings when none exist"""
        bookings = self.booking_system.view_bookings()
        self.assertEqual(len(bookings), 0)

    def test_create_valid_booking(self):
        """Test creating a valid booking"""
        booking_id = self.booking_system.create_booking(
            bus_number="101",
            passenger_name="John Doe",
            phone="1234567890",
            seat="1A"
        )
        self.assertIsNotNone(booking_id)
        bookings = self.booking_system.view_bookings()
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0].passenger_name, "John Doe")

    def test_create_booking_invalid_bus(self):
        """Test creating booking with invalid bus number"""
        with self.assertRaises(StorageError):
            self.booking_system.create_booking(
                bus_number="999",
                passenger_name="John Doe",
                phone="1234567890",
                seat="1A"
            )

    def test_create_booking_invalid_seat(self):
        """Test creating booking with invalid seat"""
        with self.assertRaises(BookingError):
            self.booking_system.create_booking(
                bus_number="101",
                passenger_name="John Doe",
                phone="1234567890",
                seat="9Z"
            )

    def test_create_booking_missing_fields(self):
        """Test creating booking with missing fields"""
        with self.assertRaises(ValidationError):
            self.booking_system.create_booking(
                bus_number="101",
                passenger_name="",
                phone="1234567890",
                seat="1A"
            )

    def test_cancel_valid_booking(self):
        """Test canceling a valid booking"""
        # First create a booking
        booking_id = self.booking_system.create_booking(
            bus_number="101",
            passenger_name="John Doe",
            phone="1234567890",
            seat="1A"
        )
        # Then cancel it
        self.assertTrue(self.booking_system.cancel_booking(booking_id))
        # Verify the booking is cancelled
        booking = self.booking_system.storage.get_booking(booking_id)
        self.assertEqual(booking.status, TicketStatus.CANCELLED)

    def test_cancel_nonexistent_booking(self):
        """Test canceling a booking that doesn't exist"""
        with self.assertRaises(ValueError):
            self.booking_system.cancel_booking("999")

    def test_track_valid_booking(self):
        """Test tracking a valid booking"""
        # Create a booking first
        booking_id = self.booking_system.create_booking(
            bus_number="101",
            passenger_name="John Doe",
            phone="1234567890",
            seat="1A"
        )
        # Try to track it
        bus = self.booking_system.track_bus(booking_id)
        self.assertIsInstance(bus, Bus)
        self.assertEqual(bus.bus_number, "101")

    def test_track_invalid_booking(self):
        """Test tracking an invalid booking"""
        with self.assertRaises(BookingError):
            self.booking_system.track_bus("999")

    def test_track_cancelled_booking(self):
        """Test tracking a cancelled booking"""
        # Create and cancel a booking
        booking_id = self.booking_system.create_booking(
            bus_number="101",
            passenger_name="John Doe",
            phone="1234567890",
            seat="1A"
        )
        self.booking_system.cancel_booking(booking_id)
        
        # Try to track the cancelled booking
        with self.assertRaises(BookingError):
            self.booking_system.track_bus(booking_id)

if __name__ == '__main__':
    unittest.main() 