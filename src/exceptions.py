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

class AuthenticationError(BusReservationError):
    """Raised when there's an authentication error"""
    pass

class AuthorizationError(BusReservationError):
    """Raised when there's an authorization error"""
    pass

class DatabaseError(BusReservationError):
    """Raised when there's a database operation error"""
    pass

class StorageError(BusReservationError):
    """Raised when there's an error related to storage operations"""
    pass

class TrackingError(BusReservationError):
    """Raised when there's an error related to bus tracking"""
    pass

class BusError(BusReservationError):
    """Base class for bus-related errors."""
    pass

class UserError(BusReservationError):
    """Base class for user-related errors."""
    pass 