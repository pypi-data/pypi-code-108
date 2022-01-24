# StdLib
import random
from time import sleep

from .logger import Logger


class NormalSleeper:
    _log: Logger

    _MINI_SLEEP: int
    _NORMAL_SLEEP: int
    _DEEP_SLEEP: int
    _HIBERNATE_SLEEP: int

    def __init__(
        self,
        mini_sleep: int = 3,
        normal_sleep: int = 40,
        deep_sleep: int = 75,
        hibernate: int = 225,
    ):
        self._log = Logger()

        self._MINI_SLEEP = mini_sleep
        self._NORMAL_SLEEP = normal_sleep
        self._DEEP_SLEEP = deep_sleep
        self._HIBERNATE_SLEEP = hibernate

    def sleep(self, seconds: int):
        self._sleep(seconds)

    def mini_sleep(self):
        self._sleep(self._MINI_SLEEP)

    def normal_sleep(self):
        self._sleep(self._NORMAL_SLEEP)

    def deep_sleep(self):
        self._sleep(self._DEEP_SLEEP)

    def hibernate(self):
        self._sleep(self._HIBERNATE_SLEEP)

    def _sleep(self, duration: int, sigma: int = 5):
        time_in_seconds = round(random.normalvariate(duration, sigma), 5)
        if time_in_seconds <= 0:
            time_in_seconds = round(duration / 3, ndigits=2)
        self._log.print_info(f"[SLEEP] {time_in_seconds} seconds")
        sleep(time_in_seconds)
