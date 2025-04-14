# src/views/pages/admin_export_page.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional
import os
from datetime import datetime

from views.pages.admin_base_page import AdminPage
from views.config.theme import PALETTE, FONTS
from views.components.card import Card
from views.components.input import Input # For User ID input

class AdminExportPage(AdminPage):
    '''
    Admin page for exporting booking data to CSV.
    Requires admin authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state
        self._error: Optional[str] = None
        self._status_message: Optional[str] = None

        # Services inherited
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the export page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Export Bookings",
            font=FONTS["h1"],
            fg=PALETTE["text_primary"],
            bg=PALETTE["secondary"],
            anchor='w'
        )
        header_label.pack(side=tk.LEFT)

        # --- Content Area ---
        content_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # --- Export All Card ---
        export_all_card = Card(content_frame, props={'title': 'Export All Bookings', 'padding': 15})
        export_all_card.pack(pady=10, fill=tk.X)

        export_all_btn = ttk.Button(
            export_all_card.main_area,
            text="Export All to CSV...",
            style="Accent.TButton",
            command=self._handle_export_all
        )
        export_all_btn.pack(pady=5)

        # --- Export Specific User Card ---
        export_user_card = Card(content_frame, props={'title': 'Export User Bookings', 'padding': 15})
        export_user_card.pack(pady=10, fill=tk.X)

        user_form_frame = export_user_card.main_area

        self.user_id_input = Input(
            user_form_frame,
            props={
                'label': 'User ID',
                'placeholder': 'Enter User ID to export',
                'required': True,
                'validate': lambda v: v.isdigit() and int(v) > 0 # Basic numeric validation
            }
        )
        self.user_id_input.pack(fill=tk.X, pady=(5, 10))

        export_user_btn = ttk.Button(
            user_form_frame,
            text="Export User's Bookings to CSV...",
            style="Accent.TButton",
            command=self._handle_export_user
        )
        export_user_btn.pack(pady=5)

        # --- Status Label ---
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=FONTS["caption"],
            fg=PALETTE["text_secondary"],
            bg=PALETTE["secondary"],
            anchor='w',
            wraplength=600 # Allow wrapping
        )
        self.status_label.pack(pady=(10,0), fill=tk.X)

    def _update_status(self, message: str, is_error: bool = False):
        '''Update the status label text and color.'''
        self.status_label.config(text=message, fg=PALETTE["danger"] if is_error else PALETTE["text_secondary"])

    def _get_save_filepath(self, suggested_filename: str) -> Optional[str]:
        '''Open a save file dialog and return the selected path.'''
        # Default directory (e.g., user's home or a dedicated exports folder)
        # For simplicity, let's default to the directory containing the script
        # In a real app, consider user preferences or a dedicated exports dir
        initial_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # Project root approx.
        exports_dir = os.path.join(initial_dir, 'exports')
        os.makedirs(exports_dir, exist_ok=True)

        filepath = filedialog.asksaveasfilename(
            initialdir=exports_dir,
            initialfile=suggested_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        return filepath # Returns empty string if cancelled

    def _handle_export_all(self):
        '''Handle exporting all bookings.'''
        self._update_status("Preparing to export all bookings...")
        if not self.booking_service:
            self._update_status("Booking service not available.", is_error=True)
            messagebox.showerror("Error", "Booking service not available.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        suggested_filename = f"bookings_export_all_{timestamp}.csv"

        filepath = self._get_save_filepath(suggested_filename)
        if not filepath: # User cancelled dialog
            self._update_status("Export cancelled.")
            return

        self._update_status(f"Exporting all bookings to {os.path.basename(filepath)}...")
        try:
            success = self.booking_service.export_bookings_to_csv(filepath)
            if success:
                self._update_status(f"Successfully exported all bookings to: {filepath}")
                messagebox.showinfo("Export Successful", f"All bookings exported to:\n{filepath}")
            else:
                self._update_status("Failed to export all bookings (service returned false).", is_error=True)
                messagebox.showerror("Export Failed", "The export process failed.")
        except Exception as e:
            self._update_status(f"Error exporting all bookings: {str(e)}", is_error=True)
            messagebox.showerror("Export Error", f"An error occurred during export:\n{str(e)}")

    def _handle_export_user(self):
        '''Handle exporting bookings for a specific user.'''
        if not self.user_id_input.is_valid():
            self._update_status("Please enter a valid User ID.", is_error=True)
            messagebox.showwarning("Invalid Input", "Please enter a valid positive User ID.")
            return

        user_id = int(self.user_id_input.get_value())
        self._update_status(f"Preparing to export bookings for User ID: {user_id}...")

        if not self.booking_service:
            self._update_status("Booking service not available.", is_error=True)
            messagebox.showerror("Error", "Booking service not available.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # TODO: Optionally fetch username for filename if AuthService allows get_by_id
        suggested_filename = f"bookings_user_{user_id}_{timestamp}.csv"

        filepath = self._get_save_filepath(suggested_filename)
        if not filepath: # User cancelled dialog
            self._update_status("Export cancelled.")
            return

        self._update_status(f"Exporting bookings for User ID {user_id} to {os.path.basename(filepath)}...")
        try:
            success = self.booking_service.export_user_bookings_to_csv(user_id, filepath)
            if success:
                self._update_status(f"Successfully exported User {user_id}'s bookings to: {filepath}")
                messagebox.showinfo("Export Successful", f"User {user_id}'s bookings exported to:\n{filepath}")
            else:
                self._update_status(f"Failed to export User {user_id}'s bookings (service returned false).", is_error=True)
                messagebox.showerror("Export Failed", f"The export process failed for User ID {user_id}.")
        except Exception as e:
            self._update_status(f"Error exporting User {user_id}'s bookings: {str(e)}", is_error=True)
            messagebox.showerror("Export Error", f"An error occurred during export for User ID {user_id}:\n{str(e)}")

    def reset_state(self) -> None:
        '''Reset state when page is shown.'''
        self._update_status("") # Clear status message
        if hasattr(self, 'user_id_input'):
            self.user_id_input.clear() 