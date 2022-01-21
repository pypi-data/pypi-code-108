"""

This module contains primitive functions designed to be used in the creation
of more complex functions.
"""

import math
from typing import Tuple


def min_max(a: float, b: float) -> Tuple[float, float]:
    """
    Return (a, b) in order: ( min(a,b), max(a,b) )

    :type a: float
    :type b: float
    :return: min(a,b), max(a,b)
    :rtype: float, float
    """
    return min(a, b), max(a, b)


def clamp01(x: float) -> float:
    """
    Clamp input value to ［0.0, 1.0］
    """
    return max(0.0, min(x, 1.0))


def smooth101(x: float) -> float:
    """
    Smooth step down on the interval ［-1,0］ and up on ［0,1］.

    **WARNING**: this function is *also* defined outside the interval ［-1,1］.
    It is intended to be used as a primitive to build other functions,
    so for efficiency reasons, it is not clamped or otherwise modified.

    .. image:: /figures/smooth101.*

    :type x: float
    """
    return 0.5 * math.sin(math.pi * (x - 0.5)) + 0.5


def smooth010(x: float) -> float:
    """
    Smooth step up on the interval ［-1,0］, and down on ［0,1］.

    **WARNING**: this function is *also* defined outside the interval ［-1,1］.
    It is intended to be used as a primitive to build other functions,
    so for efficiency reasons, it is not clamped or otherwise modified.

    .. image:: /figures/smooth010.*

    :type x: float
    """
    return 0.5 * math.cos(math.pi * x) + 0.5


def smooth_step_up(x: float) -> float:
    """
    Step up from 0 to 1 on the interval ［0,1］, and clamp to 0.0 and 1.0
    outside the interval.

    .. image:: /figures/smooth_step_up.*

    :type x: float
    :rtype: float
    """
    if x <= 0.0:
        return 0.0
    if 1.0 <= x:
        return 1.0
    return smooth101(x)


def smooth_step_down(x: float) -> float:
    """
    Step up from 0 to 1 on the interval ［0,1］, and clamp to 0.0 and 1.0
    outside the interval.

    .. image:: /figures/smooth_step_down.*

    :type x: float
    :rtype: float
    """
    if x <= 0.0:
        return 1.0
    if 1.0 <= x:
        return 0.0
    return smooth010(x)


def bump(x: float) -> float:
    """
    Smooth step up on the interval ［-1,0］, and down on ［0,1］.  Clamp to 0.0
    outside the interval.  This is the clamped version of [smooth010].

    .. image:: /figures/bump.*

    :type x: float
    :rtype: float
    """
    if x <= -1.0:
        return 0.0
    if 1.0 <= x:
        return 0.0
    return smooth010(x)


def rect(x: float) -> float:
    """
    The rect function defined as:

        * 1 for -½ ≤ x ≤ ½
        * 0 otherwise.

    .. image:: /figures/rect.*

    """
    return 1.0 if abs(x) <= 0.5 else 0.0


def wrap_to_interval(x: float, x0: float, s: float) -> float:
    """
    Given an interval (［x0,x0+s), map x to this interval by assuming the
    interval repeats its values on this interval infinitely in both directions.
    """
    return ((x - x0) % s) + x0


def wrap_to_centered_interval(x: float, center: float,
                              half_width: float) -> float:
    """
    Given an interval (［center-half_width, center+half_width),
    map x to this interval by assuming the interval repeats infinitely.
    """
    return ((x - (center - half_width)) % (2.0 * half_width)) + (
            center - half_width)


def clamp(x: float, x0: float, x1: float) -> float:
    """
    Clamp x to lie within the interval [x0, x1]

    :param x: the value to clamp
    :type x: float
    :param x0: left edge of the interval
    :type x0: float
    :param x1: right edge of the interval
    :type x1: float
    :return: x restricted to [x0, x1]
    :rtype: float
    """
    return max(x0, min(x, x1))
