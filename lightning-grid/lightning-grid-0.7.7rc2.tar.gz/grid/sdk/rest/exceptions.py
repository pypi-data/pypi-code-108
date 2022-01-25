import functools
import json

from grid.openapi.rest import ApiException


class GridException(Exception):
    """Base class for all exceptions raised by the Grid APIs"""
    pass


def throw_with_message(fn):
    """
    Decorator to ignore OpenAPI traceback and raise a custom
    exception with a message passed by Grid Backend. Strictly use it
    for all the functions in the sdk/rest module (assuming they are for
    calling Grid Backend).
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ApiException as e:
            try:
                details = json.loads(e.body)['details']
            except (json.decoder.JSONDecodeError, KeyError):
                raise e
            if len(details) == 1 and isinstance(details[0], dict) and 'message' in details[0]:
                raise GridException(details[0]['message']) from None
            raise e

    return wrapper
