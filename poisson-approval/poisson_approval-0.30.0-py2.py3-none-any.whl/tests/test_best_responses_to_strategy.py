from fractions import Fraction
from poisson_approval import ProfileOrdinal
from poisson_approval import StrategyOrdinal


def test():
    """
    >>> profile = ProfileOrdinal({'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)})
    >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'}, profile=profile)
    >>> strategy_response = profile.best_responses_to_strategy(strategy.tau)
    >>> print(strategy_response)
    <abc: a, bac: ab, cab: c> ==> a
    """
    pass
