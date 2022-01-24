from poisson_approval.utils.Util import rand_simplex, initialize_random_seeds
from poisson_approval.utils.DictPrintingInOrder import DictPrintingInOrder


class RandSimplexUniform:
    """A random factory of an object defined by shares on the simplex.

    Parameters
    ----------
    cls : class
        The class of object we want to create. It must accept as parameter a dictionary of the form ``key: share``,
        where share is a number.
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
        >>> rand_dict = RandSimplexUniform(cls=DictPrintingInOrder, keys=['a', 'b'])
        >>> rand_dict()
        {'a': 0.5488135039273248, 'b': 0.45118649607267525}

    If `d_key_fixed_share` is given, then these shares are fixed, and the remaining share is split between `keys`:

        >>> initialize_random_seeds()
        >>> rand_dict = RandSimplexUniform(cls=DictPrintingInOrder, keys=['a', 'b'],
        ...                                d_key_fixed_share={'c': 0.5})
        >>> rand_dict()
        {'a': 0.2744067519636624, 'b': 0.22559324803633762, 'c': 0.5}

    The keys in `d_fixed_share` may overlap with `keys`:

        >>> initialize_random_seeds()
        >>> rand_dict = RandSimplexUniform(cls=DictPrintingInOrder, keys=['a', 'b'],
        ...                                d_key_fixed_share={'b': 0.5})
        >>> rand_dict()
        {'a': 0.2744067519636624, 'b': 0.7255932480363376}

    If you want the created object to meet a particular condition, use :class:`RandConditional`.
    """

    def __init__(self, cls, keys, d_key_fixed_share=None, **kwargs):
        # Default values
        if d_key_fixed_share is None:
            d_key_fixed_share = dict()
        # Parameters
        self.cls = cls
        self.keys = keys
        self.d_key_fixed_share = d_key_fixed_share
        self.kwargs = kwargs
        # Computed variables
        self.n_keys = len(keys)
        self.total_variable_share = 1 - sum(d_key_fixed_share.values())

    def __call__(self):
        x_simplex = rand_simplex(d=self.n_keys) * self.total_variable_share
        d_key_share = dict(zip(self.keys, x_simplex))
        for key, fixed_share in self.d_key_fixed_share.items():
            d_key_share[key] = d_key_share.get(key, 0) + fixed_share
        return self.cls(d_key_share, **self.kwargs)
