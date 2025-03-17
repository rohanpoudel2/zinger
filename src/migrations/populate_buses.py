import sys
import os
from datetime import datetime
import requests
import random

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_manager import DatabaseManager
from repositories.bus_repository import BusRepository
from models.database_models import BusModel, RouteModel
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

def create_route(session, route_id):
    """Create a new route in the database."""
    try:
        route = RouteModel(
            route_id=route_id,
            route_short_name=f"Route {route_id}",
            route_long_name=f"Route {route_id}",
            route_type="local"
        )
        session.add(route)
        session.commit()
        print(f"Created route: {route_id}")
        return route
    except Exception as e:
        print(f"Error creating route {route_id}: {str(e)}")
        session.rollback()
        return None

def get_route_info(session, route_id):
    """Get route information from the routes table."""
    if not route_id:
        return None
    
    try:
        route = session.query(RouteModel).filter_by(route_id=route_id).first()
        if route:
            return {
                "short_name": route.route_short_name or "",
                "long_name": route.route_long_name or ""
            }
        return None
    except Exception as e:
        print(f"Error getting route info for {route_id}: {str(e)}")
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
        
        # First, gather all unique route IDs
        route_ids = set()
        for entity in vehicle_data['entity']:
            if 'vehicle' in entity and not entity.get('isDeleted', False):
                route_id = entity['vehicle'].get('trip', {}).get('route_id', '')
                if route_id:
                    route_ids.add(route_id)
        
        # Create routes first
        print("Creating routes...")
        for route_id in route_ids:
            try:
                route = session.query(RouteModel).filter_by(route_id=route_id).first()
                if not route:
                    route = create_route(session, route_id)
            except Exception as e:
                print(f"Error checking/creating route {route_id}: {str(e)}")
                continue
        
        # Now process buses
        print("Processing buses...")
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
            
            # Get route information
            route_info = get_route_info(session, route_id)
            route_name = f"{route_info['short_name']} - {route_info['long_name']}" if route_info else "Unknown Route"
            
            # Create or update bus
            try:
                bus = bus_repository.get(vehicle_id)
                if not bus:
                    # Create new bus
                    bus = BusModel(
                        bus_number=vehicle_id,
                        route_id=route_id,
                        route=route_name,
                        latitude=position.get('latitude', 0.0),
                        longitude=position.get('longitude', 0.0),
                        speed=position.get('speed', 0.0),
                        trip_id=trip.get('trip_id', ''),
                        next_stop=None,
                        last_updated=datetime.utcnow(),
                        is_active=True,
                        current_location=None,
                        available_seats=random.randint(10, 30),
                        total_seats=30,
                        fare=1.75,
                        route_type='local',
                        distance_to_user=0.0
                    )
                    session.add(bus)
                else:
                    # Update existing bus
                    bus.route_id = route_id
                    bus.route = route_name
                    bus.latitude = position.get('latitude', 0.0)
                    bus.longitude = position.get('longitude', 0.0)
                    bus.speed = position.get('speed', 0.0)
                    bus.trip_id = trip.get('trip_id', '')
                    bus.last_updated = datetime.utcnow()
                    bus.is_active = True
                    bus.fare = 1.75
                    bus.distance_to_user = 0.0
                
                session.commit()
                print(f"Successfully processed bus {vehicle_id}")
            except Exception as e:
                print(f"Error processing bus {vehicle_id}: {str(e)}")
                session.rollback()
                continue

if __name__ == "__main__":
    populate_buses()