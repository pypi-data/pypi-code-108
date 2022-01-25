import logging
import sys

DEFAULT_LOGGING_LEVEL = logging.INFO
# A level lower than DEBUG for extremely low-level logging
TRACE = logging.DEBUG - 1

# Set the basic config to INFO, so that individual loggers can be configured without interference.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
_loggers = set()
_level = DEFAULT_LOGGING_LEVEL


# Thin wrapper around Logger, which adds itself into a global registry.
class _RegisteredLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _loggers.add(self)


def get_logger(name):
    """Get the Tecton logger. Default every logger to ERROR level, unless explicitly changed by the user."""
    try:
        logger_cls = logging.getLoggerClass()
        logging.setLoggerClass(_RegisteredLogger)
        logger = logging.getLogger(name)
        logger.setLevel(_level)
        return logger
    finally:
        logging.setLoggerClass(logger_cls)


def set_logging_level(level):
    """Set the logging level of Tecton SDK."""
    global _level
    _level = level
    for logger in _loggers:
        logger.setLevel(level)


def get_logging_level():
    return _level
