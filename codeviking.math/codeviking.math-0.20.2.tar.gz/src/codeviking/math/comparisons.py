r"""
Numerical Comparison Functions
------------------------------

Comparing floating-point numbers for equality can be problematic.  Testing
for exact equality is usually not a good idea.  Instead, we usually want to
consider two values equal if they are very close.  The functions in this
module can be used to create comparison functions that tolerate a
user-specified amount of error.

Definitions:
````````````

  Relative Difference

    .. math::

        \textrm{rel_diff} (a, b) = \frac{\left| a - b \right|}{
            \max\left( |a|, |b|\right)}


  Absolute Difference
    .. math:: \textrm{abs_diff}(a, b) = |a - b|

"""
from typing import Callable, TypeVar, Sequence

F = TypeVar('F')

FloatToFloat = Callable[[float], float]
floatToF = Callable[[float], F]


def make_relative_equals(tol: float) -> Callable[[float, float], bool]:
    r"""
    Create a comparison function `is_equal(a,b)` that returns True if
    :math:`\textrm{rel_diff}(a, b) \leq tol`

    :param tol: relative tolerance
    :return: function that returns True if relative difference between a and b
             is less than tol.
    """

    def is_equal(a: float, b: float) -> bool:
        mx = max(abs(a), abs(b))
        delta = abs(a - b)
        return delta <= tol * mx

    return is_equal


def make_absolute_equals(tol: float) -> Callable[[float, float], bool]:
    r"""
    Create a comparison function `is_equal(a,b)` that returns True if
    :math:`\textrm{abs_diff}(a, b) \leq tol`

    :param tol: absolute tolerance
    :return: function that returns True if absolute difference between a and b
             is less than tol.
    """

    def is_equal(a: float, b: float) -> bool:
        delta = abs(a - b)
        return delta <= tol

    return is_equal


def make_equals(abs_tol: float, rel_tol: float) -> Callable[
    [float, float], bool]:
    r"""
    Create a comparison that returns True if either
        :math:`\textrm{rel_diff}(a, b) \leq \textit{rel_tol}` or
        :math:`\textrm{rel_diff}(a, b) \leq \textit{abs_tol}`

    :param abs_tol: absolute tolerance
    :param rel_tol: relative tolerance
    :return: function that returns True if either the relative difference is
             less than rel_tol or absolute difference is less than abs_tol
    """

    def is_equal(a: float, b: float) -> bool:
        mx = max(abs(a), abs(b))
        delta = abs(a - b)
        return delta <= max(abs_tol, rel_tol * mx)

    return is_equal


def make_seq_equals(equals_func: Callable[[float, float], bool]) -> \
        Callable[[Sequence[float], Sequence[float]], bool]:
    r"""
    Create a comparison function that compares corresponding elements of two
    sequences.  Two sequences are considered equal if they have the same
    length, and :math:`\textrm{equals_func}(a_i, b_i) \textrm{ is true for
    all }
    i=0,..., n`

    :param equals_func: function that compares two elements of a sequence

    :return: comparison function
    """

    def _(a: Sequence[float], b: Sequence[float]) -> bool:
        if len(a) != len(b):
            return False
        for i in range(len(a)):
            if not equals_func(a[i], b[i]):
                return False
        return True

    return _
