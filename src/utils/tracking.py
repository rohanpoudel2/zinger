import time
import random
from typing import List, Tuple
import os
import sys

class BusTracker:
    def __init__(self):
        self.locations: List[str] = [
            "Chapel Street, New Haven",
            "Union Station, New Haven",
            "Milford Station",
            "Bridgeport Station",
            "Stamford Station",
            "Grand Central, New York"
        ]
        
        self.boston_locations: List[str] = [
            "Chapel Street, New Haven",
            "Union Station, New Haven",
            "Old Saybrook",
            "New London",
            "Providence",
            "South Station, Boston"
        ]
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_route_locations(self, route: str) -> List[str]:
        """Get locations based on route."""
        if "Boston" in route:
            return self.boston_locations
        return self.locations
    
    def get_random_status(self) -> Tuple[str, str]:
        """Generate random status and delay information."""
        statuses = [
            ("On Time", "No delays reported"),
            ("Slight Delay", "5 minutes behind schedule"),
            ("Minor Traffic", "10 minutes delay expected"),
            ("Heavy Traffic", "15-20 minutes delay possible"),
            ("Weather Delay", "Exercise caution, moving slower")
        ]
        return random.choice(statuses)
    
    def generate_progress_bar(self, progress: int) -> str:
        """Generate a progress bar."""
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        return f'[{bar}] {progress}%'
    
    def track_bus(self, bus_number: str, route: str, departure: str) -> None:
        """Simulate real-time bus tracking."""
        locations = self.get_route_locations(route)
        total_stops = len(locations)
        
        try:
            for i in range(5):  # Show 5 updates
                self.clear_screen()
                current_location_idx = min(i, total_stops - 1)
                current_location = locations[current_location_idx]
                next_location = locations[min(current_location_idx + 1, total_stops - 1)]
                
                progress = min((i + 1) * 20, 100)
                status, delay_info = self.get_random_status()
                
                print(f"\n=== Real-Time Bus Tracking ===")
                print(f"Bus Number: {bus_number}")
                print(f"Route: {route}")
                print(f"Departure Time: {departure}")
                print(f"\nCurrent Location: {current_location}")
                print(f"Next Stop: {next_location}")
                print(f"\nProgress: {self.generate_progress_bar(progress)}")
                print(f"Status: {status}")
                print(f"Info: {delay_info}")
                print("\nUpdating in real-time...")
                print("\nPress Ctrl+C to stop tracking")
                
                time.sleep(5)  
                
        except KeyboardInterrupt:
            print("\nStopped tracking.")
            time.sleep(1) 