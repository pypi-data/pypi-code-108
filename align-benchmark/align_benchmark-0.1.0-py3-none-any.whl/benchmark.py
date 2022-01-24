"""Benchmark test1 (wu-ch1)."""
# pylint: disable=invalid-name

from typing import List, Optional, Tuple, Union

from pathlib import Path
from itertools import zip_longest
import numpy as np
import pandas as pd

from align_benchmark.twotuple_metric import twotuple_metric

file_loc = "data/para-wh-ch1-benchmark1.xlsx"
if not Path(file_loc).exists():
    raise SystemExit(f"File [{file_loc}] does not exist.")

_ = pd.read_excel(file_loc, header=0)[["Unnamed: 1", "Unnamed: 3"]]
_.columns = ["list1", "list2"]
bm1 = _.to_numpy().tolist()


def benchmark(
    lst_: Optional[List[Union[Tuple[int, int], List[int]]]] = None,
    bench: List[Union[Tuple[int, int], List[int]]] = bm1
) -> float:
    """Bnechmark para wh-ch1.

    Args:
        lst_: List of two-tuples of integers

    Return
        benchmark score between 0 and 1, 1 being the best.

    from itertools import zip_longest
    lst = [*zip_longest(range(33), range(36), fillvalue=32)]

    mat = np.zeros((36, 36))

    np.vectorize(lambda x, y: x * y)(*np.meshgrid(range(5), range(4), sparse=True))

    mat = np.vectorize(lambda x, y: twotuple_metric(lst[x], bm1[y]))(
        *np.meshgrid(range(36), range(36), sparse=False)
    )
    """
    if lst_ is None:
        lst = [*zip_longest(range(33), range(36), fillvalue=32)]
    else:
        lst = lst_[:]

    def func(x: int, y: int):
        """Make a dummy."""
        return twotuple_metric(lst[int(x)], bench[int(y)])  # type: ignore

    len_1 = len(lst)
    len_ = len(bench)
    row = np.arange(len_1)
    col = np.arange(len_)
    _ = np.meshgrid(row, col, sparse=True)
    mat = np.vectorize(func)(*_)

    benchmark.mat = mat
    benchmark.lst = lst
    benchmark.bench = bench

    return np.sum(mat.max(axis=0)) / len_
