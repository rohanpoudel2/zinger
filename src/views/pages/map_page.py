# src/views/pages/map_page.py
import tkinter as tk
import tkintermapview
from tkinter import ttk
from typing import Dict, Any, List, Optional
import tkinter.messagebox as messagebox

from views.pages.base_page import AuthenticatedPage
from views.config.theme import PALETTE, FONTS
from views.context.app_context import AppContext

class MapPage(AuthenticatedPage):
    '''
    Page to display real-time bus locations on a map.
    Requires authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state
        self._bus_markers: Dict[str, tkintermapview.CanvasPositionMarker] = {} # Store markers by bus number
        self._user_marker: Optional[tkintermapview.CanvasPositionMarker] = None # Add user marker state
        self._user_location: Optional[Dict[str, float]] = None # Store user lat/lon
        self._is_loading: bool = True
        self._error: Optional[str] = None
        self._map_widget: Optional[tkintermapview.TkinterMapView] = None
        self._update_job = None # To store the id from self.after
        self._route_paths = {} # Add dictionary to store route paths

        # Call super().__init__ FIRST to set up self.context, self.current_user, etc.
        # This ALSO calls self._create_page_widgets() internally via base class.
        super().__init__(parent, props=props, **kwargs)
        
        # Now get LocationService using the initialized context.
        # This makes it available for methods called AFTER __init__ (e.g., button commands)
        self.location_service = self.context.get_service('location_service') if hasattr(self, 'context') else None

    def _create_page_widgets(self) -> None:
        '''Create widgets for the map page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Real-Time Bus Map",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # Add Center on Me button to header
        center_button = ttk.Button(
            header_frame,
            text="Center on Me",
            style="Primary.TButton", # Use a defined style
            command=self._center_on_user
        )
        center_button.pack(side=tk.RIGHT, padx=5)

        # Check if library is available
        if tkintermapview is None:
            error_label = tk.Label(
                self,
                text="Map functionality requires the 'tkintermapview' library.\nPlease install it: pip install tkintermapview",
                font=FONTS["body_bold"],
                fg=PALETTE["danger"],
                bg=PALETTE["secondary"],
                wraplength=600
            )
            error_label.pack(pady=50)
            return # Don't create map widget

        # Map Widget Container (takes up remaining space)
        map_frame = tk.Frame(self, bg="grey") # Simple background for the frame
        map_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Create map widget
        self._map_widget = tkintermapview.TkinterMapView(
            map_frame, 
            width=800, 
            height=600, 
            corner_radius=0
        )
        self._map_widget.pack(fill=tk.BOTH, expand=True)

        # --- Get location service HERE specifically for initial centering --- 
        # Because this method (_create_page_widgets) is called by super().__init__ 
        # *before* self.location_service is assigned in MapPage.__init__.
        location_service = self.context.get_service('location_service')
        location_store = self.context.get_store('location')

        # Try to get initial user location for centering
        initial_lat, initial_lon = 41.2818, -72.9542 # Default UNH
        initial_zoom = 14
        # Use the location_store here:
        if location_store:
            lat = location_store.get('latitude')
            lon = location_store.get('longitude')
            if lat is not None and lon is not None:
                initial_lat, initial_lon = lat, lon
                self._user_location = {'latitude': initial_lat, 'longitude': initial_lon}
                initial_zoom = 15
                print(f"DEBUG: Initial map center set to user location: {initial_lat}, {initial_lon}")
            else:
                print("DEBUG: User location coordinates not found in store, centering on default.")
        else:
             print("DEBUG: Location store not available, centering on default.")

        # Set initial position (user location or default)
        self._map_widget.set_position(initial_lat, initial_lon)
        self._map_widget.set_zoom(initial_zoom)

        # Load initial data and start updates
        self._load_and_plot_buses()
        self._schedule_map_update()

    def _load_and_plot_buses(self):
        '''Fetch initial bus data and plot markers.'''
        if not self._map_widget:
            return

        self._is_loading = True
        self._error = None
        # Clear existing markers (including user marker)
        self._map_widget.delete_all_marker()
        self._bus_markers = {}
        self._user_marker = None # Reset user marker
        self._route_paths = {} # Add dictionary to store route paths

        # Plot user marker first if location is known
        if self._user_location:
            try:
                self._user_marker = self._map_widget.set_marker(
                    self._user_location['latitude'],
                    self._user_location['longitude'],
                    text="Your Location",
                    marker_color_circle="#FF0000", # Red circle
                    marker_color_outside="#FFFFFF", # White outside
                    text_color="#000000" # Black text
                )
            except Exception as e:
                 print(f"ERROR plotting user marker: {e}")

        if not self.booking_service: # Assuming this service provides bus data
            self._error = "Service not available to fetch bus locations."
            self._is_loading = False
            print(f"ERROR: {self._error}") # Replace with status display later
            return

        try:
            # TODO: Confirm the method to get bus data with locations
            # Might be get_available_buses() if it includes lat/lon, 
            # or potentially a method from transit_service.
            buses = self.booking_service.get_available_buses()

            if not buses:
                print("No active buses found to plot.") # Info message
                self._is_loading = False
                return

            for bus in buses:
                lat = getattr(bus, 'latitude', None)
                lon = getattr(bus, 'longitude', None)
                bus_num = getattr(bus, 'bus_number', 'Unknown')
                route = getattr(bus, 'route', '')
                route_id = getattr(bus, 'route_id', '')
                
                if lat is not None and lon is not None:
                    marker_text = f"Bus {bus_num}\n{route}"
                    # Use set_marker for initial placement - use default marker style
                    marker = self._map_widget.set_marker(
                        lat, lon, 
                        text=marker_text,
                        marker_color_circle="#1E88E5", # Blue circle for bus markers
                        marker_color_outside="#FFFFFF" # White outside
                    )
                    # Store bus data with marker for route displaying
                    marker.bus_data = {
                        'bus_number': bus_num,
                        'route': route,
                        'route_id': route_id
                    }
                    # Add click event to show route
                    marker.command = lambda m=marker: self._show_bus_route(m)
                    self._bus_markers[bus_num] = marker # Store marker by bus number
                else:
                    print(f"Bus {bus_num} has no location data.")

            self._is_loading = False

        except Exception as e:
            self._error = f"Failed to load bus locations: {e}"
            self._is_loading = False
            print(f"ERROR: {self._error}")

    def _get_bus_icon(self):
        """Create a simple bus icon as a text character - fallback if custom icon fails"""
        try:
            # Try to use a Unicode bus character as a simple icon
            return "🚌"
        except Exception as e:
            print(f"Error creating bus icon: {e}")
            return None

    def _show_bus_route(self, marker):
        '''Show information about the bus and its route when clicked'''
        try:
            # Get bus data from marker
            bus_data = getattr(marker, 'bus_data', {})
            bus_number = bus_data.get('bus_number', 'Unknown')
            route_id = bus_data.get('route_id')
            
            if not route_id:
                messagebox.showinfo("Bus Information", 
                                   f"No route information available for Bus {bus_number}.")
                return
            
            # Get transit service
            transit_service = self.context.get_service('transit_service')
            if not transit_service:
                messagebox.showinfo("Bus Information", 
                                   f"Transit service not available to fetch information for Bus {bus_number}.")
                return
            
            # Fetch route info
            route_info = transit_service.get_route_info(route_id)
            route_details = route_info.get('route_details', {})
            route_name = route_details.get('display_name', f"Route {route_id}")
            
            # Get bus stops information from trip updates if available
            trip_updates = route_info.get('trip_updates', [])
            stops_info = []
            
            for trip in trip_updates:
                stop_updates = trip.get('stop_updates', [])
                for stop in stop_updates:
                    stop_name = stop.get('stop_name', '')
                    if stop_name and stop_name not in [s.get('name') for s in stops_info]:
                        stops_info.append({
                            'name': stop_name,
                            'arrival_time': stop.get('arrival_time')
                        })
            
            # Get the next stop info from the bus data
            next_stop = None
            active_buses = route_info.get('active_buses', [])
            for bus in active_buses:
                if bus.get('bus_number') == bus_number:
                    next_stop = bus.get('next_stop')
                    break
            
            # Construct bus info message
            info_message = f"Bus {bus_number}: {route_name}\n\n"
            
            if next_stop:
                info_message += f"Next Stop: {next_stop}\n\n"
            
            if stops_info:
                info_message += "Stops on this route:\n"
                for i, stop in enumerate(stops_info, 1):
                    # Format arrival time if available
                    arrival_time = ""
                    if stop.get('arrival_time'):
                        from datetime import datetime
                        try:
                            arrival_dt = datetime.fromtimestamp(stop['arrival_time'])
                            arrival_time = f" - Arrives: {arrival_dt.strftime('%I:%M %p')}"
                        except:
                            pass
                    
                    info_message += f"{i}. {stop['name']}{arrival_time}\n"
            else:
                info_message += "No stop information available for this route."
            
            # Show info popup
            messagebox.showinfo("Bus Information", info_message)
                
        except Exception as e:
            print(f"ERROR showing bus information: {e}")
            messagebox.showerror("Error", f"Failed to show bus information: {str(e)}")

    def _clear_route_paths(self):
        '''Clear any existing route paths from the map'''
        for path_list in self._route_paths.values():
            if isinstance(path_list, list):
                for path in path_list:
                    path.delete()
            else:
                # Handle case where it might be a single path object
                path_list.delete()
        self._route_paths = {}

    def _update_bus_positions(self):
        '''Fetch latest bus positions and update markers.'''
        if not self._map_widget or not self.booking_service:
            return # Don't attempt update if map or service unavailable

        # print("DEBUG: Updating bus positions...") # Optional debug print
        try:
            latest_buses = self.booking_service.get_available_buses()
            if not latest_buses:
                return

            current_marker_keys = set(self._bus_markers.keys())
            updated_bus_keys = set()

            for bus in latest_buses:
                lat = getattr(bus, 'latitude', None)
                lon = getattr(bus, 'longitude', None)
                bus_num = getattr(bus, 'bus_number', None)
                route = getattr(bus, 'route', '')
                route_id = getattr(bus, 'route_id', '')
                
                if bus_num and lat is not None and lon is not None:
                    updated_bus_keys.add(bus_num)
                    marker_text = f"Bus {bus_num}\n{route}"
                    if bus_num in self._bus_markers:
                        # Update existing marker position
                        marker = self._bus_markers[bus_num]
                        marker.set_position(lat, lon)
                        marker.set_text(marker_text) # Update text in case route changes
                        # Update bus data
                        marker.bus_data = {
                            'bus_number': bus_num,
                            'route': route,
                            'route_id': route_id
                        }
                    else:
                        # Add new marker if bus wasn't previously shown
                        marker = self._map_widget.set_marker(
                            lat, lon, 
                            text=marker_text,
                            marker_color_circle="#1E88E5", # Blue circle for bus markers
                            marker_color_outside="#FFFFFF" # White outside
                        )
                        # Store bus data with marker
                        marker.bus_data = {
                            'bus_number': bus_num,
                            'route': route,
                            'route_id': route_id
                        }
                        # Add click event to show route
                        marker.command = lambda m=marker: self._show_bus_route(m)
                        self._bus_markers[bus_num] = marker

            # Remove markers for buses that are no longer reported
            buses_to_remove = current_marker_keys - updated_bus_keys
            for bus_num_remove in buses_to_remove:
                if bus_num_remove in self._bus_markers:
                    self._bus_markers[bus_num_remove].delete()
                    del self._bus_markers[bus_num_remove]
                    # print(f"DEBUG: Removed marker for bus {bus_num_remove}")

        except Exception as e:
            print(f"ERROR updating bus positions: {e}")
        
        # Schedule the next update
        self._schedule_map_update()

    def _schedule_map_update(self):
        """Use self.after to schedule the next position update."""
        # Cancel previous job if it exists
        if self._update_job:
            self.after_cancel(self._update_job)
            
        # Schedule next update (e.g., every 30 seconds = 30000 ms)
        update_interval_ms = 30000 
        self._update_job = self.after(update_interval_ms, self._update_bus_positions)

    def reset_state(self) -> None:
        '''Reload data and restart updates when page is shown.'''
        self._load_and_plot_buses()
        self._schedule_map_update()

    def destroy(self):
        """Override destroy to cancel scheduled updates."""
        if self._update_job:
            self.after_cancel(self._update_job)
            self._update_job = None
        # Clear route paths
        self._clear_route_paths()
        super().destroy()

    # Add method to handle centering
    def _center_on_user(self):
        if not self._map_widget:
            return
        
        # Fetch current location again from store
        location_store = self.context.get_store('location')
        if location_store:
            lat = location_store.get('latitude')
            lon = location_store.get('longitude')
            if lat is not None and lon is not None:
                self._user_location = {'latitude': lat, 'longitude': lon} # Update stored location
                self._map_widget.set_position(lat, lon)
                self._map_widget.set_zoom(15) # Zoom in
                 # Optionally update marker position if needed
                if self._user_marker:
                    self._user_marker.set_position(lat, lon)
                else: # If marker didn't exist, plot it now
                     self._user_marker = self._map_widget.set_marker(lat, lon, text="Your Location", marker_color_circle="#FF0000", marker_color_outside="#FFFFFF", text_color="#000000")
                print(f"DEBUG: Centered map on user location: {lat}, {lon}")
            else:
                messagebox.showwarning("Location Unknown", "Could not retrieve your current location from the store.")
                print("DEBUG: Failed to get user location from store for centering.")
        else:
            messagebox.showerror("Context Error", "Location store is not available.")
            print("DEBUG: Location store not available for centering.") 