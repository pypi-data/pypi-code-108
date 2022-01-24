import numpy as np
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.Util import initialize_random_seeds


class RandStrategyThresholdUniform:
    """A random factory of threshold strategies (:class:`StrategyThreshold`) following the uniform distribution.

    Parameters
    ----------
    profile : Profile, optional
        The attached profile.
    voting_rule : str, optional
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.
    d_ranking_fixed_strategy : dict
        Key: ranking. Value: fixed strategy. Cf. examples below.
    ratio_optimistic : Number, optional
        If specified, it will be applied to all voters, except those in `d_ranking_fixed_strategy`.
        If not specified, it depends on `profile`. If `profile` is specified and is an instance of
        :class:`ProfileCardinalContinuous`, then the ratios of optimistic voters are not mentioned in the strategy
        (because they are useless). In other cases, they are drawn at random.

    Examples
    --------
    Basic usage:

        >>> initialize_random_seeds()
        >>> rand_strategy = RandStrategyThresholdUniform()
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: utility-dependent (0.5488135039273248, 0.7151893663724195), \
acb: utility-dependent (0.6027633760716439, 0.5448831829968969), \
bac: utility-dependent (0.4236547993389047, 0.6458941130666561), \
bca: utility-dependent (0.4375872112626925, 0.8917730007820798), \
cab: utility-dependent (0.9636627605010293, 0.3834415188257777), \
cba: utility-dependent (0.7917250380826646, 0.5288949197529045)>

    Specify a profile:

        >>> from poisson_approval import ProfileHistogram
        >>> profile = ProfileHistogram({'abc': 0.75, 'bac': 0.25}, {'abc': [1], 'bac': [1]})
        >>> rand_strategy = RandStrategyThresholdUniform(profile=profile)
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: utility-dependent (0.5680445610939323), bac: utility-dependent (0.925596638292661)> ==> a

    Specify some fixed strategies:

        >>> rand_strategy = RandStrategyThresholdUniform(
        ...     d_ranking_fixed_strategy={'abc': 1, 'acb': 1, 'bac': 1, 'bca': (0.5, 0.5)})
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: utility-dependent (0.5, 0.5), \
cab: utility-dependent (0.07103605819788694, 0.08712929970154071), \
cba: utility-dependent (0.02021839744032572, 0.832619845547938)>

    Give the ratio of optimistic voters explicitly:

        >>> rand_strategy = RandStrategyThresholdUniform(
        ...     d_ranking_fixed_strategy={'abc': 1, 'acb': 1, 'bac': 1, 'bca': 1},
        ...     ratio_optimistic=0.42)
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: utility-dependent (0.7781567509498505, 0.42), \
cba: utility-dependent (0.8700121482468192, 0.42)>
    """

    def __init__(self, profile=None, voting_rule=None, d_ranking_fixed_strategy=None, ratio_optimistic=None):
        # Default parameters
        if d_ranking_fixed_strategy is None:
            d_ranking_fixed_strategy = dict()
        # Parameters
        self.profile = profile
        # noinspection PyProtectedMember
        self.voting_rule = Strategy._get_voting_rule_(profile, voting_rule)
        self.d_ranking_fixed_strategy = d_ranking_fixed_strategy
        self.ratio_optimistic = ratio_optimistic

        # Computed variables
        self.rankings_to_decide = RANKINGS if self.profile is None else self.profile.support_in_rankings
        self.rankings_to_decide = sorted(self.rankings_to_decide - self.d_ranking_fixed_strategy.keys())
        self.n_rankings_to_decide = len(self.rankings_to_decide)

    def __call__(self):
        if self.ratio_optimistic is None:
            if self.profile is not None and self.profile.is_continuous:
                d = {ranking: np.random.rand() for ranking in self.rankings_to_decide}
            else:
                d = {ranking: (np.random.rand(), np.random.rand()) for ranking in self.rankings_to_decide}
        else:
            d = {ranking: (np.random.rand(), self.ratio_optimistic) for ranking in self.rankings_to_decide}
        d.update(self.d_ranking_fixed_strategy)
        return StrategyThreshold(d, profile=self.profile, voting_rule=self.voting_rule)
