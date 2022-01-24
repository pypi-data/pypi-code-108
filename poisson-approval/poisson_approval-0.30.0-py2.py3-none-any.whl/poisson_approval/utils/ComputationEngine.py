import math
import numpy as np
from abc import ABC, abstractmethod


# noinspection PyPropertyDefinition,PyNestedDecorators
class ComputationEngine(ABC):
    """Computation engine.

    Define how some mathematical operations are performed. Cf. :class:`ComputationEngineSymbolic` and
    :class:`ComputationEngineNumeric` for some examples.
    """

    # Constants

    inf = None
    """Positive infinity."""

    nan = None
    """Not a Number."""

    pi = None
    """Pi."""

    # Functions

    @classmethod
    def barycenter(cls, a, b, ratio_b):
        """Barycenter.

        Cf. :meth:`ComputationEngineNumeric.barycenter` for specifications and examples.
        """
        try:
            # b and ratio_b are numbers
            return cls.multiply_with_absorbing_zero(1 - ratio_b, a) + cls.multiply_with_absorbing_zero(ratio_b, b)
        except TypeError:
            # b and ratio_b are iterables
            ratio_a = 1 - sum(ratio_b)
            return cls.multiply_with_absorbing_zero(ratio_a, a) + sum([
                cls.multiply_with_absorbing_zero(r, x) for r, x in zip(b, ratio_b)])

    @classmethod
    @abstractmethod
    def exp(cls, x):
        """Exponential.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def factorial(cls, x):
        """Factorial.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def log(cls, x):
        """Logarithm.
        """
        raise NotImplementedError

    @classmethod
    def look_equal(cls, x, y, *args, **kwargs):
        """Test if two numbers can reasonably be considered as equal.

        Parameters
        ----------
        x,y : Number
        *args
            Cf. ``math.isclose``.
        **kwargs
            Cf. ``math.isclose``.

        Returns
        -------
        bool
            If `x` or `y` is a float or `numpy` float (but not a `sympy` float), then return
            ``math.isclose(x, y, *args, **kwargs)``. In all other cases, return True iff `x` is equal to `y`.
        """
        if isinstance(x, float) or isinstance(y, float):
            return math.isclose(x, y, *args, **kwargs)
        else:
            return cls.simplify(x - y) == 0

    @classmethod
    def multiply_with_absorbing_zero(cls, x, y):
        """Multiplication with absorbing zero.

        Parameters
        ----------
        x,y : Number

        Returns
        -------
        Number
            If `x` or `y` is 0, then 0 (even if the other input is `nan`). Otherwise, the product
            of `x` and `y`.
        """
        x = cls.simplify(x)
        y = cls.simplify(y)
        return cls.S(0) if x == 0 or y == 0 else x * y

    @classmethod
    def ones(cls, *args, **kwargs):
        """Array of ones.
        """
        return np.ones(*args, **kwargs, dtype=int)

    # noinspection PyPep8Naming
    @classmethod
    @abstractmethod
    def Rational(cls, x, y):
        """Rational number. Should return a fraction, even in a numeric engine.
        """
        raise NotImplementedError

    # noinspection PyPep8Naming
    @classmethod
    @abstractmethod
    def S(cls, x):
        """Convert the number if necessary.

        Return a number that has the same value as `x`. Cf. function ``S`` of the package `sympy`.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def simplify(cls, x):
        """Simplify the number if necessary.

        Return a number that has the same value as `x`. Cf. function ``simplify`` of the package `sympy`.
        """
        raise NotImplementedError

    @classmethod
    def simplify_vector(cls, x):
        """Simplify the coefficients if necessary.
        """
        return np.array([cls.simplify(value) for value in x])

    @classmethod
    @abstractmethod
    def sqrt(cls, x):
        """Square root.
        """
        raise NotImplementedError

    @classmethod
    def zeros(cls, *args, **kwargs):
        """Array of zeros.
        """
        return np.zeros(*args, **kwargs, dtype=int)
