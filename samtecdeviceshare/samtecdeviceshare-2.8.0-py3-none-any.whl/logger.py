import os
import sys
import logging
from logging.handlers import RotatingFileHandler

class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        self.max_level = max_level
        super().__init__(name='MaxLevelFilter')

    def filter(self, record):
        return record.levelno <= self.max_level

def setup_logger(logName, logFolder):
    log_formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s', '%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger(logName)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    info_file_handler = RotatingFileHandler(
        filename=os.path.join(logFolder, logName+'.info.log'),
        maxBytes=3*1024*1024,
        backupCount=10
    )
    info_file_handler.setFormatter(log_formatter)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.addFilter(MaxLevelFilter(logging.WARNING))
    error_file_handler = RotatingFileHandler(
        filename=os.path.join(logFolder, logName+'.error.log'),
        maxBytes=3*1024*1024,
        backupCount=10
    )
    error_file_handler.setFormatter(log_formatter)
    error_file_handler.setLevel(logging.ERROR)
    logger.addHandler(info_file_handler)
    logger.addHandler(error_file_handler)
    # For development print to stdout and stderr
    if os.getenv('PYTHON_ENV') == 'development' or os.getenv('LOG_VERBOSE'):
        so_handler = logging.StreamHandler(sys.stdout)
        so_handler.setFormatter(log_formatter)
        so_handler.setLevel(logging.DEBUG)
        so_handler.addFilter(MaxLevelFilter(logging.WARNING))
        se_handler = logging.StreamHandler(sys.stderr)
        se_handler.setFormatter(log_formatter)
        se_handler.setLevel(logging.WARNING)
        logger.addHandler(so_handler)
        logger.addHandler(se_handler)
        logger.setLevel(logging.DEBUG)
    return logger
