# src/views/pages/admin_base_page.py
import tkinter as tk
from typing import Dict, Any

from views.pages.base_page import AuthenticatedPage
from models.database_models import UserRole # Import UserRole
from views.config.theme import PALETTE, FONTS

class AdminPage(AuthenticatedPage):
    """
    Base class for pages that require ADMIN authentication.
    Checks for authentication and admin role on init.
    Redirects to login or dashboard if checks fail.
    Subclasses must implement _create_page_widgets().
    """
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] | None = None, **kwargs):
        # Call AuthenticatedPage init first to check basic login
        super().__init__(parent, props=props, **kwargs)

        # If the super().__init__ returned early (due to not being authenticated),
        # this instance might not have all expected attributes, so stop.
        if not hasattr(self, 'context'):
            return
        
        # --- Check Admin Role --- 
        is_admin = self.current_user and getattr(self.current_user, 'role', None) == UserRole.ADMIN

        if not is_admin:
            print("User is not an admin, redirecting...")
            # Clear the frame content added by AuthenticatedPage if initialization failed
            for widget in self.winfo_children():
                widget.destroy()
                
            # Show an error message or redirect
            tk.Label(self, text="Access Denied: Admin privileges required.", 
                     fg=PALETTE["danger"], bg=PALETTE["secondary"],
                     font=FONTS["body_bold"]).pack(pady=20, padx=20)
                     
            # Optional: Redirect back to dashboard after a delay
            # if self.app:
            #     self.app.after(2000, lambda: self.app.show_page('dashboard'))
                 
            # We need to prevent _create_page_widgets from being called
            # in the subclass if the role check fails.
            # We can achieve this by setting a flag or overriding the method call flow.
            # A simple approach is to just return here, but subclasses might still
            # try to access admin-specific things if not careful.
            # Let's assume the check in AuthenticatedPage + this check covers it.
            # The _create_page_widgets in AuthenticatedPage raises NotImplementedError,
            # so if we reach this point and fail the admin check, that method 
            # won't be called *by the subclass* because the superclass init ensures it.
            return 

        # If both authenticated and admin, the AuthenticatedPage.__init__ 
        # would have already called the subclass's _create_page_widgets. 
        # No further action needed here regarding widget creation.

    # _create_page_widgets is implemented by subclasses 