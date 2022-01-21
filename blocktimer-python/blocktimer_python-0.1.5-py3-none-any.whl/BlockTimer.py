# -*- encoding: utf-8 -*-
# ! python3

import sys
import time
from contextlib import ContextDecorator
from typing import Optional
import numpy as np


class BlockTimeManager:
    def __init__(self, window_size=10, buf_size=100000):
        self.timers = dict()
        self.timer_fmts = dict()
        self.window_size = window_size
        self.buf_size = buf_size


btm = BlockTimeManager(window_size=100000)


class Timer:
    def __init__(self, name, window_size, buf_size=100000):
        self.name = name
        self.buf_size = buf_size
        self.window_size = window_size
        self.init()

    def init(self):
        self.measures_arr = np.empty((0, 2))  # LIFO
        self.current_start = None
        self.current_end = None

    def reset(self):
        self.init()

    def tic(self):
        if self.current_start is not None:
            # another tic executed before a toc
            self.toc()
        self.current_start = time.perf_counter()

    def toc(self):
        self.current_end = time.perf_counter()
        self._add_current_measure()

    def _add_current_measure(self):
        self.measures_arr = np.concatenate(
            [np.array([[self.current_start, self.current_end]]), self.measures_arr[: self.buf_size]]
        )
        self.current_start = None
        self.current_end = None

    @property
    def avg(self) -> float:
        return np.mean(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def wavg(self) -> float:
        return np.mean(self.measures_arr[: self.window_size, 1] - self.measures_arr[: self.window_size, 0])

    @property
    def max(self) -> float:
        return np.max(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def min(self) -> float:
        return np.min(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def total(self) -> float:
        return np.sum(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def latest(self) -> float:
        return self.measures_arr[0, 1] - self.measures_arr[0, 0]

    @property
    def median(self) -> float:
        return np.median(self.measures_arr[:, 1] - self.measures_arr[:, 0])

    @property
    def var(self) -> float:
        return np.var(self.measures_arr[:, 1] - self.measures_arr[:, 0])


class BlockTimer(ContextDecorator):
    @staticmethod
    def timers():
        return list(btm.timers.keys())

    def __init__(self, name, fmt=None, window_size=100):
        self.name = name
        if name in btm.timers:
            self.timer = btm.timers[name]
            # restore format
            self.fmt = fmt if fmt is not None else btm.timer_fmts[name]
        else:
            self.timer = Timer(name, btm.window_size, btm.buf_size)
            btm.timers[name] = self.timer
            btm.timer_fmts[name] = fmt
        self.timer.window_size = window_size
        self._default_fmt = "[{name}] num: {num} latest: {latest:.4f} --wind_avg: {wavg:.4f} -- avg: {avg:.4f} --var: {var:.4f} -- total: {total:.4f}"
        if fmt == "default":
            self.fmt = self._default_fmt
        # extend here for new formats
        else:
            self.fmt = None

        self.num_calls = 0

    def __enter__(self) -> "Timer":
        self.tic()
        return self

    def __exit__(self, *args):
        self.toc()
        if self.fmt is not None:
            print(str(self))

    def __str__(self) -> str:
        return self.display()

    def reset(self):
        self.timer.reset()
        self.num_calls = 0

    def display(self, fmt=None):
        if fmt is None:
            if self.fmt is not None:
                fmt = self.fmt
            else:
                fmt = self._default_fmt
        return fmt.format(
            name=self.name, num=self.num_calls, latest=self.latest, wavg=self.wavg, avg=self.avg, var=self.var, total=self.total
        )

    def tic(self):
        self.timer.tic()
        self.num_calls += 1

    def toc(self, display=False):
        self.timer.toc()
        if display:
            return self.display()

    @property
    def latest(self) -> float:
        return self.timer.latest

    @property
    def avg(self) -> float:
        return self.timer.avg

    @property
    def wavg(self) -> float:
        return self.timer.wavg

    @property
    def max(self) -> float:
        return self.timer.max

    @property
    def min(self) -> float:
        return self.timer.min

    @property
    def total(self) -> float:
        return self.timer.total

    @property
    def median(self) -> float:
        return self.timer.median

    @property
    def var(self) -> float:
        return self.timer.var


if __name__ == "__main__":

    @BlockTimer("fct", "default")
    def fct(bobo):
        time.sleep(0.5)

    fct(2)

    for i in range(10):
        with BlockTimer("affe", "default"):
            time.sleep(0.1)
    for i in range(1000):
        with BlockTimer("test", None):
            time.sleep(0.001)

        # BlockTimer("test").display = f"""avg: {BlockTimer("test").avg}  total: {BlockTimer("test").total}"""
        # print(str(BlockTimer("test")))

    print(BlockTimer("test"))
    BlockTimer("test").tic()
    BlockTimer("t2", "default").tic()
    time.sleep(0.4)
    print(BlockTimer("t2").toc(True))

    time.sleep(0.4)
    print(BlockTimer("test").toc(True))
