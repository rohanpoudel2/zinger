from sqlalchemy import create_engine, text
from utils.base import Base
from models.database_models import UserModel, BusModel, RouteModel, BookingModel
import os
from rich.console import Console

console = Console()

def reset_database():
    """Reset the database by dropping all tables and recreating them."""
    try:
        # Get the database URL from environment or use default
        database_url = os.getenv('DATABASE_URL', 'sqlite:///bus_system.db')
        
        # Create engine
        engine = create_engine(database_url)
        
        # Drop all existing tables
        Base.metadata.drop_all(engine)
        console.print("[green]Dropped all existing tables[/green]")
        
        # Create all tables with the latest schema
        Base.metadata.create_all(engine)
        console.print("[green]Created all tables with the latest schema[/green]")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        console.print(f"[blue]Created tables: {', '.join(tables)}[/blue]")
        
        console.print("[green]Database reset completed successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Database reset failed: {e}[/red]")
        raise

if __name__ == "__main__":
    from sqlalchemy import inspect
    reset_database() 