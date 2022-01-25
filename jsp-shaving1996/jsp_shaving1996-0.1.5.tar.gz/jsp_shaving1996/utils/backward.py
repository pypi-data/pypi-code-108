import math
from typing import Tuple


def _find_center_integer(u: int, v: int) -> int:
    # 一番最初以外は必ず偶数個の整数が含まれているので，ピッタリ中央の整数はない
    # ので，小数点以下を含む中央の値を計算して，その左側の値を中央の値として取り扱うこととする
    # NOTE: 想定通りに動いている
    c = math.floor((u + v) / 2)
    return c


def get_next_interval(u: int, v: int) -> Tuple[int, int]:
    # NOTE: 想定通りに動いている
    return u, _find_center_integer(u, v)
