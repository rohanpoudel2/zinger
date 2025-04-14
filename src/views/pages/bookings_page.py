# src/views/pages/bookings_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
from datetime import datetime

from views.pages.base_page import AuthenticatedPage
from views.config.theme import PALETTE, FONTS
from views.context.app_context import AppContext
# from models.database_models import BookingModel # Optional: for type hinting

class BookingsPage(AuthenticatedPage):
    '''
    Page to display all bookings for the currently logged-in user.
    Requires authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state for data
        self._bookings: List[Any] = [] # Store BookingModel or similar objects
        self._is_loading: bool = True
        self._error: Optional[str] = None
        self._selected_booking_id: Optional[int] = None

        # Booking service is available via AuthenticatedPage as self.booking_service
        # current_user is available via AuthenticatedPage as self.current_user

        # Call AuthenticatedPage init (handles auth check and calls _create_page_widgets)
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the bookings page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="My Bookings",
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
            command=self._load_bookings
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

        # Content area for the list/table
        self.content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.rowconfigure(0, weight=1) # Treeview container row
        self.content_frame.rowconfigure(1, weight=0) # Button row
        self.content_frame.columnconfigure(0, weight=1)

        # Container for Treeview and scrollbar
        self.tree_container = tk.Frame(self.content_frame, bg=PALETTE["card_bg"])
        self.tree_container.grid(row=0, column=0, sticky='nsew')
        self.tree_container.rowconfigure(0, weight=1)
        self.tree_container.columnconfigure(0, weight=1)

        # Status Label (initially hidden, shown during load/error)
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)
        self.status_label.grid_remove()

        # --- Add Cancel Button --- 
        button_frame = tk.Frame(self.content_frame, bg=PALETTE["secondary"])
        button_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        # Center the button within the frame
        button_frame.columnconfigure(0, weight=1)

        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancel Selected Booking", 
            style="Danger.TButton", # Use Danger style for cancel
            command=self._handle_cancel_booking,
            state=tk.DISABLED # Initially disabled
        )
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5) # Grid within button_frame

        # Load data initially
        self._load_bookings()

    def _load_bookings(self) -> None:
        '''Fetch bookings for the current user.'''
        self._is_loading = True
        self._error = None
        self._bookings = [] # Clear previous data
        self._selected_booking_id = None # Clear selection
        # Disable cancel button during load
        if hasattr(self, 'cancel_button') and self.cancel_button.winfo_exists():
            self.cancel_button.config(state=tk.DISABLED)
        self._render_ui_states() # Show loading state

        if not self.booking_service:
            self._is_loading = False
            self._error = "Booking service not available."
            self._render_ui_states()
            return
        if not self.current_user:
            self._is_loading = False
            self._error = "User information not found."
            self._render_ui_states()
            return

        try:
            bookings = self.booking_service.get_user_bookings(self.current_user.id)
            self._bookings = bookings or []
            self._is_loading = False
            if not self._bookings:
                self._error = "You have no bookings yet." # Info message

        except Exception as e:
            print(f"ERROR: src.views.pages.bookings_page._load_bookings: {e}") # Log error
            self._is_loading = False
            self._error = f"Failed to load bookings: {str(e)}"

        self._render_ui_states()

    def _render_ui_states(self) -> None:
        '''Render the UI based on loading/error state and booking data.'''
        # Clear previous treeview/scrollbar or status label
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        # Recreate status label
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)

        if self._is_loading:
            self.status_label.config(text="Loading your bookings...", fg=PALETTE["text_secondary"])
        elif self._error and not self._bookings:
             self.status_label.config(text=self._error, fg=PALETTE["danger"], wraplength=400)
        elif not self._bookings:
            message = self._error if self._error else "You have no bookings yet."
            self.status_label.config(text=message, fg=PALETTE["text_secondary"])
        else:
            self.status_label.grid_remove() # Hide status label
            self._create_bookings_treeview()

        # TODO: Update cancel button state if implemented

    def _create_bookings_treeview(self) -> None:
        '''Create and populate the bookings list Treeview.'''
        columns = ('id', 'bus', 'route', 'seats', 'date', 'status')
        tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', style="Treeview")

        # Define headings
        tree.heading('id', text='ID')
        tree.heading('bus', text='Bus #')
        tree.heading('route', text='Route')
        tree.heading('seats', text='Seats')
        tree.heading('date', text='Date')
        tree.heading('status', text='Status')

        # Define column properties
        tree.column('id', width=50, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('bus', width=80, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('route', width=250, stretch=tk.YES)
        tree.column('seats', width=50, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('date', width=120, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

        # Populate Treeview
        for booking in self._bookings:
            # Safely get related data
            bus_number = getattr(booking.bus, 'bus_number', 'N/A') if booking.bus else 'N/A'
            route_display = getattr(booking.bus, 'route', 'Unknown Route') if booking.bus else 'Unknown Route'
            booking_time_dt = getattr(booking, 'booking_time', None)

            date_str = booking_time_dt.strftime('%Y-%m-%d %H:%M') if isinstance(booking_time_dt, datetime) else 'N/A'
            status = getattr(booking, 'status', 'Unknown').capitalize()
            seat_count_display = getattr(booking, 'seat_count', 1) # Default to 1 if missing

            # Clean route name (optional, reuse from BusListPage if needed)
            # ... (add route cleaning logic if desired)

            tree.insert('', tk.END, values=(
                booking.id,
                bus_number,
                route_display,
                seat_count_display, # Use the safe value
                date_str,
                status
            ), iid=str(booking.id)) # Use booking ID as item ID

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind selection event
        tree.bind('<<TreeviewSelect>>', self._on_booking_select)

    def _on_booking_select(self, event):
        '''Handle Treeview selection changes.'''
        selected_items = event.widget.selection() # This gives the item ID (booking.id)
        if selected_items:
            selected_iid = selected_items[0]
            self._selected_booking_id = int(selected_iid)

            # Find the booking object to check its status
            selected_booking = next((b for b in self._bookings if b.id == self._selected_booking_id), None)
            
            # Enable cancel button only if booking exists and is not already cancelled/completed
            # (Adjust the condition based on your BookingModel status values)
            is_cancellable = selected_booking and getattr(selected_booking, 'status', 'Unknown').lower() not in ['cancelled', 'completed']
            
            if self.cancel_button and self.cancel_button.winfo_exists():
                 self.cancel_button.config(state=tk.NORMAL if is_cancellable else tk.DISABLED)
        else:
            self._selected_booking_id = None
            # Disable cancel button if nothing is selected
            if self.cancel_button and self.cancel_button.winfo_exists():
                self.cancel_button.config(state=tk.DISABLED)

    def _handle_cancel_booking(self):
        '''Handle the cancel button click.'''
        if not self._selected_booking_id:
            messagebox.showwarning("No Selection", "Please select a booking to cancel.")
            return
        # Confirmation dialog
        if messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel booking {self._selected_booking_id}?"):
            # Disable button during cancellation attempt
            if self.cancel_button and self.cancel_button.winfo_exists():
                self.cancel_button.config(state=tk.DISABLED)
            try:
                success = self.booking_service.cancel_booking(self._selected_booking_id)
                if success:
                    messagebox.showinfo("Success", "Booking cancelled successfully.")
                    self._load_bookings() # Refresh the list
                else:
                    # This case might be less likely if cancel_booking raises exceptions
                    messagebox.showerror("Error", "Failed to cancel booking (Service returned false).")
            except Exception as e:
                 messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")
            # No finally block needed as _load_bookings will reset selection and button state

    def reset_state(self) -> None:
        '''Reset state when page is shown.'''
        self._load_bookings() # Refresh bookings list (also resets selection and button)
        # Ensure button is disabled after potential load errors
        # if hasattr(self, 'cancel_button') and self.cancel_button.winfo_exists():
        #     self.cancel_button.config(state=tk.DISABLED)
        # self._selected_booking_id = None # _load_bookings handles this 