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

class RegisterPage(tk.Frame):
    """
    Registration page frame using standard Tkinter patterns.
    """
    
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        super().__init__(parent, bg=PALETTE["secondary"], **kwargs)
        self.props = props or {}
        self.app = self.props.get('app') # Get the main App instance
        self.context = AppContext()
        self.auth_service = self.context.get_service('auth_service')
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout the widgets for the registration page."""
        # Center the card
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Registration card
        card = Card(
            self,
            props={
                'title': 'Register',
                'width': 400,
                'padding': 20,
                'elevation': 2
            }
        )
        card.grid(row=1, column=1, padx=20, pady=20)
        
        # Logo
        logo_label = tk.Label(card.main_area, text="🚌", font=('Arial', 48), bg=PALETTE["card_bg"])
        logo_label.pack(pady=(20, 30)) # Increased padding
        
        # Form frame
        form_frame = tk.Frame(card.main_area, bg=PALETTE["card_bg"])
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True) # Increased padding
        
        # --- Input Fields ---
        self.username_input = Input(
            form_frame,
            props={
                'label': 'Username',
                'placeholder': 'Choose a username',
                'required': True,
                'validate': self._validate_username,
                'on_change': lambda v: self._update_button_state()
            }
        )
        self.username_input.pack(fill=tk.X, pady=5)
        
        self.email_input = Input(
            form_frame,
            props={
                'label': 'Email',
                'placeholder': 'Enter your email',
                'required': True,
                'validate': self._validate_email,
                'on_change': lambda v: self._update_button_state()
            }
        )
        self.email_input.pack(fill=tk.X, pady=5)
        
        self.password_input = Input(
            form_frame,
            props={
                'label': 'Password',
                'placeholder': 'Choose a password (min 6 chars)',
                'type': 'password',
                'required': True,
                'validate': self._validate_password,
                'on_change': self._on_password_or_confirm_change # Special handler
            }
        )
        self.password_input.pack(fill=tk.X, pady=5)
        
        self.confirm_password_input = Input(
            form_frame,
            props={
                'label': 'Confirm Password',
                'placeholder': 'Confirm your password',
                'type': 'password',
                'required': True,
                'validate': self._validate_confirm_password,
                'on_change': self._on_password_or_confirm_change # Special handler
            }
        )
        self.confirm_password_input.pack(fill=tk.X, pady=5)
        
        # Error message label
        self.error_label = tk.Label(
            form_frame, text='', fg=PALETTE["danger"], bg=PALETTE["card_bg"],
            anchor='w', justify=tk.LEFT, wraplength=350
        )
        self.error_label.pack(fill=tk.X, pady=(5, 0))
        self.error_label.pack_forget()

        # Button frame
        button_frame = tk.Frame(form_frame, bg=PALETTE["card_bg"])
        button_frame.pack(fill=tk.X, pady=10)
        
        # Register button (using ttk.Button with Accent style)
        self.register_button = ttk.Button(
            button_frame,
            text='REGISTER', # Uppercase text
            command=self._handle_register,
            style='Accent.TButton',
            state=tk.DISABLED
        )
        self.register_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Login link frame
        login_frame = tk.Frame(form_frame, bg=PALETTE["card_bg"])
        login_frame.pack(fill=tk.X, pady=20) # Increased padding
        
        tk.Label(login_frame, text="Already have an account?", bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"], font=FONTS["body"]).pack(side=tk.LEFT)
        login_link = tk.Label(
            login_frame, text="Login", fg=PALETTE["primary"], 
            cursor='hand2', bg=PALETTE["card_bg"], font=FONTS["body_bold"] # Bold link
        )
        login_link.pack(side=tk.LEFT, padx=5)
        login_link.bind('<Button-1>', self._navigate_to_login)

        # Perform initial button state check *after* all widgets are created
        self._update_button_state()

    # --- Validation Methods ---
    def _validate_username(self, value: str) -> bool:
        return len(value.strip()) >= 4
    
    def _validate_email(self, value: str) -> bool:
        import re # Simple regex for email validation
        return re.match(r"[^@]+@[^@]+\.[^@]+", value) is not None

    def _validate_password(self, value: str) -> bool:
        return len(value) >= 6

    def _validate_confirm_password(self, value: str) -> bool:
        # Also check match against the current password value
        password = self.password_input.get_value() if self.password_input else ''
        return value == password and value != ''

    def _on_password_or_confirm_change(self, value: str) -> None:
        """Called when password or confirm password changes."""
        # Trigger validation update for confirm password field manually
        # because its validity depends on the password field
        # Ensure the confirm password input exists before accessing
        if hasattr(self, 'confirm_password_input') and self.confirm_password_input:
             self.confirm_password_input._validate_and_update()
        self._update_button_state()

    def _is_form_valid(self) -> bool:
        """Check if all input fields are currently valid."""
        # Add hasattr checks for robustness during initialization
        usr_valid = hasattr(self, 'username_input') and self.username_input and self.username_input.is_valid()
        eml_valid = hasattr(self, 'email_input') and self.email_input and self.email_input.is_valid()
        pwd_valid = hasattr(self, 'password_input') and self.password_input and self.password_input.is_valid()
        cnf_valid = hasattr(self, 'confirm_password_input') and self.confirm_password_input and self.confirm_password_input.is_valid()
        
        return usr_valid and eml_valid and pwd_valid and cnf_valid
    
    def _update_button_state(self) -> None:
        """Update register button enabled state based on overall form validity."""
        is_valid = self._is_form_valid()
        new_state = tk.NORMAL if is_valid else tk.DISABLED
        # Ensure button exists before configuring
        if hasattr(self, 'register_button') and self.register_button and self.register_button.winfo_exists():
            if self.register_button.cget('state') != new_state:
                self.register_button.config(state=new_state)
    
    def _handle_register(self) -> None:
        """Handle register button click."""
        if not self._is_form_valid():
            messagebox.showwarning("Invalid Input", "Please correct the errors before submitting.")
            return

        self.register_button.config(state=tk.DISABLED, text="REGISTER")
        self.error_label.pack_forget()

        username = self.username_input.get_value()
        email = self.email_input.get_value()
        password = self.password_input.get_value()
        
        if not self.auth_service:
            messagebox.showerror("Error", "Authentication service not available.")
            if hasattr(self, 'register_button') and self.register_button:
                self.register_button.config(state=tk.NORMAL)
            return

        try:
            user = self.auth_service.register(username, email, password)
            if user:
                messagebox.showinfo("Success", "Registration successful! Please log in.")
                if self.app:
                    self.app.show_page('login')
            else:
                # This case might not happen if register throws exceptions on failure
                self._show_error("Registration failed. Please try again.")
                if hasattr(self, 'register_button') and self.register_button:
                    self.register_button.config(state=tk.NORMAL)
        except ValueError as e: # Catch specific exceptions from service
            self._show_error(str(e))
            if hasattr(self, 'register_button') and self.register_button:
                self.register_button.config(state=tk.NORMAL)
        except Exception as e:
            self._show_error(f"An unexpected error occurred: {str(e)}")
            if hasattr(self, 'register_button') and self.register_button:
                self.register_button.config(state=tk.NORMAL)

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        self.error_label.config(text=message, font=FONTS["caption"], fg=PALETTE["danger"]) # Use theme
        self.error_label.pack(fill=tk.X, pady=(5, 0), before=self.register_button.master)

    def _navigate_to_login(self, event=None) -> None:
        """Navigate back to the login page."""
        if self.app and hasattr(self.app, 'show_page'):
            self.app.show_page('login')
        else:
            print("Error: App instance not found or doesn't have show_page method.")

    def reset_state(self) -> None:
        """Reset the page to its initial state when shown."""
        # Clear error message
        if hasattr(self, 'error_label'):
            self.error_label.config(text='')
            self.error_label.pack_forget()
            
        # Reset button text and state
        if hasattr(self, 'register_button') and self.register_button:
            self.register_button.config(state=tk.DISABLED, text="REGISTER")
            # Re-check validity
            self._update_button_state()

    # Removed: init, render, state management methods
    # ... existing code ... 