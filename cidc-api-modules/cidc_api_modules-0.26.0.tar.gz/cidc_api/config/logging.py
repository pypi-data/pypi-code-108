import sys
import logging
from typing import Optional

from .settings import IS_GUNICORN, ENV

# TODO: consider adding custom formatting that automatically adds request context
# to all logs, like who the requesting user is and what URL they're accessing, e.g.


def get_logger(name: Optional[str]) -> logging.Logger:
    """Get a configured logger with the given `name`."""
    # If the app is running in gunicorn, inherit all config from gunicorn's loggers.
    # Otherwise, configure a logger with reasonable defaults.
    logger = logging.getLogger(name)
    if IS_GUNICORN:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        logger.handlers = gunicorn_logger.handlers
        logger.setLevel(gunicorn_logger.level)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(threadName)s] [%(levelname)s]: %(message)s"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if ENV == "dev" else logging.INFO)
    return logger
