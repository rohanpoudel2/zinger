import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logs directory if it doesn't exist
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create formatters
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]'
    )

    # Set up different log files
    files_config = {
        'app': {'path': 'app.log', 'level': logging.INFO, 'formatter': standard_formatter},
        'auth': {'path': 'auth.log', 'level': logging.INFO, 'formatter': detailed_formatter},
        'error': {'path': 'error.log', 'level': logging.ERROR, 'formatter': detailed_formatter},
        'access': {'path': 'access.log', 'level': logging.INFO, 'formatter': detailed_formatter}
    }

    # Configure root logger first
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers (including the default console handler)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    loggers = {}
    
    # Configure each log file
    for name, config in files_config.items():
        # Create handler
        handler = RotatingFileHandler(
            os.path.join(log_directory, config['path']),
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        handler.setFormatter(config['formatter'])
        handler.setLevel(config['level'])

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(config['level'])
        
        # Remove any existing handlers
        for h in logger.handlers[:]:
            logger.removeHandler(h)
            
        logger.addHandler(handler)
        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        loggers[name] = logger

    # Write initial log entry to app.log
    app_logger = loggers['app']
    app_logger.info("Logging setup completed")
    
    return loggers 