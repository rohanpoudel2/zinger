import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from models.database_models import BusModel, RouteModel
from repositories.bus_repository import BusRepository
from utils.database_manager import DatabaseManager
import json
import time
import os
import zipfile
import io
import random
from sqlalchemy.orm import Session
from math import radians, sin, cos, sqrt, atan2
import pickle
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TransitService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.BASE_URL = "https://cttprdtmgtfs.ctttrpcloud.com/TMGTFSRealTimeWebService"
        self.GTFS_URL = "https://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip"
        
        # API Endpoints
        self.vehicle_positions_url = f"{self.BASE_URL}/Vehicle/VehiclePositions.json"
        self.trip_updates_url = f"{self.BASE_URL}/TripUpdate/TripUpdates.json"
        self.alerts_url = f"{self.BASE_URL}/Alert/Alerts.json"
        
        # University of New Haven coordinates
        self.UNH_LOCATION = (41.2897, -72.9622)  # latitude, longitude
        
        # Cache paths
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.routes_cache_file = os.path.join(self.cache_dir, 'routes.pickle')
        
        # Initialize route cache
        self._route_cache = self._load_cache(self.routes_cache_file)
        
        # Load GTFS data if needed
        if not self._route_cache:
            self._load_gtfs_data()

    def _load_cache(self, cache_file: str) -> dict:
        """Load cached data from file."""
        if os.path.exists(cache_file):
            cache_age = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - cache_age < timedelta(days=1):  # Cache is less than 1 day old
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except Exception as e:
                    logging.error(f"Error loading cache {cache_file}: {e}")
        return {}

    def _save_cache(self, data: dict, cache_file: str) -> None:
        """Save data to cache file."""
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logging.error(f"Error saving cache {cache_file}: {e}")

    def _load_gtfs_data(self) -> None:
        """Load GTFS data and cache it locally."""
        try:
            response = requests.get(self.GTFS_URL)
            response.raise_for_status()
            
            routes = {}
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Load routes
                with z.open('routes.txt') as f:
                    lines = f.read().decode('utf-8').split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            fields = line.strip().split(',')
                            if len(fields) >= 4:
                                route_id = fields[0]
                                short_name = fields[2].strip('"').strip()
                                long_name = fields[3].strip('"').strip()
                                
                                # Store the complete route info
                                route_info = {
                                    'route_id': route_id,
                                    'short_name': short_name,
                                    'long_name': long_name,
                                    'display_name': f"{short_name} - {long_name}"
                                }
                                routes[route_id] = route_info
            
            # Save to cache
            self._route_cache = routes
            self._save_cache(routes, self.routes_cache_file)
            
        except Exception as e:
            logging.error(f"Error loading GTFS data: {e}")
            if not self._route_cache:
                self._route_cache = {}

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance_km = R * c
        # Convert distance from km to miles
        return distance_km * 0.621371

    def _format_route_name(self, route_data) -> Optional[str]:
        """Format route name from either string or dictionary data. Returns None for invalid routes."""
        if isinstance(route_data, dict):
            # Extract both short name (route number) and long name
            short_name = route_data.get('short_name', '').strip()
            long_name = route_data.get('long_name', '').strip()
            
            # Only use entries that have both a route number and a descriptive name
            if short_name and long_name and not long_name.startswith('Route '):
                return f"{short_name} - {long_name}"
            return None
            
        elif isinstance(route_data, str):
            # Skip invalid routes
            if not route_data or route_data == '-' or 'unknown' in route_data.lower():
                return None
                
            # If it's just a route number or starts with "Route", skip it
            if route_data.isdigit() or route_data.startswith('Route '):
                return None
                
            # If it's a valid descriptive name, use it as is
            return route_data
            
        return None

    def fetch_real_time_buses(self, user_location=None, radius_miles=3.0) -> List[Dict]:
        """Fetch real-time bus data for buses within radius of UNH."""
        try:
            # Always use UNH location
            user_lat, user_lon = self.UNH_LOCATION
            if user_location:
                user_lat, user_lon = user_location
            
            # Convert radius from miles to kilometers for internal calculations
            radius_km = radius_miles / 0.621371
            
            response = requests.get(self.vehicle_positions_url)
            response.raise_for_status()
            data = response.json()
            
            # Create a list of valid route IDs that have proper descriptive names
            valid_route_ids = set()
            for route_id, route_info in self._route_cache.items():
                if (isinstance(route_info, dict) and 
                    route_info.get('short_name') and 
                    route_info.get('long_name') and 
                    not route_info['long_name'].startswith('Route')):
                    valid_route_ids.add(route_id)
            
            buses = []
            for entity in data.get('entity', []):
                if entity.get('is_deleted'):
                    continue
                
                vehicle = entity.get('vehicle')
                if not vehicle:
                    continue
                
                position = vehicle.get('position', {})
                lat = float(position.get('latitude', 0.0) or 0.0)
                lon = float(position.get('longitude', 0.0) or 0.0)
                
                # Skip if no valid coordinates
                if lat == 0.0 or lon == 0.0:
                    continue
                
                # Calculate distance to UNH
                distance = self._calculate_distance(lat, lon, user_lat, user_lon)
                
                # Skip buses outside the radius
                if distance > radius_km:
                    continue
                
                trip = vehicle.get('trip', {})
                route_id = trip.get('route_id', '')
                
                # Skip buses without a valid route ID
                if route_id not in valid_route_ids:
                    continue
                
                # Get route information
                route_info = self._route_cache[route_id]
                route_name = f"{route_info['short_name']} - {route_info['long_name']}"
                
                # Calculate speed in mph for easier understanding
                speed_mps = float(position.get('speed', 0.0) or 0.0)
                speed_mph = speed_mps * 2.237  # Convert m/s to mph
                
                bus = {
                    'bus_number': vehicle.get('vehicle', {}).get('label', ''),
                    'route_id': route_id,
                    'route': route_name,
                    'latitude': lat,
                    'longitude': lon,
                    'speed': speed_mph,
                    'timestamp': vehicle.get('timestamp', 0),
                    'distance_to_user': distance,
                    'next_departure': self._get_next_departure(vehicle.get('timestamp', 0))
                }
                buses.append(bus)
            
            return sorted(buses, key=lambda x: x['distance_to_user'])
            
        except Exception as e:
            logging.error(f"Error fetching real-time bus data: {e}")
            return []

    def _get_next_departure(self, timestamp: int) -> str:
        """Calculate next departure time from timestamp."""
        if not timestamp:
            return "N/A"
            
        try:
            departure_time = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            
            if departure_time > now:
                time_diff = departure_time - now
                total_minutes = int(time_diff.total_seconds() / 60)
                
                if total_minutes < 1:
                    return "Now"
                elif total_minutes < 60:
                    return f"{total_minutes}m"
                else:
                    hours = total_minutes // 60
                    minutes = total_minutes % 60
                    return f"{hours}h {minutes}m"
            else:
                return departure_time.strftime("%I:%M %p")
                
        except Exception as e:
            logging.error(f"Error calculating departure time: {e}")
            return "N/A"

    def update_bus_database(self, user_location=None) -> None:
        """Update the database with the latest bus information."""
        try:
            buses = self.fetch_real_time_buses(user_location=user_location)
            
            # Use the update session if available, otherwise fall back to db_session
            session = getattr(self, 'update_session', self.db_session)
            
            # First, ensure all routes exist
            route_ids = {bus_data['route_id'] for bus_data in buses if bus_data.get('route_id')}
            for route_id in route_ids:
                route = session.query(RouteModel).filter_by(route_id=route_id).first()
                if not route:
                    route = RouteModel(
                        route_id=route_id,
                        route_type='local'  # Default to local, will be updated when GTFS data is loaded
                    )
                    session.add(route)
            
            # Commit routes first
            session.commit()
            
            # Now process buses
            for bus_data in buses:
                try:
                    bus_number = bus_data.get('bus_number')
                    bus = session.query(BusModel).filter_by(
                        bus_number=bus_number
                    ).first()
                    
                    # Ensure route is in the correct format (NUMBER - NAME)
                    route_name = bus_data.get('route')
                    if not route_name or ' - ' not in route_name:
                        continue
                    
                    # Safely create timestamp
                    timestamp = None
                    try:
                        if bus_data['timestamp']:
                            timestamp = datetime.fromtimestamp(bus_data['timestamp'])
                        else:
                            timestamp = datetime.utcnow()
                    except Exception as e:
                        print(f"Error creating timestamp: {e}, value: {bus_data['timestamp']}")
                        timestamp = datetime.utcnow()
                    
                    if bus:
                        # Update existing bus
                        bus.route_id = bus_data['route_id']
                        bus.route = route_name
                        bus.latitude = bus_data['latitude']
                        bus.longitude = bus_data['longitude']
                        bus.speed = bus_data['speed']
                        bus.last_updated = timestamp
                        bus.distance_to_user = bus_data.get('distance_to_user', 0.0)
                        
                        # Optional fields
                        if 'trip_id' in bus_data:
                            bus.trip_id = bus_data['trip_id']
                        if 'next_stop' in bus_data:
                            bus.next_stop = bus_data['next_stop']
                        if 'current_location' in bus_data:
                            bus.current_location = bus_data['current_location']
                    else:
                        # Create new bus with required fields
                        bus = BusModel(
                            bus_number=bus_data['bus_number'],
                            route_id=bus_data['route_id'],
                            route=route_name,
                            latitude=bus_data['latitude'],
                            longitude=bus_data['longitude'],
                            speed=bus_data['speed'],
                            last_updated=timestamp,
                            is_active=True,
                            distance_to_user=bus_data.get('distance_to_user', 0.0),
                            # Optional fields
                            trip_id=bus_data.get('trip_id'),
                            next_stop=bus_data.get('next_stop'),
                            current_location=bus_data.get('current_location'),
                            available_seats=bus_data.get('available_seats', 0),
                            total_seats=bus_data.get('total_seats', 0),
                            fare=bus_data.get('fare', 0.0),
                            route_type=bus_data.get('route_type', 'local')
                        )
                        session.add(bus)
                except Exception as e:
                    print(f"Error processing bus {bus_data.get('bus_number', 'unknown')}: {e}")
                    continue
            
            session.commit()
        except Exception as e:
            print(f"Error updating bus database: {e}")
            session = getattr(self, 'update_session', self.db_session)
            session.rollback()

    def get_route_info(self, route_id: str) -> Dict:
        """Get detailed information about a specific route, including real-time updates and alerts."""
        if not self._route_cache:
            self._load_gtfs_data()
            
        route_info = {
            'route_id': route_id,
            'route_details': self._route_cache.get(route_id, {}),
            'active_buses': [],
            'trip_updates': [],
            'alerts': []
        }
        
        # Get active buses on this route
        try:
            active_buses = self.db_session.query(BusModel).filter_by(route_id=route_id).all()
            route_info['active_buses'] = []
            
            for bus in active_buses:
                # Use the helper method for last_updated
                last_updated_str = None
                if hasattr(bus, 'get_last_updated_str'):
                    last_updated_str = bus.get_last_updated_str()
                elif hasattr(bus, 'last_updated') and bus.last_updated is not None:
                    try:
                        last_updated_str = bus.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
                    except Exception as e:
                        print(f"Error formatting last_updated: {e}, value: {bus.last_updated}, type: {type(bus.last_updated)}")
                
                bus_info = {
                    'bus_number': bus.bus_number,
                    'latitude': bus.latitude if hasattr(bus, 'latitude') else None,
                    'longitude': bus.longitude if hasattr(bus, 'longitude') else None,
                    'speed': bus.speed if hasattr(bus, 'speed') else None,
                    'next_stop': bus.next_stop if hasattr(bus, 'next_stop') else None,
                    'last_updated': last_updated_str
                }
                route_info['active_buses'].append(bus_info)
        except Exception as e:
            print(f"Error getting active buses: {e}")
            import traceback
            print(traceback.format_exc())
        
        # Get trip updates
        try:
            response = requests.get(self.trip_updates_url)
            response.raise_for_status()
            data = response.json()
            
            for entity in data.get('entity', []):
                if entity.get('is_deleted'):
                    continue
                    
                trip_update = entity.get('trip_update', {})
                trip = trip_update.get('trip', {})
                
                if trip.get('route_id') == route_id:
                    stop_updates = []
                    for stop_time in trip_update.get('stop_time_update', []):
                        stop_id = stop_time.get('stop_id', '')
                        stop_info = self._route_cache.get(stop_id, {})
                        
                        arrival = stop_time.get('arrival', {})
                        departure = stop_time.get('departure', {})
                        
                        stop_updates.append({
                            'stop_id': stop_id,
                            'stop_name': stop_info.get('name', ''),
                            'arrival_time': arrival.get('time'),
                            'departure_time': departure.get('time'),
                            'schedule_relationship': stop_time.get('schedule_relationship', 0)
                        })
                    
                    route_info['trip_updates'].append({
                        'trip_id': trip.get('trip_id', ''),
                        'start_time': trip.get('start_time', ''),
                        'start_date': trip.get('start_date', ''),
                        'schedule_relationship': trip.get('schedule_relationship', 0),
                        'vehicle': trip_update.get('vehicle', {}),
                        'stop_updates': stop_updates
                    })
        except Exception as e:
            print(f"Error fetching trip updates: {e}")
        
        # Get alerts
        try:
            response = requests.get(self.alerts_url)
            response.raise_for_status()
            data = response.json()
            
            for entity in data.get('entity', []):
                if entity.get('is_deleted'):
                    continue
                    
                alert = entity.get('alert', {})
                informed_entities = alert.get('informed_entity', [])
                
                # Check if alert applies to this route
                for entity in informed_entities:
                    if entity.get('route_id') == route_id:
                        route_info['alerts'].append({
                            'id': entity.get('id', ''),
                            'effect': alert.get('effect', ''),
                            'header': alert.get('header_text', {}).get('translation', [{}])[0].get('text', ''),
                            'description': alert.get('description_text', {}).get('translation', [{}])[0].get('text', ''),
                            'active_period': alert.get('active_period', []),
                            'severity_level': alert.get('severity_level', '')
                        })
                        break
        except Exception as e:
            print(f"Error fetching alerts: {e}")
        
        return route_info 

    def start_periodic_updates(self, location_service=None):
        """Start periodic updates of bus data."""
        # Create a separate database session for updates to avoid locking issues
        try:
            db_manager = DatabaseManager()
            engine = create_engine(db_manager.connection_string)
            Session = sessionmaker(bind=engine)
            update_session = Session()
            
            # Assign the new session
            self.update_session = update_session
        except Exception as e:
            print(f"Error creating update session: {e}")
            self.update_session = self.db_session  # Fall back to original session
        
        while True:
            try:
                # Get user location if available
                user_location = None
                if location_service and location_service.current_location:
                    user_location = location_service.current_location
                
                # Use a transaction with retry mechanism to avoid locking issues
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Fetch and update bus data
                        self.update_bus_database(user_location=user_location)
                        break  # Success, exit retry loop
                    except Exception as e:
                        if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                            # Database is locked, retry after a short delay
                            print(f"Database locked, retrying update (attempt {attempt+1}/{max_retries})...")
                            time.sleep(2)  # Wait before retry
                            continue
                        # Other error or last retry failed
                        print(f"Error updating bus data (attempt {attempt+1}/{max_retries}): {e}")
                        if hasattr(self, 'update_session'):
                            self.update_session.rollback()
                        break
                
                # Wait for 15 seconds before next update
                time.sleep(15)
                
            except Exception as e:
                print(f"Error in periodic update: {e}")
                # Wait a bit before retrying on error
                time.sleep(5) 