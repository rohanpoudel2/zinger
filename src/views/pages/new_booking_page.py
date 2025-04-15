# src/views/pages/new_booking_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List

from views.pages.base_page import AuthenticatedPage
from views.config.theme import PALETTE, FONTS
from views.context.app_context import AppContext
from views.components.input import Input # Use the custom Input component
from views.components.card import Card

class NewBookingPage(AuthenticatedPage):
    '''
    Page for creating a new bus booking.
    Requires authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state
        self._is_loading_buses: bool = True # Track bus list loading
        self._error: Optional[str] = None
        self._available_buses: List[Any] = [] # Store full bus objects
        self._bus_display_options: List[str] = [] # Store strings for dropdown (e.g., "123 - Route Name")
        self._selected_bus_number = tk.StringVar()

        # Booking service is inherited via AuthenticatedPage as self.booking_service

        # Call AuthenticatedPage init (handles auth check and calls _create_page_widgets)
        super().__init__(parent, props=props, **kwargs)

        # Load available buses *after* widgets are created (called from _create_page_widgets now)
        # self._load_available_buses()

    def _load_available_buses(self) -> None:
        '''Fetch available buses to populate the dropdown.'''
        self._is_loading_buses = True
        self._error = None
        self._available_buses = []
        self._bus_display_options = []
        self._selected_bus_number.set('') # Clear selection
        if hasattr(self, 'bus_number_combo'): # Update dropdown state
            self.bus_number_combo.config(values=[], state=tk.DISABLED)
            self.bus_number_combo.set('Loading buses...')
        self._update_button_state()

        if not self.booking_service:
            self._error = "Booking service not available."
            self._is_loading_buses = False
            if hasattr(self, 'bus_number_combo'):
                 self.bus_number_combo.set('Error loading buses')
            # Don't necessarily show error in main label, dropdown indicates issue
            self._update_button_state()
            return

        try:
            # Assuming get_available_buses returns BusModel objects
            buses = self.booking_service.get_available_buses()
            self._available_buses = buses or []

            # Create display strings (e.g., "Bus 123 - Route X to Y")
            display_options = []
            for bus in self._available_buses:
                bus_num = getattr(bus, 'bus_number', 'N/A')
                route = getattr(bus, 'route', 'Unknown Route')
                display_options.append(f"{bus_num} - {route}")
            self._bus_display_options = display_options

            self._is_loading_buses = False

        except Exception as e:
            print(f"Error loading available buses for dropdown: {e}")
            self._error = "Failed to load bus list."
            self._is_loading_buses = False

        # Update combobox values and state
        if hasattr(self, 'bus_number_combo'):
            if self._error:
                self.bus_number_combo.set(self._error)
                self.bus_number_combo.config(values=[], state=tk.DISABLED)
            elif not self._bus_display_options:
                self.bus_number_combo.set('No buses available')
                self.bus_number_combo.config(values=[], state=tk.DISABLED)
            else:
                self.bus_number_combo.config(values=self._bus_display_options, state='readonly')
                self.bus_number_combo.set('Select a bus...') # Placeholder
        self._update_button_state()

    def _create_page_widgets(self) -> None:
        '''Create widgets for the new booking page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Book New Ticket",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # --- Booking Form Card ---
        # Center the card
        card_frame = tk.Frame(self, bg=PALETTE["secondary"])
        card_frame.pack(expand=True, fill=tk.NONE, anchor=tk.CENTER, pady=20)

        booking_card = Card(
            card_frame,
            props={
                'title': 'Enter Booking Details',
                'width': 450,
                'padding': 20
            }
        )
        booking_card.pack()

        form_frame = booking_card.main_area # Use the card's main_area for content

        # --- Bus Number Dropdown --- 
        bus_label = tk.Label(form_frame, text="Bus Number", anchor='w',
                           bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"],
                           font=FONTS["caption"])
        bus_label.pack(fill=tk.X, pady=(10, 0))

        self.bus_number_combo = ttk.Combobox(
            form_frame,
            textvariable=self._selected_bus_number,
            state='disabled', # Start disabled until loaded
            font=FONTS["input"],
            # values will be set by _load_available_buses
        )
        self.bus_number_combo.pack(fill=tk.X, pady=(0, 10))
        self.bus_number_combo.set('Loading buses...') # Initial text
        # Bind selection change event
        self.bus_number_combo.bind('<<ComboboxSelected>>', lambda e: self._update_button_state())

        # Passenger Name Input
        self.passenger_name_input = Input(
            form_frame,
            props={
                'label': 'Passenger Name',
                'placeholder': 'Enter full name',
                'required': True,
                'validate': lambda v: v.strip() != '',
                'on_change': lambda v: self._update_button_state()
            }
        )
        self.passenger_name_input.pack(fill=tk.X, pady=10)

        # Phone Number Input
        self.phone_number_input = Input(
            form_frame,
            props={
                'label': 'Phone Number',
                'placeholder': 'Enter contact number',
                'required': True,
                'validate': lambda v: v.strip() != '', # Basic validation
                'on_change': lambda v: self._update_button_state()
            }
        )
        self.phone_number_input.pack(fill=tk.X, pady=10)

        # Error message label
        self.error_label = tk.Label(
            form_frame, text='', fg=PALETTE["danger"], bg=PALETTE["card_bg"],
            anchor='w', justify=tk.LEFT, wraplength=400,
            font=FONTS["caption"]
        )
        self.error_label.pack(fill=tk.X, pady=(5, 0))
        self.error_label.pack_forget() # Hide initially

        # Confirm Button (using ttk)
        self.confirm_button = ttk.Button(
            form_frame,
            text="CONFIRM BOOKING",
            style="Primary.TButton",
            command=self._handle_confirm_booking,
            state=tk.DISABLED # Initially disabled
        )
        self.confirm_button.pack(fill=tk.X, pady=(15, 5))

        # Load available buses for the dropdown
        self._load_available_buses()

        # Initial check for button state
        self._update_button_state()

    def _is_form_valid(self) -> bool:
        '''Check if all required input fields are valid.'''
        # Check if a valid bus is selected (not empty, not placeholder/error text)
        bus_selection = self._selected_bus_number.get()
        is_bus_selected = hasattr(self, 'bus_number_combo') and bus_selection and bus_selection not in ['Loading buses...', 'Error loading buses', 'No buses available', 'Select a bus...']

        name_valid = hasattr(self, 'passenger_name_input') and self.passenger_name_input.is_valid()
        phone_valid = hasattr(self, 'phone_number_input') and self.phone_number_input.is_valid()
        return is_bus_selected and name_valid and phone_valid

    def _update_button_state(self) -> None:
        '''Enable/disable the confirm button based on form validity.'''
        if hasattr(self, 'confirm_button') and self.confirm_button.winfo_exists():
            new_state = tk.NORMAL if self._is_form_valid() else tk.DISABLED
            if self.confirm_button.cget('state') != new_state:
                self.confirm_button.config(state=new_state)

    def _handle_confirm_booking(self) -> None:
        '''Handle the confirm booking button click.'''
        if not self._is_form_valid():
            self._show_error("Please fill in all required fields.")
            return

        self.confirm_button.config(state=tk.DISABLED, text="Booking...")
        self._show_error('') # Clear previous errors

        # Extract only the bus number from the selected dropdown string
        selected_option = self._selected_bus_number.get()
        bus_number = selected_option.split(' - ')[0] if selected_option and ' - ' in selected_option else None

        if not bus_number:
            self._show_error("Invalid bus selection.")
            self.confirm_button.config(state=tk.NORMAL, text="CONFIRM BOOKING") # Re-enable if validation failed here
            return

        passenger_name = self.passenger_name_input.get_value()
        phone_number = self.phone_number_input.get_value()

        if not self.booking_service:
            self._show_error("Booking service not available.")
            self.confirm_button.config(state=tk.NORMAL, text="CONFIRM BOOKING")
            return

        try:
            # The book_seat method in the service needs auth_service passed to it
            # We get auth_service from the context inherited in AuthenticatedPage
            booking = self.booking_service.book_seat(
                bus_number,
                passenger_name,
                phone_number,
                auth_service=self.auth_service # Pass the auth service instance
            )

            if booking:
                # Reset button state before showing message or navigating
                self.confirm_button.config(state=tk.NORMAL, text="CONFIRM BOOKING")
                
                # Revert to using messagebox
                messagebox.showinfo("Booking Successful",
                                    f"Booking confirmed!\n\n"
                                    f"Booking ID: {booking}\n" 
                                    f"Bus Number: {bus_number}\n"
                                    f"Passenger: {passenger_name}")

                # Reset form before navigating
                self.reset_state()
                
                # Navigate back to dashboard immediately
                if self.app:
                    self.app.show_page('dashboard')
            else:
                # This case might not be reachable if book_seat raises exceptions on failure
                self._show_error("Booking failed. Please try again.")
                self.confirm_button.config(state=tk.NORMAL, text="CONFIRM BOOKING")

        except Exception as e:
            # Catch specific validation errors or general exceptions
            self._show_error(f"Booking Error: {str(e)}")
            self.confirm_button.config(state=tk.NORMAL, text="CONFIRM BOOKING")

    def _show_error(self, message: str) -> None:
        '''Display an error message below the inputs.'''
        if hasattr(self, 'error_label'):
            self.error_label.config(text=message)
            if message:
                self.error_label.pack(fill=tk.X, pady=(5, 0), before=self.confirm_button)
            else:
                self.error_label.pack_forget()

    def reset_state(self) -> None:
        '''Reset the form when the page is shown.'''
        # Clear standard inputs
        if hasattr(self, 'passenger_name_input'): self.passenger_name_input.clear()
        if hasattr(self, 'phone_number_input'): self.phone_number_input.clear()
        if hasattr(self, 'error_label'): self._show_error('')
        
        # Reset confirm button to original state
        if hasattr(self, 'confirm_button'):
            self.confirm_button.config(state=tk.DISABLED, text="CONFIRM BOOKING")
        
        # Reload bus list and reset combobox
        self._load_available_buses() 
        
        # Update button state after everything is reset
        self._update_button_state() 