from typing import Optional
from services.booking_service import BookingService
from services.auth_service import AuthService
from services.location_service import LocationService
from models.database_models import UserRole
from exceptions import ValidationError, BookingError, SeatError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os

console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Menu:
    def __init__(self, booking_service: BookingService, auth_service: AuthService, location_service: LocationService):
        self.booking_service = booking_service
        self.auth_service = auth_service
        self.location_service = location_service

    def display_main_menu(self) -> None:
        """Display the main menu options."""
        while True:
            clear_screen()
            if self.auth_service.is_authenticated():
                user = self.auth_service.get_current_user()
                location_info = ""
                if self.location_service.get_location_name():
                    location_info = f" - Location: [yellow]{self.location_service.get_location_name()}[/yellow]"
                console.print(Panel(f"[blue]Bus Booking System[/blue] - Logged in as [green]{user.username}[/green] ({user.role.value}){location_info}"))
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

        choice = console.input("\nEnter your choice (1-4): ")
        
        try:
            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._handle_registration()
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

        choice = console.input(f"\nEnter your choice (1-{max_choice}): ")
        
        try:
            if choice == "1":
                self.view_available_buses()
            elif choice == "2":
                self._handle_booking()
            elif choice == "3":
                self._view_user_bookings()
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

    def _handle_login(self) -> None:
        """Handle user login."""
        username = console.input("\nEnter username: ")
        password = console.input("Enter password: ", password=True)
        
        if self.auth_service.login(username, password):
            console.print("[green]Login successful![/green]")
        else:
            console.print("[red]Invalid username or password.[/red]")
            self._pause()

    def _handle_registration(self) -> None:
        """Handle user registration."""
        username = console.input("\nEnter username: ")
        email = console.input("Enter email: ")
        password = console.input("Enter password: ", password=True)
        
        try:
            self.auth_service.register(username, email, password)
            console.print("[green]Registration successful! Please login.[/green]")
        except ValidationError as e:
            console.print(f"[red]Registration failed:[/red] {str(e)}")
            self._pause()

    def view_available_buses(self) -> None:
        """Display available buses."""
        buses = self.booking_service.get_available_buses()
        if not buses:
            console.print("\n[yellow]No buses available.[/yellow]")
            self._pause()
            return

        table = Table(
            title="Available Buses in New Haven",
            title_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Bus Number", style="cyan", justify="center")
        table.add_column("Route", style="magenta")
        table.add_column("Current Location", style="green")
        table.add_column("Next Departure", style="blue")
        table.add_column("Type", style="yellow")
        table.add_column("Fare", style="green")
        table.add_column("Available Seats", style="cyan", justify="center")

        for bus in buses:
            available_seats = len(self.booking_service.get_available_seats(bus.bus_number))
            departure_time = bus.departure.strftime("%I:%M %p")
            
            # Format fare display
            fare_display = "Free" if bus.fare == 0 else f"${bus.fare:.2f}"
            
            # Format route type with emoji
            type_emoji = "🚐" if bus.route_type == "shuttle" else "🚌"
            route_type = f"{type_emoji} {bus.route_type.title()}"
            
            table.add_row(
                str(bus.bus_number),
                bus.route,
                bus.current_location or "N/A",
                departure_time,
                route_type,
                fare_display,
                f"{available_seats}/30"
            )

        console.print("\n[bold blue]Real-time Bus Information[/bold blue]")
        console.print(table)
        
        # Show route information
        if len(buses) > 0:
            console.print("\n[bold cyan]Route Information:[/bold cyan]")
            for bus in buses[:1]:  # Show info for the first bus of each route
                route_info = self.booking_service.get_route_info(bus.route)
                if route_info:
                    info_table = Table(show_header=False, box=None)
                    info_table.add_row("Frequency:", f"[green]{route_info.get('frequency', 'N/A')}[/green]")
                    info_table.add_row("Operating Hours:", f"[green]{route_info.get('operating_hours', 'N/A')}[/green]")
                    info_table.add_row("Wheelchair Accessible:", "✅" if route_info.get('wheelchair_accessible') else "❌")
                    info_table.add_row("Bike Racks Available:", "✅" if route_info.get('bike_racks') else "❌")
                    console.print(info_table)
        
        self._pause()

    def _pause(self) -> None:
        """Pause execution until user presses Enter."""
        console.input("\n[cyan]Press Enter to continue...[/cyan]")

    def _handle_booking(self) -> None:
        """Handle ticket booking."""
        self.auth_service.require_auth()
        
        # First check if there are any available buses
        buses = self.booking_service.get_available_buses()
        if not buses:
            console.print("\n[yellow]No buses available for booking.[/yellow]")
            self._pause()
            return

        # Show available buses
        self.view_available_buses()
        
        # Get booking details
        bus_number = console.input("\nEnter bus number to book: ")
        passenger_name = console.input("Enter passenger name: ")
        phone = console.input("Enter phone number: ")
        
        # Show available seats for selected bus
        available_seats = self.booking_service.get_available_seats(bus_number)
        if not available_seats:
            console.print("[red]No seats available on this bus.[/red]")
            self._pause()
            return
            
        # Display available seats in a formatted way
        console.print("\n[cyan]Available Seats:[/cyan]")
        seat_groups = [available_seats[i:i+6] for i in range(0, len(available_seats), 6)]
        for row in seat_groups:
            console.print(" ".join(f"[green]{seat}[/green]" for seat in row))
        
        seat = console.input("\nEnter seat number (e.g., 1A): ")
        
        try:
            booking_id = self.booking_service.create_booking(
                bus_number=bus_number,
                passenger_name=passenger_name,
                phone=phone,
                seat=seat,
                user_id=self.auth_service.get_current_user().id
            )
            console.print(f"\n[green]Booking successful! Your booking ID is: {booking_id}[/green]")
            self._pause()
        except (ValidationError, BookingError, SeatError) as e:
            console.print(f"\n[red]Booking failed:[/red] {str(e)}")
            self._pause()

    def _view_user_bookings(self) -> None:
        """View bookings for the current user."""
        self.auth_service.require_auth()
        bookings = self.booking_service.get_user_bookings(
            self.auth_service.get_current_user().id
        )
        
        if not bookings:
            console.print("\n[yellow]No bookings found.[/yellow]")
            self._pause()
            return

        table = Table(title="Your Bookings")
        table.add_column("Booking ID", style="cyan")
        table.add_column("Bus Route", style="magenta")
        table.add_column("Seat", style="green")
        table.add_column("Departure Time", style="blue")
        table.add_column("Status", style="yellow")

        for booking in bookings:
            # Get bus details
            bus = self.booking_service.bus_repository.get(booking.bus_number)
            
            table.add_row(
                str(booking.booking_id),
                bus.route if bus else "Unknown",
                booking.seat,
                bus.departure.strftime("%I:%M %p") if bus else "Unknown",
                booking.status.value
            )

        console.print(table)
        self._pause()

    def _view_all_bookings(self) -> None:
        """View all bookings (admin only)."""
        self.auth_service.require_role(UserRole.ADMIN)
        bookings = self.booking_service.get_all_bookings()
        
        if not bookings:
            console.print("\n[yellow]No bookings found.[/yellow]")
            self._pause()
            return

        table = Table(title="All Bookings")
        table.add_column("Booking ID", style="cyan")
        table.add_column("User", style="magenta")
        table.add_column("Bus Route", style="green")
        table.add_column("Seat", style="blue")
        table.add_column("Departure Time", style="yellow")
        table.add_column("Status", style="red")

        for booking in bookings:
            # Get user and bus details
            user = self.auth_service.get_user_by_id(booking.user_id)
            bus = self.booking_service.bus_repository.get(booking.bus_number)
            
            table.add_row(
                str(booking.booking_id),
                user.username if user else "Unknown",
                bus.route if bus else "Unknown",
                booking.seat,
                bus.departure.strftime("%I:%M %p") if bus else "Unknown",
                booking.status.value
            )

        console.print(table)
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