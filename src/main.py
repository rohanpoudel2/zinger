from services.booking_service import BookingService
from services.auth_service import AuthService
from services.transit_service import TransitService
from services.location_service import LocationService
from repositories.user_repository import UserRepository
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from menu import Menu
from utils.database_manager import DatabaseManager
from rich.console import Console
from rich.traceback import install
import os
import signal
import threading
import time

# Install rich traceback handler
install(show_locals=False)
console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_interrupt(signum, frame):
    """Handle interrupt signal gracefully."""
    clear_screen()
    console.print("\n[yellow]Shutting down...[/yellow]")
    exit(0)

def update_bus_data(transit_service: TransitService):
    """Periodically update bus data."""
    while True:
        try:
            transit_service.update_bus_database()
            time.sleep(60)  # Update every minute
        except Exception as e:
            console.print(f"[red]Error updating bus data:[/red] {str(e)}")
            time.sleep(5)

def main():
    # Set up interrupt handler
    signal.signal(signal.SIGINT, handle_interrupt)
    
    # Clear screen on startup
    clear_screen()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Initialize services
    transit_service = TransitService(db_manager)
    location_service = LocationService()
    
    # Start bus data update thread
    update_thread = threading.Thread(
        target=update_bus_data,
        args=(transit_service,),
        daemon=True
    )
    update_thread.start()
    
    # Get database session
    with db_manager.get_session() as session:
        # Initialize repositories with session
        user_repository = UserRepository(session)
        booking_repository = BookingRepository(session)
        bus_repository = BusRepository(session)
        
        # Initialize services
        booking_service = BookingService(booking_repository, bus_repository)
        auth_service = AuthService(user_repository)
        
        # Initialize menu
        menu = Menu(booking_service, auth_service, location_service)
        
        try:
            # Initial bus data update
            transit_service.update_bus_database()
            
            # Start the application
            menu.display_main_menu()
        except KeyboardInterrupt:
            clear_screen()
            console.print("\n[yellow]Shutting down...[/yellow]")
        except Exception as e:
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
        finally:
            db_manager.close()

if __name__ == "__main__":
    main()
