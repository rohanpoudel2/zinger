import tkinter as tk
from typing import Dict, Any, List, Optional
from views.components.base_component import Component
from views.config.theme import PALETTE, FONTS # Import theme

class Card(Component):
    """
    A card component with a title and content area.
    
    Props:
        title: Card title
        padding: Padding inside the card
        background: Background color (defaults to theme card_bg)
        border_color: Border color (defaults to theme divider)
        border_width: Border width (defaults to 1)
        # elevation: Shadow elevation (deprecated, using flat style)
        width: Card width
        height: Card height
    """
    
    def __init__(self, parent: tk.Widget, props: Dict[str, Any] = None, **kwargs):
        """Initialize and configure the Card Frame."""
        # Get props with theme defaults
        props = props or {}
        title = props.get('title', '')
        padding = props.get('padding', 16) # Material standard padding
        background = props.get('background', PALETTE["card_bg"])
        border_color = props.get('border_color', PALETTE["divider"]) # Use divider color for border
        border_width = props.get('border_width', 1) # Subtle border
        width = props.get('width')
        height = props.get('height')
        
        # Update kwargs for the super().__init__ call
        kwargs['bg'] = background
        kwargs['bd'] = border_width
        kwargs['relief'] = tk.FLAT
        kwargs['highlightthickness'] = border_width
        kwargs['highlightbackground'] = border_color if border_width > 0 else background
        if width:
            kwargs['width'] = width
        if height:
            kwargs['height'] = height
            
        # Call BaseComponent.__init__ (which calls tk.Frame.__init__)
        super().__init__(parent, props=props, **kwargs)
        
        # Configure padding AFTER init (pack/grid affects internal padding differently)
        # Use internal Frames for content padding instead of configuring the Card itself
        
        # Main content frame within the card for padding
        self.main_area = tk.Frame(self, bg=background, padx=padding, pady=padding)
        self.main_area.pack(fill=tk.BOTH, expand=True)
        
        # Add title if provided (within main_area)
        if title:
            title_label = tk.Label(
                self.main_area,
                text=title,
                font=FONTS["h3"], # Material title font
                fg=PALETTE["text_primary"],
                bg=background,
                anchor='w'
            )
            title_label.pack(fill=tk.X, side=tk.TOP, pady=(0, padding // 2))
            # Optional Separator:
            # separator = tk.Frame(self.main_area, height=1, bg=border_color)
            # separator.pack(fill=tk.X, side=tk.TOP, pady=(0, padding // 2))

    # Removed init() and render() - logic moved to __init__ and _create_widgets
    # Override _create_widgets if Card needs internal widgets beyond title/content frame
    # The content (children) will be packed into self.main_area by the parent component
    
    # def init(self) -> None:
    #     """Initialize card state."""
    #     pass
    
    # def render(self) -> None:
    #     """Render the card component."""
    #     ... 