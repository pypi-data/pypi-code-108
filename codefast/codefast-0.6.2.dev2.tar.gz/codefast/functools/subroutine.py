import time
from typing import Callable


class Retry(object):
    def __init__(self, f: Callable, *args, **kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def load(self, f: Callable, *args, **kwargs):
        """ load a function and its arguments
        """
        self.f = f
        self.args = args
        self.kwargs = kwargs
        return self

    def ensure_nontrivial_return(self, repeat_number: int = 3, sleep_time: float = 10):
        """ retry a few times on empty/None return due to unexpected error such
        as network failure
        Args:
            repeat_number: number of retry
            sleep_time: sleep time between retry
        """
        for _ in range(repeat_number):
            result = self.f(*self.args, **self.kwargs)
            if result:
                return result
            time.sleep(sleep_time)
        return None

    def sleep_and_run(self, sleep_time: float = 10):
        time.sleep(sleep_time)
        return self.f(*self.args, **self.kwargs)
