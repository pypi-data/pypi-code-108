import numpy as np
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder
from poisson_approval.utils.Util import iterate_simplex_grid


class IterableSimplexGrid:
    """Iterate over some objects defined by shares on a discrete simplex.

    Parameters
    ----------
    cls : class
        The class of object we want to create. It must accept as parameter a dictionary of the form ``key: share``,
        where share is a number.
    denominator : int or iterable
        The grain(s) of the grid.
    keys : iterable
        These keys will have a variable share.
    d_key_fixed_share : dict
        A dictionary. For each entry ``key: fixed_share``, this key will have at least this fixed share. The total
        must be lower or equal to 1.
    test : callable
        A function ``cls -> bool``.
    kwargs
        Additional parameters are passed to `cls` when creating the object.

    Examples
    --------
    Basic usage:

        >>> from fractions import Fraction
        >>> for d in IterableSimplexGrid(cls=DictPrintingInOrder, denominator=3, keys=['a', 'b']):
        ...     print(d)
        {a: 1, b: 0}
        {a: 2/3, b: 1/3}
        {a: 1/3, b: 2/3}
        {a: 0, b: 1}

    It is possible to specify an iterable of denominators:

        >>> from fractions import Fraction
        >>> for d in IterableSimplexGrid(cls=DictPrintingInOrder, denominator=range(2, 4), keys=['a', 'b']):
        ...     print(d)
        {a: 1, b: 0}
        {a: 1/2, b: 1/2}
        {a: 0, b: 1}
        {a: 1, b: 0}
        {a: 2/3, b: 1/3}
        {a: 1/3, b: 2/3}
        {a: 0, b: 1}

    If `d_key_fixed_share` is given, then these shares are fixed, and the remaining share is split between `keys`:

        >>> for d in IterableSimplexGrid(cls=DictPrintingInOrder, denominator=3, keys=['a', 'b'],
        ...                              d_key_fixed_share={'c': Fraction(1, 2)}):
        ...     print(d)
        {a: 1/2, b: 0, c: 1/2}
        {a: 1/3, b: 1/6, c: 1/2}
        {a: 1/6, b: 1/3, c: 1/2}
        {a: 0, b: 1/2, c: 1/2}

    The keys in `d_fixed_share` may overlap with `keys`:

        >>> for d in IterableSimplexGrid(cls=DictPrintingInOrder, denominator=3, keys=['a', 'b'],
        ...                              d_key_fixed_share={'b': Fraction(1, 2)}):
        ...     print(d)
        {a: 1/2, b: 1/2}
        {a: 1/3, b: 2/3}
        {a: 1/6, b: 5/6}
        {a: 0, b: 1}

    It is possible to add a condition with the parameter `test`:

        >>> def test_small_euclidean_norm(d):
        ...     return sum(x**2 for x in d.values()) < 0.6
        >>> for d in IterableSimplexGrid(cls=DictPrintingInOrder, denominator=11, keys=['a', 'b'],
        ...                              test=test_small_euclidean_norm):
        ...     print(d)
        {a: 7/11, b: 4/11}
        {a: 6/11, b: 5/11}
        {a: 5/11, b: 6/11}
        {a: 4/11, b: 7/11}
    """

    def __init__(self, cls, denominator, keys, d_key_fixed_share=None, test=None, **kwargs):
        # Default parameters
        if d_key_fixed_share is None:
            d_key_fixed_share = dict()
        # Parameters
        self.cls = cls
        self.denominator = denominator
        self.keys = keys
        self.d_key_fixed_share = d_key_fixed_share
        self.test = test
        self.kwargs = kwargs
        # Computed variables
        self.n_keys = len(keys)
        self.total_variable_share = 1 - sum(d_key_fixed_share.values())

    def __iter__(self):
        for x_simplex in iterate_simplex_grid(d=self.n_keys, denominator=self.denominator):
            x_simplex = np.array(x_simplex) * self.total_variable_share
            d_key_share = dict(zip(self.keys, x_simplex))
            for key, fixed_share in self.d_key_fixed_share.items():
                d_key_share[key] = d_key_share.get(key, 0) + fixed_share
            result = self.cls(d_key_share, **self.kwargs)
            if self.test is None or self.test(result):
                yield result
