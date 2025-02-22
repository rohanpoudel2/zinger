import unittest
from utils.storage import InMemoryStorage
from utils.logger import setup_logger
from models.bus import Bus
from models.ticket import Ticket, TicketStatus
from models.user import User, UserRole

class TestBusReservation(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        self.storage = InMemoryStorage()
        self.logger = setup_logger()
        self.bus = Bus(
            bus_number="101",
            route="New Haven -> New York",
            departure="10:00 AM",
            total_seats=30,
            fare=30.0
        )
        self.user = User(name="John Doe")
    
    ### TESTS FOR BUS CLASS ###
    
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

    ### TESTS FOR TICKET CLASS ###
    
    def test_ticket_creation(self):
        """Test ticket creation"""
        ticket = Ticket("123", self.bus, "John Doe", "1234567890", "1A")
        self.assertEqual(ticket.booking_id, "123")
        self.assertEqual(ticket.passenger_name, "John Doe")
        self.assertEqual(ticket.status, TicketStatus.CONFIRMED)
    
    def test_cancel_ticket(self):
        # Setup: Book the seat first
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")  # Ensure the seat is booked before canceling

        # Now cancel the ticket
        ticket.cancel()

        # Verify the seat is now available
        available_seats = self.bus.get_available_seats()
        self.assertIn("1A", available_seats)
    
    def test_cancel_already_cancelled_ticket(self):
        # Setup: Ensure the ticket is booked first, then cancel
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")  # Book the seat
        ticket.cancel()  # Cancel first time

        # Try canceling the already canceled ticket
        with self.assertRaises(ValueError) as context:
            ticket.cancel()

        self.assertEqual(str(context.exception), "Ticket is already cancelled")

    ### TESTS FOR USER CLASS ###
    
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
        # Setup: Ensure the ticket is booked before cancellation
        ticket = Ticket(booking_id="123", bus=self.bus, passenger_name="John Doe", phone="555-1234", seat="1A")
        self.user.add_booking(ticket)
        self.bus.book_seat("1A")  # Book the seat

        # Cancel the booking
        self.user.cancel_booking("123")

        # Verify the seat is available again
        available_seats = self.bus.get_available_seats()
        self.assertIn("1A", available_seats)
    
    def test_cancel_nonexistent_booking(self):
        """Test canceling a booking that doesn't exist"""
        with self.assertRaises(ValueError):
            self.user.cancel_booking("999")

    ### TESTS FOR STORAGE CLASS ###
    
    def test_get_all_buses(self):
        """Test getting all available buses"""
        buses = self.storage.get_all_buses()
        self.assertIn("101", buses)
        self.assertIn("102", buses)
    
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
