import sys
import os
import requests
import zipfile
import io
import csv
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from sqlalchemy import text
from models.database_models import RouteType

def download_and_extract_gtfs():
    """Download and extract the GTFS data from CTTransit."""
    print("Downloading GTFS data...")
    url = "https://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip"
    response = requests.get(url)
    response.raise_for_status()
    
    # Extract the routes.txt file from the zip
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open('routes.txt') as f:
            return [row for row in csv.DictReader(io.TextIOWrapper(f))]

def add_routes_table():
    """Create routes table and populate it with GTFS data."""
    print("Creating routes table and updating bus relationships...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a session
    with db_manager.get_session() as session:
        try:
            # Create routes table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS routes (
                    route_id VARCHAR(50) PRIMARY KEY,
                    agency_id VARCHAR(50) NOT NULL,
                    route_short_name VARCHAR(50),
                    route_long_name VARCHAR(255),
                    route_desc VARCHAR(255),
                    route_type INTEGER,
                    route_url VARCHAR(255),
                    route_color VARCHAR(6),
                    route_text_color VARCHAR(6),
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Download and process GTFS data
            routes_data = download_and_extract_gtfs()
            
            # Insert routes data
            for route in routes_data:
                session.execute(
                    text("""
                        INSERT OR REPLACE INTO routes (
                            route_id, agency_id, route_short_name, route_long_name,
                            route_desc, route_type, route_url, route_color, route_text_color
                        ) VALUES (:route_id, :agency_id, :route_short_name, :route_long_name,
                                :route_desc, :route_type, :route_url, :route_color, :route_text_color)
                    """),
                    {
                        'route_id': route.get('route_id', ''),
                        'agency_id': route.get('agency_id', 'CTTRANSIT'),
                        'route_short_name': route.get('route_short_name', ''),
                        'route_long_name': route.get('route_long_name', ''),
                        'route_desc': route.get('route_desc', ''),
                        'route_type': int(route.get('route_type', 3)),  # Default to BUS
                        'route_url': route.get('route_url', ''),
                        'route_color': route.get('route_color', ''),
                        'route_text_color': route.get('route_text_color', '')
                    }
                )
            
            print("Successfully created and populated routes table.")
            
        except Exception as e:
            print(f"Error creating routes table: {str(e)}")
            session.rollback()
            raise

if __name__ == "__main__":
    add_routes_table() 