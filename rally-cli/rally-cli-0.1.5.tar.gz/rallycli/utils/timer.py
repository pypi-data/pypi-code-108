import time
from threading import Thread


class Timer(Thread):
    """Utility timer for simple scheduling. Runs forever in sleep_time execution intervals"""

    def __init__(self, sleep_time: int):
        super().__init__()
        self._sleep_time: int = sleep_time
        self._subscribers = []
        self._running = True

    def add(self, function):
        self._subscribers.append(function)

    def run(self):
        while True:
            time.sleep(self._sleep_time)
            self._execute_subs()

    def _execute_subs(self):
        for func in self._subscribers:
            func()
