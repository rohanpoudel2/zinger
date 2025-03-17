import sys
import os
from datetime import datetime
import requests

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from repositories.bus_repository import BusRepository
from models.database_models import BusModel
from sqlalchemy import text

def fetch_vehicle_positions():
    """Fetch real-time vehicle positions from CTTransit API."""
    url = "https://cttprdtmgtfs.ctttrpcloud.com/TMGTFSRealTimeWebService/Vehicle/VehiclePositions.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching vehicle positions: {str(e)}")
        return None

def get_route_info(session, route_id):
    """Get route information from the routes table."""
    if not route_id:
        return None
        
    result = session.execute(
        text("SELECT route_short_name, route_long_name FROM routes WHERE route_id = :route_id"),
        {"route_id": route_id}
    ).fetchone()
    
    if result:
        return {
            "short_name": result[0] or "",
            "long_name": result[1] or ""
        }
    return None

def populate_buses():
    """Populate the database with real CTTransit bus data."""
    print("Populating database with real CTTransit bus data...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Fetch real-time vehicle positions
    vehicle_data = fetch_vehicle_positions()
    if not vehicle_data or 'entity' not in vehicle_data:
        print("No vehicle data available. Aborting.")
        return
    
    # Create a session
    with db_manager.get_session() as session:
        # Initialize bus repository
        bus_repository = BusRepository(session)
        
        # Get all route IDs from the database for comparison
        available_routes = session.execute(
            text("SELECT route_id FROM routes")
        ).fetchall()
        available_route_ids = {r[0] for r in available_routes}
        print(f"\nAvailable route IDs in database: {available_route_ids}\n")
        
        buses_created = 0
        for entity in vehicle_data['entity']:
            if 'vehicle' not in entity or entity.get('isDeleted', False):
                continue
                
            vehicle = entity['vehicle']
            vehicle_id = vehicle.get('vehicle', {}).get('label', '')
            if not vehicle_id:
                continue
                
            # Extract vehicle information
            position = vehicle.get('position', {})
            trip = vehicle.get('trip', {})
            route_id = trip.get('route_id', '')
            print(f"Bus {vehicle_id} has route_id: {route_id}")
            
            # Get route information
            route_info = get_route_info(session, route_id)
            route_name = f"{route_info['short_name']} - {route_info['long_name']}" if route_info else "Unknown Route"
            
            # Create or update bus
            try:
                bus = bus_repository.get(vehicle_id)
                if not bus:
                    bus = BusModel(
                        bus_number=vehicle_id,
                        route=route_name,
                        route_id=route_id,
                        trip_id=trip.get('trip_id', ''),
                        latitude=position.get('latitude', 0.0),
                        longitude=position.get('longitude', 0.0),
                        speed=position.get('speed', 0.0),
                        bearing=position.get('bearing', 0.0),
                        is_active=True,
                        capacity=50,  # Default capacity
                        current_location='En Route',
                        route_type='local',
                        agency_id='CTTRANSIT',
                        last_updated=datetime.fromtimestamp(vehicle.get('timestamp', 0)),
                        next_stop=vehicle.get('stop_id', '')
                    )
                    bus_repository.add(bus)
                    buses_created += 1
                    print(f"Added bus: {vehicle_id} - {route_name}")
                else:
                    # Update existing bus
                    bus.route = route_name
                    bus.route_id = route_id
                    bus.trip_id = trip.get('trip_id', '')
                    bus.latitude = position.get('latitude', 0.0)
                    bus.longitude = position.get('longitude', 0.0)
                    bus.speed = position.get('speed', 0.0)
                    bus.bearing = position.get('bearing', 0.0)
                    bus.last_updated = datetime.fromtimestamp(vehicle.get('timestamp', 0))
                    bus.next_stop = vehicle.get('stop_id', '')
                    print(f"Updated bus: {vehicle_id} - {route_name}")
                    
            except Exception as e:
                print(f"Error processing bus {vehicle_id}: {str(e)}")
        
        print(f"Successfully added {buses_created} buses to the database.")

if __name__ == "__main__":
    populate_buses()