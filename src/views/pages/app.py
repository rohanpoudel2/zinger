import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Callable, Type

# Removed: from views.components.base_component import Component # Keep if needed
from views.context.app_context import AppContext, Observer
from views.pages.login_page import LoginPage
from views.pages.dashboard_page import DashboardPage
from views.pages.register_page import RegisterPage
from views.config.theme import PALETTE, FONTS # Import from theme config

# This will be imported later when the pages are created
# from views.pages.login_page import LoginPage
# from views.pages.dashboard_page import DashboardPage
# from views.pages.bus_list_page import BusListPage
# from views.pages.booking_page import BookingPage

# Define color palette
# PALETTE = {
#     "primary": "#3498db",
#     "secondary": "#ecf0f1",
#     "accent": "#2ecc71",
#     "danger": "#e74c3c",
#     "navbar_bg": "#2c3e50",
#     "card_bg": "#ffffff",
#     "text_primary": "#34495e",
#     "text_secondary": "#7f8c8d",
#     "text_light": "#ffffff",
#     "placeholder": "#bdc3c7", # Lighter gray for placeholder
#     "border": "#bdc3c7" # Border color for inputs
# }

class App(tk.Tk, Observer):
    """
    Main application window.
    Handles page navigation by showing/hiding page frames.
    Observes application context for state changes.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Bus Booking System")
        self.geometry("800x600")

        # Configure ttk styles based on Material Theme
        self._configure_ttk_styles()

        # Configure main window grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Context
        self.context = AppContext()
        self.context.get_store('auth').attach(self)
        
        # Page storage
        self._pages: Dict[str, tk.Frame] = {}
        self._current_page_name: Optional[str] = None
        
        # Create shared UI elements
        self._create_navbar()
        self._create_main_container()
        self._create_status_bar()
        
        # Define routes (Page Classes)
        self._routes: Dict[str, Type[tk.Frame]] = { # Use Type[tk.Frame] or specific page types
            'login': LoginPage,
            'register': RegisterPage,
            'dashboard': DashboardPage,
            # 'buses': BusListPage,
            # 'booking': BookingPage,
        }
        
        # Initialize with the correct starting page based on auth state
        initial_route = 'dashboard' if self.context.get_store('auth').get_state()['is_authenticated'] else 'login'
        self.show_page(initial_route)
        self._update_navbar()
        self._update_status_bar()

    def _configure_ttk_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style(self) 
        # Try 'clam' or 'alt' for a base theme less likely to be overridden by OS
        try:
            style.theme_use('clam') 
        except tk.TclError:
            print("Warning: 'clam' theme not found, using default ttk theme.")

        # --- Button Styles ---
        # General settings for TButton
        style.configure('TButton', 
                        font=FONTS["button"], 
                        relief='flat', 
                        borderwidth=0,
                        padding=(16, 8)) # Default padding
        style.map('TButton', 
                  foreground=[('disabled', PALETTE["text_secondary"]), ('active', PALETTE["text_primary_on_primary"])], # Define only specific state changes
                  background=[('disabled', PALETTE["divider"]), ('active', PALETTE["primary_dark"])], # Default is set in style.configure
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])

        # Primary Button (inherits TButton, overrides colors)
        style.configure('Primary.TButton', 
                        background=PALETTE["primary"],
                        foreground=PALETTE["text_primary_on_primary"])
        style.map('Primary.TButton', 
                  background=[('active', PALETTE["primary_dark"]), ('disabled', PALETTE["divider"])])
        
        # Accent Button
        style.configure('Accent.TButton', 
                        background=PALETTE["accent"],
                        foreground=PALETTE["text_accent"])
        style.map('Accent.TButton', 
                  background=[('active', '#E64A19'), ('disabled', PALETTE["divider"])]) # Darker Orange for accent active

        # Danger Button (for Logout)
        style.configure('Danger.TButton', 
                        background=PALETTE["danger"],
                        foreground=PALETTE["text_light"])
        style.map('Danger.TButton', 
                  background=[('active', '#D32F2F'), ('disabled', PALETTE["divider"])]) # Darker Red for danger active

        # Navbar Button (Text-like)
        style.configure('Navbar.TButton', 
                        font=FONTS["button"],
                        background=PALETTE["navbar_bg"],
                        foreground=PALETTE["text_primary_on_primary"],
                        padding=(8,8))
        style.map('Navbar.TButton', 
                  background=[('active', PALETTE["primary_dark"])]) # Use primary dark for hover/click

        # --- Treeview Style ---
        style.configure("Treeview.Heading", 
                        font=FONTS["body_bold"], 
                        background=PALETTE["primary_light"], 
                        foreground=PALETTE["text_primary"])
        style.configure("Treeview", 
                        font=FONTS["body"], 
                        rowheight=int(FONTS["body"][1] * 2.0)) # Adjust row height based on font
        style.map("Treeview", 
                  background=[('selected', PALETTE["primary"])],
                  foreground=[('selected', PALETTE["text_primary_on_primary"])])

    def _create_navbar(self) -> None:
        """Create the persistent navigation bar frame."""
        self.navbar = tk.Frame(self, height=60, bg=PALETTE["navbar_bg"], bd=0, relief=tk.FLAT)
        self.navbar.grid(row=0, column=0, sticky='ew')
        self.navbar.grid_columnconfigure(0, weight=1)
        
        # App title (persistent)
        title_label = tk.Label(
            self.navbar,
            text="Bus Booking System",
            font=FONTS["h2"],
            fg=PALETTE["text_light"],
            bg=PALETTE["navbar_bg"],
            anchor='w',
            padx=20
        )
        title_label.grid(row=0, column=0, sticky='w')
        
        # Frame for dynamic buttons (will be updated)
        self.nav_buttons_frame = tk.Frame(self.navbar, bg=PALETTE["navbar_bg"], bd=0)
        self.nav_buttons_frame.grid(row=0, column=1, sticky='e', padx=(0, 10))

    def _create_main_container(self) -> None:
        """Create the container where page frames will be placed."""
        self.main_content_container = tk.Frame(self, bg=PALETTE["secondary"])
        self.main_content_container.grid(row=1, column=0, sticky='nsew')
        # Ensure the container allows pages to expand
        self.main_content_container.grid_rowconfigure(0, weight=1)
        self.main_content_container.grid_columnconfigure(0, weight=1)

    def _create_status_bar(self) -> None:
        """Create the persistent status bar frame."""
        # Use highlightbackground and highlightthickness for border
        self.status_bar = tk.Frame(self, height=25, bg=PALETTE["secondary"], 
                                 highlightbackground=PALETTE["divider"], 
                                 highlightthickness=1, bd=0, relief=tk.FLAT)
        self.status_bar.grid(row=2, column=0, sticky='ew')
        
        # Persistent labels (content will be updated)
        self.status_label = tk.Label(
            self.status_bar, text="Ready",
            font=FONTS["caption"], # Use caption font
            fg=PALETTE["text_secondary"], bg=PALETTE["secondary"], anchor='w', padx=10
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.user_label = tk.Label(
            self.status_bar, text="",
            font=FONTS["caption"], # Use caption font
            fg=PALETTE["text_secondary"], bg=PALETTE["secondary"], anchor='e', padx=10
        )
        self.user_label.pack(side=tk.RIGHT)

    def _update_navbar(self) -> None:
        """Update the buttons in the navigation bar based on auth state."""
        # Clear existing buttons
        for widget in self.nav_buttons_frame.winfo_children():
            widget.destroy()
            
        is_authenticated = self.context.get_store('auth').get_state()['is_authenticated']
        current_page = self._current_page_name # Get current page to avoid redundant buttons
        
        # Use ttk.Button with Navbar.TButton style
        # Options like text, command are passed directly

        if is_authenticated:
            # Only show Dashboard if not already there
            if current_page != 'dashboard':
                ttk.Button(self.nav_buttons_frame, text="DASHBOARD", style='Navbar.TButton', command=lambda: self.show_page('dashboard')).pack(side=tk.LEFT, padx=5)
            # tk.Button(self.nav_buttons_frame, text="View Buses", bg=PALETTE["primary"], command=lambda: self.show_page('buses'), **common_btn_options).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.nav_buttons_frame, text="LOGOUT", style='Danger.TButton', command=self._logout).pack(side=tk.LEFT, padx=5) # Use Danger style for Logout
        # No Login/Register buttons needed in navbar if already on those pages
        # elif current_page not in ['login', 'register']:
        #     tk.Button(self.nav_buttons_frame, text="Login", bg=PALETTE["primary"], command=lambda: self.show_page('login'), **common_btn_options).pack(side=tk.LEFT, padx=10)
        #     tk.Button(self.nav_buttons_frame, text="Register", bg=PALETTE["accent"], command=lambda: self.show_page('register'), **common_btn_options).pack(side=tk.LEFT, padx=10)

    def _update_status_bar(self) -> None:
        """Update the text in the status bar labels."""
        # Update status text (can be enhanced with loading/error states from context later)
        self.status_label.config(text="Ready") 

        # Update user info using AppContext convenience methods
        if self.context.is_authenticated():
            user = self.context.get_current_user()
            self.user_label.config(text=f"Logged in as: {user.username}" if user else "Logged In")
        else:
            self.user_label.config(text="Not logged in")
            
    def show_page(self, page_name: str) -> None:
        """Show the requested page frame, creating it if necessary."""
        if page_name == self._current_page_name:
            return # Already showing this page
            
        page_class = self._routes.get(page_name)
        if not page_class:
            print(f"Error: Route '{page_name}' not found.")
            return
            
        # Create page if it doesn't exist
        if page_name not in self._pages:
            # Pass context or necessary callbacks/data via props if needed
            # Example: props={'app': self, 'context': self.context}
            page_frame = page_class(self.main_content_container, props={'app': self}) 
            self._pages[page_name] = page_frame
            # Place the new frame in the main container, stacked underneath others
            page_frame.grid(row=0, column=0, sticky='nsew')
        
        # Get the frame to show
        frame_to_show = self._pages[page_name]
        
        # Reset page state before showing (if method exists)
        if hasattr(frame_to_show, 'reset_state') and callable(frame_to_show.reset_state):
            frame_to_show.reset_state()
        
        # Raise the requested frame to the top
        frame_to_show.tkraise()
        self._current_page_name = page_name
        print(f"Navigated to: {page_name}") # Debugging

    def update(self, subject, data: Any) -> None:
        """Observer method called when stores change."""
        auth_store = self.context.get_store('auth')
        # Check if auth state specifically changed
        if 'is_authenticated' in data:
            is_authenticated = data['is_authenticated']
            
            # Update UI elements that depend on auth state
            self._update_navbar()
            self._update_status_bar()
            
            # Navigate based on auth change
            current_page = self._current_page_name
            if is_authenticated and current_page in ['login', 'register']:
                self.show_page('dashboard')
            elif not is_authenticated and current_page not in ['login', 'register']:
                 self.show_page('login')
        
        # Can handle other state updates here (e.g., loading, errors) 
        # to update the status bar label if needed.

    def _logout(self) -> None:
        """Handle user logout by calling AuthService."""
        auth_service = self.context.get_service('auth_service')
        if auth_service:
            auth_service.logout()
        else:
            print("Error: AuthService not found in context during logout.")
        # The update method will handle navigation via observation

    # Removed: render (split into _create_ methods), 
    # _render_navbar, _render_status_bar, _render_current_route (replaced by show_page),
    # navigate (replaced by show_page)
    # Removed: State management related to routes/loading/error within App, 
    # rely on context and direct UI updates (_update_navbar, _update_status_bar) 