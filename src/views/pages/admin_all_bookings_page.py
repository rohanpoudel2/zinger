# src/views/pages/admin_all_bookings_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
from datetime import datetime

from views.pages.admin_base_page import AdminPage # Inherit from AdminPage
from views.config.theme import PALETTE, FONTS
from views.context.app_context import AppContext

class AdminAllBookingsPage(AdminPage):
    '''
    Admin page to display ALL bookings in the system.
    Requires admin authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state
        self._all_bookings: List[Any] = []
        self._is_loading: bool = True
        self._error: Optional[str] = None

        # Services inherited from AdminPage -> AuthenticatedPage
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the admin all bookings page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="All System Bookings",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # Refresh Button
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            style="Primary.TButton",
            command=self._load_all_bookings
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

        # Content area for the list/table
        self.content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # Container for Treeview and scrollbar
        self.tree_container = tk.Frame(self.content_frame, bg=PALETTE["card_bg"])
        self.tree_container.grid(row=0, column=0, sticky='nsew')
        self.tree_container.rowconfigure(0, weight=1)
        self.tree_container.columnconfigure(0, weight=1)

        # Status Label
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)
        self.status_label.grid_remove()

        # Load data initially
        self._load_all_bookings()

    def _load_all_bookings(self) -> None:
        '''Fetch all bookings from the service.'''
        self._is_loading = True
        self._error = None
        self._all_bookings = []
        self._render_ui_states()

        if not self.booking_service:
            self._is_loading = False
            self._error = "Booking service not available."
            self._render_ui_states()
            return

        try:
            bookings = self.booking_service.get_all_bookings()
            self._all_bookings = bookings or []
            self._is_loading = False
            if not self._all_bookings:
                self._error = "No bookings found in the system."

        except Exception as e:
            print(f"ERROR loading all bookings: {e}")
            self._is_loading = False
            self._error = f"Failed to load bookings: {str(e)}"

        self._render_ui_states()

    def _render_ui_states(self) -> None:
        '''Render the UI based on loading/error state and booking data.'''
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)

        if self._is_loading:
            self.status_label.config(text="Loading all bookings...", fg=PALETTE["text_secondary"])
        elif self._error and not self._all_bookings:
             self.status_label.config(text=self._error, fg=PALETTE["danger"], wraplength=400)
        elif not self._all_bookings:
            message = self._error if self._error else "No bookings found."
            self.status_label.config(text=message, fg=PALETTE["text_secondary"])
        else:
            self.status_label.grid_remove()
            self._create_all_bookings_treeview()

    def _create_all_bookings_treeview(self) -> None:
        '''Create and populate the Treeview for all bookings.'''
        # Add 'User ID' column compared to user's booking page
        columns = ('id', 'user_id', 'bus', 'route', 'passenger', 'phone', 'date', 'status')
        tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', style="Treeview")

        # Define headings
        tree.heading('id', text='ID')
        tree.heading('user_id', text='User ID')
        tree.heading('bus', text='Bus #')
        tree.heading('route', text='Route')
        tree.heading('passenger', text='Passenger')
        tree.heading('phone', text='Phone')
        tree.heading('date', text='Date')
        tree.heading('status', text='Status')

        # Define column properties
        tree.column('id', width=50, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('user_id', width=70, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('bus', width=70, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('route', width=200, stretch=tk.YES)
        tree.column('passenger', width=150, stretch=tk.YES)
        tree.column('phone', width=120, stretch=tk.NO)
        tree.column('date', width=120, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

        # Populate Treeview
        for booking in self._all_bookings:
            bus_number = getattr(booking.bus, 'bus_number', 'N/A') if booking.bus else 'N/A'
            route_display = getattr(booking.bus, 'route', 'Unknown') if booking.bus else 'Unknown'
            booking_time_dt = getattr(booking, 'booking_time', None)
            date_str = booking_time_dt.strftime('%Y-%m-%d %H:%M') if isinstance(booking_time_dt, datetime) else 'N/A'
            status = getattr(booking, 'status', 'Unknown').capitalize()
            user_id = getattr(booking, 'user_id', 'N/A')
            passenger_name = getattr(booking, 'passenger_name', 'N/A')
            phone_number = getattr(booking, 'phone_number', 'N/A')

            # Route cleaning could be added here if needed

            tree.insert('', tk.END, values=(
                booking.id,
                user_id,
                bus_number,
                route_display,
                passenger_name,
                phone_number,
                date_str,
                status
            ), iid=str(booking.id))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def reset_state(self) -> None:
        '''Reload data when page is shown.'''
        self._load_all_bookings() 