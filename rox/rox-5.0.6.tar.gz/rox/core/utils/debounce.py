from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import time

class debounce(object):
    def __init__(self, seconds = 1):
        self.seconds = seconds
        self.cancel_until = datetime.min

    def __call__(self, function_to_call):
        @wraps(function_to_call)
        def wrapper(*args, **kwargs):
            now = datetime.now()

            if now < self.cancel_until:
                return

            self.cancel_until = now + timedelta(seconds = self.seconds)
            executor = ThreadPoolExecutor(1)
            executor.submit(self.delayed_call, self.seconds, function_to_call, *args, **kwargs)

        return wrapper

    def delayed_call(self, seconds, fn, *args, **kwargs):
        time.sleep(seconds)
        fn( *args, **kwargs)