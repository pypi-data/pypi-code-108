from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal


class RandProfileOrdinalUniform(RandSimplexUniform):
    """A random factory of ordinal profiles (:class:`ProfileOrdinal`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_profile = RandProfileOrdinalUniform()
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 0.4236547993389047, acb: 0.12122838365799216, bac: 0.0039303209304278885, bca: 0.05394987214431912, \
cab: 0.1124259903007756, cba: 0.2848106336275805> (Condorcet winner: a)

    Using the optional parameters:

        >>> rand_profile = RandProfileOrdinalUniform(
        ...     orders=['abc', 'acb'], d_order_fixed_share={'acb': 0.8, 'a~b>c': 0.1},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 0.0645894113066656, acb: 0.8354105886933344, a~b>c: 0.1> (Condorcet winner: a) (Plurality)

    For more examples, cf. :class:`RandSimplexUniform`.
    """

    def __init__(self, orders=None, d_order_fixed_share=None, **kwargs):
        if orders is None:
            orders = RANKINGS
        super().__init__(cls=ProfileOrdinal, keys=orders, d_key_fixed_share=d_order_fixed_share, **kwargs)
