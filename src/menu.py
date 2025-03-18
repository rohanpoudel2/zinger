from typing import Optional
from services.booking_service import BookingService
from services.auth_service import AuthService
from services.location_service import LocationService
from models.database_models import UserRole, BusModel
from exceptions import ValidationError, BookingError, SeatError
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

console = Console()

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

    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interrupt."""
        clear_screen()
        console.print("\n[yellow]Shutting down...[/yellow]")
        sys.exit(0)

    def start(self):
        """Start the menu system."""
        clear_screen()
        try:
            self.display_main_menu()
        except KeyboardInterrupt:
            clear_screen()
            console.print("\n[yellow]Shutting down...[/yellow]")
        except Exception as e:
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            import traceback
            console.print(traceback.format_exc())

    def display_main_menu(self) -> None:
        """Display the main menu options."""
        while True:
            clear_screen()
            if self.auth_service.is_authenticated():
                user = self.auth_service.get_current_user()
                location_info = ""
                if self.location_service.get_location_name():
                    location_info = f" - Location: [yellow]{self.location_service.get_location_name()}[/yellow]"
                console.print(Panel(f"[blue]Bus Booking System[/blue] - Logged in as [green]{user.username}[/green] ({user.role}){location_info}"))
                self._display_authenticated_menu()
            else:
                location_info = ""
                if self.location_service.get_location_name():
                    location_info = f" - Location: [yellow]{self.location_service.get_location_name()}[/yellow]"
                console.print(Panel(f"[blue]Bus Booking System[/blue]{location_info}"))
                self._display_unauthenticated_menu()

    def _display_unauthenticated_menu(self) -> None:
        """Display menu options for unauthenticated users."""
        console.print("\n1. [cyan]Login[/cyan]")
        console.print("2. [cyan]Register[/cyan]")
        console.print("3. [cyan]View Available Buses[/cyan]")
        console.print("4. [red]Exit[/red]")

        choice = Prompt.ask("\nEnter your choice (1-4): ")
        
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
                exit()
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
                self._pause()
        except ValidationError as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            self._pause()
        except Exception as e:
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            self._pause()

    def _display_authenticated_menu(self) -> None:
        """Display menu options for authenticated users."""
        console.print("\n1. [cyan]View Available Buses[/cyan]")
        console.print("2. [cyan]Book a Ticket[/cyan]")
        console.print("3. [cyan]View My Bookings[/cyan]")
        console.print("4. [cyan]Logout[/cyan]")
        console.print("5. [red]Exit[/red]")

        if self.auth_service.get_current_user().role == UserRole.ADMIN:
            console.print("\n[yellow]Admin Options:[/yellow]")
            console.print("6. [cyan]View All Bookings[/cyan]")
            console.print("7. [cyan]Manage Users[/cyan]")
            max_choice = 7
        else:
            max_choice = 5

        choice = Prompt.ask(f"\nEnter your choice (1-{max_choice}): ")
        
        try:
            if choice == "1":
                self.view_available_buses()
            elif choice == "2":
                self.book_seat()
            elif choice == "3":
                self.view_user_bookings()
            elif choice == "4":
                self.auth_service.logout()
                console.print("[green]Logged out successfully.[/green]")
            elif choice == "5":
                clear_screen()
                console.print("\n[green]Thank you for using the Bus Booking System![/green]")
                exit()
            elif choice == "6" and self.auth_service.get_current_user().role == UserRole.ADMIN:
                self._view_all_bookings()
            elif choice == "7" and self.auth_service.get_current_user().role == UserRole.ADMIN:
                self._manage_users()
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
                self._pause()
        except ValidationError as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            self._pause()
        except Exception as e:
            console.print(f"\n[red]An error occurred:[/red] {str(e)}")
            self._pause()

    def login(self):
        """Handle user login."""
        console.print("\n[bold cyan]Login[/bold cyan]")
        
        username = Prompt.ask("\nUsername")
        password = Prompt.ask("Password", password=True)
        
        try:
            user = self.auth_service.login(username, password)
            if user:
                self.current_user = user
                console.print("\n[green]Login successful![/green]")
                self._pause()
            else:
                console.print("\n[red]Invalid username or password[/red]")
                self._pause()
        except Exception as e:
            console.print(f"\n[red]Login failed:[/red] {str(e)}")
            self._pause()

    def register(self):
        """Handle user registration."""
        console.print("\n[bold cyan]Register New User[/bold cyan]")
        
        username = Prompt.ask("\nUsername")
        password = Prompt.ask("Password", password=True)
        confirm_password = Prompt.ask("Confirm Password", password=True)
        
        if password != confirm_password:
            console.print("\n[red]Passwords do not match[/red]")
            self._pause()
            return
        
        try:
            user = self.auth_service.register(username, password)
            if user:
                console.print("\n[green]Registration successful! Please login.[/green]")
            else:
                console.print("\n[red]Registration failed[/red]")
            self._pause()
        except Exception as e:
            console.print(f"\n[red]Registration failed:[/red] {str(e)}")
            self._pause()

    def view_available_buses(self) -> None:
        """Display available buses with real-time information."""
        try:
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
            
            if not valid_buses:
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

            console.print(table)
            console.print("\n[dim]Status Legend: ■ STOP = Stopped, ▲ SLOW = Moving slowly, ● MOVE = Moving normally[/dim]")
            
        except Exception as e:
            console.print(f"\n[red]Error displaying available buses: {str(e)}[/red]")
            import traceback
            console.print(traceback.format_exc())
        
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
                
            # Book the seat
            booking_id = self.booking_service.book_seat(bus_number, passenger_name, phone_number)
            
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
            self.auth_service.require_role(UserRole.ADMIN)
            bookings = self.booking_service.get_all_bookings()
            
            if not bookings:
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

            console.print(table)
        except Exception as e:
            console.print(f"\n[red]An error occurred while viewing all bookings:[/red] {str(e)}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        self._pause()

    def _manage_users(self) -> None:
        """Manage user accounts (admin only)."""
        self.auth_service.require_role(UserRole.ADMIN)
        
        console.print("\n[yellow]User Management[/yellow]")
        console.print("1. [cyan]View All Users[/cyan]")
        console.print("2. [cyan]Deactivate User Account[/cyan]")
        console.print("3. [cyan]Back to Main Menu[/cyan]")
        
        choice = console.input("\nEnter your choice (1-3): ")
        
        try:
            if choice == "1":
                self._view_all_users()
            elif choice == "2":
                self._deactivate_user()
            elif choice == "3":
                return
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValidationError as e:
            console.print(f"[red]Error:[/red] {str(e)}")

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