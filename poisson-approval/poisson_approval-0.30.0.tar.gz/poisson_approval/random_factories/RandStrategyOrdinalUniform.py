import random
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyOrdinal import StrategyOrdinal
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.utils.UtilBallots import ballot_low_u, ballot_high_u


class RandStrategyOrdinalUniform:
    """A random factory of ordinal strategies (:class:`StrategyOrdinal`) following the uniform distribution.

    Parameters
    ----------
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
        >>> rand_strategy = RandStrategyOrdinalUniform()
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: ab, acb: ac, bac: b, bca: bc, cab: ac, cba: bc>

    Specify a profile:

        >>> from poisson_approval import ProfileOrdinal
        >>> profile = ProfileOrdinal({'abc': 0.75, 'bac': 0.25})
        >>> rand_strategy = RandStrategyOrdinalUniform(profile=profile)
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: ab, bac: ab> ==> a, b

    Specify some fixed strategies:

        >>> rand_strategy = RandStrategyOrdinalUniform(
        ...     d_ranking_fixed_strategy={'abc': 'a', 'acb': 'a', 'bac': 'b', 'bca': 'b'})
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: c>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: bc>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: c>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: ac, cba: bc>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: b, cab: c, cba: c>
    """

    def __init__(self, profile=None, voting_rule=None, d_ranking_fixed_strategy=None):
        # Default parameters
        if d_ranking_fixed_strategy is None:
            d_ranking_fixed_strategy = dict()
        # Parameters
        self.profile = profile
        # noinspection PyProtectedMember
        self.voting_rule = Strategy._get_voting_rule_(profile, voting_rule)
        self.d_ranking_fixed_strategy = d_ranking_fixed_strategy

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

    def __call__(self):
        return StrategyOrdinal(
            d_ranking_ballot={ranking: random.choice(possible_ballots)
                              for ranking, possible_ballots in self.d_ranking_possible_ballots.items()},
            profile=self.profile,
            voting_rule=self.voting_rule
        )
