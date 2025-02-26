import logging


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
