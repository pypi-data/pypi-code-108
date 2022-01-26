import time
from typing import Callable


def sleep_and_run(sleep_time: float, function: Callable, *args, **kwargs):
    time.sleep(sleep_time)
    return function(*args, **kwargs)
