import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from repositories.bus_repository import BusRepository
from models.database_models import BusModel

def populate_buses():
    """Populate the database with sample bus data."""
    print("Populating database with sample bus data...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create a session
    with db_manager.get_session() as session:
        # Initialize bus repository
        bus_repository = BusRepository(session)
        
        # Sample bus routes
        routes = [
            {
                "route": "Downtown Shuttle",
                "stops": ["Union Station", "Green", "Yale", "Church & Chapel"],
                "type": "shuttle",
                "fare": 1.75
            },
            {
                "route": "Yale Shuttle",
                "stops": ["Yale Station", "Science Hill", "Medical Center", "Central Campus"],
                "type": "shuttle",
                "fare": 0.0  # Free for Yale affiliates
            },
            {
                "route": "Whitney Avenue",
                "stops": ["Downtown", "East Rock", "Hamden", "Cheshire"],
                "type": "local",
                "fare": 2.00
            },
            {
                "route": "Dixwell Avenue",
                "stops": ["Union Station", "Dixwell", "Hamden Plaza", "Southern CT State"],
                "type": "local",
                "fare": 2.00
            }
        ]
        
        # Current time for departures
        current_time = datetime.now()
        
        # Create buses for each route
        buses_created = 0
        for route in routes:
            num_buses = 3  # Create multiple buses per route
            for i in range(num_buses):
                bus_number = f"NH{route['route'][:3]}{i+1}"
                
                # Check if bus already exists
                existing_bus = bus_repository.get(bus_number)
                if existing_bus:
                    print(f"Bus '{bus_number}' already exists. Skipping.")
                    continue
                
                # Create departure time (15 min intervals)
                departure_time = current_time + timedelta(minutes=15 * i)
                
                # Create bus
                bus = BusModel(
                    bus_number=bus_number,
                    route=route['route'],
                    departure=departure_time,
                    fare=route['fare'],
                    is_active=True,
                    capacity=30,
                    current_location=route['stops'][i % len(route['stops'])],
                    route_type=route['type'],
                    agency_id="CTTRANSIT",
                    last_updated=datetime.now()
                )
                
                # Add bus to database
                try:
                    bus_repository.add(bus)
                    buses_created += 1
                    print(f"Added bus: {bus_number} - {route['route']}")
                except Exception as e:
                    print(f"Error adding bus {bus_number}: {str(e)}")
        
        print(f"Successfully added {buses_created} buses to the database.")

if __name__ == "__main__":
    populate_buses() 