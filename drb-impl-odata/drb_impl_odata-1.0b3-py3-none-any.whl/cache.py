from functools import lru_cache, wraps
from datetime import datetime, timedelta

DEFAULT_TIME = 120


def timed_lru_cache(seconds: int, maxsize: int):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.size = maxsize
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        def reset_cache_expiration_time(sec: int = DEFAULT_TIME):
            func.lifetime = timedelta(seconds=sec)
            func.expiration = datetime.fromisoformat("1970-01-01")

        func.reset_expiration_time = reset_cache_expiration_time

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
