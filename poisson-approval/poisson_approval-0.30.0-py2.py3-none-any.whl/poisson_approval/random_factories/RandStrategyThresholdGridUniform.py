import numpy as np
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.Util import initialize_random_seeds, my_division


class RandStrategyThresholdGridUniform:
    """A random factory of threshold strategies (:class:`StrategyThreshold`), uniform on a grid.

    Parameters
    ----------
    denominator_threshold : int
        The grain of the grid for the utility thresholds.
    denominator_ratio_optimistic : int, optional
        The grain of the grid for the ratios of optimistic voters.
    profile : Profile, optional
        The attached profile.
    voting_rule : str, optional
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.
    d_ranking_fixed_strategy : dict
        Key: ranking. Value: fixed strategy. Cf. examples below.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_strategy = RandStrategyThresholdGridUniform(denominator_threshold=7)
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: utility-dependent (4/7), acb: a, bac: utility-dependent (5/7), bca: bc, cab: utility-dependent (3/7), \
cba: utility-dependent (3/7)>

    Specify a profile:

        >>> from poisson_approval import ProfileHistogram
        >>> profile = ProfileHistogram({'abc': 0.75, 'bac': 0.25}, {'abc': [1], 'bac': [1]})
        >>> rand_strategy = RandStrategyThresholdGridUniform(denominator_threshold=7, profile=profile)
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: utility-dependent (3/7), bac: b> ==> a

    Specify some fixed strategies:

        >>> from fractions import Fraction
        >>> rand_strategy = RandStrategyThresholdGridUniform(
        ...     denominator_threshold=7, denominator_ratio_optimistic=17,
        ...     d_ranking_fixed_strategy={'abc': 1, 'acb': 1, 'bac': 1, 'bca': (Fraction(1, 2), Fraction(1, 2))})
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: utility-dependent (1/2, 1/2), cab: utility-dependent (1/7, 4/17), cba: c>
    """

    def __init__(self, denominator_threshold, denominator_ratio_optimistic=None, profile=None, voting_rule=None,
                 d_ranking_fixed_strategy=None):
        # Default parameters
        if d_ranking_fixed_strategy is None:
            d_ranking_fixed_strategy = dict()
        # Parameters
        self.denominator_threshold = denominator_threshold
        self.denominator_ratio_optimistic = denominator_ratio_optimistic
        self.profile = profile
        # noinspection PyProtectedMember
        self.voting_rule = Strategy._get_voting_rule_(profile, voting_rule)
        self.d_ranking_fixed_strategy = d_ranking_fixed_strategy

        # Computed variables
        self.rankings_to_decide = RANKINGS if self.profile is None else self.profile.support_in_rankings
        self.rankings_to_decide = sorted(self.rankings_to_decide - self.d_ranking_fixed_strategy.keys())
        self.n_rankings_to_decide = len(self.rankings_to_decide)

    def __call__(self):
        if self.denominator_ratio_optimistic is None:
            d = {ranking: my_division(np.random.randint(0, self.denominator_threshold + 1),
                                      self.denominator_threshold)
                 for ranking in self.rankings_to_decide}
        else:
            d = {ranking: (my_division(np.random.randint(0, self.denominator_threshold + 1),
                                       self.denominator_threshold),
                           my_division(np.random.randint(0, self.denominator_ratio_optimistic + 1),
                                       self.denominator_ratio_optimistic))
                 for ranking in self.rankings_to_decide}
        d.update(self.d_ranking_fixed_strategy)
        return StrategyThreshold(d, profile=self.profile, voting_rule=self.voting_rule)
