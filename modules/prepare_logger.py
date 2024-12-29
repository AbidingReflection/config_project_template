import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
import sys
import os
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Custom formatter for microsecond-level timestamp logging."""
    
    def formatTime(self, record, datefmt=None):
        """Format log timestamp to include milliseconds."""
        ct = self.converter(record.created)
        if datefmt:
            s = datetime.fromtimestamp(record.created).strftime(datefmt)
        else:
            t = datetime.fromtimestamp(record.created)
            s = t.strftime("%Y-%m-%d %H:%M:%S") + ",%03d" % (record.msecs)
        return s

def prepare_logger(log_path: str, output_name_prefix="") -> Logger:
    """Create and configure a logger with console and rotating file handlers."""
    
    if not os.path.exists(log_path):
        os.makedirs(log_path)  # Ensure log directory exists

    timestamp_str = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    log_file = os.path.join(log_path, f"{output_name_prefix}{timestamp_str}.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_format = CustomFormatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S.%f')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    # File handler with log rotation
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
