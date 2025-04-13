import tkinter as tk
from typing import Dict, Any, Callable, Optional, List, TypeVar
import uuid

# Import theme for default styling
from views.config.theme import PALETTE, FONTS 

T = TypeVar('T')

class Component(tk.Frame):
    """
    Simplified base class for Tkinter UI elements.
    Provides basic props handling and a standard structure.
    """
    
    def __init__(
        self, 
        parent: Optional[tk.Widget], 
        props: Dict[str, Any] = None,
        **kwargs
    ):
        """
        Initialize a new component.
        
        Args:
            parent: The parent Tkinter widget.
            props: Component properties (passed during initialization).
            **kwargs: Additional keyword arguments for the tk.Frame.
        """
        # Ensure Frame has a default background consistent with the theme
        # Components can override this via props or direct config if needed
        if 'bg' not in kwargs:
            kwargs['bg'] = PALETTE["card_bg"] # Default to card background (white)
        
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.props = props or {}
        self._children: List[tk.Widget] = [] # Store generic child widgets
        
        # Call subclass method to create widgets
        self._create_widgets()

    def _create_widgets(self) -> None:
        """
        Placeholder method for creating widgets within the component.
        Subclasses should override this method to build their UI.
        """
        pass

    def add_child(self, child: tk.Widget) -> None:
        """
        Keep track of manually created child widgets if needed.
        Note: Standard Tkinter parenting already handles hierarchy.
        This is mostly for potential custom management if required.
        """
        self._children.append(child)

    # Removed: init, component_did_mount, component_will_unmount,
    # should_component_update, mount, unmount, set_state, get_state,
    # on, emit, render (replaced by _create_widgets)
    # Removed the custom destroy override for now, relying on Tkinter's default.
    # If specific cleanup (like cancelling 'after' jobs) is needed, 
    # it should be handled in the specific component needing it using
    # bind('<Destroy>', ...) or a specific cleanup method.

# Example usage (conceptual - specific components will be refactored next)
# class MyWidget(Component):
#     def _create_widgets(self):
#         self.label = tk.Label(self, text="Hello")
#         self.label.pack()
#         self.button = tk.Button(self, text="Click Me")
#         self.button.pack()
#         self.add_child(self.label) # Optional tracking
#         self.add_child(self.button) # Optional tracking 