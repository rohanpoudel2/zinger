from sqlalchemy.ext.declarative import declarative_base
import os
import signal
import sys
from utils.logger import get_access_logger

Base = declarative_base()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_interrupt_handler(console=None):
    """Set up a handler for interrupt signals."""
    def handle_interrupt(signum, frame):
        """Handle interrupt signal (Ctrl+C)."""
        clear_screen()
        if console:
            console.print("\n[yellow]Shutting down...[/yellow]")
        get_access_logger().info("Application shutdown by interrupt signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_interrupt) 