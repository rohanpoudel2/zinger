import requests
from datetime import datetime
from typing import List, Dict, Optional
from models.database_models import BusModel
from repositories.bus_repository import BusRepository
from utils.database_manager import DatabaseManager
import json
import time
import os
import zipfile
import io
from sqlalchemy.orm import Session

class TransitService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.gtfs_url = "https://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip"
        self.vehicle_positions_url = "https://cttprdtmgtfs.ctttrpcloud.com/TMGTFSRealTimeWebService/Vehicle/VehiclePositions.json"
        self.trip_updates_url = "https://cttprdtmgtfs.ctttrpcloud.com/TMGTFSRealTimeWebService/TripUpdate/TripUpdates.json"
        self.alerts_url = "https://cttprdtmgtfs.ctttrpcloud.com/TMGTFSRealTimeWebService/Alert/Alerts.json"
        
        # Cache for GTFS data
        self._route_cache = {}
        self._stop_cache = {}
        self._load_gtfs_data()

    def _load_gtfs_data(self) -> None:
        """Load GTFS data from CTTransit and cache routes and stops."""
        if not self._route_cache or not self._stop_cache:
            try:
                response = requests.get(self.gtfs_url)
                response.raise_for_status()
                
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # Load routes
                    with z.open('routes.txt') as f:
                        lines = f.read().decode('utf-8').split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                fields = line.strip().split(',')
                                self._route_cache[fields[0]] = {
                                    'route_short_name': fields[1],
                                    'route_long_name': fields[2],
                                    'route_desc': fields[3] if len(fields) > 3 else ''
                                }
                    
                    # Load stops
                    with z.open('stops.txt') as f:
                        lines = f.read().decode('utf-8').split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                fields = line.strip().split(',')
                                self._stop_cache[fields[0]] = {
                                    'stop_name': fields[1],
                                    'stop_desc': fields[2] if len(fields) > 2 else '',
                                    'stop_lat': float(fields[3]),
                                    'stop_lon': float(fields[4])
                                }
            except Exception as e:
                print(f"Error loading GTFS data: {e}")

    def fetch_real_time_buses(self) -> List[Dict]:
        """Fetch real-time bus data from CTTransit."""
        try:
            response = requests.get(self.vehicle_positions_url)
            response.raise_for_status()
            data = response.json()
            
            buses = []
            for entity in data.get('entity', []):
                if entity.get('is_deleted'):
                    continue
                    
                vehicle = entity.get('vehicle')
                if not vehicle:
                    continue
                
                vehicle_data = vehicle.get('vehicle', {})
                position = vehicle.get('position', {})
                trip = vehicle.get('trip', {})
                
                bus = {
                    'bus_number': vehicle_data.get('label', ''),
                    'route_id': trip.get('route_id', ''),
                    'trip_id': trip.get('trip_id', ''),
                    'latitude': position.get('latitude', 0.0),
                    'longitude': position.get('longitude', 0.0),
                    'speed': position.get('speed', 0.0),
                    'bearing': position.get('bearing', 0.0),
                    'timestamp': vehicle.get('timestamp', 0),
                    'next_stop': vehicle.get('stop_id', '')
                }
                buses.append(bus)
            
            return buses
        except Exception as e:
            print(f"Error fetching real-time bus data: {e}")
            return []

    def update_bus_database(self) -> None:
        """Update the database with the latest bus information."""
        try:
            buses = self.fetch_real_time_buses()
            for bus_data in buses:
                try:
                    bus = self.db_session.query(BusModel).filter_by(
                        bus_number=bus_data['bus_number']
                    ).first()
                    
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
                        bus.latitude = bus_data['latitude']
                        bus.longitude = bus_data['longitude']
                        bus.speed = bus_data['speed']
                        bus.bearing = bus_data['bearing']
                        bus.trip_id = bus_data['trip_id']
                        bus.next_stop = bus_data['next_stop']
                        bus.last_updated = timestamp
                    else:
                        # Create new bus
                        bus = BusModel(
                            bus_number=bus_data['bus_number'],
                            route_id=bus_data['route_id'],
                            route="Unknown Route",  # Add default route name
                            latitude=bus_data['latitude'],
                            longitude=bus_data['longitude'],
                            speed=bus_data['speed'],
                            bearing=bus_data['bearing'],
                            trip_id=bus_data['trip_id'],
                            next_stop=bus_data['next_stop'],
                            last_updated=timestamp,
                            is_active=True,
                            current_location='En Route',
                            route_type='local',
                            agency_id='CTTRANSIT'
                        )
                        self.db_session.add(bus)
                except Exception as e:
                    print(f"Error processing bus {bus_data.get('bus_number', 'unknown')}: {e}")
                
            self.db_session.commit()
        except Exception as e:
            print(f"Error updating bus database: {e}")
            self.db_session.rollback()

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
                    'bearing': bus.bearing if hasattr(bus, 'bearing') else None,
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
                        stop_info = self._stop_cache.get(stop_id, {})
                        
                        arrival = stop_time.get('arrival', {})
                        departure = stop_time.get('departure', {})
                        
                        stop_updates.append({
                            'stop_id': stop_id,
                            'stop_name': stop_info.get('stop_name', ''),
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