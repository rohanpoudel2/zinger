from services.booking_service import BookingService
from services.auth_service import AuthService
from services.location_service import LocationService
from models.database_models import UserRole, BusModel
from exceptions import ValidationError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from sqlalchemy.orm import Session
import os
import signal
import sys
from datetime import datetime
import logging

console = Console()

# Get loggers
app_logger = logging.getLogger('app')
auth_logger = logging.getLogger('auth')
error_logger = logging.getLogger('error')
access_logger = logging.getLogger('access')

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Menu:
    def __init__(
        self,
        booking_service: BookingService,
        auth_service: AuthService,
        location_service: LocationService,
        db_session: Session
    ):
        self.booking_service = booking_service
        self.auth_service = auth_service
        self.location_service = location_service
        self.db_session = db_session
        self.current_user = None
        signal.signal(signal.SIGINT, self._handle_interrupt)
        app_logger.info("Menu system initialized with all services")
        access_logger.info("Menu system initialized")

    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interrupt."""
        clear_screen()
        console.print("\n[yellow]Shutting down...[/yellow]")
        access_logger.info("Application shutdown initiated by user interrupt")
        app_logger.info("Application terminated by user interrupt")
        sys.exit(0)

    def start(self):
        """Start the menu system."""
        clear_screen()
        try:
            app_logger.info("Menu system starting")
            access_logger.info("Menu system started")
            self.display_main_menu()
        except KeyboardInterrupt:
            clear_screen()
            console.print("\n[yellow]Shutting down...[/yellow]")
            access_logger.info("Application shutdown by keyboard interrupt")
            app_logger.info("Application terminated by keyboard interrupt")
        except Exception as e:
            error_msg = f"Unexpected error in menu system: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error(f"Critical error in menu system: {str(e)}")
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")

    def display_main_menu(self) -> None:
        """Display the main menu options."""
        while True:
            clear_screen()
            if self.auth_service.is_authenticated():
                user = self.auth_service.get_current_user()
                location_info = ""
                if self.location_service.get_location_name():
                    location_info = f" - Location: [yellow]{self.location_service.get_location_name()}[/yellow]"
                console.print(Panel(f"[blue]Bus Booking System[/blue] - Logged in as [green]{user.username}[/green] ({str(user.role).split('.')[-1]}){location_info}"))
                app_logger.debug(f"Displaying authenticated menu for user: {user.username}")
                self._display_authenticated_menu()
            else:
                location_info = ""
                if self.location_service.get_location_name():
                    location_info = f" - Location: [yellow]{self.location_service.get_location_name()}[/yellow]"
                console.print(Panel(f"[blue]Bus Booking System[/blue]{location_info}"))
                app_logger.debug("Displaying unauthenticated menu")
                self._display_unauthenticated_menu()

    def _display_unauthenticated_menu(self) -> None:
        """Display menu options for unauthenticated users."""
        app_logger.debug("Showing unauthenticated menu options")
        console.print("\n1. [cyan]Login[/cyan]")
        console.print("2. [cyan]Register[/cyan]")
        console.print("3. [cyan]View Available Buses[/cyan]")
        console.print("4. [red]Exit[/red]")

        choice = Prompt.ask("\nEnter your choice (1-4): ")
        app_logger.debug(f"Unauthenticated user selected option: {choice}")
        
        try:
            if choice == "1":
                self.login()
            elif choice == "2":
                self.register()
            elif choice == "3":
                self.view_available_buses()
            elif choice == "4":
                clear_screen()
                console.print("\n[green]Thank you for using the Bus Booking System![/green]")
                app_logger.info("User initiated normal application shutdown")
                access_logger.info("Application shutdown by user selection")
                exit()
            else:
                app_logger.warning(f"Invalid menu choice attempted: {choice}")
                console.print("[red]Invalid choice. Please try again.[/red]")
                self._pause()
        except ValidationError as e:
            error_logger.error(f"Validation error in unauthenticated menu: {str(e)}")
            console.print(f"\n[red]Error:[/red] {str(e)}")
            self._pause()
        except Exception as e:
            error_logger.error(f"Unexpected error in unauthenticated menu: {str(e)}", exc_info=True)
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            self._pause()

    def _display_authenticated_menu(self) -> None:
        """Display menu options for authenticated users."""
        user = self.auth_service.get_current_user()
        app_logger.debug(f"Showing authenticated menu options for user: {user.username}")
        
        console.print("\n1. [cyan]View Available Buses[/cyan]")
        console.print("2. [cyan]Book a Ticket[/cyan]")
        console.print("3. [cyan]View My Bookings[/cyan]")
        console.print("4. [cyan]Logout[/cyan]")
        console.print("5. [red]Exit[/red]")

        if user.role == UserRole.ADMIN:
            app_logger.debug("Showing additional admin options")
            console.print("\n[yellow]Admin Options:[/yellow]")
            console.print("6. [cyan]View All Bookings[/cyan]")
            console.print("7. [cyan]Manage Users[/cyan]")
            console.print("8. [cyan]Export Bookings to CSV[/cyan]")
            max_choice = 8
        else:
            max_choice = 5

        choice = Prompt.ask(f"\nEnter your choice (1-{max_choice}): ")
        app_logger.debug(f"User {user.username} selected option: {choice}")
        
        try:
            if choice == "1":
                self.view_available_buses()
            elif choice == "2":
                self.book_seat()
            elif choice == "3":
                self.view_user_bookings()
            elif choice == "4":
                self.auth_service.logout()
                app_logger.info(f"User {user.username} logged out")
                access_logger.info(f"User {user.username} logged out")
                console.print("[green]Logged out successfully.[/green]")
            elif choice == "5":
                clear_screen()
                console.print("\n[green]Thank you for using the Bus Booking System![/green]")
                app_logger.info(f"User {user.username} initiated normal application shutdown")
                access_logger.info("Application shutdown by user selection")
                exit()
            elif choice == "6" and user.role == UserRole.ADMIN:
                self._view_all_bookings()
            elif choice == "7" and user.role == UserRole.ADMIN:
                self._manage_users()
            elif choice == "8" and user.role == UserRole.ADMIN:
                self._export_bookings_to_csv()
            else:
                app_logger.warning(f"Invalid menu choice attempted by user {user.username}: {choice}")
                console.print("[red]Invalid choice. Please try again.[/red]")
                self._pause()
        except ValidationError as e:
            error_logger.error(f"Validation error in authenticated menu for user {user.username}: {str(e)}")
            console.print(f"\n[red]Error:[/red] {str(e)}")
            self._pause()
        except Exception as e:
            error_logger.error(f"Unexpected error in authenticated menu for user {user.username}: {str(e)}", exc_info=True)
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            self._pause()

    def login(self):
        """Handle user login."""
        console.print("\n[bold cyan]Login[/bold cyan]")
        
        username = Prompt.ask("\nUsername")
        password = Prompt.ask("Password", password=True)
        
        try:
            auth_logger.info(f"Login attempt for user: {username}")
            user = self.auth_service.login(username, password)
            if user:
                self.current_user = user
                auth_logger.info(f"Login successful for user: {username} (ID: {user.id})")
                access_logger.info(f"User {username} (ID: {user.id}) logged in")
                console.print("\n[green]Login successful![/green]")
                self._pause()
            else:
                auth_logger.warning(f"Failed login attempt for user: {username}")
                console.print("\n[red]Invalid username or password[/red]")
                self._pause()
        except Exception as e:
            error_msg = f"Login error for user {username}: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            auth_logger.error(f"Login failed for user {username}: {str(e)}")
            console.print(f"\n[red]Login failed:[/red] {str(e)}")
            self._pause()

    def register(self):
        """Handle user registration."""
        console.print("\n[bold cyan]Register New User[/bold cyan]")
        
        username = Prompt.ask("\nUsername")
        password = Prompt.ask("Password", password=True)
        confirm_password = Prompt.ask("Confirm Password", password=True)
        
        if password != confirm_password:
            auth_logger.warning(f"Registration failed for user {username}: Passwords do not match")
            console.print("\n[red]Passwords do not match[/red]")
            self._pause()
            return
        
        try:
            auth_logger.info(f"Registration attempt for user: {username}")
            user = self.auth_service.register(username, password)
            if user:
                auth_logger.info(f"Registration successful for user: {username} (ID: {user.id})")
                console.print("\n[green]Registration successful! Please login.[/green]")
            else:
                auth_logger.warning(f"Registration failed for user: {username}")
                console.print("\n[red]Registration failed[/red]")
            self._pause()
        except Exception as e:
            error_msg = f"Registration error for user {username}: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            auth_logger.error(f"Registration failed for user {username}: {str(e)}")
            console.print(f"\n[red]Registration failed:[/red] {str(e)}")
            self._pause()

    def view_available_buses(self) -> None:
        """Display available buses with real-time information."""
        try:
            app_logger.info("User accessing available buses view")
            # Get all active buses within 5km of UNH
            buses = self.db_session.query(BusModel).filter(
                BusModel.is_active == True,
                BusModel.distance_to_user <= 5.0,
                BusModel.route.isnot(None),
                BusModel.route != '',
                BusModel.route != '-',
                ~BusModel.route.contains(' - Route '),  # Skip duplicated route numbers
                ~BusModel.route.contains('Unknown')
            ).order_by(BusModel.distance_to_user).all()
            
            app_logger.debug(f"Found {len(buses)} total buses before filtering")
            
            # Further filter to keep only buses with descriptive route names
            valid_buses = []
            for bus in buses:
                # Skip if the route doesn't have a proper format
                if not bus.route or ' - ' not in bus.route:
                    continue
                
                # Split the route into number and name
                parts = bus.route.split(' - ', 1)
                if len(parts) != 2:
                    continue
                    
                route_number, route_name = parts
                
                # Skip if route name is just a duplicate of the route number
                if route_name == route_number or route_name == f"Route {route_number}":
                    continue
                    
                # Skip if route name is empty
                if not route_name.strip():
                    continue
                
                # Clean up route format to be consistent
                if route_number.startswith('Route '):
                    route_number = route_number.replace('Route ', '')
                
                # Update the route to have a clean format
                bus.route = f"{route_number} - {route_name}"
                valid_buses.append(bus)
            
            app_logger.info(f"Displaying {len(valid_buses)} valid buses to user")
            
            if not valid_buses:
                app_logger.info("No valid buses available to display")
                console.print("\nNo buses currently available near UNH.")
                self._pause()
                return

            console.print("\n[bold cyan]Real-time Bus Information[/bold cyan]")
            console.print("[italic]Showing buses within 5km of University of New Haven[/italic]")
            console.print("[dim]Distance shows how far the bus is from UNH campus[/dim]")
            
            # Create table for bus information
            table = Table(
                title="Available Buses Near UNH",
                box=box.DOUBLE,
                show_header=True,
                header_style="bold magenta",
                padding=(0, 1),
                collapse_padding=False,
                width=100
            )
            
            # Add columns with specific widths
            table.add_column("Bus #", justify="center", style="cyan", width=8)
            table.add_column("Route", justify="left", style="green", width=50, overflow="fold")
            table.add_column("Distance", justify="right", style="yellow", width=12)
            table.add_column("Last Update", justify="center", style="blue", width=12)
            table.add_column("Status", justify="center", style="red", width=8)

            # Add rows for each bus
            for bus in valid_buses:
                # Format distance with proper units
                if hasattr(bus, 'distance_to_user') and bus.distance_to_user is not None:
                    # Convert km to miles (1 km ≈ 0.621371 miles)
                    distance_miles = bus.distance_to_user * 0.621371
                    if bus.distance_to_user < 0.1:  # Less than 100m
                        distance_display = "At stop"
                    elif bus.distance_to_user < 1:
                        # Convert meters to feet (1m ≈ 3.28084 feet)
                        feet = bus.distance_to_user * 1000 * 3.28084
                        distance_display = f"{feet:.0f}ft"
                    else:
                        distance_display = f"{distance_miles:.1f}mi"
                else:
                    distance_display = "N/A"
                
                # Format last update time
                if hasattr(bus, 'last_updated') and bus.last_updated:
                    time_diff = datetime.now() - bus.last_updated
                    if time_diff.total_seconds() < 60:  # Less than a minute
                        last_update = "Just now"
                    elif time_diff.total_seconds() < 3600:  # Less than an hour
                        minutes = int(time_diff.total_seconds() // 60)
                        last_update = f"{minutes}m ago"
                    else:
                        last_update = bus.last_updated.strftime("%I:%M%p")
                else:
                    last_update = "N/A"
                
                # Get bus status based on speed
                if hasattr(bus, 'speed') and bus.speed is not None:
                    if bus.speed < 1:  # Less than 1 mph
                        status = "■ STOP"
                    elif bus.speed < 10:  # Less than 10 mph
                        status = "▲ SLOW"
                    else:
                        status = "● MOVE"
                else:
                    status = "N/A"
                
                table.add_row(
                    bus.bus_number,
                    bus.route,
                    distance_display,
                    last_update,
                    status
                )
                app_logger.debug(f"Added bus {bus.bus_number} to display table")

            console.print(table)
            console.print("\n[dim]Status Legend: ■ STOP = Stopped, ▲ SLOW = Moving slowly, ● MOVE = Moving normally[/dim]")
            
        except Exception as e:
            error_msg = f"Error displaying available buses: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error(f"Failed to display available buses: {str(e)}")
            console.print(f"\n[red]Error displaying available buses: {str(e)}[/red]")
        
        self._pause()

    def _pause(self) -> None:
        """Pause execution until user presses Enter."""
        Prompt.ask("\n[cyan]Press Enter to continue...[/cyan]")

    def book_seat(self) -> None:
        """Book a seat on a bus."""
        try:
            # Require authentication
            try:
                self.auth_service.require_auth()
            except Exception as e:
                console.print(f"\n[red]Authentication required:[/red] {str(e)}")
                self._pause()
                return
                
            console.print("\n[bold cyan]Book a Seat[/bold cyan]")
            
            # Show available buses
            self.view_available_buses()
            
            # Get bus number
            bus_number = console.input("\nEnter bus number to book: ")
            
            # Get passenger name
            passenger_name = console.input("Enter passenger name: ")
            if not passenger_name:
                console.print("[red]Passenger name cannot be empty[/red]")
                self._pause()
                return
                
            # Get phone number
            phone_number = console.input("Enter phone number: ")
            if not phone_number:
                console.print("[red]Phone number cannot be empty[/red]")
                self._pause()
                return
                
            # Book the seat, passing the auth_service instance
            booking_id = self.booking_service.book_seat(
                bus_number, 
                passenger_name, 
                phone_number,
                auth_service=self.auth_service
            )
            
            console.print("\n[green]Booking successful![/green]")
            console.print(f"Booking ID: {booking_id}")
            console.print(f"Bus: {bus_number}")
            console.print(f"Passenger: {passenger_name}")
            console.print(f"Phone: {phone_number}")
            
        except Exception as e:
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            
        self._pause()

    def view_user_bookings(self):
        """Display user's bookings."""
        try:
            # Require authentication
            try:
                self.auth_service.require_auth()
                user = self.auth_service.get_current_user()
            except Exception as e:
                console.print(f"\n[red]Authentication required:[/red] {str(e)}")
                self._pause()
                return
                
            bookings = self.booking_service.get_user_bookings(user.id)
            
            if not bookings:
                console.print("\n[yellow]You have no bookings[/yellow]")
                self._pause()
                return
            
            table = Table(
                title="Your Bookings",
                box=box.DOUBLE,
                show_header=True,
                header_style="bold"
            )
            
            table.add_column("Booking ID", justify="center")
            table.add_column("Bus", justify="left")
            table.add_column("Route", justify="left")
            table.add_column("Status", justify="center")
            table.add_column("Booked On", justify="center")
            
            for booking in bookings:
                bus = self.db_session.query(BusModel).get(booking.bus_id)
                if bus:
                    booking_time = booking.booking_time.strftime("%Y-%m-%d %H:%M") if booking.booking_time else "N/A"
                    table.add_row(
                        str(booking.id),
                        bus.bus_number,
                        bus.route or "N/A",
                        booking.status,
                        booking_time
                    )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"\n[red]Error retrieving bookings:[/red] {str(e)}")
            import traceback
            console.print(traceback.format_exc())
        
        self._pause()

    def _view_all_bookings(self) -> None:
        """View all bookings (admin only)."""
        try:
            app_logger.info("Admin accessing all bookings view")
            self.auth_service.require_role(UserRole.ADMIN)
            bookings = self.booking_service.get_all_bookings()
            
            if not bookings:
                app_logger.info("No bookings found to display")
                console.print("\n[yellow]No bookings found.[/yellow]")
                self._pause()
                return

            table = Table(title="All Bookings")
            table.add_column("Booking ID", style="cyan")
            table.add_column("User ID", style="magenta")
            table.add_column("Bus Number", style="green")
            table.add_column("Passenger", style="blue")
            table.add_column("Phone", style="blue")
            table.add_column("Status", style="red")
            table.add_column("Booking Time", style="yellow")

            for booking in bookings:
                # Get bus details
                bus = self.db_session.query(BusModel).get(booking.bus_id)
                bus_number = bus.bus_number if bus else "N/A"
                
                # Format booking time
                booking_time = booking.booking_time.strftime("%Y-%m-%d %H:%M") if booking.booking_time else "N/A"
                
                table.add_row(
                    str(booking.id),
                    str(booking.user_id) if booking.user_id else "N/A",
                    bus_number,
                    booking.passenger_name,
                    booking.phone_number,
                    booking.status,
                    booking_time
                )
                app_logger.debug(f"Added booking {booking.id} to display table")

            console.print(table)
            app_logger.info(f"Displayed {len(bookings)} bookings to admin")
        except Exception as e:
            error_msg = f"Error viewing all bookings: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error("Failed to display all bookings")
            console.print(f"\n[red]An error occurred while viewing all bookings:[/red] {str(e)}")
        self._pause()

    def _manage_users(self) -> None:
        """Manage user accounts (admin only)."""
        try:
            app_logger.info("Admin accessing user management")
            self.auth_service.require_role(UserRole.ADMIN)
            
            console.print("\n[yellow]User Management[/yellow]")
            console.print("1. [cyan]View All Users[/cyan]")
            console.print("2. [cyan]Deactivate User Account[/cyan]")
            console.print("3. [cyan]Back to Main Menu[/cyan]")
            
            choice = console.input("\nEnter your choice (1-3): ")
            app_logger.debug(f"Admin selected user management option: {choice}")
            
            try:
                if choice == "1":
                    self._view_all_users()
                elif choice == "2":
                    self._deactivate_user()
                elif choice == "3":
                    return
                else:
                    app_logger.warning(f"Invalid user management choice attempted: {choice}")
                    console.print("[red]Invalid choice. Please try again.[/red]")
            except ValidationError as e:
                error_logger.error(f"Validation error in user management: {str(e)}")
                console.print(f"[red]Error:[/red] {str(e)}")
        except Exception as e:
            error_msg = f"Error in user management: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error("Failed to access user management")
            console.print(f"\n[red]An error occurred in user management:[/red] {str(e)}")

    def _view_all_users(self, show_admins: bool = True) -> None:
        """View all users (admin only)."""
        users = self.auth_service.get_all_users()
        if not users:
            console.print("\n[yellow]No users found.[/yellow]")
            return

        table = Table(title="All Users")
        table.add_column("ID", style="cyan")
        table.add_column("Username", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Role", style="blue")
        table.add_column("Status", style="yellow")

        for user in users:
            # Skip admin users if show_admins is False
            if not show_admins and user.role == UserRole.ADMIN:
                continue
                
            status = "[green]Active[/green]" if user.is_active else "[red]Inactive[/red]"
            table.add_row(
                str(user.id),
                user.username,
                user.email,
                user.role.value,
                status
            )

        console.print(table)
        self._pause()

    def _deactivate_user(self) -> None:
        """Deactivate a user account (admin only)."""
        # Show only non-admin users for deactivation
        self._view_all_users(show_admins=False)
        user_id = console.input("\nEnter user ID to deactivate: ")
        
        try:
            if self.auth_service.deactivate_user(user_id):
                console.print("[green]User account deactivated successfully.[/green]")
                console.print("[yellow]Note: The user will no longer be able to log in, but their data is preserved.[/yellow]")
            else:
                console.print("[red]Failed to deactivate user account.[/red]")
        except ValidationError as e:
            console.print(f"[red]Error:[/red] {str(e)}")
        self._pause()

    def _export_bookings_to_csv(self) -> None:
        """Export all bookings to a CSV file (admin only)."""
        try:
            app_logger.info("Admin accessing booking export function")
            self.auth_service.require_role(UserRole.ADMIN)
            
            console.print("\n[yellow]Export Bookings to CSV[/yellow]")
            console.print("1. [cyan]Export All Bookings[/cyan]")
            console.print("2. [cyan]Export Bookings for a Specific User[/cyan]")
            console.print("3. [cyan]Back to Main Menu[/cyan]")
            
            choice = console.input("\nEnter your choice (1-3): ")
            app_logger.debug(f"Admin selected export option: {choice}")
            
            try:
                if choice == "1":
                    self._export_all_bookings_to_csv()
                elif choice == "2":
                    self._export_bookings_for_specific_user()
                elif choice == "3":
                    return
                else:
                    app_logger.warning(f"Invalid export choice attempted: {choice}")
                    console.print("[red]Invalid choice. Please try again.[/red]")
            except ValidationError as e:
                error_logger.error(f"Validation error in booking export: {str(e)}")
                console.print(f"[red]Error:[/red] {str(e)}")
        except Exception as e:
            error_msg = f"Error in booking export: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error("Failed to export bookings")
            console.print(f"\n[red]An error occurred during export:[/red] {str(e)}")

    def _export_all_bookings_to_csv(self) -> None:
        """Export all bookings to a CSV file."""
        try:
            app_logger.info("Starting export of all bookings to CSV")
            # Check if there are any bookings
            bookings = self.booking_service.get_all_bookings()
            
            if not bookings:
                app_logger.info("No bookings found to export")
                console.print("\n[yellow]No bookings found.[/yellow]")
                self._pause()
                return

            # Get the export path
            from datetime import datetime
            import os
            
            # Create 'exports' directory if it doesn't exist
            exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            # Default filename with timestamp
            default_filename = f"bookings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filename = Prompt.ask("\nEnter filename to save the CSV file", default=default_filename)
            
            # Make sure filename has .csv extension
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
                
            # Create full filepath
            filepath = os.path.join(exports_dir, filename)
            
            # Export to CSV
            if self.booking_service.export_bookings_to_csv(filepath):
                app_logger.info(f"Successfully exported all bookings to {filepath}")
                console.print(f"\n[green]Bookings exported successfully to:[/green] {filepath}")
            else:
                app_logger.error("Failed to export bookings to CSV")
                console.print("\n[red]Failed to export bookings[/red]")
                
        except Exception as e:
            error_msg = f"Error exporting all bookings: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error(f"Failed to export all bookings: {str(e)}")
            console.print(f"\n[red]Error exporting bookings: {str(e)}[/red]")
        self._pause()

    def _export_bookings_for_specific_user(self) -> None:
        """Export bookings for a specific user."""
        try:
            app_logger.info("Starting export of user-specific bookings")
            # Show user list first
            self._view_all_users()
            
            user_id = Prompt.ask("\nEnter user ID")
            
            if not user_id:
                app_logger.warning("No user ID provided for export")
                console.print("[red]User ID cannot be empty[/red]")
                self._pause()
                return
            
            # Verify user exists
            user = self.auth_service.get_user_by_id(int(user_id))
            if not user:
                app_logger.warning(f"Attempted to export bookings for non-existent user ID: {user_id}")
                console.print("[red]User not found[/red]")
                self._pause()
                return
                
            app_logger.info(f"Exporting bookings for user {user.username} (ID: {user_id})")
            
            # Get user's bookings
            bookings = self.booking_service.get_user_bookings(int(user_id))
            
            if not bookings:
                app_logger.info(f"No bookings found for user {user.username}")
                console.print(f"\n[yellow]No bookings found for user {user.username}.[/yellow]")
                self._pause()
                return

            # Get the export path
            from datetime import datetime
            import os
            
            # Create 'exports' directory if it doesn't exist
            exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            # Default filename with username and timestamp
            default_filename = f"bookings_user_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filename = Prompt.ask("\nEnter filename to save the CSV file", default=default_filename)
            
            # Make sure filename has .csv extension
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
                
            # Create full filepath
            filepath = os.path.join(exports_dir, filename)
            
            # Use the user-specific export function
            if self.booking_service.export_user_bookings_to_csv(int(user_id), filepath):
                app_logger.info(f"Successfully exported bookings for user {user.username} to {filepath}")
                console.print(f"\n[green]Bookings for user {user.username} exported successfully to:[/green] {filepath}")
            else:
                app_logger.error(f"Failed to export bookings for user {user.username}")
                console.print("\n[red]Failed to export bookings[/red]")
                
        except Exception as e:
            error_msg = f"Error exporting user bookings: {str(e)}"
            error_logger.error(error_msg, exc_info=True)
            app_logger.error(f"Failed to export user bookings: {str(e)}")
            console.print(f"\n[red]Error exporting bookings: {str(e)}[/red]")
        self._pause() 