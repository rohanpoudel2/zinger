class InMemoryStorage:
    def __init__(self):
        # Initialize empty storage
        self.buses = {
            "101": {
                "bus_number": "101",
                "route": "New Haven -> New York",
                "departure": "10:00 AM",
                "total_seats": 30,
                "booked_seats": [],
                "fare": 30
            },
            "102": {
                "bus_number": "102",
                "route": "New Haven -> Boston",
                "departure": "11:00 AM",
                "total_seats": 30,
                "booked_seats": [],
                "fare": 35
            }
        }
        
        self.bookings = {}
        self.booking_id_counter = 1000
    
    def get_all_buses(self):
        return self.buses
    
    def get_bus(self, bus_number):
        return self.buses.get(bus_number)
    
    def get_available_seats(self, bus_number):
        bus = self.get_bus(bus_number)
        if not bus:
            return []
        all_seats = [f"{row}{seat}" for row in range(1, 6) for seat in ['A', 'B', 'C', 'D', 'E', 'F']]
        return [seat for seat in all_seats if seat not in bus['booked_seats']]
    
    def create_booking(self, bus_number, passenger_name, phone, seat):
        bus = self.get_bus(bus_number)
        if not bus:
            raise ValueError("Invalid bus number")
        
        if seat in bus['booked_seats']:
            raise ValueError("Seat already booked")
        
        booking_id = str(self.booking_id_counter)
        self.booking_id_counter += 1
        
        booking = {
            "booking_id": booking_id,
            "bus_number": bus_number,
            "passenger_name": passenger_name,
            "phone": phone,
            "seat": seat,
            "status": "Confirmed"
        }
        
        self.bookings[booking_id] = booking
        bus['booked_seats'].append(seat)
        
        return booking_id
    
    def get_booking(self, booking_id):
        return self.bookings.get(booking_id)
    
    def get_all_bookings(self):
        return self.bookings
    
    def cancel_booking(self, booking_id):
        booking = self.get_booking(booking_id)
        if not booking:
            raise ValueError("Invalid booking ID")
        
        if booking['status'] == 'Cancelled':
            raise ValueError("Booking already cancelled")
        
        bus = self.get_bus(booking['bus_number'])
        bus['booked_seats'].remove(booking['seat'])
        booking['status'] = 'Cancelled'
        
        return True 