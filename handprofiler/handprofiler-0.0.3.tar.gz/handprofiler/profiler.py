__all__ = ("track", "start", "stop", "clear", "printstats")

import contextlib
import datetime as dt
import multiprocessing
from collections import Counter
from timeit import default_timer as timer
from typing import Dict, Tuple

import numpy as np

Token = Tuple[str, float]

# TODO: other contexts
manager = multiprocessing.Manager()
_stats = manager.list()


def _save(label: str, delta: dt.timedelta) -> None:
    _stats.append((label, delta.microseconds))


def _load() -> Dict[str, np.ndarray]:
    reduce = dict()
    for label, time in _stats:
        if label not in reduce:
            reduce[label] = list()
        reduce[label].append(time)
    return {label: np.asarray(stats) for label, stats in reduce.items()}


@contextlib.contextmanager
def track(label: str) -> None:
    start = timer()
    yield
    delta = dt.timedelta(seconds=timer() - start)
    _save(label, delta)


def start(label: str) -> Token:
    return label, timer()


def stop(token: Token) -> None:
    label, start = token
    delta = dt.timedelta(seconds=timer() - start)
    _save(label, delta)


def clear() -> None:
    _stats[:] = []


def printstats() -> None:
    result = dict()
    stats = _load()
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
