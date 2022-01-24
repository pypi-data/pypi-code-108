from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyTwelve import StrategyTwelve
from poisson_approval.utils.Util import product_dict
from poisson_approval.utils.UtilBallots import ballot_low_u, ballot_high_u


class IterableStrategyTwelve:
    """Iterate over twelve-type strategies (:class:`StrategyTwelve`).

    Parameters
    ----------
    profile : Profile, optional
        The attached profile.
    voting_rule : str, optional
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``. Default: the same
        voting rule as `profile` if a profile is specified, ``APPROVAL`` otherwise.
    d_ranking_fixed_strategy : dict
        Key: ranking. Value: fixed strategy. Cf. examples below.
    test : callable
        A function ``StrategyTwelve -> bool``. Only strategies meeting this test are given.

    Examples
    --------
    Basic usage:

        >>> for strategy in IterableStrategyTwelve():  # doctest: +ELLIPSIS
        ...     print(strategy)
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: bc>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: utility-dependent>
        ...
        <abc: utility-dependent, acb: utility-dependent, bac: utility-dependent, bca: utility-dependent, \
cab: utility-dependent, cba: utility-dependent>

    Specify a profile:

        >>> from poisson_approval import ProfileTwelve
        >>> profile = ProfileTwelve({'ab_c': 0.5, 'a_bc': 0.25, 'b_ac': 0.25})
        >>> for strategy in IterableStrategyTwelve(profile=profile):
        ...     print(strategy)
        <abc: a, bac: b> ==> a
        <abc: a, bac: ab> ==> a
        <abc: ab, bac: b> ==> b
        <abc: ab, bac: ab> ==> a, b
        <abc: utility-dependent, bac: b> ==> a, b
        <abc: utility-dependent, bac: ab> ==> a

    Specify some fixed strategies:

        >>> iterable = IterableStrategyTwelve(
        ...     d_ranking_fixed_strategy={'abc': 'a', 'acb': 'a', 'bac': 'b', 'bca': UTILITY_DEPENDENT})
        >>> for strategy in iterable:
        ...     print(strategy)
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: c, cba: c>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: c, cba: bc>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: c, cba: utility-dependent>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: ac, cba: c>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: ac, cba: bc>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: ac, cba: utility-dependent>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: utility-dependent, cba: c>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: utility-dependent, cba: bc>
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: utility-dependent, cba: utility-dependent>

    Use a condition with the parameter `test`:

        >>> profile = ProfileTwelve({'ab_c': 0.5, 'a_bc': 0.25, 'b_ac': 0.25})
        >>> def test_a_wins(strategy):
        ...     return strategy.winners == {'a'}
        >>> for strategy in IterableStrategyTwelve(profile=profile, test=test_a_wins):
        ...     print(strategy)
        <abc: a, bac: b> ==> a
        <abc: a, bac: ab> ==> a
        <abc: utility-dependent, bac: ab> ==> a
    """

    def __init__(self, profile=None, voting_rule=None, d_ranking_fixed_strategy=None, test=None):
        # Default parameters
        if d_ranking_fixed_strategy is None:
            d_ranking_fixed_strategy = dict()
        # Parameters
        self.profile = profile
        # noinspection PyProtectedMember
        self.voting_rule = Strategy._get_voting_rule_(profile, voting_rule)
        self.d_ranking_fixed_strategy = d_ranking_fixed_strategy
        self.test = test
        # Computed variables

        def possible_ballots(ranking):
            try:
                return [self.d_ranking_fixed_strategy[ranking]]
            except KeyError:
                pass
            if self.profile is not None:
                share_ranking_1 = self.profile.d_type_share[ranking[0] + '_' + ranking[1:]]
                share_ranking_12 = self.profile.d_type_share[ranking[0:2] + '_' + ranking[2]]
                strategy_1 = ballot_low_u(ranking, self.voting_rule)
                strategy_12 = ballot_high_u(ranking, self.voting_rule)
                if share_ranking_1 > 0 and share_ranking_12 > 0:
                    return [strategy_1, strategy_12, UTILITY_DEPENDENT]
                elif share_ranking_1 > 0 or share_ranking_12 > 0:
                    return [strategy_1, strategy_12]
                else:
                    return ['']
            else:
                return [ballot_low_u(ranking, self.voting_rule), ballot_high_u(ranking, self.voting_rule),
                        UTILITY_DEPENDENT]

        self.d_ranking_possible_ballots = {ranking: possible_ballots(ranking) for ranking in RANKINGS}

    def __iter__(self):
        for d_ranking_ballot in product_dict(self.d_ranking_possible_ballots):
            strategy = StrategyTwelve(d_ranking_ballot, profile=self.profile, voting_rule=self.voting_rule)
            if self.test is None or self.test(strategy):
                yield strategy
