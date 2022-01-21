import time
from pprint import pformat
import threading
from functools import (
    wraps,
    reduce,
)
from werkzeug.exceptions import (
    TooManyRequests,
    GatewayTimeout,
    RequestTimeout,
)
from ._format import pf_echo


def ajax_func(func, daemon=True):
    @wraps(func)
    def wrapper(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.daemon = daemon
        th.start()

    return wrapper


def retry(func, count=3):
    '''
    @retry
    def func():
        pass
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        for i in range(count - 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(pf_echo(func, *args, **kwargs))
                print("[ERROR]: ", pformat(e))
        return func(*args, **kwargs)

    return wrapper


def retry_api(count=3, delay=30, exceptions=None):
    '''
    @retry_api(exceptions=(TooManyRequests))
    def func():
        pass
    '''
    if exceptions is None:
        exceptions = (
            RequestTimeout,
            GatewayTimeout,
            TooManyRequests,
        )

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(count - 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    time.sleep(delay)

            return func(*args, **kwargs)

        return wrapper

    return deco
