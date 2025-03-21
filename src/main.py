from services.booking_service import BookingService
from services.auth_service import AuthService
from services.location_service import LocationService
from services.transit_service import TransitService
from repositories.user_repository import UserRepository
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from utils.database_manager import DatabaseManager
from menu import Menu
from rich.console import Console
from rich.traceback import install
import os
import threading
import time
from config.logging_config import setup_logging
import logging

install(show_locals=False)
console = Console()

# Get loggers
app_logger = logging.getLogger('app')
error_logger = logging.getLogger('error')
access_logger = logging.getLogger('access')

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_interrupt(signum, frame):
    """Handle interrupt signal (Ctrl+C)."""
    clear_screen()
    console.print("\n[yellow]Shutting down...[/yellow]")
    access_logger.info("Application shutdown by interrupt signal")
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
                error_msg = f"Error updating bus data: {str(e)}"
                error_logger.error(error_msg, exc_info=True)
                console.print(f"\n[red]Error updating bus data:[/red] {str(e)}")

def main():
    # Setup logging
    setup_logging()
    
    app_logger.info("Application starting...")
    access_logger.info("Application initialization begun")

    try:
        # Initialize services and repositories
        db_manager = DatabaseManager()
        app_logger.info("Database manager initialized")
        
        # Create tables if they don't exist
        db_manager.create_tables()
        app_logger.info("Database tables created/verified")
        
        # Initialize location service first
        location_service = LocationService()
        app_logger.info("Location service initialized")
        
        # Create a session for TransitService (will be used in background thread)
        transit_session = db_manager.Session()
        transit_service = TransitService(transit_session)
        app_logger.info("Transit service initialized")
        
        # Start the background update thread
        update_thread = threading.Thread(
            target=transit_service.start_periodic_updates,
            args=(location_service,),
            daemon=True
        )
        update_thread.start()
        app_logger.info("Background update thread started")
        
        # Use a context manager for the main session
        with db_manager.get_session() as session:
            user_repository = UserRepository(session)
            booking_repository = BookingRepository(session)
            bus_repository = BusRepository(session)
            
            booking_service = BookingService(
                booking_repo=booking_repository,
                bus_repo=bus_repository,
                user_repo=user_repository
            )
            auth_service = AuthService(user_repository)
            
            app_logger.info("All services and repositories initialized")
            
            # Initialize and start the menu
            menu = Menu(
                booking_service=booking_service,
                auth_service=auth_service,
                location_service=location_service,
                db_session=session
            )
            app_logger.info("Menu initialized, starting application interface")
            menu.start()
            
    except Exception as e:
        error_msg = f"Critical application error: {str(e)}"
        error_logger.critical(error_msg, exc_info=True)
        print(f"Application error: {str(e)}")
    finally:
        if 'transit_session' in locals():
            transit_session.close()
        if 'db_manager' in locals():
            db_manager.close()
        app_logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
