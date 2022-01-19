import contextlib
import datetime as dt
import multiprocessing
from collections import Counter
from timeit import default_timer as timer
from typing import Dict

import numpy as np

# TODO: other contexts
manager = multiprocessing.Manager()
stats = manager.list()


class Profiler:
    _starts = dict()
    i: int = 0

    @classmethod
    def _save(cls, label: str, delta: dt.timedelta) -> None:
        stats.append((label, delta.microseconds))

    @classmethod
    def _load(cls) -> Dict[str, np.ndarray]:
        reduce = dict()
        for label, time in stats:
            if label not in reduce:
                reduce[label] = list()
            reduce[label].append(time)
        return {label: np.asarray(stats) for label, stats in reduce.items()}

    @classmethod
    def clear(cls) -> None:
        stats.clear()

    @classmethod
    @contextlib.contextmanager
    def track(cls, label: str) -> None:
        start = timer()
        yield
        delta = dt.timedelta(seconds=timer() - start)
        cls._save(label, delta)

    @classmethod
    def start(cls, label: str) -> int:
        cls.i += 1
        token = cls.i
        cls._starts[cls.i] = [label, timer()]
        return token

    @classmethod
    def stop(cls, token: int) -> None:
        assert token in cls._starts
        label, start = cls._starts[token]
        delta = dt.timedelta(seconds=timer() - start)
        del cls._starts[token]
        cls._save(label, delta)

    @classmethod
    def printstats(cls) -> None:
        stats = cls._load()
        result = dict()
        for label, stat in stats.items():
            runs = len(stat)
            total = str(dt.timedelta(microseconds=int(np.sum(stat))))
            avg = str(dt.timedelta(microseconds=int(np.mean(stat))))
            std = str(dt.timedelta(microseconds=int(np.std(stat))))
            estimate = f"total={total} avg={avg}±{std} {runs=}"
            string = f"{estimate:80} {label}"
            result[string] = string
        sort = map(lambda x: x[0], Counter(result).most_common())
        for string in sort:
            print(string)
