# src/views/config/theme.py

import sys
import tkinter as tk

# --- Material Design Palette (example: Blue Grey) ---
PALETTE = {
    "primary": "#607d8b",       # Blue Grey 500
    "primary_dark": "#455a64",  # Blue Grey 700
    "primary_light": "#cfd8dc", # Blue Grey 100
    "accent": "#ff5722",        # Deep Orange A200
    "secondary": "#eceff1",    # Blue Grey 50 (Background)
    "card_bg": "#ffffff",       # White (Card Background)
    "danger": "#f44336",        # Red 500
    "text_primary": "#212121",  # Grey 900 (Primary Text)
    "text_secondary": "#757575",# Grey 600 (Secondary Text)
    "text_light": "#ffffff",     # White (Text on dark)
    "text_primary_on_primary": "#ffffff", # Text on primary color
    "text_accent": "#ffffff",    # Text on accent color
    "divider": "#bdbdbd",       # Grey 400 (Dividers/Borders)
    "placeholder": "#bdbdbd",   # Grey 400 (Placeholder)
    "border": "#bdbdbd",         # Grey 400 (Input Borders)
    "navbar_bg": "#546e7a"       # Blue Grey 600 (Navbar)
}

# --- Material Design Fonts (Roboto fallback) ---
# Note: Ensure Roboto is installed on the system for best results

def get_font(name, weight="normal", size_adjust=0):
    base_size = 14 # Base font size for Material
    family = "Roboto" # Preferred Material font
    temp_root = None # Initialize temporary root variable
    try:
        # Check if Roboto exists: Create a temporary, hidden root for the check
        temp_root = tk.Tk()
        temp_root.withdraw() # Hide the temporary window
        tk.Label(temp_root, font=(family, base_size)) # Create label as child of temp root
        # If the above line doesn't raise TclError, Roboto likely exists
    except tk.TclError:
        # Fallback font based on OS
        if sys.platform == "darwin":
            family = "SF Pro Text" # macOS default
            base_size = 14
        elif sys.platform == "win32":
            family = "Segoe UI"
            base_size = 11
        else:
            family = "DejaVu Sans" # Common Linux fallback
            base_size = 11
            
    finally:
        # Ensure the temporary root is destroyed if it was created
        if temp_root:
            temp_root.destroy()
            
    actual_size = base_size + size_adjust
    
    if weight == "bold":
        return (family, actual_size, "bold")
    elif weight == "medium": # Tkinter doesn't always support medium
        # Try bold as fallback if medium isn't distinct
        return (family, actual_size, "bold") 
    else:
        return (family, actual_size)

FONTS = {
    "body": get_font("body"),                       # Regular body text
    "body_bold": get_font("body", weight="bold"),
    "button": get_font("button", weight="medium"),   # Medium weight for buttons
    "caption": get_font("caption", size_adjust=-2),    # Smaller text
    "h1": get_font("h1", weight="light", size_adjust=10), # Large headings (Tk might not have light)
    "h2": get_font("h2", weight="normal", size_adjust=6),
    "h3": get_font("h3", weight="medium", size_adjust=4),
    "label": get_font("label", weight="medium"),      # Input labels
    "input": get_font("input")                       # Input text
} 