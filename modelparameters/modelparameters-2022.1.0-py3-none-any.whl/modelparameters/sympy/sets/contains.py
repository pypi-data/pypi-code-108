from __future__ import print_function, division

from ..core import Basic
from ..logic.boolalg import BooleanFunction


class Contains(BooleanFunction):
    """
    Asserts that x is an element of the set S

    Examples
    ========

    >>> from .. import Symbol, Integer, S
    >>> from .contains import Contains
    >>> Contains(Integer(2), S.Integers)
    True
    >>> Contains(Integer(-2), S.Naturals)
    False
    >>> i = Symbol('i', integer=True)
    >>> Contains(i, S.Naturals)
    Contains(i, S.Naturals)

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Element_%28mathematics%29
    """
    @classmethod
    def eval(cls, x, S):
        from .sets import Set

        if not isinstance(x, Basic):
            raise TypeError
        if not isinstance(S, Set):
            raise TypeError

        ret = S.contains(x)
        if not isinstance(ret, Contains):
            return ret
