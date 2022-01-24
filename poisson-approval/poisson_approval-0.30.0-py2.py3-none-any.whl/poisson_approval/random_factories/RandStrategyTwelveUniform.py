import random
from poisson_approval.constants.basic_constants import *
from poisson_approval.strategies.Strategy import Strategy
from poisson_approval.strategies.StrategyTwelve import StrategyTwelve
from poisson_approval.utils.Util import initialize_random_seeds
from poisson_approval.utils.UtilBallots import ballot_low_u, ballot_high_u


class RandStrategyTwelveUniform:
    """A random factory of twelve-type strategies (:class:`StrategyTwelve`) following the uniform distribution.

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
        >>> rand_strategy = RandStrategyTwelveUniform()
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: ab, acb: ac, bac: b, bca: bc, cab: utility-dependent, cba: bc>

    Specify a profile:

        >>> from poisson_approval import ProfileTwelve
        >>> profile = ProfileTwelve({'ab_c': 0.5, 'a_bc': 0.25, 'b_ac': 0.25})
        >>> rand_strategy = RandStrategyTwelveUniform(profile=profile)
        >>> strategy = rand_strategy()
        >>> print(strategy)
        <abc: ab, bac: ab> ==> a, b

    Specify some fixed strategies:

        >>> rand_strategy = RandStrategyTwelveUniform(
        ...     d_ranking_fixed_strategy={'abc': 'a', 'acb': 'a', 'bac': 'b', 'bca': UTILITY_DEPENDENT})
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: utility-dependent, cba: utility-dependent>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: utility-dependent, cba: bc>
        >>> print(rand_strategy())
        <abc: a, acb: a, bac: b, bca: utility-dependent, cab: ac, cba: utility-dependent>
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

    def __call__(self):
        return StrategyTwelve(
            d_ranking_ballot={ranking: random.choice(possible_ballots)
                              for ranking, possible_ballots in self.d_ranking_possible_ballots.items()},
            profile=self.profile,
            voting_rule=self.voting_rule
        )
