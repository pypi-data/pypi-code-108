import math
import numpy as np
import sympy as sp
from fractions import Fraction
from poisson_approval.utils.ComputationEngine import ComputationEngine


class ComputationEngineNumeric(ComputationEngine):
    """Computation engine: numeric computation.

    This engine performs numeric computation, using floats when necessary:

        >>> ce = ComputationEngineNumeric
        >>> ce.inf
        inf
        >>> ce.nan
        nan
        >>> ce.exp(3)
        20.085536923187668
        >>> ce.log(3)
        1.0986122886681098
        >>> ce.Rational(1, 3)
        Fraction(1, 3)
        >>> ce.S(1) / 3
        0.3333333333333333
        >>> ce.simplify(- ce.Rational(1, 10) - (- ce.sqrt(15) / 5 + ce.sqrt(30) / 10)**2)
        -0.151471862576143
        >>> ce.sqrt(3)
        1.7320508075688772

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
        True
"""

    # Constants

    inf = np.inf
    nan = np.nan
    pi = math.pi

    # Functions

    @classmethod
    def barycenter(cls, a, b, ratio_b):
        """Barycenter.

        Parameters
        ----------
        a : Number
        b : Number or iterable
        ratio_b : Number or iterable
            The ratio of `b` in the result. If an iterable, must be the same size as `b`.

        Returns
        -------
        Number
            The result of `(1 - ratio_b) * a + ratio_b * b`. The added value of this function is to preserve the type
            of `a` (resp. `b`) when `ratio_b` is 0 (resp. 1). If `b` and `ratio_b` are iterable, return
            `(1 - sum(ratio_b)) * a + sum(ratio_b * b)`.

        Examples
        --------
        In this first example, `barycenter` preserves the type Fraction, whereas a naive computation returns a float:

            >>> from fractions import Fraction
            >>> a, b = Fraction(1, 10), 0.7
            >>> ratio_b = 0
            >>> ComputationEngineNumeric.barycenter(a, b, ratio_b)
            Fraction(1, 10)
            >>> (1 - ratio_b) * a + ratio_b * b
            0.1

        The second example is symmetric of the first one, in the sense that it preserves the type of `b`:

            >>> a, b = 0.7, 42
            >>> ratio_b = 1
            >>> ComputationEngineNumeric.barycenter(a, b, ratio_b)
            42
            >>> (1 - ratio_b) * a + ratio_b * b
            42.0

        In the following example, `b` and `ratio_b` are iterables:

            >>> a = 0
            >>> b = [-1 , 1]
            >>> ComputationEngineNumeric.barycenter(0, [-1, 1], [Fraction(2, 10), Fraction(3, 10)])
            Fraction(1, 10)
        """
        return super().barycenter(a, b, ratio_b)

    @classmethod
    def exp(cls, x):
        return math.exp(x)

    @classmethod
    def factorial(cls, x):
        return math.factorial(x)

    @classmethod
    def log(cls, x):
        return math.log(x)

    @classmethod
    def Rational(cls, x, y):
        return Fraction(x, y)

    @classmethod
    def S(cls, x):
        return x

    @classmethod
    def simplify(cls, x):
        if isinstance(x, Fraction) and x.denominator == 1:
            return x.numerator
        else:
            return x

    @classmethod
    def sqrt(cls, x):
        return math.sqrt(x)
