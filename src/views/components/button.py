import tkinter as tk
from typing import Dict, Any, Callable, Optional
from views.components.base_component import Component

class Button(Component):
    """
    A reusable button component with styling options.
    
    Props:
        text: Button text
        command: Function to call when clicked
        color: Text color
        bg_color: Background color
        width: Button width
        height: Button height
        font: Button font
        disabled: Whether the button is disabled
    """
    
    def init(self) -> None:
        """Initialize button state."""
        self.button = None
        
    def render(self) -> None:
        """Render the button."""
        text = self.props.get('text', 'Button')
        command = self.props.get('command')
        color = self.props.get('color', 'black')
        bg_color = self.props.get('bg_color', '#eeeeee')
        width = self.props.get('width', 15)
        height = self.props.get('height', 1)
        font = self.props.get('font', ('Arial', 10))
        disabled = self.props.get('disabled', False)
        
        self.button = tk.Button(
            self,
            text=text,
            command=command,
            fg=color,
            bg=bg_color,
            width=width,
            height=height,
            font=font,
            state='disabled' if disabled else 'normal'
        )
        self.button.pack(fill=tk.X, padx=5, pady=5)
    
    def set_text(self, text: str) -> None:
        """Update the button text."""
        if self.button:
            self.button.config(text=text)
    
    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the button."""
        if self.button:
            self.button.config(state='disabled' if disabled else 'normal')
    
    def set_color(self, color: str) -> None:
        """Update the button text color."""
        if self.button:
            self.button.config(fg=color)
    
    def set_bg_color(self, color: str) -> None:
        """Update the button background color."""
        if self.button:
            self.button.config(bg=color) 