from typing import List, Optional, Dict
from models.database_models import BookingModel, BookingStatus, BusModel
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from repositories.user_repository import UserRepository
from exceptions import BookingError, ValidationError, BusError, UserError
from datetime import datetime
import logging

class BookingService:
    def __init__(self, booking_repo: BookingRepository, bus_repo: BusRepository, user_repo: UserRepository):
        self.booking_repo = booking_repo
        self.bus_repo = bus_repo
        self.user_repo = user_repo

    def get_available_buses(self) -> List:
        """Get all available buses."""
        return [bus for bus in self.bus_repo.get_all() if bus.is_active]

    def get_route_info(self, route: str) -> Dict:
        """Get detailed information about a specific route."""
        # Return empty dict - we'll use real-time data from the API instead of static data
        return {}

    def create_booking(self, user_id: int, bus_id: int, seats: int) -> BookingModel:
        """Create a new booking."""
        try:
            # Verify user exists
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise UserError("User not found")

            # Verify bus exists and is active
            bus = self.bus_repo.get_by_id(bus_id)
            if not bus:
                raise BusError("Bus not found")
            if not bus.is_active:
                raise BusError("Bus is not active")

            # Create booking
            booking = self.booking_repo.create_booking(
                user_id=user_id,
                bus_id=bus_id,
                seats=seats,
                departure_time=bus.last_updated
            )

            return booking

        except (UserError, BusError, BookingError) as e:
            raise e
        except Exception as e:
            raise BookingError(f"Failed to create booking: {str(e)}")

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        """Get a booking by ID."""
        return self.booking_repo.get_booking(booking_id)

    def get_all_bookings(self) -> List[BookingModel]:
        """Get all bookings."""
        return self.booking_repo.get_all()

    def get_user_bookings(self, user_id: int) -> List[BookingModel]:
        """Get all bookings for a user."""
        return self.booking_repo.get_user_bookings(user_id)

    def get_bus_bookings(self, bus_id: int) -> List[BookingModel]:
        """Get all bookings for a bus."""
        return self.booking_repo.get_bus_bookings(bus_id)

    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel a booking."""
        try:
            booking = self.booking_repo.get_booking(booking_id)
            if not booking:
                raise BookingError("Booking not found")

            if booking.status == "cancelled":
                raise BookingError("Booking is already cancelled")

            # Cancel the booking
            return self.booking_repo.cancel_booking(booking_id)

        except (BookingError, BusError) as e:
            raise e
        except Exception as e:
            raise BookingError(f"Failed to cancel booking: {str(e)}")

    def get_active_bookings(self) -> List[BookingModel]:
        """Get all active bookings."""
        return self.booking_repo.get_active_bookings()

    def book_seat(self, bus_number, passenger_name, phone_number, auth_service=None):
        """Book a seat on a bus."""
        try:
            # Get the bus
            bus = self.bus_repo.get_by_bus_number(bus_number)
            if not bus:
                raise ValidationError(f"Bus with number {bus_number} not found")
            
            # Check if bus is active
            if not bus.is_active:
                raise ValidationError(f"Bus {bus_number} is not currently active")
            
            # Get current user ID if available
            user_id = None
            if auth_service and auth_service.is_authenticated():
                user = auth_service.get_current_user()
                user_id = user.id
                logging.info(f"Booking with authenticated user_id: {user_id}")
            else:
                logging.warning("No auth_service provided or user not authenticated")
            
            # Create a new booking using book_seat method with user_id
            return self.booking_repo.book_seat(
                bus_id=bus.id,
                passenger_name=passenger_name,
                phone_number=phone_number,
                user_id=user_id
            )
        except Exception as e:
            logging.error(f"Error booking seat: {e}")
            raise ValidationError(f"Failed to book seat: {e}")

    def export_bookings_to_csv(self, filepath: str) -> bool:
        """Export all bookings to a CSV file."""
        try:
            import csv
            import os
            from datetime import datetime
            
            # Get all bookings
            bookings = self.get_all_bookings()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write to CSV
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['Booking ID', 'User ID', 'Bus Number', 'Passenger Name', 
                             'Phone Number', 'Status', 'Booking Time', 'Route']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for booking in bookings:
                    # Get bus information
                    bus = self.bus_repo.get_by_id(booking.bus_id)
                    bus_number = bus.bus_number if bus else "N/A"
                    route = bus.route if bus else "N/A"
                    
                    # Format booking time
                    booking_time = booking.booking_time.strftime("%Y-%m-%d %H:%M:%S") if booking.booking_time else "N/A"
                    
                    writer.writerow({
                        'Booking ID': booking.id,
                        'User ID': booking.user_id if booking.user_id else "N/A",
                        'Bus Number': bus_number,
                        'Passenger Name': booking.passenger_name,
                        'Phone Number': booking.phone_number,
                        'Status': booking.status,
                        'Booking Time': booking_time,
                        'Route': route
                    })
            
            return True
        except Exception as e:
            logging.error(f"Error exporting bookings to CSV: {e}")
            return False
            
    def export_user_bookings_to_csv(self, user_id: int, filepath: str) -> bool:
        """Export bookings for a specific user to a CSV file."""
        try:
            import csv
            import os
            from datetime import datetime
            
            # Get bookings for the specified user
            bookings = self.get_user_bookings(user_id)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write to CSV
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['Booking ID', 'User ID', 'Bus Number', 'Passenger Name', 
                             'Phone Number', 'Status', 'Booking Time', 'Route']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for booking in bookings:
                    # Get bus information
                    bus = self.bus_repo.get_by_id(booking.bus_id)
                    bus_number = bus.bus_number if bus else "N/A"
                    route = bus.route if bus else "N/A"
                    
                    # Format booking time
                    booking_time = booking.booking_time.strftime("%Y-%m-%d %H:%M:%S") if booking.booking_time else "N/A"
                    
                    writer.writerow({
                        'Booking ID': booking.id,
                        'User ID': booking.user_id if booking.user_id else "N/A",
                        'Bus Number': bus_number,
                        'Passenger Name': booking.passenger_name,
                        'Phone Number': booking.phone_number,
                        'Status': booking.status,
                        'Booking Time': booking_time,
                        'Route': route
                    })
            
            return True
        except Exception as e:
            logging.error(f"Error exporting user bookings to CSV: {e}")
            return False 