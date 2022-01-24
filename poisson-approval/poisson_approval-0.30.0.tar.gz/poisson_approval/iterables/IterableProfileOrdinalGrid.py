from poisson_approval.constants.basic_constants import *
from poisson_approval.iterables.IterableSimplexGrid import IterableSimplexGrid
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal


class IterableProfileOrdinalGrid:
    """Iterate over ordinal profiles (:class:`ProfileOrdinal`) defined on a grid.

    Parameters
    ----------
    denominator : int or iterable
        The grain(s) of the grid.
    orders : iterable, optional
        These orders will have a variable share. They can be rankings, e.g. ``'abc'``, or weak orders, e.g.
        ``'a~b>c'``. Default: all rankings.
    d_order_fixed_share : dict, optional
        A dictionary. For each entry ``order: fixed_share``, this order will have at least this fixed share. The total
        must be lower or equal to 1.
    standardized : bool, optional
        If True, then only standardized profiles are given. Cf. :meth:`Profile.is_standardized`. You should
        probably use this option if the arguments `orders`, `d_order_fixed_share` and `test` treat the candidates
        symmetrically.
    test : callable, optional
        A function ``ProfileOrdinal -> bool``. Only profiles meeting this test are given.
    kwargs
        Additional parameters are passed to :class:`ProfileOrdinal` when creating the profile.

    Examples
    --------
    Basic usage:

        >>> for profile in IterableProfileOrdinalGrid(denominator=3, standardized=True):
        ...     print(profile)
        <abc: 1> (Condorcet winner: a)
        <abc: 2/3, acb: 1/3> (Condorcet winner: a)
        <abc: 2/3, bac: 1/3> (Condorcet winner: a)
        <abc: 2/3, bca: 1/3> (Condorcet winner: a)
        <abc: 2/3, cab: 1/3> (Condorcet winner: a)
        <abc: 2/3, cba: 1/3> (Condorcet winner: a)
        <abc: 1/3, acb: 1/3, bac: 1/3> (Condorcet winner: a)
        <abc: 1/3, acb: 1/3, bca: 1/3> (Condorcet winner: a)
        <abc: 1/3, bac: 1/3, cab: 1/3> (Condorcet winner: a)
        <abc: 1/3, bca: 1/3, cab: 1/3>

    For more examples, cf. :class:`IterableSimplexGrid`.
    """
    def __init__(self, denominator, orders=None, d_order_fixed_share=None, standardized=False, test=None, **kwargs):
        if orders is None:
            orders = RANKINGS
        self.standardized = standardized
        self._base_iterator = IterableSimplexGrid(cls=ProfileOrdinal, denominator=denominator, keys=orders,
                                                  d_key_fixed_share=d_order_fixed_share, test=test, **kwargs)

    def __iter__(self):
        return (profile for profile in self._base_iterator
                if not self.standardized or profile.is_standardized)
