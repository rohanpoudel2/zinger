import tkinter as tk
from tkinter import ttk # Optional: For themed widgets
from typing import Dict, Any, Callable, Optional

# Import the palette definition
from views.config.theme import PALETTE, FONTS

class Input(tk.Frame): # Inherit directly from tk.Frame
    """
    A reusable Tkinter input component with validation and placeholder.
    Uses standard Tkinter patterns instead of a custom component base.
    """
    
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        """
        Initialize the Input component.
        
        Args:
            parent: The parent Tkinter widget.
            props: Dictionary of properties:
                - label (str): Input label text.
                - placeholder (str): Placeholder text.
                - default_value (str): Default input value.
                - type (str): Input type ('text', 'password', 'number').
                - validate (Callable[[str], bool]): Validation function.
                - on_change (Callable[[str], None]): Function to call when value changes.
                - required (bool): Whether input is required.
                - error_message (str): Error message for validation failures.
                - width (int): Input width.
            **kwargs: Additional keyword arguments for the tk.Frame.
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.props = props or {}
        self._is_valid = True
        self._error_message = None
        self._placeholder_active = False
        self._on_change_cb_prop = self.props.get('on_change')
        self._validate_cb = self.props.get('validate')

        self.entry_var = tk.StringVar()
        # Ensure the frame itself has a background color if needed (e.g., card_bg)
        # If it should blend with parent, ensure parent sets BG.
        # Let's assume it should be white like the card background for now.
        self.config(bg=PALETTE["card_bg"])
        self._widget_initialized = False
        self._create_widgets() # Creates widgets, assigns to self
        self._configure_styles() # Styles widgets AND lays them out using grid
        self._setup_bindings_and_trace() # Binds events
        
        # Set initial value and state *after* widgets exist
        # but *before* enabling the parent callback
        initial_value = self.props.get('default_value', '')
        self._on_change_cb = None # Disable callback temporarily
        self.entry_var.set(initial_value)
        self._on_change_cb = self._on_change_cb_prop # Restore callback
        
        # Handle initial placeholder and validation state
        self._handle_placeholder()
        self._validate_and_update() # Validate initial value 

        # Mark as initialized *after* all internal widgets are created and styled
        self._widget_initialized = True 

    def _configure_styles(self):
        """Configure styles AND LAYOUT for the input field."""
        # Configure the main frame
        self.config(bd=0, relief=tk.FLAT, bg=PALETTE["card_bg"])
        self.columnconfigure(0, weight=1)

        # Create and Grid the underline frame (moved creation here for clarity)
        self.underline = tk.Frame(self, height=1, bg=PALETTE["divider"])
        # Calculate grid rows
        label_row = 0
        entry_row = 1 if self.label_widget else 0
        underline_row = entry_row + 1
        error_row = underline_row + 1
        
        # Grid all elements
        if self.label_widget:
            self.label_widget.grid(row=label_row, column=0, sticky='ew', padx=0, pady=0)
        self.entry_widget.grid(row=entry_row, column=0, sticky='ew', padx=0, pady=(0, 0))
        self.underline.grid(row=underline_row, column=0, sticky='ew', padx=0, pady=0)
        self.error_label.grid(row=error_row, column=0, sticky='ew', padx=0, pady=(1,0))
        self.error_label.grid_remove() # Hide error initially

        # Configure focus highlight for the underline
        self.entry_widget.bind("<FocusIn>", self._on_focus_in_underline)
        self.entry_widget.bind("<FocusOut>", self._on_focus_out_underline)

    def _on_focus_in_underline(self, event=None):
        self.underline.config(bg=PALETTE["primary"], height=2)
    
    def _on_focus_out_underline(self, event=None):
        self.underline.config(bg=PALETTE["divider"], height=1)

    def _create_widgets(self) -> None:
        """Instantiate the child widgets for the Input component (NO LAYOUT)."""
        # --- Label (Optional) ---
        label_text = self.props.get('label')
        if label_text:
            self.label_widget = tk.Label(self, text=label_text, anchor='w', 
                                       bg=PALETTE["card_bg"], fg=PALETTE["text_secondary"], # Secondary color for label
                                       font=FONTS["caption"]) # Smaller caption font for label
        else:
            self.label_widget = None

        # --- Entry Widget ---
        input_type = self.props.get('type', 'text')
        show_char = '*' if input_type == 'password' else ''
        width = self.props.get('width', 30)
        
        # Consider using ttk.Entry for better styling if ttk is imported
        self.entry_widget = tk.Entry(
            self,
            textvariable=self.entry_var,
            width=width,
            show=show_char,
            font=FONTS["input"], # Set entry font
            bg=PALETTE["card_bg"], # Set background to white (like card)
            bd=0, 
            highlightthickness=0, 
            fg=PALETTE["text_primary"], 
            disabledbackground=PALETTE["secondary"], 
            disabledforeground=PALETTE["text_secondary"], 
            insertbackground=PALETTE["text_primary"], 
            selectbackground=PALETTE["primary_light"], # Lighter selection
            selectforeground=PALETTE["text_primary"]
        )

        # --- Error Label ---
        self.error_label = tk.Label(self, text='', fg=PALETTE["danger"], anchor='w',
                                  bg=PALETTE["card_bg"], 
                                  font=FONTS["caption"]) # Caption font for error

    def _setup_bindings_and_trace(self) -> None:
        """Setup event bindings and variable tracing."""
        # Trace variable changes
        self.entry_var.trace_add('write', self._on_var_change)
        
        # Handle placeholder logic on focus changes
        self.entry_widget.bind('<FocusIn>', self._on_focus_in)
        self.entry_widget.bind('<FocusOut>', self._on_focus_out)

    def _on_var_change(self, *args) -> None:
        """Callback when the entry_var changes."""
        # If placeholder is active, ignore the programmatic change inserting it
        if self._placeholder_active and self.entry_var.get() == self.props.get('placeholder', ''):
           # This check might be needed if set_value could trigger this trace unwantedly
           # during placeholder management. Usually, direct var.set bypasses placeholder state.
           pass 
        else: 
            self._placeholder_active = False # Any user input deactivates placeholder
            self._validate_and_update()
            # If input becomes valid while typing, hide any existing error
            if self._is_valid:
                self.error_label.grid_remove()
            # Trigger parent callback if it exists
            if self._on_change_cb:
                self._on_change_cb(self.entry_var.get()) # Pass current value

    def _validate_and_update(self) -> None:
        """Validate the current value and update the UI state (text only)."""
        # Skip validation if the widget hasn't been fully drawn/initialized yet
        if not self.winfo_exists() or not getattr(self, '_widget_initialized', False):
            return
        
        current_value = self.entry_var.get()
        is_currently_valid = True
        error_msg = None

        # Perform validation
        if self._validate_cb:
            try:
                is_currently_valid = self._validate_cb(current_value)
                if not is_currently_valid:
                    error_msg = self.props.get('error_message', 'Invalid input')
            except Exception as e:
                is_currently_valid = False
                error_msg = str(e)
        elif self.props.get('required', False) and not current_value:
            is_currently_valid = False
            error_msg = 'This field is required'

        # Update internal state
        self._is_valid = is_currently_valid
        self._error_message = error_msg

        # Update UI (Error Label Text Only)
        self.error_label.config(text=self._error_message or '')
        # Visibility is handled by event handlers
        # if error_msg:
        #     # self.error_label.config(text=error_msg)
        #     # self.error_label.grid() # Defer showing
        # else:
        #     self.error_label.grid_remove()

    def _handle_placeholder(self) -> None:
        """Manage the placeholder text visibility and color."""
        placeholder = self.props.get('placeholder')
        if not placeholder:
            return

        current_value = self.entry_var.get()
        is_focused = self.focus_get() == self.entry_widget

        if not current_value and not is_focused:
            # Show placeholder
            self._placeholder_active = True
            self.entry_var.set(placeholder)
            self.entry_widget.config(fg=PALETTE["placeholder"])
        elif self._placeholder_active and (current_value != placeholder or is_focused):
           # Hide placeholder (if it was active)
           # This case handles focus-in or if value was changed programmatically
            self._placeholder_active = False
            if current_value == placeholder: # Clear placeholder text only if it's still there
                 self.entry_var.set('')
            self.entry_widget.config(fg=PALETTE["text_primary"])
        elif not self._placeholder_active and current_value:
             # Ensure text color is normal if placeholder wasn't active but there's text
             self.entry_widget.config(fg=PALETTE["text_primary"])

    def _on_focus_in(self, event=None) -> None:
        """Handle FocusIn event for placeholder and underline."""
        self._on_focus_in_underline()
        self._handle_placeholder() # Check placeholder state

    def _on_focus_out(self, event=None) -> None:
        """Handle FocusOut event for placeholder, underline, and validation visibility."""
        self._on_focus_out_underline()
        self._handle_placeholder() # Check placeholder state
        self._show_error_if_invalid() # Show error only if needed

    def _show_error_if_invalid(self):
        """Show error label only if the field is invalid."""
        self._validate_and_update() # Ensure validation state is current
        if not self._is_valid:
            self.error_label.grid() # Show error label
        else:
            self.error_label.grid_remove()

    # --- Public Methods ---
    def get_value(self) -> str:
        """Get the current valid input value (excluding placeholder)."""
        if self._placeholder_active:
            return ""
        return self.entry_var.get()
    
    def set_value(self, value: str) -> None:
        """Set the input value programmatically."""
        self._placeholder_active = False # Setting value clears placeholder state
        self.entry_var.set(value)
        self._handle_placeholder() # Ensure placeholder state is correct after setting
        self._validate_and_update() # Validate the new value
    
    def is_valid(self) -> bool:
        """Check if the current input value is valid."""
        return self._is_valid
    
    def get_error(self) -> Optional[str]:
        """Get the current validation error message."""
        return self._error_message
    
    def clear(self) -> None:
        """Clear the input value and show placeholder if applicable."""
        self.set_value('') # Use set_value to handle placeholder and validation

    # Removed: component_will_unmount, destroy (rely on default Tkinter handling for this simple widget) 