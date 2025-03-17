import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from sqlalchemy import text

def update_bus_constraints():
    """Update bus table constraints to make departure and fare nullable."""
    print("Updating bus table constraints...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a session
    with db_manager.get_session() as session:
        try:
            # SQLite doesn't support ALTER COLUMN, so we need to:
            # 1. Create a new table with the updated schema
            # 2. Copy the data
            # 3. Drop the old table
            # 4. Rename the new table
            
            # Create new table with updated schema
            session.execute(text("""
                CREATE TABLE buses_new (
                    bus_number VARCHAR(50) PRIMARY KEY,
                    route VARCHAR(100) NOT NULL,
                    route_id VARCHAR(50),
                    departure DATETIME,
                    fare FLOAT,
                    is_active BOOLEAN DEFAULT 1,
                    capacity INTEGER DEFAULT 30,
                    current_location VARCHAR(100),
                    route_type VARCHAR(50),
                    agency_id VARCHAR(50) DEFAULT 'CTTRANSIT',
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    latitude FLOAT,
                    longitude FLOAT,
                    speed FLOAT,
                    bearing FLOAT,
                    trip_id VARCHAR(50),
                    next_stop VARCHAR(100)
                )
            """))
            
            # Copy data from old table
            session.execute(text("""
                INSERT INTO buses_new 
                SELECT * FROM buses
            """))
            
            # Drop old table
            session.execute(text("DROP TABLE buses"))
            
            # Rename new table
            session.execute(text("ALTER TABLE buses_new RENAME TO buses"))
            
            # Recreate index on route_id
            session.execute(text("CREATE INDEX ix_buses_route_id ON buses (route_id)"))
            
            print("Successfully updated bus table constraints.")
            
        except Exception as e:
            print(f"Error updating bus table constraints: {str(e)}")
            session.rollback()
            raise

if __name__ == "__main__":
    update_bus_constraints() 