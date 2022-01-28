"""
This module provides methods to construct regular spaced arrays similar to `numpy.linspace`.
"""
from numpy import arange, geomspace, linspace, logspace
from numpy.typing import NDArray

__all__ = ["stepspace", "linspace", "arange", "geomspace", "logspace"]


## from https://stackoverflow.com/questions/31820107/is-there-a-numpy-function-that-allows-you-to-specify-start-step-and-number
def stepspace(start: float, step: float, num: int, axis=0) -> NDArray:
    """Return an array of `num` values evenly space by `step`."""
    stop = start + (step * num)

    space, retstep = linspace(start, stop, num, endpoint=False, retstep=True, axis=axis)
    assert (
        step == retstep
    ).all(), "This should never be happening, please report a bug!"
    return space
