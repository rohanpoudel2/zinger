import logging
from utils.logger import setup_logger
from utils.storage import InMemoryStorage

# Initialize storage
storage = InMemoryStorage()

def display_main_menu():
    print("\n=== Welcome to Bus Tracking System ===")
    print("1. View Available Buses")
    print("2. My Bookings")
    print("3. Book a Ticket")
    print("4. Cancel My Booking")
    print("5. Track My Bus")
    print("6. Exit")
    print("====================================")
    return input("Select an option (1-6): ")

def view_available_buses():
    print("\n--- Available Buses ---")
    buses = storage.get_all_buses()
    
    for bus_number, bus in buses.items():
        available_seats = 30 - len(bus['booked_seats'])
        print(f"{bus_number}. Bus {bus['bus_number']}: {bus['route']} | {bus['departure']} | {available_seats} seats | ${bus['fare']}")
    
    input("\nPress Enter to continue...")

def view_my_bookings():
    print("\n--- My Bookings ---")
    bookings = storage.get_all_bookings()
    
    if not bookings:
        print("\nNo bookings found.")
    else:
        for booking_id, booking in bookings.items():
            bus = storage.get_bus(booking['bus_number'])
            print(f"Booking #{booking_id} | Bus {booking['bus_number']} | {bus['route']} | "
                  f"{bus['departure']} | Seat {booking['seat']} | {booking['status']}")
    
    input("\nPress Enter to continue...")

def book_ticket():
    print("\n--- Book a Ticket ---")
    
    # Show available buses
    print("\nAvailable Buses:")
    view_available_buses()
    
    # Get booking details
    bus_number = input("\nEnter Bus Number: ")
    if bus_number not in storage.get_all_buses():
        print("\nInvalid bus number!")
        input("Press Enter to continue...")
        return
    
    # Show available seats
    available_seats = storage.get_available_seats(bus_number)
    if not available_seats:
        print("\nSorry, no seats available on this bus!")
        input("Press Enter to continue...")
        return
    
    print("\nAvailable Seats:", ", ".join(available_seats))
    
    # Get passenger details
    passenger_name = input("Enter Passenger Name: ")
    phone = input("Enter Phone Number: ")
    seat = input("Enter Seat Number (e.g., 1A): ").upper()
    
    if seat not in available_seats:
        print("\nInvalid or unavailable seat!")
        input("Press Enter to continue...")
        return
    
    try:
        booking_id = storage.create_booking(bus_number, passenger_name, phone, seat)
        print(f"\nBooking Confirmed! Your booking ID is: {booking_id}")
    except ValueError as e:
        print(f"\nError: {str(e)}")
    
    input("Press Enter to continue...")

def cancel_booking():
    print("\n--- Cancel Booking ---")
    booking_id = input("Enter Booking ID to cancel: ")
    
    try:
        storage.cancel_booking(booking_id)
        print(f"\nBooking #{booking_id} has been cancelled")
        print("Refund will be processed within 3-5 business days")
    except ValueError as e:
        print(f"\nError: {str(e)}")
    
    input("Press Enter to continue...")

def track_bus():
    print("\n--- Track My Bus ---")
    booking_id = input("Enter Booking ID: ")
    
    booking = storage.get_booking(booking_id)
    if not booking:
        print("\nInvalid booking ID!")
    elif booking['status'] == 'Cancelled':
        print("\nThis booking has been cancelled!")
    else:
        bus = storage.get_bus(booking['bus_number'])
        print(f"\nTracking Bus {booking['bus_number']} ({bus['route']})")
        print("Current Location: Chapel Street, New Haven")
        print("Expected Arrival: On Time (10 minutes)")
    
    input("Press Enter to continue...")

def main():
    logger = setup_logger()
    
    while True:
        choice = display_main_menu()
        
        try:
            if choice == '1':
                logger.info("Selected: View Available Buses")
                view_available_buses()
            elif choice == '2':
                logger.info("Selected: View My Bookings")
                view_my_bookings()
            elif choice == '3':
                logger.info("Selected: Book a Ticket")
                book_ticket()
            elif choice == '4':
                logger.info("Selected: Cancel Booking")
                cancel_booking()
            elif choice == '5':
                logger.info("Selected: Track Bus")
                track_bus()
            elif choice == '6':
                logger.info("Exiting application")
                print("\nThank you for using Bus Tracking System!")
                break
            else:
                print("\nInvalid option. Please try again.")
                input("Press Enter to continue...")
                
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print(f"\nError: {str(e)}")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()