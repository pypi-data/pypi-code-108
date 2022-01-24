from poisson_approval.utils.Util import rand_simplex_grid, initialize_random_seeds
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder


class RandSimplexGridUniform:
    """A random factory of an object defined by shares on a discrete simplex.

    Parameters
    ----------
    cls : class
        The class of object we want to create. It must accept as parameter a dictionary of the form ``key: share``,
        where share is a number.
    denominator : int
        The grain of the grid.
    keys : iterable
        These keys will have a variable share.
    d_key_fixed_share : dict
        A dictionary. For each entry ``key: fixed_share``, this key will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        Additional parameters are passed to `cls` when creating the object.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_dict = RandSimplexGridUniform(cls=DictPrintingInOrder, denominator=7, keys=['a', 'b'])
        >>> rand_dict()
        {'a': Fraction(6, 7), 'b': Fraction(1, 7)}

    If `d_key_fixed_share` is given, then these shares are fixed, and the remaining share is split between `keys`:

        >>> from fractions import Fraction
        >>> initialize_random_seeds()
        >>> rand_dict = RandSimplexGridUniform(cls=DictPrintingInOrder, denominator=3, keys=['a', 'b'],
        ...                                    d_key_fixed_share={'c': Fraction(4, 7)})
        >>> rand_dict()
        {'a': Fraction(2, 7), 'b': Fraction(1, 7), 'c': Fraction(4, 7)}

    The keys in `d_fixed_share` may overlap with `keys`:

        >>> initialize_random_seeds()
        >>> rand_dict = RandSimplexGridUniform(cls=DictPrintingInOrder, denominator=3, keys=['a', 'b'],
        ...                                    d_key_fixed_share={'b': Fraction(4, 7)})
        >>> rand_dict()
        {'a': Fraction(2, 7), 'b': Fraction(5, 7)}

    If you want the created object to meet a particular condition, use :class:`RandConditional`.
    """

    def __init__(self, cls, denominator, keys, d_key_fixed_share=None, **kwargs):
        # Default values
        if d_key_fixed_share is None:
            d_key_fixed_share = dict()
        # Parameters
        self.cls = cls
        self.keys = keys
        self.denominator = denominator
        self.d_key_fixed_share = d_key_fixed_share
        self.kwargs = kwargs
        # Computed variables
        self.n_keys = len(self.keys)
        self.total_variable_share = 1 - sum(self.d_key_fixed_share.values())

    def __call__(self):
        x_simplex = rand_simplex_grid(d=self.n_keys, denominator=self.denominator) * self.total_variable_share
        d_key_share = dict(zip(self.keys, x_simplex))
        for key, fixed_share in self.d_key_fixed_share.items():
            d_key_share[key] = d_key_share.get(key, 0) + fixed_share
        return self.cls(d_key_share, **self.kwargs)
