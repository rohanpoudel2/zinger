import requests
from datetime import datetime, timedelta
from typing import List, Dict
from models.database_models import BusModel
from repositories.bus_repository import BusRepository
from utils.database_manager import DatabaseManager
import json
import time
import random  # For simulating coordinates

class TransitService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.base_url = "https://www.cttransit.com/api/v1"
        self.new_haven_routes = [
            "New Haven Downtown", "Union Station", "Yale Shuttle",
            "Whitney Avenue", "Dixwell Avenue", "Congress Avenue"
        ]
        
        # New Haven coordinates (center of the city)
        self.new_haven_center = (41.3083, -72.9279)

    def fetch_new_haven_buses(self) -> List[Dict]:
        """Simulate fetching real-time New Haven bus data."""
        current_time = datetime.now()
        simulated_buses = []
        
        # Simulate bus routes in New Haven
        routes = [
            {
                "route": "Downtown Shuttle",
                "stops": ["Union Station", "Green", "Yale", "Church & Chapel"],
                "type": "shuttle",
                "fare": 1.75,
                "center_lat": 41.3083,  # Downtown New Haven
                "center_lng": -72.9279,
                "radius": 0.01  # Small radius for downtown
            },
            {
                "route": "Yale Shuttle",
                "stops": ["Yale Station", "Science Hill", "Medical Center", "Central Campus"],
                "type": "shuttle",
                "fare": 0.0,  # Free for Yale affiliates
                "center_lat": 41.3163,  # Yale University
                "center_lng": -72.9223,
                "radius": 0.008
            },
            {
                "route": "Whitney Avenue",
                "stops": ["Downtown", "East Rock", "Hamden", "Cheshire"],
                "type": "local",
                "fare": 2.00,
                "center_lat": 41.3300,  # Whitney Ave
                "center_lng": -72.9150,
                "radius": 0.03  # Larger radius for longer route
            },
            {
                "route": "Dixwell Avenue",
                "stops": ["Union Station", "Dixwell", "Hamden Plaza", "Southern CT State"],
                "type": "local",
                "fare": 2.00,
                "center_lat": 41.3200,  # Dixwell Ave
                "center_lng": -72.9350,
                "radius": 0.025
            }
        ]

        # Generate simulated bus data
        for route in routes:
            num_buses = 3  # Simulate multiple buses per route
            for i in range(num_buses):
                # Generate random coordinates within the route's area
                lat_offset = (random.random() - 0.5) * 2 * route['radius']
                lng_offset = (random.random() - 0.5) * 2 * route['radius']
                
                latitude = route['center_lat'] + lat_offset
                longitude = route['center_lng'] + lng_offset
                
                departure_time = current_time + timedelta(minutes=15 * i)
                bus = {
                    "bus_number": f"NH{route['route'][:3]}{i+1}",
                    "route": route['route'],
                    "departure": departure_time,
                    "fare": route['fare'],
                    "is_active": True,
                    "current_location": route['stops'][i % len(route['stops'])],
                    "route_type": route['type'],
                    "latitude": latitude,
                    "longitude": longitude
                }
                simulated_buses.append(bus)

        return simulated_buses

    def update_bus_database(self) -> None:
        """Update the database with latest bus information."""
        buses = self.fetch_new_haven_buses()
        
        # Use a fresh session for each update
        with self.db_manager.get_session() as session:
            bus_repository = BusRepository(session)
            
            # Process each bus individually to avoid batch operations
            for bus_data in buses:
                try:
                    # Create bus model
                    bus = BusModel(
                        bus_number=bus_data['bus_number'],
                        route=bus_data['route'],
                        departure=bus_data['departure'],
                        fare=bus_data['fare'],
                        is_active=bus_data['is_active'],
                        current_location=bus_data['current_location'],
                        route_type=bus_data['route_type'],
                        latitude=bus_data['latitude'],
                        longitude=bus_data['longitude'],
                        last_updated=datetime.now()
                    )
                    
                    # Check if bus exists and update it
                    existing_bus = bus_repository.get(bus_data['bus_number'])
                    if existing_bus:
                        # Update existing bus
                        existing_bus.route = bus.route
                        existing_bus.departure = bus.departure
                        existing_bus.fare = bus.fare
                        existing_bus.is_active = bus.is_active
                        existing_bus.current_location = bus.current_location
                        existing_bus.route_type = bus.route_type
                        existing_bus.latitude = bus.latitude
                        existing_bus.longitude = bus.longitude
                        existing_bus.last_updated = bus.last_updated
                        session.commit()
                    else:
                        # Add new bus
                        session.add(bus)
                        session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"Error updating bus {bus_data['bus_number']}: {str(e)}")

    def get_route_info(self, route_name: str) -> Dict:
        """Get detailed information about a specific route."""
        # In a real implementation, this would fetch from the CT Transit API
        route_info = {
            "Downtown Shuttle": {
                "frequency": "Every 10 minutes",
                "operating_hours": "6:00 AM - 10:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Yale Shuttle": {
                "frequency": "Every 15 minutes",
                "operating_hours": "7:00 AM - 6:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Whitney Avenue": {
                "frequency": "Every 20 minutes",
                "operating_hours": "5:30 AM - 11:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            },
            "Dixwell Avenue": {
                "frequency": "Every 20 minutes",
                "operating_hours": "5:30 AM - 11:00 PM",
                "wheelchair_accessible": True,
                "bike_racks": True
            }
        }
        return route_info.get(route_name, {}) 