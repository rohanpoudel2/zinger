from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from typing import List, Tuple, Optional, Any, Callable
from datetime import datetime

console = Console()

class UIHelper:
    @staticmethod
    def display_header(title: str, user_info: Optional[str] = None, location_info: Optional[str] = None) -> None:
        """Display a consistent header panel."""
        header_text = f"[blue]{title}[/blue]"
        
        if user_info:
            header_text += f" - {user_info}"
            
        if location_info:
            header_text += f" - Location: [yellow]{location_info}[/yellow]"
            
        console.print(Panel(header_text))
    
    @staticmethod
    def display_menu_options(options: List[Tuple[str, str, str]]) -> None:
        """
        Display menu options in a consistent format.
        
        Args:
            options: List of tuples (option_number, option_text, color)
        """
        for opt_num, opt_text, color in options:
            console.print(f"{opt_num}. [{color}]{opt_text}[/{color}]")
    
    @staticmethod
    def get_user_choice(max_choice: int) -> str:
        """Get user input for menu choice."""
        return Prompt.ask(f"\nEnter your choice (1-{max_choice}): ")
    
    @staticmethod
    def display_error(message: str) -> None:
        """Display an error message."""
        console.print(f"\n[red]Error:[/red] {message}")
    
    @staticmethod
    def display_success(message: str) -> None:
        """Display a success message."""
        console.print(f"\n[green]{message}[/green]")
    
    @staticmethod
    def display_warning(message: str) -> None:
        """Display a warning message."""
        console.print(f"\n[yellow]{message}[/yellow]")
    
    @staticmethod
    def display_info(message: str) -> None:
        """Display an info message."""
        console.print(f"\n[cyan]{message}[/cyan]")
    
    @staticmethod
    def create_table(title: str, columns: List[str], rows: List[List[Any]]) -> Table:
        """Create a rich table with the given data."""
        table = Table(title=title, box=box.ROUNDED)
        
        for col in columns:
            table.add_column(col)
            
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
            
        return table
    
    @staticmethod
    def pause() -> None:
        """Pause execution until user presses Enter."""
        Prompt.ask("\nPress Enter to continue", default="")
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format a datetime object for display."""
        if not dt:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M") 