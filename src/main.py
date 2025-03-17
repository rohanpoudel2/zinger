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

install(show_locals=False)
console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_interrupt(signum, frame):
    """Handle interrupt signal (Ctrl+C)."""
    clear_screen()
    console.print("\n[yellow]Shutting down...[/yellow]")
    os._exit(0)

def update_bus_data(db_manager: DatabaseManager):
    """Update bus data periodically in a separate thread with its own session."""
    while True:
        with db_manager.get_session() as thread_session:
            try:
                transit_service = TransitService(thread_session)
                transit_service.update_bus_database()
                time.sleep(30)
            except Exception as e:
                console.print(f"\n[red]Error updating bus data:[/red] {str(e)}")

def main():
    signal.signal(signal.SIGINT, handle_interrupt)
    
    clear_screen()
    
    db_manager = DatabaseManager()
    
    update_thread = threading.Thread(
        target=update_bus_data,
        args=(db_manager,),
        daemon=True
    )
    update_thread.start()
    
    with db_manager.get_session() as session:
        user_repository = UserRepository(session)
        booking_repository = BookingRepository(session)
        bus_repository = BusRepository(session)
        
        booking_service = BookingService(booking_repository, bus_repository)
        auth_service = AuthService(user_repository)
        location_service = LocationService()
        
        menu = Menu(booking_service, auth_service, location_service)
        
        try:
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
