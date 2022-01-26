import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# configuration
FORMATTER = logging.Formatter("%(asctime)s — %(threadName)s — %(process)d — %(name)s — %(levelname)s — %(message)s")
LOGS_FILE = 'logs/app.logs'
CONSOLE_LOGGING: bool = True
FILE_LOGGING: bool = False


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOGS_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, console_logging: bool = CONSOLE_LOGGING, file_logging: bool = FILE_LOGGING):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough

    if console_logging:
        logger.addHandler(get_console_handler())

    if file_logging:
        logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
