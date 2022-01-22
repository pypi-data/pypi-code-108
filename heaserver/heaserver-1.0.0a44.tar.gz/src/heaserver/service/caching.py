import datetime
import functools


DEFAULT_TTL = datetime.timedelta(hours=1)


def ttl_cache(ttl: datetime.timedelta = DEFAULT_TTL):
    def wrap(func):
        time, value = None, None

        @functools.wraps(func)
        def wrapped(*args, **kw):
            nonlocal time
            nonlocal value
            now = datetime.datetime.now()
            if not time or now - time > ttl:
                value = func(*args, **kw)
                time = now
            return value
        return wrapped
    return wrap