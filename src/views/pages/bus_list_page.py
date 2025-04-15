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
        self._filtered_buses: List[Any] = [] # Store filtered buses for search
        self._is_loading: bool = True
        self._error: Optional[str] = None
        self._search_term: tk.StringVar = tk.StringVar()

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

        # Search bar
        search_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        search_frame.pack(fill=tk.X)
        
        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=FONTS["body"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self._search_term,
            font=FONTS["input"],
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Make Enter key trigger search
        search_entry.bind("<Return>", lambda e: self._search_buses())
        
        search_button = ttk.Button(
            search_frame,
            text="Search",
            style="Secondary.TButton",
            command=self._search_buses
        )
        search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(
            search_frame,
            text="Clear",
            style="Outline.TButton",
            command=self._clear_search
        )
        clear_button.pack(side=tk.LEFT)

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
        self._filtered_buses = [] # Clear filtered buses as well
        self._search_term.set("") # Clear search term
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
            self._filtered_buses = self._buses.copy() # Initialize filtered buses with all buses
            self._is_loading = False
            if not self._buses:
                self._error = "No buses found nearby." # Use info message

        except Exception as e:
            # TODO: Replace with proper logging
            print(f"ERROR: src.views.pages.bus_list_page._load_buses: {e}")
            self._is_loading = False
            self._error = f"Failed to load bus data: {str(e)}"

        self._render_ui_states()

    def _search_buses(self) -> None:
        '''Filter buses based on search term.'''
        search_term = self._search_term.get().strip().lower()
        
        if not search_term:
            # If search term is empty, show all buses
            self._filtered_buses = self._buses.copy()
        else:
            # Filter buses based on bus number and route
            self._filtered_buses = []
            for bus in self._buses:
                bus_number = str(getattr(bus, 'bus_number', '')).lower()
                route = str(getattr(bus, 'route', '')).lower()
                
                if search_term in bus_number or search_term in route:
                    self._filtered_buses.append(bus)
        
        # Update the UI to show filtered results
        self._render_ui_states()
    
    def _clear_search(self) -> None:
        '''Clear search term and show all buses.'''
        self._search_term.set("")
        self._filtered_buses = self._buses.copy()
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
        elif not self._filtered_buses: # Have buses but none match the search term
            self.status_label.config(text=f"No buses match your search: '{self._search_term.get()}'", 
                                    fg=PALETTE["warning"], wraplength=400)
            self.status_label.grid() # Make sure it's visible
        else:
            # Data loaded successfully, hide status label and show treeview
            self.status_label.grid_remove()
            self._create_bus_treeview()

    def _create_bus_treeview(self) -> None:
        '''Create and populate the bus list Treeview.'''
        # Create the Treeview
        columns = ('number', 'route', 'distance', 'updated', 'status')
        # Apply the "Treeview" style configured in app.py
        tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', style="Treeview")

        # Define headings
        tree.heading('number', text='Bus #')
        
        # Add count to the route heading
        search_term = self._search_term.get().strip()
        if search_term:
            route_heading = f"Route (Found {len(self._filtered_buses)} matching '{search_term}')"
        else:
            route_heading = f"Route (Showing {len(self._filtered_buses)})"
        tree.heading('route', text=route_heading)
        
        tree.heading('distance', text='Distance')
        tree.heading('updated', text='Last Update')
        tree.heading('status', text='Status')

        # Define column properties
        tree.column('number', width=80, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('route', width=350, stretch=tk.YES) # Make route column wider for the count
        tree.column('distance', width=100, anchor=tk.E, stretch=tk.NO)
        tree.column('updated', width=120, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('status', width=100, anchor=tk.CENTER, stretch=tk.NO)

        # --- Populate Treeview ---
        for bus in self._filtered_buses:
            # Get attributes safely
            bus_number = getattr(bus, 'bus_number', 'N/A')
            route_display = getattr(bus, 'route', 'Unknown Route')
            distance_km = getattr(bus, 'distance_km', None)
            last_updated_dt = getattr(bus, 'last_updated', None)
            status = getattr(bus, 'status', 'Unknown').capitalize()

            # Basic display formatting - no filtering (show all buses)
            cleaned_route_display = route_display
            
            # If route has a format with " - ", clean it up a bit, but don't filter out
            if route_display and ' - ' in route_display:
                parts = route_display.split(' - ', 1)
                if len(parts) == 2:
                    route_number_part, route_name_part = parts
                    # Clean up route number part
                    route_number_part = route_number_part.replace('Route ', '')
                    cleaned_route_display = f"{route_number_part} - {route_name_part}"

            # Format display values
            distance_display = f"{distance_km:.2f} km" if distance_km is not None else "N/A"
            last_update = last_updated_dt.strftime("%H:%M:%S") if isinstance(last_updated_dt, datetime) else "N/A"

            tree.insert('', tk.END, values=(
                bus_number,
                cleaned_route_display,
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

        # Make sure the tree expands properly
        self.tree_container.rowconfigure(0, weight=1)

    def reset_state(self) -> None:
        '''Reset state when page is shown (e.g., reload data).'''
        # Reload data every time the page is navigated to ensure freshness
        self._load_buses()
        
        pass # Default does nothing, override if needed 