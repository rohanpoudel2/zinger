import logging
from utils.logger import setup_logger
from utils.storage import InMemoryStorage
from utils.menu import Menu
from utils.tracking import BusTracker

class BusTrackingSystem:
    def __init__(self):
        self.logger = setup_logger()
        self.storage = InMemoryStorage()
        self.menu = Menu()
        self.tracker = BusTracker()
    
    def view_available_buses(self):
        buses = self.storage.get_all_buses()
        
        print("\n--- Available Buses ---")
        for bus in buses.values():
            available_seats = len(bus.get_available_seats())
            print(f"Bus {bus.bus_number}: {bus.route} | "
                  f"{bus.departure} | {available_seats} seats | ${bus.fare}")
        
        self.menu.pause()
    
    def view_my_bookings(self):
        """Handle viewing user's bookings."""
        bookings = self.storage.get_all_bookings()
        
        if not bookings:
            print("\nNo bookings found.")
        else:
            for ticket in bookings:
                print(ticket.get_details())
        
        self.menu.pause()
    
    def book_ticket(self):
        """Handle ticket booking."""
        booking_data = self.menu.display_booking_menu()
        if not booking_data:
            return
        
        try:
            booking_id = self.storage.create_booking(**booking_data)
            self.menu.display_success(f"Booking confirmed! Your booking ID is: {booking_id}")
        except ValueError as e:
            self.menu.display_error(str(e))
    
    def cancel_booking(self):
        """Handle booking cancellation."""
        booking_id = self.menu.display_cancellation_menu()
        
        try:
            self.storage.cancel_booking(booking_id)
            self.menu.display_success(f"Booking #{booking_id} has been cancelled")
        except ValueError as e:
            self.menu.display_error(str(e))
    
    def track_bus(self):
        """Handle bus tracking."""
        booking_id = self.menu.display_tracking_menu()
        
        booking = self.storage.get_booking(booking_id)
        if not booking:
            self.menu.display_error("Invalid booking ID!")
        elif booking.status == "Cancelled":
            self.menu.display_error("This booking has been cancelled!")
        else:
            try:
                self.tracker.track_bus(
                    bus_number=booking.bus.bus_number,
                    route=booking.bus.route,
                    departure=booking.bus.departure
                )
            except KeyboardInterrupt:
                pass
            finally:
                self.menu.pause()
    
    def run(self):
        """Main application loop."""
        while True:
            choice = self.menu.display_main_menu()
            
            try:
                if choice == '1':
                    self.logger.info("Selected: View Available Buses")
                    self.view_available_buses()
                elif choice == '2':
                    self.logger.info("Selected: View My Bookings")
                    self.view_my_bookings()
                elif choice == '3':
                    self.logger.info("Selected: Book a Ticket")
                    self.book_ticket()
                elif choice == '4':
                    self.logger.info("Selected: Cancel Booking")
                    self.cancel_booking()
                elif choice == '5':
                    self.logger.info("Selected: Track Bus")
                    self.track_bus()
                elif choice == '6':
                    self.logger.info("Exiting application")
                    print("\nThank you for using Bus Tracking System!")
                    break
                else:
                    self.menu.display_error("Invalid option")
                    
            except Exception as e:
                self.logger.error(f"An error occurred: {str(e)}")
                self.menu.display_error(str(e))

if __name__ == '__main__':
    app = BusTrackingSystem()
    app.run()