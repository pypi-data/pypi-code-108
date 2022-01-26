import logging
import sys

LOGGER_NAME = "aporia"
LOG_FORMAT = "{asctime}:{levelname}:{name}:{message}"
DEFAULT_LOG_LEVEL = logging.INFO

logger = logging.getLogger(LOGGER_NAME)


def init_logger():
    """Initializes the Aporia logger."""
    logger.setLevel(DEFAULT_LOG_LEVEL)

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, style="{"))
        logger.addHandler(handler)


def set_log_level(debug: bool):
    """Sets the log level of the Aporia logger."""
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(DEFAULT_LOG_LEVEL)
