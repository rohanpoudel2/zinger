from typing import List, Optional, Dict
from models.database_models import BookingModel
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from repositories.user_repository import UserRepository
from exceptions import BookingError, ValidationError, BusError, UserError, DatabaseError
import logging
from rich.console import Console

# Get loggers
app_logger = logging.getLogger('app')
error_logger = logging.getLogger('error')
access_logger = logging.getLogger('access')

# Initialize Rich console
console = Console()

class BookingService:
    def __init__(self, booking_repo: BookingRepository, bus_repo: BusRepository, user_repo: UserRepository):
        self.booking_repo = booking_repo
        self.bus_repo = bus_repo
        self.user_repo = user_repo
        app_logger.info("BookingService initialized")

    def get_available_buses(self) -> List:
        """Get all available buses."""
        app_logger.info("Fetching available buses")
        buses = [bus for bus in self.bus_repo.get_all() if bus.is_active]
        app_logger.info(f"Found {len(buses)} available buses")
        return buses

    def get_route_info(self, route: str) -> Dict:
        """Get detailed information about a specific route."""
        app_logger.info(f"Fetching route info for route: {route}")
        # Return empty dict - we'll use real-time data from the API instead of static data
        return {}

    def create_booking(self, user_id: int, bus_id: int, seats: int) -> BookingModel:
        """Create a new booking."""
        try:
            app_logger.info(f"Creating booking for user {user_id} on bus {bus_id} for {seats} seats")
            
            # Verify user exists
            # This is a critical check to ensure we don't create bookings for non-existent users
            user = self.user_repo.get_by_id(user_id)
            if not user:
                error_msg = f"User {user_id} not found"
                error_logger.error(error_msg)
                raise UserError(error_msg)

            # Verify bus exists and is active
            # We check both existence and active status to prevent bookings on inactive buses
            bus = self.bus_repo.get_by_id(bus_id)
            if not bus:
                error_msg = f"Bus {bus_id} not found"
                error_logger.error(error_msg)
                raise BusError(error_msg)
            if not bus.is_active:
                error_msg = f"Bus {bus_id} is not active"
                error_logger.error(error_msg)
                raise BusError(error_msg)

            # Create booking
            # After all validation passes, we can safely create the booking record
            booking = self.booking_repo.create_booking(
                user_id=user_id,
                bus_id=bus_id,
                seats=seats,
                departure_time=bus.last_updated
            )
            
            # Log successful creation for both application monitoring and access tracking
            app_logger.info(f"Successfully created booking {booking.id} for user {user_id}")
            access_logger.info(f"New booking created - ID: {booking.id}, User: {user_id}, Bus: {bus_id}")
            return booking

        except (UserError, BusError, BookingError) as e:
            # Handle domain-specific errors with proper logging
            error_logger.error(f"Booking creation failed: {str(e)}")
            console.print(f"\n[red]Error creating booking:[/red] {e}")
            raise e
        except Exception as e:
            # Catch any unexpected errors and convert to domain-specific BookingError
            error_msg = f"Failed to create booking: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            console.print(f"\n[red]Unexpected error creating booking:[/red] {e}")
            raise BookingError(error_msg)

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        """Get a booking by ID."""
        app_logger.info(f"Fetching booking {booking_id}")
        booking = self.booking_repo.get_booking(booking_id)
        if booking:
            app_logger.info(f"Found booking {booking_id}")
        else:
            app_logger.warning(f"Booking {booking_id} not found")
        return booking

    def get_all_bookings(self) -> List[BookingModel]:
        """Get all bookings."""
        app_logger.info("Fetching all bookings")
        bookings = self.booking_repo.get_all()
        app_logger.info(f"Found {len(bookings)} bookings")
        return bookings

    def get_user_bookings(self, user_id: int) -> List[BookingModel]:
        """Get all bookings for a user."""
        app_logger.info(f"Fetching bookings for user {user_id}")
        bookings = self.booking_repo.get_user_bookings(user_id)
        app_logger.info(f"Found {len(bookings)} bookings for user {user_id}")
        return bookings

    def get_bus_bookings(self, bus_id: int) -> List[BookingModel]:
        """Get all bookings for a bus."""
        app_logger.info(f"Fetching bookings for bus {bus_id}")
        bookings = self.booking_repo.get_bus_bookings(bus_id)
        app_logger.info(f"Found {len(bookings)} bookings for bus {bus_id}")
        return bookings

    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel a booking."""
        try:
            app_logger.info(f"Attempting to cancel booking {booking_id}")
            booking = self.booking_repo.get_booking(booking_id)
            if not booking:
                error_msg = f"Booking {booking_id} not found"
                error_logger.error(error_msg)
                raise BookingError(error_msg)

            if booking.status == "cancelled":
                error_msg = f"Booking {booking_id} is already cancelled"
                error_logger.error(error_msg)
                raise BookingError(error_msg)

            # Cancel the booking
            result = self.booking_repo.cancel_booking(booking_id)
            if result:
                app_logger.info(f"Successfully cancelled booking {booking_id}")
                access_logger.info(f"Booking {booking_id} cancelled")
            else:
                app_logger.warning(f"Failed to cancel booking {booking_id}")
            return result

        except (BookingError, BusError) as e:
            error_logger.error(f"Booking cancellation failed: {str(e)}")
            raise e
        except Exception as e:
            error_msg = f"Failed to cancel booking: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            raise BookingError(error_msg)

    def get_active_bookings(self) -> List[BookingModel]:
        """Get all active bookings."""
        app_logger.info("Fetching active bookings")
        bookings = self.booking_repo.get_active_bookings()
        app_logger.info(f"Found {len(bookings)} active bookings")
        return bookings

    def book_seat(self, bus_number, passenger_name, phone_number, auth_service=None):
        """Book a seat on a bus."""
        try:
            app_logger.info(f"Attempting to book seat on bus {bus_number} for {passenger_name}")
            
            # Get the bus
            bus = self.bus_repo.get_by_bus_number(bus_number)
            if not bus:
                error_msg = f"Bus with number {bus_number} not found"
                error_logger.error(error_msg)
                raise ValidationError(error_msg)
            
            # Check if bus is active
            if not bus.is_active:
                error_msg = f"Bus {bus_number} is not currently active"
                error_logger.error(error_msg)
                raise ValidationError(error_msg)
            
            # Get current user ID if available
            user_id = None
            if auth_service and auth_service.is_authenticated():
                user = auth_service.get_current_user()
                user_id = user.id
                app_logger.info(f"Booking with authenticated user_id: {user_id}")
            else:
                app_logger.warning("No auth_service provided or user not authenticated")
            
            # Create a new booking
            booking = self.booking_repo.book_seat(
                bus_id=bus.id,
                passenger_name=passenger_name,
                phone_number=phone_number,
                user_id=user_id
            )
            
            app_logger.info(f"Successfully booked seat on bus {bus_number} for {passenger_name}")
            access_logger.info(f"New seat booking - Bus: {bus_number}, Passenger: {passenger_name}, User ID: {user_id}")
            return booking
            
        except ValidationError as e:
            error_logger.error(f"Validation error in book_seat: {e}", exc_info=True)
            console.print(f"\n[red]Validation error:[/red] {e}")
            raise
        except BusError as e:
            error_logger.error(f"Bus error in book_seat: {e}", exc_info=True)
            console.print(f"\n[red]Bus error:[/red] {e}")
            raise
        except DatabaseError as e:
            error_logger.error(f"Database error in book_seat: {e}", exc_info=True)
            console.print(f"\n[red]Database error:[/red] {e}")
            raise
        except BookingError as e:
            error_logger.error(f"Booking error in book_seat: {e}", exc_info=True)
            console.print(f"\n[red]Booking error:[/red] {e}")
            raise
        except Exception as e:
            error_msg = f"Failed to book seat: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            console.print(f"\n[red]Unexpected error in book_seat:[/red] {e}")
            raise ValidationError(error_msg)

    def export_bookings_to_csv(self, filepath: str) -> bool:
        """Export all bookings to a CSV file."""
        try:
            app_logger.info(f"Exporting all bookings to CSV: {filepath}")
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
            
            app_logger.info(f"Successfully exported {len(bookings)} bookings to {filepath}")
            return True
        except Exception as e:
            error_msg = f"Error exporting bookings to CSV: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            return False
            
    def export_user_bookings_to_csv(self, user_id: int, filepath: str) -> bool:
        """Export bookings for a specific user to a CSV file."""
        try:
            app_logger.info(f"Exporting bookings for user {user_id} to CSV: {filepath}")
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
            
            app_logger.info(f"Successfully exported {len(bookings)} bookings for user {user_id} to {filepath}")
            return True
        except Exception as e:
            error_msg = f"Error exporting user bookings to CSV: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            return False 