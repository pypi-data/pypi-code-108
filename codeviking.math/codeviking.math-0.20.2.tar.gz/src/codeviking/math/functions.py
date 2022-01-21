"""

This module contains functions that are used to create other functions.
Clamping and mixing functions are provided, as are transition functions and
piecewise function assembly.
"""

import math
from typing import Callable, TypeVar, Tuple

from codeviking.math.primitives import smooth010

__all__ = ['make_clamp', 'make_mix',
           'piecewise_func1', 'piecewise_func2',
           'make_interval_func', 'make_triangle_func', 'make_rect_func',
           'make_step', 'make_rect_func', 'make_bump_func', 'make_smooth_step',
           'make_map_from_01', 'make_map_to_01',
           'make_map_from_01c', 'make_map_to_01c']

T = TypeVar('T')
F = TypeVar('F')

FloatToFloat = Callable[[float], float]
FloatToF = Callable[[float], F]


def make_clamp(x0: float, x1: float) -> FloatToFloat:
    """
    Create a clamping function that clamps input values to the range x0, x1.
    """

    def _(x: float) -> float:
        return max(x0, min(x, x1))

    return _


# ［］（）∈∉
def make_mix(y0: F, y1: F) -> FloatToF:
    """
    Create a mix function that mixes between y0 and y1 as x varies between 0
    and 1.

      * y0  for x0 ≤ 0
      * y1 for 1 ≤ x
      * y0 + x*(y1-y0) for x ∈［0,1］
    """

    def _(x: float) -> F:
        if x <= 0.0:
            return y0
        if x < 1.0:
            return y0 * (1.0 - x) + y1 * x
        return y1

    return _


def piecewise_func1(x0: float, f0: FloatToF, f1: FloatToF) -> FloatToF:
    """
    Create a piecewise function with one knot at :math:`x_0`:

      * :math:`f_0(x) \  \mathrm{for} \ x < x_0`
      * :math:`f_1(x) \  \mathrm{for} \ x_0 \leq x`

    :param x0: knot between f0 and f1
    :param f0: function to use for x < x0
    :param f1: function to use for x0 `\leq` x
    :return: piecewise function
    """
    return lambda x: f0(x) if x < x0 else f1(x)


def piecewise_func2(x0: float, x1: float,
                    f0: FloatToF, f1: FloatToF, f2: FloatToF) -> FloatToF:
    """
    Create a piecewise function with two knots:
        * f0(x)  for x < x0
        * f1(x)  for x0 ≤ x < x1
        * f2(x)  for x1 ≤ x

    :param x0: knot between f0 and f1
    :param x1: knot between f1 and f2
    :param f0: function to use for x < x0
    :param f1: function to use for x0 ≤ x < x1
    :param f2: function to use for x1 ≤ x
    :return: piecewise function
    """

    def _(x):
        if x < x0:
            return f0(x)
        if x < x1:
            return f1(x)
        return f2(x)

    return _


def make_interval_func(x0: float, x1: float, y0: F, f: FloatToF,
                       y1: F) -> FloatToF:
    """
    Create function on the interval [x0,x1] with constant value outside that
    interval:

        * y0  for x < x0
        * f(x)  for x0 ≤ x < x1
        * y1  for x1 ≤ x

    """

    def _(x: float) -> F:
        if x < x0:
            return y0
        if x < x1:
            return f(x)
        return y1

    return _


def make_triangle_func(x0: float, x1: float, x2: float,
                       y0: F, y1: F, y2: F) -> FloatToF:
    """
    Create triangle function ( ╱╲ ) on the interval ［x0,x2］:

        * y0  for x < x0
        * linear slope from (x0,y0) to (x1,y1)  for x0 ≤ x < x1
        * linear slope from (x1,y1) to (x2,y2)  for x1 ≤ x < x2
        * y2  for x2 ≤ x

    :param x0: x value of leftmost point of the triangle
    :param x1: x value of center point of the triangle
    :param x2: x value of rightmost point of the triangle
    :param y0: y value of leftmost point of the triangle
    :param y1: y value of center point of the triangle
    :param y2: value of rightmost point of the triangle
    """
    m0 = (y1 - y0) / (x1 - x0)
    b0 = -(x1 * y0 - x0 * y1) / (x0 - x1)
    m1 = (y2 - y1) / (x2 - x1)
    b1 = -(x2 * y1 - x1 * y2) / (x1 - x2)

    def _(x):
        if x < x0:
            return y0
        if x < x1:
            return m0 * x + b0
        if x < x2:
            return m1 * x + b1
        return y2

    return _


def make_step(x0: float, y0: F = 0.0, y1: F = 1.0) -> FloatToF:
    """
    create a step function:

        * f(x) = y0 for x<x0
        * f(x) = y1 for x0≤x
    """

    def _(x):
        return y0 if (x < x0) else y1

    return _


def make_rect_func(x0: float, x1: float, y0: F, y1: F, y2: F) -> FloatToF:
    """
    Create rect function ( ┌─┐ )on the interval ［x0,x1］:

        * y0  for x < x0
        * y1  for x0 ≤ x ≤ x1
        * y2  for x1 < x
    """

    def _(x):
        if x < x0:
            return y0
        if x <= x1:
            return y1
        return y2

    return _


def make_smooth_step(x0: float,
                     x1: float,
                     y0: F = 0.0,
                     y1: F = 1.0) -> FloatToF:
    """
    Creates a smooth step function f with the following properties:

      * f(x)=y0 for x ≤ x0
      * f(x)=y1 for x1 ≤ x
      * f'(x) = 0 for x=x0 and x=x1.
      * in the interval [x0,x1], the function smoothly transitions between
        y0 and  y1.  We use a monotonically increasing sin function on this
        interval.
    """
    height = y1 - y0
    s = math.pi / (x1 - x0)
    shift = math.pi / 2.0

    def _(x: float) -> F:
        if x <= x0:
            return y0
        if x >= x1:
            return y1
        return height * 0.5 * (math.sin(s * (x - x0) - shift) + 1.0) + y0

    return _


def make_bump_func(x0: float, x1: float, x2: float,
                   y0: F, y1: F, y2: F) -> FloatToF:
    """
    Create a bump function with the following properties:

        * f(x)=y0 for x≤x0
        * f(x1)=y1
        * f(x)=y2 for x2≤x
        * f'(x) = 0 for x=x0, x=x1, x=x2.
        * in the interval ［x0,x1］, smoothly and monotonically transition
          between y0 and y1.
        * in the interval ［x1,x2］, smoothly and monotonically transition
          between y1 and y2.
    """
    ah = y1 - y0
    bh = y2 - y1
    aw = x1 - x0
    bw = x2 - x1

    def _(x: float) -> F:
        if x <= x0:
            return y0
        if x <= x1:
            return y0 + ah * smooth010((x - x1) / aw)
        if x <= x2:
            return y2 - bh * smooth010((x - x1) / bw)
        return y2

    return _


def make_map_to_01(t0: float, t1: float) -> FloatToFloat:
    """
    Create a function that linearly maps t0->0.0 and t1->1.0.  This function
    is undefined when t0==t1.  Nevertheless, we return a function that always
    returns 0.0 when t0==t1.  This means that if you construct a forword map
    f= make_map_to_01(t0,t0) and a reverse map g = make_map_from_01(t0, t0),
    then their composition will behave sensibly: g(f(t)) == t0.

    :param t0: value that maps to 0.0
    :type t0: float
    :param t1: value that maps to 1.0
    :type t1: float
    :rtype: (float) -> float
    """
    if t0 == t1:
        # map is constant
        return lambda t: 0.0
    scale = 1.0 / (t1 - t0)
    return lambda t: (t - t0) * scale


def make_map_from_01(t0: F, t1: F) -> FloatToF:
    """
    Create a function that linearly maps 0.0->t1 and 1.0->t1.

    :param t0: value that 0.0 maps to
    :type t0: float
    :param t1: value that 1.0 maps to
    :type t1: float
    :rtype: (float) -> float
    """
    if t0 == t1:
        # map is constant
        return lambda t: t0
    scale = t1 - t0
    return lambda t: t0 + t * scale


def make_map_to_01c(t0: float, t1: float) -> FloatToFloat:
    """
    Clamped version of make_map_to_01.  The resulting function will always
    return a value in [0.0, 1.0].

    :param t0: value that maps to 0.0
    :type t0: float
    :param t1: value that maps to 1.0
    :type t1: float
    :rtype: (float) -> float
    """
    if t0 == t1:
        # map is constant
        return lambda t: 0.0
    scale = 1.0 / (t1 - t0)
    return lambda t: min(max((t - t0) * scale, 0.0), 1.0)


def make_map_from_01c(t0: F, t1: F) -> FloatToF:
    """
    Clamped version of make_map_from_01.  The resulting function will always
    return a value in [t0, t1].

    :param t0: value that 0.0 maps to
    :type t0: float
    :param t1: value that 1.0 maps to
    :type t1: float
    :rtype: (float) -> float
    """
    if t0 == t1:
        # map is constant
        return lambda t: t0
    cl = make_clamp(0, 1)
    scale = t1 - t0
    return lambda x: t0 + scale * cl(x)
