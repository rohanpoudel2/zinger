import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional

# Removed: from views.components.base_component import Component # Not needed anymore
from views.components.card import Card
# Removed: from views.components.button import Button # Use ttk.Button
from views.context.app_context import AppContext
from views.config.theme import PALETTE, FONTS
from views.pages.base_page import AuthenticatedPage # Import the new base class

class DashboardPage(AuthenticatedPage): # Inherit from AuthenticatedPage
    """
    Dashboard page frame showing user information and booking stats.
    Requires user authentication.
    """
    
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state for data - initialize first
        self._bookings: List[Any] = []
        self._is_loading: bool = True
        self._error: Optional[str] = None
        
        # Call the AuthenticatedPage __init__ which handles auth check,
        # sets self.context, gets services/user, and then calls 
        # _create_page_widgets if authenticated.
        super().__init__(parent, props=props, **kwargs)
        
        # Remove service/user setup from here, it's now in AuthenticatedPage

    def _create_page_widgets(self) -> None: # Rename method
        """Create and layout the widgets for the dashboard page."""
        # Main container setup is handled by AuthenticatedPage init
        
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(
            header_frame,
            text="Dashboard",
            font=FONTS["h1"], # Use theme font
            fg=PALETTE["text_primary"], # Use theme color
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)
        
        # Content area - using grid layout
        self.content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        
        # Create placeholders for cards initially
        # Actual content will be populated by _render methods after data load
        self._create_user_card_placeholder()
        self._create_bookings_card_placeholder()
        self._create_actions_card()
        
        # Load data after placeholder widgets are created
        self._load_data()
        
    def _create_user_card_placeholder(self) -> None:
        self.user_card = Card(
            self.content_frame,
            props={
                'title': 'User Information',
                'padding': 15
            }
        )
        self.user_card.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.user_card_content = tk.Frame(self.user_card.main_area, bg=PALETTE["card_bg"])
        self.user_card_content.pack(fill=tk.BOTH, expand=True)
        # Add a loading label initially
        tk.Label(self.user_card_content, text="Loading...", font=FONTS["body"], bg=PALETTE["card_bg"]).pack(pady=20)

    def _create_bookings_card_placeholder(self) -> None:
        self.bookings_card = Card(
            self.content_frame,
            props={
                'title': 'Your Bookings',
                'padding': 15
            }
        )
        self.bookings_card.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.bookings_card_content = tk.Frame(self.bookings_card.main_area, bg=PALETTE["card_bg"])
        self.bookings_card_content.pack(fill=tk.BOTH, expand=True)
        # Add a loading label initially
        tk.Label(self.bookings_card_content, text="Loading...", font=FONTS["body"], bg=PALETTE["card_bg"]).pack(pady=20)
        
    def _create_actions_card(self) -> None:
        actions_card = Card(
            self.content_frame,
            props={
                'title': 'Quick Actions',
                'padding': 15
            }
        )
        actions_card.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
        actions_card_content = tk.Frame(actions_card.main_area, bg=PALETTE["card_bg"])
        actions_card_content.pack(fill=tk.BOTH, expand=True)

        # Add action buttons (using ttk.Button styled for Material)
        btn_frame = tk.Frame(actions_card_content, bg=PALETTE["card_bg"])
        btn_frame.pack(pady=10, fill=tk.X, expand=True)
        
        # Configure columns for button spacing
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # Book New Ticket Button
        book_button = ttk.Button(
            btn_frame, 
            text="BOOK NEW TICKET", 
            style='Primary.TButton',
            command=self._navigate_to_new_booking # Placeholder command
        )
        book_button.grid(row=0, column=0, padx=10, pady=5, sticky='ew')

        # Search Buses Button
        search_button = ttk.Button(
            btn_frame,
            text="SEARCH BUSES", 
            style='Accent.TButton', 
            command=self._navigate_to_buses # Placeholder command
        )
        search_button.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

    def _load_data(self) -> None:
        """Load user bookings and other data, then update UI."""
        self._is_loading = True
        self._error = None
        # Update UI to show loading state initially is handled by placeholders

        if not self.booking_service:
            self._is_loading = False
            self._error = 'Booking service not available'
            self._render_ui_states() # Update UI based on error
            return
        
        try:
            if self.current_user:
                # Simulate network delay if needed: time.sleep(1)
                bookings = self.booking_service.get_user_bookings(self.current_user.id)
                self._bookings = bookings or []
                self._is_loading = False
            else:
                 self._is_loading = False
                 self._error = "User not found."
        except Exception as e:
            self._is_loading = False
            self._error = f"Failed to load data: {str(e)}"
        
        # Update the UI with loaded data or errors
        self._render_ui_states()

    def _render_ui_states(self): 
         """Update card contents based on loaded data or errors."""
         self._render_user_card()
         self._render_bookings_card()
         # Actions card is static, doesn't need update unless actions change

    def _clear_frame(self, frame: tk.Frame):
        """Helper to remove all widgets from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()
            
    def _render_user_card(self) -> None:
        """Render the user information card content."""
        self._clear_frame(self.user_card_content)

        if not self.current_user:
             tk.Label(self.user_card_content, text="Error: User data not available.", font=FONTS["body"], fg=PALETTE["danger"], bg=PALETTE["card_bg"]).pack(pady=20, anchor='w')
             return

        # Use getattr for safer access
        username = getattr(self.current_user, 'username', 'N/A')
        email = getattr(self.current_user, 'email', 'N/A')
        role_enum = getattr(self.current_user, 'role', None)
        role_str = str(role_enum).split('.')[-1].capitalize() if role_enum else 'N/A'
        booking_count = str(len(self._bookings)) if self._bookings is not None else "0"

        # Pack labels directly into user_card_content
        tk.Label(self.user_card_content, text=f"Username: {username}", font=FONTS["body"], bg=PALETTE["card_bg"], anchor='w').pack(fill=tk.X, pady=2)
        tk.Label(self.user_card_content, text=f"Email: {email}", font=FONTS["body"], bg=PALETTE["card_bg"], anchor='w').pack(fill=tk.X, pady=2)
        tk.Label(self.user_card_content, text=f"Role: {role_str}", font=FONTS["body"], bg=PALETTE["card_bg"], anchor='w').pack(fill=tk.X, pady=2)
        tk.Label(self.user_card_content, text=f"Total Bookings: {booking_count}", font=FONTS["body"], bg=PALETTE["card_bg"], anchor='w').pack(fill=tk.X, pady=2)

    def _render_bookings_card(self) -> None:
        """Render the bookings summary card content."""
        self._clear_frame(self.bookings_card_content)

        if self._is_loading:
            tk.Label(self.bookings_card_content, text="Loading bookings...", font=FONTS["body"], bg=PALETTE["card_bg"]).pack(pady=20)
            return
            
        if self._error and "bookings" in self._error.lower(): # Show booking specific error here
            tk.Label(self.bookings_card_content, text=self._error, font=FONTS["body"], fg=PALETTE["danger"], bg=PALETTE["card_bg"], wraplength=300).pack(pady=20)
            return
        
        if not self._bookings:
            tk.Label(self.bookings_card_content, text="You have no bookings yet.", font=FONTS["body"], bg=PALETTE["card_bg"]).pack(pady=20)
        else:
            # Create Treeview
            columns = ('id', 'bus', 'seats', 'date', 'status')
            tree = ttk.Treeview(self.bookings_card_content, columns=columns, show='headings', height=5)

            tree.heading('id', text='ID')
            tree.heading('bus', text='Bus Route')
            tree.heading('seats', text='Seats')
            tree.heading('date', text='Date')
            tree.heading('status', text='Status')

            tree.column('id', width=40, anchor=tk.CENTER)
            tree.column('bus', width=120)
            tree.column('seats', width=50, anchor=tk.CENTER)
            tree.column('date', width=90, anchor=tk.CENTER)
            tree.column('status', width=80, anchor=tk.CENTER)
            
            # Add data (only show first few bookings maybe)
            for booking in self._bookings[:5]: # Limit to 5 for summary view
                date_str = booking.booking_time.strftime('%Y-%m-%d') if booking.booking_time else 'N/A'
                bus_route = f"Route {booking.bus.route}" if booking.bus else 'N/A'
                seat_count_display = getattr(booking, 'seat_count', 1) # Default to 1 if missing
                tree.insert('', tk.END, values=(
                    booking.id,
                    bus_route,
                    seat_count_display, # Use the safe value
                    date_str,
                    booking.status.capitalize()
                ))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Add "View All" button below the tree
            view_all_btn = ttk.Button(
                self.bookings_card_content, 
                text="View All Bookings", 
                style='Primary.TButton', 
                command=self._navigate_to_bookings # Placeholder command
            )
            view_all_btn.pack(pady=(10,0)) # Add some padding above the button
            
            # Style the Treeview
            style = ttk.Style()
            style.configure("Treeview.Heading", font=FONTS["body_bold"], background=PALETTE["primary_light"], foreground=PALETTE["text_primary"])
            style.configure("Treeview", font=FONTS["body"], rowheight=int(FONTS["body"][1] * 2.0)) # Adjust row height based on font
            style.map("Treeview", background=[('selected', PALETTE["primary"])], foreground=[('selected', PALETTE["text_primary_on_primary"])])

    # Navigation methods (remain the same, use self.app)
    def _navigate_to_bookings(self) -> None:
        if self.app and hasattr(self.app, 'show_page'):
            self.app.show_page('bookings') # Assuming a 'bookings' page exists
        else:
            print("Error: App instance not found or doesn't support navigation.")

    def _navigate_to_buses(self) -> None:
        if self.app and hasattr(self.app, 'show_page'):
            self.app.show_page('buses') # Assuming a 'buses' page exists
        else:
            print("Error: App instance not found or doesn't support navigation.")

    def _navigate_to_new_booking(self) -> None:
        if self.app and hasattr(self.app, 'show_page'):
            self.app.show_page('new_booking') # Assuming a 'new_booking' page exists
        else:
            print("Error: App instance not found or doesn't support navigation.")

    # Page Lifecycle Method
    def reset_state(self) -> None:
        """Reload data when the page is shown."""
        # Call the parent class's reset_state to refresh user data
        super().reset_state()
        
        # Now load data with the freshly updated user information
        self._load_data()

    # Removed: init, render, component_did_mount, set_state, get_state
    # Logic moved to __init__, _create_page_widgets, _load_data, _render_ui_states

    # Removed: _render_user_card, _render_bookings_card, _render_actions_card
    # Logic moved to _render_ui_states

    # Removed: _create_user_card_placeholder, _create_bookings_card_placeholder, _create_actions_card
    # Logic moved to _create_page_widgets

    # Removed: _render_ui_states
    # Logic moved to _load_data

    # Removed: _clear_frame
    # Logic moved to _render_ui_states

    # Removed: _render_user_card, _render_bookings_card, _render_actions_card
    # Logic moved to _render_ui_states

    # Removed: _render_user_card, _render_bookings_card, _render_actions_card
    # Logic moved to _render_ui_states 