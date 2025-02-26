from typing import Callable, Dict, Optional
from utils.logger import setup_logger
from utils.storage import InMemoryStorage
import os 
import re  # Add this import
from exceptions import BusReservationError, BookingError, ValidationError, StorageError

class Menu:
    def __init__(self):
        self.logger = setup_logger()
        self.current_user_role = "passenger"
        self.storage = InMemoryStorage()
        # Add phone regex pattern
        self.phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Unix/Linux/MacOS
        else:
            os.system('clear')
    
    def display_header(self, title: str) -> None:
        """Display a formatted header for menus."""
        self.clear_screen()  # Clear screen before displaying header
        print(f"\n=== {title} ===")
        print("=" * (len(title) + 8))
    
    def get_input(self, prompt: str) -> str:
        """Get user input with a prompt."""
        return input(f"{prompt}: ")
    
    def pause(self) -> None:
        """Pause execution until user presses Enter."""
        input("\nPress Enter to continue...")
    
    def display_main_menu(self) -> str:
        """Display main menu and get user choice."""
        self.clear_screen()  # Clear before showing main menu
        self.display_header("Welcome to Bus Tracking System")
        
        options = {
            "1": "View Available Buses",
            "2": "My Bookings",
            "3": "Book a Ticket",
            "4": "Cancel My Booking",
            "5": "Track My Bus",
            "6": "Exit"
        }
        
        for key, value in options.items():
            print(f"{key}. {value}")
            
        return self.get_input("\nSelect an option (1-6)")
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        return bool(self.phone_pattern.match(phone))

    def display_booking_menu(self) -> Optional[Dict[str, str]]:
        """Display booking menu and collect booking information."""
        try:
            self.clear_screen()
            self.display_header("Book a Ticket")
            
            # Show available buses first
            print("\nAvailable Buses:")
            buses = self.storage.get_all_buses()
            if not buses:
                raise StorageError("No buses available")

            for bus in buses.values():
                available_seats = len(bus.get_available_seats())
                print(f"Bus {bus.bus_number}: {bus.route} | "
                      f"{bus.departure} | {available_seats} seats | ${bus.fare}")
            
            bus_number = self.get_input("\nEnter Bus Number")
            if not bus_number:
                return None
                
            bus = self.storage.get_bus(bus_number)
            if not bus:
                raise ValidationError(f"Invalid bus number: {bus_number}")

            available_seats = bus.get_available_seats()
            if not available_seats:
                raise BookingError("No seats available on this bus")

            print("\nAvailable Seats:", ", ".join(available_seats))
            
            passenger_name = self.get_input("Enter Passenger Name")
            if not passenger_name.strip():
                raise ValidationError("Passenger name is required")

            phone = self.get_input("Enter Phone Number")
            if not phone.strip():
                raise ValidationError("Phone number is required")
            if not self.validate_phone(phone):
                raise ValidationError("Invalid phone number format. Please enter 9-15 digits (optional +1 prefix)")

            seat = self.get_input("Enter Seat Number (e.g., 1A)").upper()
            
            return {
                "bus_number": bus_number,
                "passenger_name": passenger_name,
                "phone": phone,
                "seat": seat
            }

        except BusReservationError as e:
            self.logger.error(f"Booking menu error: {str(e)}")
            self.display_error(str(e))
            return None
    
    def display_cancellation_menu(self) -> str:
        """Display cancellation menu and get booking ID."""
        self.display_header("Cancel Booking")
        return self.get_input("Enter Booking ID to cancel")
    
    def display_tracking_menu(self) -> str:
        """Display tracking menu and get booking ID."""
        self.display_header("Track My Bus")
        return self.get_input("Enter Booking ID")
    
    def display_error(self, message: str) -> None:
        """Display error message."""
        self.clear_screen()  # Clear before showing error
        print(f"\nError: {message}")
        self.pause()
    
    def display_success(self, message: str) -> None:
        """Display success message."""
        self.clear_screen()  # Clear before showing success message
        print(f"\nSuccess: {message}")
        self.pause() 