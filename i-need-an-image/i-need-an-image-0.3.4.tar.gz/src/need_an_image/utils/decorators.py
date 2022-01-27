import functools

from requests.exceptions import RequestException


def retry_request(max_retry=3):
    """decorator for request retry"""

    def concrete_decorator(function):

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            retry = max_retry
            while retry:
                try:
                    return function(*args, **kwargs)
                except RequestException:
                    retry -= 1
            return function(*args, **kwargs)
        return wrapped

    return concrete_decorator
