"""This module provides a logger."""

import logging
import os

APP_LOGGER = logging.getLogger("app_logger")


def setup_logger(dt_name, app_logger=APP_LOGGER):
    """Creates logger named app_logger.

    Logs are printed to stdout and saved to log files under '/logs'.
    Each file is names 'dt_name'.log.
    :param dt_name: Name of the digital twin.
    :returns: Created logger
    :rtype: Logger

    """
    if not os.path.exists("logs"):
        os.mkdir("logs")

    app_logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - {}: %(message)s".format(dt_name)
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    # stream_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(filename="./logs/{}.log".format(dt_name))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    app_logger.addHandler(file_handler)
    app_logger.addHandler(stream_handler)
    return app_logger
