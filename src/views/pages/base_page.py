# src/views/pages/base_page.py

import tkinter as tk
from typing import Dict, Optional, Any

from views.context.app_context import AppContext
from views.config.theme import PALETTE

class AuthenticatedPage(tk.Frame):
    """
    Base class for pages that require user authentication.
    Checks for authentication on init and redirects to login if necessary.
    Subclasses must implement _create_page_widgets() to build their UI.
    """
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] | None = None, **kwargs):
        """Initialize the frame and check authentication."""
        # Ensure props exist and get necessary instances
        props = props or {}
        self.props = props
        self.app = self.props.get('app')
        self.context = AppContext()

        # Check authentication *before* creating page-specific widgets
        if not self.context.is_authenticated():
            print("User not authenticated, redirecting to login...")
            if self.app and hasattr(self.app, 'show_page'):
                # Schedule redirection using after_idle for safety
                # This allows the current __init__ stack to unwind first
                self.app.after_idle(lambda: self.app.show_page('login'))
                
                # Initialize the Frame minimally so Tkinter is happy,
                # but don't proceed to build the actual page UI.
                kwargs['bg'] = PALETTE.get("secondary", "#eceff1")
                super().__init__(parent, **kwargs)
                # Stop this __init__ here; the redirection will take over.
                return 
            else:
                # Fallback if redirection isn't possible (shouldn't happen)
                print("ERROR: AuthenticatedPage cannot redirect - 'app' instance missing.")
                kwargs['bg'] = PALETTE.get("secondary", "#eceff1")
                super().__init__(parent, **kwargs)
                tk.Label(self, text="Authentication Required", fg="red").pack(pady=20)
                return # Stop further initialization

        # --- If Authenticated --- 
        # Proceed with normal Frame initialization
        kwargs['bg'] = PALETTE.get("secondary", "#eceff1")
        super().__init__(parent, **kwargs)
        
        # --- Initialize common attributes for authenticated pages ---
        # Ensure context was set if this path is reached
        if not hasattr(self, 'context') or not self.context:
            print("CRITICAL ERROR: Context not set in AuthenticatedPage despite passing auth check.")
            tk.Label(self, text="Internal Error", fg="red").pack(pady=20)
            return
        
        # Get common services and user info needed by most authenticated pages
        self.auth_service = self.context.get_service('auth_service')
        self.booking_service = self.context.get_service('booking_service')
        self.current_user = self.context.get_current_user()
        
        # Validate essential data (optional but good practice)
        if not self.current_user:
            print("ERROR: Authenticated user data not found in context.")
            tk.Label(self, text="Error loading user data.", fg="red").pack(pady=20)
            # Optionally redirect back to login here as well
            # self.app.after_idle(lambda: self.app.show_page('login'))
            return
        
        # Call the method that subclasses must implement to build their UI
        self._create_page_widgets()

    def _create_page_widgets(self):
        """Subclasses MUST override this method to create their widgets."""
        # This ensures that UI creation only happens if authentication passes.
        raise NotImplementedError(f"{self.__class__.__name__} must implement _create_page_widgets")

    def reset_state(self) -> None:
        """
        Optional: Placeholder for resetting page state when shown.
        Subclasses can override this if they need specific reset logic.
        """
        pass # Default implementation does nothing 