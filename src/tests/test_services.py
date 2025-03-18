import unittest
from unittest.mock import Mock, patch
from services.booking_service import BookingService
from services.location_service import LocationService
from models.database_models import BookingModel

class TestBookingService(unittest.TestCase):
    def setUp(self):
        # Create mock repositories
        self.booking_repo = Mock()
        self.bus_repo = Mock()
        self.user_repo = Mock()
        
        # Initialize service with mock repositories
        self.booking_service = BookingService(
            self.booking_repo,
            self.bus_repo,
            self.user_repo
        )

    def test_get_available_buses(self):
        # Mock data
        mock_buses = [
            Mock(is_active=True),
            Mock(is_active=False),
            Mock(is_active=True)
        ]
        self.bus_repo.get_all.return_value = mock_buses

        # Test
        available_buses = self.booking_service.get_available_buses()
        
        # Assert
        self.assertEqual(len(available_buses), 2)  # Only active buses
        self.bus_repo.get_all.assert_called_once()

    def test_create_booking_success(self):
        # Mock data
        user_id = 1
        bus_id = 1
        seats = 2
        
        self.user_repo.get_by_id.return_value = Mock()
        self.bus_repo.get_by_id.return_value = Mock(is_active=True)
        self.booking_repo.create_booking.return_value = Mock(id=1)

        # Test
        booking = self.booking_service.create_booking(user_id, bus_id, seats)
        
        # Assert
        self.assertIsNotNone(booking)
        self.booking_repo.create_booking.assert_called_once()

class TestLocationService(unittest.TestCase):
    def setUp(self):
        self.location_service = LocationService()

    @patch('services.location_service.geocoder.ip')
    def test_update_location(self, mock_geocoder):
        # Mock geocoder response
        mock_geocoder.return_value = Mock(
            ok=True,
            lat=40.7128,
            lng=-74.0060,
            city="New York"
        )

        # Update location
        self.location_service._update_location()

        # Assert
        self.assertEqual(self.location_service.location_name, "New York")
        self.assertEqual(self.location_service.current_location, (40.7128, -74.0060))

    def test_calculate_distance(self):
        # Test distance calculation between two points
        distance = self.location_service.calculate_distance(
            40.7128, -74.0060,  # New York
            34.0522, -118.2437  # Los Angeles
        )
        
        # Assert distance is reasonable (roughly 2400-2500 miles)
        self.assertTrue(2400 <= distance <= 2500)

if __name__ == '__main__':
    unittest.main() 