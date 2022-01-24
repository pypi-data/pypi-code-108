import math
import numpy as np
import sympy as sp
from fractions import Fraction
from poisson_approval.utils.ComputationEngine import ComputationEngine


class ComputationEngineSymbolic(ComputationEngine):
    """Computation engine: symbolic computation.

    This engine relies on the external package `sympy` in order to perform symbolic computation:

        >>> ce = ComputationEngineSymbolic
        >>> ce.inf
        oo
        >>> ce.nan
        nan
        >>> ce.exp(3)
        exp(3)
        >>> ce.log(3)
        log(3)
        >>> ce.Rational(1, 3)
        1/3
        >>> ce.S(1) / 3
        1/3
        >>> ce.simplify(- ce.Rational(1, 10) - (- ce.sqrt(15) / 5 + ce.sqrt(30) / 10)**2)
        -1 + 3*sqrt(2)/5
        >>> ce.sqrt(3)
        sqrt(3)

    Usage of :meth:`look_equal`:

        >>> ce.look_equal(1, 0.999999999999)
        True
        >>> ce.look_equal(1, np.float(0.999999999999))
        True
        >>> ce.look_equal(1, sp.Float(0.999999999999))
        False
        >>> ce.look_equal(1, Fraction(999999999999, 1000000000000))
        False
        >>> ce.look_equal(ce.sqrt(2), ce.Rational(14142135623730951, 10000000000000000))
        False
    """

    # Constants

    inf = sp.oo
    nan = sp.nan
    pi = sp.pi

    # Functions

    @classmethod
    def exp(cls, x):
        return sp.exp(x)

    @classmethod
    def factorial(cls, x):
        return sp.factorial(x)

    @classmethod
    def log(cls, x):
        return sp.log(x)

    @classmethod
    def Rational(cls, x, y):
        return sp.Rational(x, y)

    @classmethod
    def S(cls, x):
        return sp.S(x)

    @classmethod
    def simplify(cls, x):
        return sp.simplify(x, ratio=1)

    @classmethod
    def sqrt(cls, x):
        return sp.sqrt(x)

