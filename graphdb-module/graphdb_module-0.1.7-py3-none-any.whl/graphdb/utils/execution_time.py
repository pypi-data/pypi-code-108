import logging
import time
from functools import wraps


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # measure execution time for method
        s = time.time()
        res = func(*args, **kwargs)
        logging.debug("{} -> took {} seconds".format(func.__name__, time.time() - s))
        return res

    return wrapper
