from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal


class RandProfileOrdinalGridUniform(RandSimplexGridUniform):
    """A random factory of ordinal profiles (:class:`ProfileOrdinal`), uniform on a grid

    Parameters
    ----------
    denominator : int
        The grain of the grid.
    orders : list, optional
        These orders will have a variable share. They can be rankings, e.g. ``'abc'``, or weak orders, e.g.
        ``'a~b>c'``. Default: all rankings.
    d_order_fixed_share : dict, optional
        A dictionary. For each entry ``order: fixed_share``, this order will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`ProfileOrdinal`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileOrdinalGridUniform(denominator=7)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 2/7, acb: 1/7, bac: 1/7, bca: 3/7> (Condorcet winner: b)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_profile = RandProfileOrdinalGridUniform(
        ...     denominator=4,
        ...     orders=['abc', 'acb'], d_order_fixed_share={'acb': Fraction(2, 7), 'a~b>c': Fraction(1, 7)},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 3/7, acb: 3/7, a~b>c: 1/7> (Condorcet winner: a) (Plurality)

    For more examples, cf. :class:`RandSimplexGridUniform`.
    """

    def __init__(self, denominator, orders=None, d_order_fixed_share=None, **kwargs):
        if orders is None:
            orders = RANKINGS
        super().__init__(cls=ProfileOrdinal, denominator=denominator, keys=orders,
                         d_key_fixed_share=d_order_fixed_share, **kwargs)
