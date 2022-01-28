import functools
from etl import LOGGER as logger

def log_start_and_finalisation(msg):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if msg and logger:
                logger.info(f"Starting {msg}")
            ret = f(*args, **kwargs)
            if msg and logger:
                logger.info(f"Finished {msg}")
            return ret
        return wrapped
    return decorator
