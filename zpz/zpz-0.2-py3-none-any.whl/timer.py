import sys
import time
from functools import wraps
from typing import Callable, List


class Timer:
    def __init__(self):
        self._running = False

    def start(self):
        self._t_start = time.perf_counter()
        self._t_stop = None
        self._running = True
        return self

    def stop(self):
        if self._running:
            self._t_stop = time.perf_counter()
            self._running = False
        return self

    @property
    def seconds(self):
        if self._running:
            return time.perf_counter() - self._t_start
        return self._t_stop - self._t_start

    @property
    def milliseconds(self):
        return self.seconds * 1000


def humanize(seconds: float) -> List[str]:
    msg = []
    if seconds >= 3600:
        hours, seconds = divmod(seconds, 3600)
        hours = int(hours)
        if hours < 2:
            msg.append(f'{hours} hour')
        else:
            msg.append(f'{hours} hours')
    if seconds >= 60:
        minutes, seconds = divmod(seconds, 60)
        minutes = int(minutes)
        if minutes < 2:
            msg.append(f'{minutes} minute')
        else:
            msg.append(f'{minutes} minutes')
    msg.append(f'{round(seconds, 4)} seconds')
    return msg


def timed(print_func: Callable = None) -> Callable:
    '''
    Usage 1:

        @timed()
        def myfunc(...):
            ...

    Usage 2:

        import logging
        logger = logging.getLogger(__name__)

        @timed(logger.info)
        def myfunc(...):
            ...
    '''
    if print_func is None:
        def print_func(text):
            print(text, file=sys.stderr)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def profiled_func(*args, **kwargs):
            print_func(f'Starting function `{func.__name__}`')
            timer = Timer().start()
            result = func(*args, **kwargs)
            duration = ', '.join(humanize(timer.stop().seconds))
            print_func(f'Finishing function `{func.__name__}`')
            print_func(f'Function `{func.__name__}` took {duration} to finish')
            return result

        return profiled_func

    return decorator


def timed_call(func, *args, **kwargs):
    t0 = time.perf_counter()
    z = func(*args, **kwargs)
    seconds = time.perf_counter() - t0
    return z, seconds
