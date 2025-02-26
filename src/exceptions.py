class BusReservationError(Exception):
    """Base exception class for Bus Reservation System"""
    pass

class SeatError(BusReservationError):
    """Raised when there's an error related to seat operations"""
    pass

class BookingError(BusReservationError):
    """Raised when there's an error related to booking operations"""
    pass

class ValidationError(BusReservationError):
    """Raised when there's a validation error"""
    pass

class StorageError(BusReservationError):
    """Raised when there's an error related to storage operations"""
    pass

class TrackingError(BusReservationError):
    """Raised when there's an error related to bus tracking"""
    pass 