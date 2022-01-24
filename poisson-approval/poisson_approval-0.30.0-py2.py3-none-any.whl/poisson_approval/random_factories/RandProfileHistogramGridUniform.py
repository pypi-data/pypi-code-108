from poisson_approval.constants.basic_constants import *
from poisson_approval.random_factories.RandSimplexGridUniform import RandSimplexGridUniform
from poisson_approval.utils.Util import initialize_random_seeds, rand_simplex_grid
from poisson_approval.profiles.ProfileOrdinal import ProfileOrdinal
from poisson_approval.profiles.ProfileHistogram import ProfileHistogram


class RandProfileHistogramGridUniform(RandSimplexGridUniform):
    """A random factory of histogram profiles (:class:`ProfileHistogram`), uniform on a grid.

    Parameters
    ----------
    denominator : int
        The grain of the grid for the shares of the rankings.
    denominator_bins : int
        The grain of the grid for the bins.
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
        >>> rand_profile = RandProfileHistogramGridUniform(denominator=17, denominator_bins=7, n_bins=3)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 1/17 [Fraction(2, 7) 0 Fraction(5, 7)], \
acb: 8/17 [Fraction(1, 7) Fraction(2, 7) Fraction(4, 7)], \
bac: 2/17 [Fraction(2, 7) Fraction(1, 7) Fraction(4, 7)], \
cab: 5/17 [Fraction(1, 7) Fraction(6, 7) 0], \
cba: 1/17 [Fraction(3, 7) Fraction(4, 7) 0]> (Condorcet winner: a)

    Using the optional parameters:

        >>> from fractions import Fraction
        >>> rand_profile = RandProfileHistogramGridUniform(
        ...     denominator=17, denominator_bins=7,
        ...     n_bins=3, orders=['abc', 'a~b>c'], d_order_fixed_share={'b>a~c': Fraction(1, 2)},
        ...     voting_rule=PLURALITY)
        >>> profile = rand_profile()
        >>> print(profile)
        <abc: 1/2 [Fraction(6, 7) Fraction(1, 7) 0], b>a~c: 1/2> (Condorcet winner: a, b) (Plurality)
    """

    def __init__(self, denominator, denominator_bins, n_bins, orders=None, d_order_fixed_share=None, **kwargs):
        if orders is None:
            orders = RANKINGS
        self.denominator = denominator
        self.denominator_bins = denominator_bins
        self.n_bins = n_bins
        self.kwargs_histogram = kwargs
        super().__init__(cls=ProfileOrdinal, denominator=denominator, keys=orders,
                         d_key_fixed_share=d_order_fixed_share)

    def __call__(self):
        profile_ordinal = super().__call__()
        d_ranking_histogram = {}
        for ranking in sorted(profile_ordinal.support_in_rankings):
            d_ranking_histogram[ranking] = rand_simplex_grid(d=self.n_bins, denominator=self.denominator_bins)
        return ProfileHistogram(d_ranking_share=profile_ordinal.d_ranking_share,
                                d_ranking_histogram=d_ranking_histogram,
                                d_weak_order_share=profile_ordinal.d_weak_order_share,
                                **self.kwargs_histogram)
