# src/views/pages/admin_dashboard_page.py
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from views.pages.admin_base_page import AdminPage # Inherit from AdminPage
from views.config.theme import PALETTE, FONTS
from views.components.card import Card

class AdminDashboardPage(AdminPage):
    '''
    Main dashboard page for Admin users.
    Requires admin authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Call AdminPage init (handles auth checks and calls _create_page_widgets)
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the admin dashboard page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Admin Dashboard",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # --- Admin Actions Card ---
        content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        actions_card = Card(
            content_frame,
            props={
                'title': 'Admin Actions',
                'padding': 20
            }
        )
        actions_card.pack(pady=10, fill=tk.X)

        button_container = actions_card.main_area
        # Use pack for buttons since Card uses pack internally for title
        # button_container.columnconfigure(0, weight=1) # Remove grid config

        # View All Bookings Button
        view_bookings_btn = ttk.Button(
            button_container,
            text="View All Bookings",
            style="Primary.TButton",
            command=self._navigate_to_all_bookings # Placeholder for now
        )
        # view_bookings_btn.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        view_bookings_btn.pack(fill=tk.X, padx=10, pady=5)

        # Manage Users Button
        manage_users_btn = ttk.Button(
            button_container,
            text="Manage Users",
            style="Primary.TButton",
            command=self._navigate_to_manage_users # Placeholder for now
        )
        # manage_users_btn.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        manage_users_btn.pack(fill=tk.X, padx=10, pady=5)

        # Export Bookings Button
        export_bookings_btn = ttk.Button(
            button_container,
            text="Export Bookings",
            style="Accent.TButton",
            command=self._navigate_to_export_bookings # Placeholder for now
        )
        # export_bookings_btn.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        export_bookings_btn.pack(fill=tk.X, padx=10, pady=5)

    # --- Navigation Placeholders --- 
    # These will navigate to other admin pages we haven't created yet
    def _navigate_to_all_bookings(self):
        if self.app:
            self.app.show_page('admin_all_bookings') # Navigate to the new page
            # print("Navigate to View All Bookings (Not Implemented)")
            # messagebox.showinfo("Not Implemented", "Admin - View All Bookings page is not yet implemented.")

    def _navigate_to_manage_users(self):
        if self.app:
            self.app.show_page('admin_manage_users') # Navigate to the new page
            # print("Navigate to Manage Users (Not Implemented)")
            # messagebox.showinfo("Not Implemented", "Admin - Manage Users page is not yet implemented.")

    def _navigate_to_export_bookings(self):
        if self.app:
            self.app.show_page('admin_export_bookings') # Navigate to the new page
            # print("Navigate to Export Bookings (Not Implemented)")
            # messagebox.showinfo("Not Implemented", "Admin - Export Bookings page is not yet implemented.")

    def reset_state(self) -> None:
        """Reset state when page is shown (nothing to reset here yet)."""
        pass 