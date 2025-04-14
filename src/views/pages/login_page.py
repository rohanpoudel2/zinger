import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Any, Optional

# Removed: from views.components.base_component import Component
from views.components.input import Input
# Removed: from views.components.button import Button
from views.components.card import Card
from views.context.app_context import AppContext

# Import the palette and font definitions
from views.config.theme import PALETTE, FONTS

# Inherit from tk.Frame directly or the simplified BaseComponent
class LoginPage(tk.Frame):
    """
    Login page frame using standard Tkinter patterns.
    """
    
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        super().__init__(parent, bg=PALETTE["secondary"], **kwargs)
        self.props = props or {}
        self.app = self.props.get('app') # Get the main App instance if passed
        self.context = AppContext()
        self.auth_service = self.context.get_service('auth_service')

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout the widgets for the login page."""
        # Center the login card using grid in this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Login card
        card = Card(
            self,
            props={
                'title': 'Login',
                'width': 400,
                'padding': 20,
                'elevation': 2
            }
        )
        card.grid(row=1, column=1, padx=20, pady=20)
        
        # Logo
        logo_label = tk.Label(card.main_area, text="🚌", font=('Arial', 48), bg=PALETTE["card_bg"])
        logo_label.pack(pady=(20, 30)) # Increased padding
        
        # Form frame inside card
        form_frame = tk.Frame(card.main_area, bg=PALETTE["card_bg"])
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True) # Increased padding
        
        # Username input
        self.username_input = Input(
            form_frame,
            props={
                'label': 'Username',
                'placeholder': 'Enter your username',
                'required': True,
                'validate': self._validate_username,
                'on_change': lambda v: self._update_button_state() # Update button on change
            }
        )
        self.username_input.pack(fill=tk.X, pady=5)
        
        # Password input
        self.password_input = Input(
            form_frame,
            props={
                'label': 'Password',
                'placeholder': 'Enter your password',
                'type': 'password',
                'required': True,
                'validate': lambda v: v != '', # Simple validation
                'on_change': lambda v: self._update_button_state()
            }
        )
        self.password_input.pack(fill=tk.X, pady=5)
        
        # Error message label (initially empty)
        self.error_label = tk.Label(
            form_frame, text='', fg=PALETTE["danger"], bg=PALETTE["card_bg"],
            anchor='w', justify=tk.LEFT, wraplength=350
        )
        self.error_label.pack(fill=tk.X, pady=(5, 0))
        self.error_label.pack_forget() # Hide initially
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg=PALETTE["card_bg"])
        button_frame.pack(fill=tk.X, pady=10)
        
        # Login button (using ttk.Button with Primary style)
        self.login_button = ttk.Button(
            button_frame,
            text='LOGIN', # Uppercase text
            command=self._handle_login,
            style='Primary.TButton',
            state=tk.DISABLED # Initially disabled
        )
        self.login_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Register link frame
        register_frame = tk.Frame(form_frame, bg=PALETTE["card_bg"])
        register_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(register_frame, text="Don't have an account?", bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"], font=FONTS["body"]).pack(side=tk.LEFT)
        register_link = tk.Label(
            register_frame, text="Register", fg=PALETTE["primary"], 
            cursor='hand2', bg=PALETTE["card_bg"], font=FONTS["body_bold"] 
        )
        register_link.pack(side=tk.LEFT, padx=5)
        register_link.bind('<Button-1>', self._navigate_to_register)

        # Perform initial button state check *after* all widgets are created
        self._update_button_state()

    def _validate_username(self, value: str) -> bool:
        """Validate username input."""
        is_valid = value.strip() != ''
        # Update component's visual state if needed (e.g., border color)
        # This logic might reside within the Input component itself in a real scenario
        return is_valid
    
    def _update_button_state(self) -> None:
        """Update login button enabled state based on form validity."""
        # Check validity directly from the Input components, ensuring they exist first
        is_username_valid = hasattr(self, 'username_input') and self.username_input and self.username_input.is_valid()
        is_password_valid = hasattr(self, 'password_input') and self.password_input and self.password_input.is_valid()
        
        new_state = tk.NORMAL if (is_username_valid and is_password_valid) else tk.DISABLED
        # Ensure button exists before configuring
        if hasattr(self, 'login_button') and self.login_button and self.login_button.winfo_exists():
            if self.login_button.cget('state') != new_state:
                self.login_button.config(state=new_state)
    
    def _handle_login(self) -> None:
        """Handle login button click."""
        self.login_button.config(state=tk.DISABLED, text="Logging in...")
        self.error_label.pack_forget() # Hide previous errors
        
        username = self.username_input.get_value()
        password = self.password_input.get_value()
        
        if not self.auth_service:
            messagebox.showerror("Error", "Authentication service not available.")
            self.login_button.config(state=tk.NORMAL, text="LOGIN")
            return
            
        try:
            user = self.auth_service.login(username, password)
            if user:
                # App context update will trigger App.update via observer
                # App.update will handle navigation
                pass 
            else:
                if hasattr(self, 'login_button') and self.login_button:
                    self.login_button.config(state=tk.NORMAL) # Re-enable ttk.Button (text is fixed)
                self._show_error("Invalid username or password") # Show error after potential re-enable
                # Button text update handled separately or not needed if error shown
        except Exception as e:
            if hasattr(self, 'login_button') and self.login_button:
                self.login_button.config(state=tk.NORMAL)
            self._show_error(f"Login failed: {str(e)}")

    def _show_error(self, message: str) -> None:
        """Display an error message below the inputs."""
        self.error_label.config(text=message, font=FONTS["caption"], fg=PALETTE["danger"]) # Use theme
        self.error_label.pack(fill=tk.X, pady=(5, 0), before=self.login_button.master) # Place it before button frame
    
    def _navigate_to_register(self, event=None) -> None:
        """Navigate to register page using the App instance."""
        if self.app and hasattr(self.app, 'show_page'):
            self.app.show_page('register')
        else:
            print("Error: App instance not found or doesn't have show_page method.")

    def reset_state(self) -> None:
        """Reset the page to its initial state when shown."""
        self.username_input.clear()
        self.password_input.clear()
        
        # Clear error message
        if hasattr(self, 'error_label'):
            self.error_label.config(text='')
            self.error_label.pack_forget()
            
        # Reset button text and state
        if hasattr(self, 'login_button') and self.login_button:
            self.login_button.config(state=tk.DISABLED, text="LOGIN") 
            # Re-check validity in case fields have persisted values
            self._update_button_state() 

    # Removed: init, render, state management methods (_state, set_state, get_state)
    # Removed: _on_username_change, _on_password_change (logic moved to _update_button_state)
    # Removed: Direct validation callbacks, using Input component's internal validation trigger
    # Removed: _validate_password (simplified) 