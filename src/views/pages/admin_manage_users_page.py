# src/views/pages/admin_manage_users_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from views.pages.admin_base_page import AdminPage
from views.config.theme import PALETTE, FONTS
from models.database_models import UserModel, UserRole # For type hinting and role display
# AuthService is available via self.auth_service from AuthenticatedPage

class AdminManageUsersPage(AdminPage):
    '''
    Admin page to view and manage user accounts.
    Requires admin authentication.
    '''
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        # Local state
        self._all_users: List[UserModel] = []
        self._is_loading: bool = True
        self._error: Optional[str] = None
        self._selected_user_id: Optional[int] = None

        # Services inherited
        super().__init__(parent, props=props, **kwargs)

    def _create_page_widgets(self) -> None:
        '''Create widgets for the manage users page.'''
        # Page header
        header_frame = tk.Frame(self, bg=PALETTE["secondary"], padx=20, pady=20)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(
            header_frame,
            text="Manage Users",
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
            command=self._load_users
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)

        # Content area
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

        # Status Label
        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)
        self.status_label.grid_remove()

        # Deactivate Button
        button_frame = tk.Frame(self.content_frame, bg=PALETTE["secondary"])
        button_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        button_frame.columnconfigure(0, weight=1) # Center button

        self.deactivate_button = ttk.Button(
            button_frame,
            text="Deactivate Selected User",
            style="Danger.TButton",
            command=self._handle_deactivate_user,
            state=tk.DISABLED
        )
        self.deactivate_button.grid(row=0, column=0, padx=10, pady=5)

        # Load data initially
        self._load_users()

    def _load_users(self) -> None:
        '''Fetch all users using AuthService.'''
        self._is_loading = True
        self._error = None
        self._all_users = []
        self._selected_user_id = None
        if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
            self.deactivate_button.config(state=tk.DISABLED)
        self._render_ui_states()

        if not self.auth_service:
            self._is_loading = False
            self._error = "Authentication service not available."
            self._render_ui_states()
            return

        try:
            users = self.auth_service.get_all_users()
            self._all_users = users or []
            self._is_loading = False
            if not self._all_users:
                self._error = "No users found in the system."

        except Exception as e:
            print(f"ERROR loading all users: {e}")
            self._is_loading = False
            self._error = f"Failed to load users: {str(e)}"

        self._render_ui_states()

    def _render_ui_states(self) -> None:
        '''Render the UI based on loading/error state and user data.'''
        for widget in self.tree_container.winfo_children():
            widget.destroy()

        self.status_label = tk.Label(self.tree_container, text="", font=FONTS["body"], bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"])
        self.status_label.grid(row=0, column=0, pady=30)

        if self._is_loading:
            self.status_label.config(text="Loading users...", fg=PALETTE["text_secondary"])
        elif self._error and not self._all_users:
             self.status_label.config(text=self._error, fg=PALETTE["danger"], wraplength=400)
        elif not self._all_users:
            message = self._error if self._error else "No users found."
            self.status_label.config(text=message, fg=PALETTE["text_secondary"])
        else:
            self.status_label.grid_remove()
            self._create_users_treeview()

        # Ensure button state is updated after render
        self._update_button_state()

    def _create_users_treeview(self) -> None:
        '''Create and populate the Treeview for all users.'''
        columns = ('id', 'username', 'email', 'role', 'active')
        tree = ttk.Treeview(self.tree_container, columns=columns, show='headings', style="Treeview")

        # Define headings
        tree.heading('id', text='ID')
        tree.heading('username', text='Username')
        tree.heading('email', text='Email')
        tree.heading('role', text='Role')
        tree.heading('active', text='Active')

        # Define column properties
        tree.column('id', width=50, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('username', width=150, stretch=tk.YES)
        tree.column('email', width=200, stretch=tk.YES)
        tree.column('role', width=80, anchor=tk.CENTER, stretch=tk.NO)
        tree.column('active', width=70, anchor=tk.CENTER, stretch=tk.NO)

        # Populate Treeview
        for user in self._all_users:
            user_id = getattr(user, 'id', 'N/A')
            username = getattr(user, 'username', 'N/A')
            email = getattr(user, 'email', 'N/A')
            role_enum = getattr(user, 'role', None)
            role_str = str(role_enum).split('.')[-1].capitalize() if role_enum else 'N/A'
            is_active = getattr(user, 'is_active', False)
            active_str = "Yes" if is_active else "No"

            tree.insert('', tk.END, values=(
                user_id,
                username,
                email,
                role_str,
                active_str
            ), iid=str(user_id)) # Use user ID as item ID

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind selection event
        tree.bind('<<TreeviewSelect>>', self._on_user_select)

    def _on_user_select(self, event):
        '''Handle Treeview selection changes.'''
        selected_items = event.widget.selection()
        if selected_items:
            self._selected_user_id = int(selected_items[0])
        else:
            self._selected_user_id = None
        self._update_button_state()

    def _update_button_state(self):
        '''Enable/disable deactivate button based on selection and user status.'''
        enable = False
        if self._selected_user_id is not None:
            selected_user = next((u for u in self._all_users if u.id == self._selected_user_id), None)
            # Enable only if user is found, is active, and is not the currently logged-in admin
            if selected_user and selected_user.is_active and selected_user.id != self.current_user.id:
                enable = True
        
        if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
            self.deactivate_button.config(state=tk.NORMAL if enable else tk.DISABLED)

    def _handle_deactivate_user(self):
        '''Handle the deactivate button click.'''
        if self._selected_user_id is None:
            messagebox.showwarning("No Selection", "Please select a user to deactivate.")
            return
        
        selected_user = next((u for u in self._all_users if u.id == self._selected_user_id), None)
        if not selected_user:
            messagebox.showerror("Error", "Selected user not found.")
            return
        if selected_user.id == self.current_user.id:
            messagebox.showerror("Error", "You cannot deactivate your own account.")
            return
        if not selected_user.is_active:
            messagebox.showinfo("Info", "This user is already deactivated.")
            return

        # Confirmation
        if messagebox.askyesno("Confirm Deactivation", f"Are you sure you want to deactivate user '{selected_user.username}' (ID: {self._selected_user_id})?"):
            if self.deactivate_button and self.deactivate_button.winfo_exists():
                 self.deactivate_button.config(state=tk.DISABLED)
            try:
                success = self.auth_service.deactivate_user(self._selected_user_id)
                if success:
                    messagebox.showinfo("Success", f"User '{selected_user.username}' deactivated successfully.")
                    self._load_users() # Refresh the list
                else:
                    messagebox.showerror("Error", "Failed to deactivate user (Service returned false).")
            except Exception as e:
                 messagebox.showerror("Error", f"Failed to deactivate user: {str(e)}")
            # Button state will be reset by _load_users -> _render_ui_states -> _update_button_state

    def reset_state(self) -> None:
        '''Reload data when page is shown.'''
        self._load_users() 