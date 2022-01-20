import time
from functools import wraps

from cnvrgv2.errors import CnvrgRetryError


def retry(tries=10, delay=5, backoff=2, log_error=False):
    """
    Will retry decorated function with exponential backoff
    @param tries: Number of retries
    @param delay: Initial delay between attempts
    @param backoff: exponential backoff factor
    @param log_error: Whether or not print the raised error
    @return: decorator for retrying a function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            backoff_delay = delay
            while attempt < tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if log_error:
                        print(e)
                    time.sleep(backoff_delay)
                    attempt += 1
                    backoff_delay *= backoff
            raise CnvrgRetryError("Number of retries exceeded")
        return wrapper
    return decorator
