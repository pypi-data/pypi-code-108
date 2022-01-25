from typing import Tuple


def get_next_interval(u: int, v: int) -> Tuple[int, int]:
    # NOTE: 想定通りに動いている
    n = v - u + 1
    u = v + 1
    v = v + 2 * n
    return u, v
