from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from models.database_models import Base
from exceptions import DatabaseError
from contextlib import contextmanager
from typing import Generator
from rich.console import Console
import os

console = Console()

class DatabaseManager:
    def __init__(self, db_path: str = "bus_booking.db"):
        try:
            # Ensure the database directory exists
            db_dir = os.path.dirname(os.path.abspath(db_path))
            os.makedirs(db_dir, exist_ok=True)
            
            # Create engine with proper configuration
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Configure session maker
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            self.initialize_database()
            
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with proper error handling."""
        session = self.SessionLocal()
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

    def initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        try:
            # Create tables without dropping existing ones
            Base.metadata.create_all(self.engine)
            console.print("[green]Database connection established.[/green]")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create database tables: {str(e)}")

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