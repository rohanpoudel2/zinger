import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from sqlalchemy import text
from datetime import datetime

def fix_datetime_fields():
    """Fix datetime fields in the database to ensure they are properly formatted."""
    print("Fixing datetime fields in the database...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a session
    with db_manager.get_session() as session:
        try:
            # 1. Update last_updated field in buses table
            session.execute(text("""
                UPDATE buses 
                SET last_updated = CURRENT_TIMESTAMP
                WHERE last_updated IS NULL OR typeof(last_updated) != 'text'
            """))
            
            # 2. Update departure field in buses table
            session.execute(text("""
                UPDATE buses 
                SET departure = NULL
                WHERE departure IS NOT NULL AND typeof(departure) != 'text'
            """))
            
            # 3. Update booking_time field in bookings table
            session.execute(text("""
                UPDATE bookings 
                SET booking_time = CURRENT_TIMESTAMP
                WHERE booking_time IS NULL OR typeof(booking_time) != 'text'
            """))
            
            # 4. Update last_updated field in routes table
            session.execute(text("""
                UPDATE routes 
                SET last_updated = CURRENT_TIMESTAMP
                WHERE last_updated IS NULL OR typeof(last_updated) != 'text'
            """))
            
            # 5. Update created_at field in users table
            session.execute(text("""
                UPDATE users 
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL OR typeof(created_at) != 'text'
            """))
            
            # Commit the changes
            session.commit()
            print("Successfully fixed datetime fields in the database.")
            
        except Exception as e:
            session.rollback()
            print(f"Error fixing datetime fields: {e}")
            raise e

if __name__ == "__main__":
    fix_datetime_fields() 