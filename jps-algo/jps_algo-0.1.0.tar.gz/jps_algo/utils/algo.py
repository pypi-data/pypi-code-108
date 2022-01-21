import math
from typing import List

from .merge import merge
from .operation import Operation


def update_S(S: List[List[int]], ops: List[Operation], alpha: List[int], k0: int, m: int):
    """
    S の更新をする.
    参照渡しにより更新するので注意
    """
    scheduled, asc_not_scheduled = list(), [m]
    for i in range(k0):
        # NOTE: αはリストが空の場合 or 全てがスケジュール済みの場合の両方で None になるので,
        # スケジュール済みとそうでないものを分けるために, lenで取得する必要がある
        partition_job_idx = len(S[i]) if alpha[i] is None else alpha[i]
        scheduled += S[i][:partition_job_idx]
        asc_not_scheduled = merge(asc_not_scheduled, S[i][partition_job_idx:], ops)
        S[i] = list()
        alpha[i] = None

    alpha[k0] = len(scheduled)
    S[k0] = scheduled + asc_not_scheduled


def setup_params(sorted_ops: List[Operation]):
    m, n = 0, len(sorted_ops)
    t = sorted_ops[0].r
    p = math.floor(math.log2(n))
    return m, n, t, p


def setup_container(p: int):
    alpha = [None for _ in range(p + 1)]
    S = [list() for _ in range(p + 1)]
    schedule = dict()
    return alpha, S, schedule
