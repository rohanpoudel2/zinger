import logging


def setup_logger():
    logger = logging.getLogger('bus_reservation')

    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)

        # Logs will be saved to 'bus_reservation.log' instead of appearing in CLI
        handler = logging.FileHandler("bus_reservation.log")
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    logger.propagate = False  # Prevent duplicate logging
    return logger
