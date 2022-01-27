# -*- coding: utf-8 -*-
import datetime
from timeit import default_timer


class Timer(object):
    """
    A context manager to help measure execution times
    """

    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed = end - self.start
        self.delta = datetime.timedelta(seconds=self.elapsed)
