import gc
from contextlib import contextmanager
from functools import wraps


@contextmanager
def no_gc():
    isgc = gc.isenabled()
    if isgc:
        gc.disable()
    yield
    if isgc:
        gc.enable()


def nogc(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        with no_gc():
            return func(*args, **kwargs)

    return decorated
