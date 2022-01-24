from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexUniform import RandSimplexUniform
from poisson_approval.utils.Util import initialize_random_seeds, rand_simplex
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal
from poisson_approval.profiles.ProfileHistogram import ProfileHistogram


class RandProfileHistogramUniform(RandSimplexUniform):
    """A random factory of histogram profiles (:class:`ProfileHistogram`) following the uniform distribution.

    Parameters
    ----------
    n_bins : int
        The number of bins in each histogram. Cf. :class:`ProfileHistogram`.
    orders : list, optional
        These orders will have a variable share. They can be rankings, e.g. ``'abc'``, or weak orders, e.g.
        ``'a~b>c'``. Default: all rankings.
    d_order_fixed_share : dict, optional
        A dictionary. For each entry ``order: fixed_share``, this order will have at least this fixed share. The total
        must be lower or equal to 1.
    kwargs
        These additional arguments will be passed directly to :class:`ProfileHistogram`.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_profile = RandProfileHistogramUniform(n_bins=3)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 0.4236547993389047 [0.43758721 0.2083069  0.35410589], \
acb: 0.12122838365799216 [0.891773   0.07188976 0.03633724], \
bac: 0.0039303209304278885 [0.38344152 0.40828352 0.20827496], \
bca: 0.05394987214431912 [0.52889492 0.03914964 0.43195544], \
cab: 0.1124259903007756 [0.07103606 0.85456058 0.07440336], \
cba: 0.2848106336275805 [0.0202184 0.0669109 0.9128707]> (Condorcet winner: a)

    Using the optional parameters:

        >>> rand_profile = RandProfileHistogramUniform(
        ...     n_bins=3, orders=['abc', 'a~b>c'], d_order_fixed_share={'b>a~c': 0.5},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 0.416309922773969 [0.77815675 0.0918554  0.12998785], a~b>c: 0.083690077226031, b>a~c: 0.5> \
(Condorcet winner: b) (Plurality)
    """

    def __init__(self, n_bins, orders=None, d_order_fixed_share=None, **kwargs):
        if orders is None:
            orders = RANKINGS
        self.n_bins = n_bins
        self.kwargs_histogram = kwargs
        super().__init__(cls=ProfileOrdinal, keys=orders, d_key_fixed_share=d_order_fixed_share)

    def __call__(self):
        profile_ordinal = super().__call__()
        d_ranking_histogram = {}
        for ranking in sorted(profile_ordinal.support_in_rankings):
            d_ranking_histogram[ranking] = rand_simplex(d=self.n_bins)
        return ProfileHistogram(d_ranking_share=profile_ordinal.d_ranking_share,
                                d_ranking_histogram=d_ranking_histogram,
                                d_weak_order_share=profile_ordinal.d_weak_order_share,
                                **self.kwargs_histogram)
