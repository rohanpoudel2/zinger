from typing import Optional, Tuple, List
from rich.console import Console
import geocoder
from geopy.distance import geodesic

console = Console()

class LocationService:
    def __init__(self):
        self.current_location: Optional[Tuple[float, float]] = None
        self.location_name: Optional[str] = None
        # Get location immediately upon initialization
        self._update_location()
    
    def _update_location(self) -> None:
        """
        Update the current device location using IP-based geolocation.
        """
        try:
            g = geocoder.ip('me')
            if g.ok:
                self.current_location = (g.lat, g.lng)
                self.location_name = g.city
                console.print(f"[green]Location detected:[/green] {self.location_name}")
            else:
                console.print("[yellow]Could not determine your location automatically.[/yellow]")
                self.current_location = None
                self.location_name = None
        except Exception as e:
            console.print(f"[red]Error getting location:[/red] {str(e)}")
            self.current_location = None
            self.location_name = None

    def get_location_name(self) -> Optional[str]:
        """
        Get the current location name.
        """
        return self.location_name

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the distance between two points in miles.
        """
        km_distance = geodesic((lat1, lng1), (lat2, lng2)).kilometers
        # Convert kilometers to miles
        return km_distance * 0.621371
    
    def filter_nearby_buses(self, buses: List, max_distance_miles: float = 3.0) -> List:
        """
        Filter buses to only include those within the specified distance (in miles).
        """
        if not self.current_location:
            self._update_location()
            
        if not self.current_location:
            # If we still don't have a location, return all buses
            return buses
            
        nearby_buses = []
        for bus in buses:
            if hasattr(bus, 'latitude') and hasattr(bus, 'longitude'):
                distance = self.calculate_distance(
                    self.current_location[0], 
                    self.current_location[1],
                    bus.latitude, 
                    bus.longitude
                )
                
                # Add distance attribute to bus object (already in miles due to calculate_distance update)
                bus.distance = round(distance, 2)
                
                if distance <= max_distance_miles:
                    nearby_buses.append(bus)
                    
        # Sort by distance
        return sorted(nearby_buses, key=lambda x: x.distance) 