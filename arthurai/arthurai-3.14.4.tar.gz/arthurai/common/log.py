
import logging


DEFAULT_LOG_LEVEL = logging.INFO


def initialize_logging():
    """Creates a parent 'arthurai' logger with a console output and INFO level.
    """
    arthur_logger = logging.getLogger("arthurai")
    arthur_logger.setLevel(DEFAULT_LOG_LEVEL)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    arthur_logger.handlers = []
    arthur_logger.addHandler(ch)


def _set_arthur_log_level(level: int):
    logging.getLogger("arthurai").setLevel(level)


def enable_debug_logging():
    """Enables debug logging for the arthurai package.
    """
    _set_arthur_log_level(logging.DEBUG)


def disable_debug_logging():
    """Disables debug logging for the arthurai package.
    """
    _set_arthur_log_level(DEFAULT_LOG_LEVEL)
