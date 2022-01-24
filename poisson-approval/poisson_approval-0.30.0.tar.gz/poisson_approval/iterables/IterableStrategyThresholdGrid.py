from itertools import product
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.Util import my_division


class IterableStrategyThresholdGrid:
    """Iterate over threshold strategies (:class:`StrategyThreshold`).

    Parameters
    ----------
    denominator_threshold : int or iterable
        The grain(s) of the grid for the utility thresholds.
    denominator_ratio_optimistic : int or iterable, optional
        The grain(s) of the grid for the ratios of optimistic voters.
    profile : Profile, optional
        The attached profile.
    voting_rule : str, optional
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.
    d_ranking_fixed_strategy : dict
        Key: ranking. Value: fixed strategy. Cf. examples below.
    test : callable
        A function ``StrategyThreshold -> bool``. Only strategies meeting this test are given.
    kwargs
        Additional parameters are passed to :class:`StrategyThreshold` when creating the strategy.

    Examples
    --------
    Basic usage:

        >>> for strategy in IterableStrategyThresholdGrid(denominator_threshold=3):  # doctest: +ELLIPSIS
        ...     print(strategy)
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: ac, cba: bc>
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: ac, cba: utility-dependent (1/3)>
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: ac, cba: utility-dependent (2/3)>
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: ac, cba: c>
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: utility-dependent (1/3), cba: bc>
        ...
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>

    Specify a profile:

        >>> from poisson_approval import ProfileHistogram
        >>> profile = ProfileHistogram({'abc': 0.75, 'bac': 0.25}, {'abc': [1], 'bac': [1]})
        >>> for strategy in IterableStrategyThresholdGrid(denominator_threshold=2, profile=profile):
        ...     print(strategy)
        <abc: ab, bac: ab> ==> a, b
        <abc: ab, bac: utility-dependent (1/2)> ==> b
        <abc: ab, bac: b> ==> b
        <abc: utility-dependent (1/2), bac: ab> ==> a
        <abc: utility-dependent (1/2), bac: utility-dependent (1/2)> ==> a
        <abc: utility-dependent (1/2), bac: b> ==> a
        <abc: a, bac: ab> ==> a
        <abc: a, bac: utility-dependent (1/2)> ==> a
        <abc: a, bac: b> ==> a

    Specify some fixed strategies:

        >>> iterable = IterableStrategyThresholdGrid(
        ...     denominator_threshold=2,
        ...     d_ranking_fixed_strategy={'abc': 1, 'acb': 1, 'bac': 1, 'bca': 1})
        >>> for strategy in iterable:
        ...     print(strategy)
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: bc>
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: utility-dependent (1/2)>
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: utility-dependent (1/2), cba: bc>
        <abc: a, acb: a, bac: b, bca: b, cab: utility-dependent (1/2), cba: utility-dependent (1/2)>
        <abc: a, acb: a, bac: b, bca: b, cab: utility-dependent (1/2), cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: bc>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: utility-dependent (1/2)>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>

    Use a condition with the parameter `test`:

        >>> profile = ProfileHistogram({'abc': 0.75, 'bac': 0.25}, {'abc': [1], 'bac': [1]})
        >>> def test_a_wins(strategy):
        ...     return strategy.winners == {'a'}
        >>> for strategy in IterableStrategyThresholdGrid(denominator_threshold=2, profile=profile, test=test_a_wins):
        ...     print(strategy)
        <abc: utility-dependent (1/2), bac: ab> ==> a
        <abc: utility-dependent (1/2), bac: utility-dependent (1/2)> ==> a
        <abc: utility-dependent (1/2), bac: b> ==> a
        <abc: a, bac: ab> ==> a
        <abc: a, bac: utility-dependent (1/2)> ==> a
        <abc: a, bac: b> ==> a

    Loop also over the ratios of optimistic voters:

        >>> from poisson_approval import ProfileDiscrete
        >>> profile = ProfileDiscrete({('abc', 0.2): 0.75, ('bac', 0.4): 0.25})
        >>> iterable = IterableStrategyThresholdGrid(denominator_threshold=2, denominator_ratio_optimistic=2,
        ...                                          profile=profile)
        >>> for strategy in iterable:  # doctest: +ELLIPSIS
        ...     print(repr(strategy))
        StrategyThreshold({'abc': 0, 'bac': 0})
        StrategyThreshold({'abc': 0, 'bac': (Fraction(1, 2), 0)})
        StrategyThreshold({'abc': 0, 'bac': (Fraction(1, 2), Fraction(1, 2))})
        StrategyThreshold({'abc': 0, 'bac': (Fraction(1, 2), 1)})
        StrategyThreshold({'abc': 0, 'bac': 1})
        StrategyThreshold({'abc': (Fraction(1, 2), 0), 'bac': 0})
        ...
        StrategyThreshold({'abc': 1, 'bac': 1})
    """

    def __init__(self, denominator_threshold, denominator_ratio_optimistic=None, profile=None, voting_rule=None,
                 d_ranking_fixed_strategy=None, test=None, **kwargs):
        """
        We can use an iterable for `denominator_threshold` and `denominator_ratio_optimistic`:

            >>> from poisson_approval import ProfileDiscrete
            >>> profile = ProfileDiscrete({('abc', 0.2): 0.75})
            >>> iterable = IterableStrategyThresholdGrid(denominator_threshold=[2, 3],
            ...                                          denominator_ratio_optimistic=[2],
            ...                                          profile=profile)
            >>> for strategy in iterable:
            ...     print(repr(strategy))
            StrategyThreshold({'abc': 0})
            StrategyThreshold({'abc': (Fraction(1, 2), 0)})
            StrategyThreshold({'abc': (Fraction(1, 2), Fraction(1, 2))})
            StrategyThreshold({'abc': (Fraction(1, 2), 1)})
            StrategyThreshold({'abc': 1})
            StrategyThreshold({'abc': 0})
            StrategyThreshold({'abc': (Fraction(1, 3), 0)})
            StrategyThreshold({'abc': (Fraction(1, 3), Fraction(1, 2))})
            StrategyThreshold({'abc': (Fraction(1, 3), 1)})
            StrategyThreshold({'abc': (Fraction(2, 3), 0)})
            StrategyThreshold({'abc': (Fraction(2, 3), Fraction(1, 2))})
            StrategyThreshold({'abc': (Fraction(2, 3), 1)})
            StrategyThreshold({'abc': 1})
        """
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
        self.test = test
        self.kwargs = kwargs
        # Computed variables
        if isinstance(self.denominator_threshold, int):
            self.denominators_threshold = [self.denominator_threshold]
        else:
            self.denominators_threshold = self.denominator_threshold
        if isinstance(self.denominator_ratio_optimistic, int) or self.denominator_ratio_optimistic is None:
            self.denominators_ratio = [self.denominator_ratio_optimistic]
        else:
            self.denominators_ratio = self.denominator_ratio_optimistic
        self.rankings_to_decide = RANKINGS if self.profile is None else self.profile.support_in_rankings
        self.rankings_to_decide = sorted(self.rankings_to_decide - self.d_ranking_fixed_strategy.keys())
        self.n_rankings_to_decide = len(self.rankings_to_decide)

    def __iter__(self):
        for denominator_t in self.denominators_threshold:
            for denominator_r in self.denominators_ratio:
                for tuple_thresholds in product(range(denominator_t + 1), repeat=self.n_rankings_to_decide):
                    if denominator_r is None:
                        d = {ranking: (my_division(threshold, denominator_t))
                             for ranking, threshold
                             in zip(self.rankings_to_decide, tuple_thresholds)}
                        d.update(self.d_ranking_fixed_strategy)
                        strategy = StrategyThreshold(d, profile=self.profile, voting_rule=self.voting_rule,
                                                     **self.kwargs)
                        if self.test is None or self.test(strategy):
                            yield strategy
                    else:
                        iterables_ratios = []
                        for threshold in tuple_thresholds:
                            if threshold in {0, denominator_t}:
                                iterables_ratios.append([None])
                            else:
                                iterables_ratios.append(range(denominator_r + 1))
                        for tuple_ratios in product(*iterables_ratios):
                            d = {ranking: (my_division(threshold, denominator_t),
                                           None if ratio is None else my_division(ratio, denominator_r))
                                 for ranking, threshold, ratio
                                 in zip(self.rankings_to_decide, tuple_thresholds, tuple_ratios)}
                            d.update(self.d_ranking_fixed_strategy)
                            strategy = StrategyThreshold(d, profile=self.profile, voting_rule=self.voting_rule,
                                                         **self.kwargs)
                            if self.test is None or self.test(strategy):
                                yield strategy
