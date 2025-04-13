import tkinter as tk
from tkinter import ttk
import os
import sys
import threading

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.booking_service import BookingService
from services.auth_service import AuthService
from services.location_service import LocationService
from services.transit_service import TransitService
from repositories.user_repository import UserRepository
from repositories.booking_repository import BookingRepository
from repositories.bus_repository import BusRepository
from utils.database_manager import DatabaseManager
from config.logging_config import setup_logging
import logging

from views.context.app_context import AppContext
from views.pages.app import App

class BusBookingGUI:
    """Main GUI application wrapper (initializes services and runs App)."""
    
    def __init__(self):
        """Initialize the application."""
        # Setup logging
        setup_logging()
        
        # Get loggers
        self.app_logger = logging.getLogger('app')
        self.error_logger = logging.getLogger('error')
        self.access_logger = logging.getLogger('access')
        
        self.app_logger.info("GUI Application starting...")
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        self.app_logger.info("Database initialized")
        
        # Initialize services with a session
        self.session = self.db_manager.Session()
        
        # Initialize repositories
        self.user_repository = UserRepository(self.session)
        self.booking_repository = BookingRepository(self.session)
        self.bus_repository = BusRepository(self.session)
        
        # Initialize services
        self.location_service = LocationService()
        self.auth_service = AuthService(self.user_repository)
        self.booking_service = BookingService(
            booking_repo=self.booking_repository,
            bus_repo=self.bus_repository,
            user_repo=self.user_repository
        )
        self.transit_service = TransitService(self.session)
        
        # Initialize the application context
        self.context = AppContext()
        
        # Register services with the context
        self.context.register_service('auth_service', self.auth_service)
        self.context.register_service('booking_service', self.booking_service)
        self.context.register_service('location_service', self.location_service)
        self.context.register_service('transit_service', self.transit_service)
        
        self.app_logger.info("Services initialized and registered with context")
        
        # Start background update thread
        self.update_thread = threading.Thread(
            target=self.transit_service.start_periodic_updates,
            args=(self.location_service,),
            daemon=True
        )
        self.update_thread.start()
        self.app_logger.info("Background update thread started")
        
        # Create and configure the main application component
        self.app = App() # App now inherits from tk.Tk
        self.app.protocol("WM_DELETE_WINDOW", self.on_close) # Set protocol on App
        # No packing or mounting needed as App is the root window
        
        # Register app component with context (optional, if needed by services)
        # self.context.register_service('app', self.app)
        
        self.app_logger.info("GUI Application initialized and ready")
    
    def run(self):
        """Run the application main loop."""
        self.app_logger.info("Starting GUI application main loop")
        self.app.mainloop() # Call mainloop on the App instance
    
    def on_close(self):
        """Handle application closure."""
        self.app_logger.info("Application closing...")
        
        # Perform cleanup
        try:
            if hasattr(self, 'session'):
                self.session.close()
            
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
                
            self.app_logger.info("Application resources cleaned up")
        except Exception as e:
            self.error_logger.error(f"Error during application cleanup: {str(e)}")
        
        # Destroy the root window (which is now the App instance)
        self.app.destroy()
        
        self.app_logger.info("Application closed")

if __name__ == "__main__":
    gui = BusBookingGUI()
    gui.run() 