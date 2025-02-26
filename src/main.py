import logging
from utils.logger import setup_logger
from utils.storage import InMemoryStorage
from utils.menu import Menu
from utils.tracking import BusTracker
from models.bus import Bus
from models.booking import Booking
from exceptions import BookingError


class BusTrackingSystem:
    def __init__(self):
        self.logger = setup_logger()
        self.storage = InMemoryStorage()
        self.menu = Menu()
        self.tracker = BusTracker()
        self.booking = Booking()

    def view_available_buses(self):
        self.booking.view_available_buses()
        self.menu.pause()

    def view_my_bookings(self):
        """Handle viewing user's bookings."""
        bookings = self.booking.view_bookings()
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
            booking_id = self.booking.create_booking(**booking_data)
            self.menu.display_success(
                f"Booking confirmed! Your booking ID is: {booking_id}")
        except (BookingError, ValueError) as e:
            self.menu.display_error(str(e))

    def cancel_booking(self):
        """Handle booking cancellation."""
        booking_id = self.menu.display_cancellation_menu()
        try:
            self.booking.cancel_booking(booking_id)
            self.menu.display_success(
                f"Booking #{booking_id} has been cancelled")
        except ValueError as e:
            self.menu.display_error(str(e))

    def track_bus(self):
        """Handle bus tracking."""
        booking_id = self.menu.display_tracking_menu()
        try:
            bus = self.booking.track_bus(booking_id)
            self.tracker.track_bus(
                bus_number=bus.bus_number,
                route=bus.route,
                departure=bus.departure
            )
        except BookingError as e:
            self.menu.display_error(str(e))
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
