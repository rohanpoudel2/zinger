import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
from datetime import datetime

from views.pages.base_page import AuthenticatedPage
from views.config.theme import PALETTE, FONTS
from views.context.app_context import AppContext
# TODO: Import specific services if needed directly, although AuthenticatedPage provides booking_service
# from services.booking_service import BookingService
# from services.location_service import LocationService

class BusListPage(AuthenticatedPage):
    '''
    Page to display available buses based on user location.
    Requires authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state for data
        self._buses: List[Any] = [] # Store BusModel or similar objects
        self._is_loading: bool = True
        self._error: Optional[str] = None

        # Booking service is available via AuthenticatedPage as self.booking_service
        # self.location_service = self.context.get_service('location_service') # Fetch if needed

        # Call AuthenticatedPage init (handles auth check and calls _create_page_widgets)
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the bus list page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Available Buses Nearby",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # Refresh Button (using ttk)
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            style="Primary.TButton", # Use a style defined in App
            command=self._load_buses
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

        # Content area for the list/table
        self.content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # Container for Treeview and scrollbar
        # Use card background for the Treeview area for contrast
        self.tree_container = tk.Frame(self.content_frame, bg=PALETTE["card_bg"])
        self.tree_container.grid(row=0, column=0, sticky='nsew')
        self.tree_container.rowconfigure(0, weight=1)
        self.tree_container.columnconfigure(0, weight=1)

        # Add initial loading message (will be placed in grid)
        # We create it here but place it in _render_ui_states initially
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)
        self.status_label.grid_remove() # Hide initially

        # Load data initially
        self._load_buses()

    def _load_buses(self) -> None:
        '''Fetch available bus data.'''
        self._is_loading = True
        self._error = None
        self._buses = [] # Clear previous buses before loading
        self._render_ui_states() # Show loading state

        # --- Service Interaction ---
        # The CLI used booking_service.get_buses_near_location.
        # Let's assume a method `get_available_buses` exists for the GUI context.

        if not self.booking_service:
            self._is_loading = False
            self._error = "Booking service not available."
            self._render_ui_states()
            return

        try:
            # TODO: Confirm/replace 'get_available_buses()' with the correct method
            # from BookingService. Check if it needs coordinates or other params.
            # Example: buses = self.booking_service.get_buses_near_location(radius_km=5)
            buses = self.booking_service.get_available_buses()

            self._buses = buses or []
            self._is_loading = False
            if not self._buses:
                self._error = "No buses found nearby." # Use info message

        except Exception as e:
            # TODO: Replace with proper logging
            print(f"ERROR: src.views.pages.bus_list_page._load_buses: {e}")
            self._is_loading = False
            self._error = f"Failed to load bus data: {str(e)}"

        self._render_ui_states()

    def _render_ui_states(self) -> None:
        '''Render the UI based on loading/error state and bus data.'''
        # Clear previous content (Treeview/scrollbar or status label)
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        # Recreate the status label within the container
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30) # Place it

        if self._is_loading:
            self.status_label.config(text="Loading available buses...", fg=PALETTE["text_secondary"])
        elif self._error and not self._buses: # Show error only if loading failed AND no data
             self.status_label.config(text=self._error, fg=PALETTE["danger"], wraplength=400)
        elif not self._buses: # No data, possibly with an info message like "No buses found"
            no_buses_message = self._error if self._error else "No buses found nearby."
            self.status_label.config(text=no_buses_message, fg=PALETTE["text_secondary"])
        else:
            # Data loaded successfully, hide status label and show treeview
            self.status_label.grid_remove()
            self._create_bus_treeview()

    def _create_bus_treeview(self) -> None:
        '''Create and populate the bus list Treeview.'''
        columns = ('number', 'route', 'distance', 'updated', 'status')
        # Apply the "Treeview" style configured in app.py
        tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', style="Treeview")

        # Define headings
        tree.heading('number', text='Bus #')
        tree.heading('route', text='Route')
        tree.heading('distance', text='Distance')
        tree.heading('updated', text='Last Update')
        tree.heading('status', text='Status')

        # Define column properties
        tree.column('number', width=80, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('route', width=250, stretch=tk.YES) # Allow route to stretch
        tree.column('distance', width=100, anchor=tk.E, stretch=tk.NO)
        tree.column('updated', width=120, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('status', width=100, anchor=tk.CENTER, stretch=tk.NO)

        # --- Populate Treeview ---
        for bus in self._buses:
            # Get attributes safely
            bus_number = getattr(bus, 'bus_number', 'N/A')
            route_display = getattr(bus, 'route', 'Unknown Route')
            distance_km = getattr(bus, 'distance_km', None)
            last_updated_dt = getattr(bus, 'last_updated', None)
            status = getattr(bus, 'status', 'Unknown').capitalize()

            # --- Filtering Logic (similar to CLI menu.py:258-277) ---
            # Skip if the route doesn't have a proper format or is empty
            if not route_display or ' - ' not in route_display or not route_display.strip():
                continue 
                
            # Split the route into number and name
            parts = route_display.split(' - ', 1)
            if len(parts) != 2:
                continue 
            route_number_part, route_name_part = parts
            
            # Clean up route number part
            route_number_part = route_number_part.replace('Route ', '')

            # Skip if route name is just a duplicate of the route number or empty
            if not route_name_part.strip() or route_name_part == route_number_part or route_name_part == f"Route {route_number_part}":
                continue
            # --- End Filtering Logic ---

            # Format display values
            distance_display = f"{distance_km:.2f} km" if distance_km is not None else "N/A"
            last_update = last_updated_dt.strftime("%H:%M:%S") if isinstance(last_updated_dt, datetime) else "N/A"

            # Use cleaned/formatted route for display
            cleaned_route_display = f"{route_number_part} - {route_name_part}"

            tree.insert('', tk.END, values=(
                bus_number,
                cleaned_route_display, # Use cleaned route
                distance_display,
                last_update,
                status
            ))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Grid layout for tree and scrollbar
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Styling is applied via style="Treeview" which uses styles from App

    def reset_state(self) -> None:
        '''Reset state when page is shown (e.g., reload data).'''
        # Reload data every time the page is navigated to ensure freshness
        self._load_buses()
        
        pass # Default does nothing, override if needed 