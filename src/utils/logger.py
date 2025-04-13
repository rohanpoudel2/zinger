import logging
from typing import Dict

# Global logger instances
_loggers: Dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name. Creates a new logger if one doesn't exist.
    
    Args:
        name: The name of the logger to get
        
    Returns:
        The requested logger
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]

# Convenience methods to get specific loggers
def get_app_logger() -> logging.Logger:
    """Get the application logger"""
    return get_logger('app')

def get_error_logger() -> logging.Logger:
    """Get the error logger"""
    return get_logger('error')

def get_access_logger() -> logging.Logger:
    """Get the access logger"""
    return get_logger('access')

def get_auth_logger() -> logging.Logger:
    """Get the authentication logger"""
    return get_logger('auth')

def setup_logger():
    logger = logging.getLogger('bus_reservation')

    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)

        # File handler for all logs
        file_handler = logging.FileHandler("bus_reservation.log")
        file_handler.setLevel(logging.INFO)

        # Error file handler for error logs
        error_handler = logging.FileHandler("bus_reservation_error.log")
        error_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

    logger.propagate = False
    return logger
