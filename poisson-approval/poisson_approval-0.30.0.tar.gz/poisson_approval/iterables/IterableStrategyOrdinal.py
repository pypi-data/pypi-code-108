from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyOrdinal import StrategyOrdinal
from poisson_approval.utils.Util import product_dict
from poisson_approval.utils.UtilBallots import ballot_low_u, ballot_high_u


class IterableStrategyOrdinal:
    """Iterate over ordinal strategies (:class:`StrategyOrdinal`).

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
        A function ``StrategyOrdinal -> bool``. Only strategies meeting this test are given.

    Examples
    --------
    Basic usage:

        >>> for strategy in IterableStrategyOrdinal():  # doctest: +ELLIPSIS
        ...     print(strategy)
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: bc>
        ...
        <abc: ab, acb: ac, bac: ab, bca: bc, cab: ac, cba: bc>

    Specify a profile:

        >>> from poisson_approval import ProfileOrdinal
        >>> profile = ProfileOrdinal({'abc': 0.75, 'bac': 0.25})
        >>> for strategy in IterableStrategyOrdinal(profile=profile):
        ...     print(strategy)
        <abc: a, bac: b> ==> a
        <abc: a, bac: ab> ==> a
        <abc: ab, bac: b> ==> b
        <abc: ab, bac: ab> ==> a, b

    Specify some fixed strategies:

        >>> iterable = IterableStrategyOrdinal(
        ...     d_ranking_fixed_strategy={'abc': 'a', 'acb': 'a', 'bac': 'b', 'bca': 'b'})
        >>> for strategy in iterable:
        ...     print(strategy)
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: bc>
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: c>
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: bc>

    Use a condition with the parameter `test`:

        >>> profile = ProfileOrdinal({'abc': 0.75, 'bac': 0.25})
        >>> def test_a_wins(strategy):
        ...     return strategy.winners == {'a'}
        >>> for strategy in IterableStrategyOrdinal(profile=profile, test=test_a_wins):
        ...     print(strategy)
        <abc: a, bac: b> ==> a
        <abc: a, bac: ab> ==> a
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
            if self.profile is not None and self.profile.d_ranking_share[ranking] == 0:
                return ['']
            return [ballot_low_u(ranking, self.voting_rule), ballot_high_u(ranking, self.voting_rule)]

        self.d_ranking_possible_ballots = {ranking: possible_ballots(ranking) for ranking in RANKINGS}

    def __iter__(self):
        for d_ranking_ballot in product_dict(self.d_ranking_possible_ballots):
            strategy = StrategyOrdinal(d_ranking_ballot, profile=self.profile, voting_rule=self.voting_rule)
            if self.test is None or self.test(strategy):
                yield strategy
