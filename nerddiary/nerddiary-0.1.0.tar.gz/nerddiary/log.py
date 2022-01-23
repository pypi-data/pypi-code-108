"""Module for setting up logging."""
import logging
import sys

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_FORMATS = {
    "DEBUG": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "INFO": "%(asctime)s - %(levelname)s - %(message)s",
    "WARNING": "%(asctime)s - %(levelname)s - %(message)s",
    "ERROR": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "CRITICAL": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}


def configure_logger(
    log_level: str = "INFO", log_file: str | None = None
) -> logging.Logger:
    """Configure logging

    Set up logging to stdout with ``log_level``. If ``log_file`` is given use it instead.
    """
    # Set up 'cookiecutter' logger
    logger = logging.getLogger("nerddiary")
    logger.setLevel(logging.DEBUG)

    handler: logging.Handler = logging.StreamHandler(stream=sys.stdout)
    # Create a file handler if a log file is provided
    if log_file is not None:
        handler = logging.FileHandler(log_file)

    formatter = logging.Formatter(LOG_FORMATS[log_level])
    handler.setLevel(LOG_LEVELS[log_level])
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
