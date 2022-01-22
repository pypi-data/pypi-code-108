from functools import reduce, partial
from typing import Tuple, Callable


def compose(*functions: Tuple[Callable]):
    def compose2(f, g):
        return lambda x: f(g(x))
    return reduce(compose2, functions, lambda x: x)