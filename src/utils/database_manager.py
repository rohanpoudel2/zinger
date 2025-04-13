from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from utils.base import Base
from exceptions import DatabaseError
from contextlib import contextmanager
from typing import Generator
from rich.console import Console
import os

console = Console()

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL', 'sqlite:///bus_system.db')
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def initialize_database(self) -> None:
        """Initialize the database by creating tables if they don't exist."""
        try:
            # Create tables without dropping existing ones
            Base.metadata.create_all(self.engine)
            console.print("[green]Database initialized successfully.[/green]")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with proper error handling."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Unexpected error during database operation: {str(e)}")
        finally:
            session.close()

    def close(self) -> None:
        """Close database connections."""
        try:
            self.engine.dispose()
        except Exception as e:
            raise DatabaseError(f"Failed to close database connections: {str(e)}")

# Configure SQLite for better concurrency
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close() 