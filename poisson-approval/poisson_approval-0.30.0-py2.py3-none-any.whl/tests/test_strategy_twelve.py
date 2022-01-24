import pytest
from poisson_approval import StrategyTwelve, APPROVAL, PLURALITY, ANTI_PLURALITY, UTILITY_DEPENDENT, SPLIT


def test_strategy_twelve_plurality():
    """
        >>> strategy = StrategyTwelve({'abc': UTILITY_DEPENDENT, 'cba': 'b'}, voting_rule=PLURALITY)
        >>> strategy
        StrategyTwelve({'abc': 'utility-dependent', 'cba': 'b'}, voting_rule='Plurality')
        >>> print(strategy)
        <abc: utility-dependent, cba: b> (Plurality)
        >>> strategy.a_bc
        'a'
        >>> strategy.ab_c
        'b'
    """
    pass


def test_strategy_twelve_anti_plurality():
    """
        >>> strategy = StrategyTwelve({'abc': UTILITY_DEPENDENT, 'cba': 'bc'}, voting_rule=ANTI_PLURALITY)
        >>> strategy
        StrategyTwelve({'abc': 'utility-dependent', 'cba': 'bc'}, voting_rule='Anti-plurality')
        >>> print(strategy)
        <abc: utility-dependent, cba: bc> (Anti-plurality)
        >>> strategy.a_bc
        'ac'
        >>> strategy.ab_c
        'ab'
    """
    pass


def test_strategy_twelve_with_weak_order():
    # APPROVAL
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
                                  d_weak_order_ballot={'a~b>c': SPLIT}, voting_rule=APPROVAL)
    # PLURALITY
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
                                  d_weak_order_ballot={'a>b~c': SPLIT}, voting_rule=PLURALITY)
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
                                  d_weak_order_ballot={'not a weak order': 'a'}, voting_rule=PLURALITY)
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'b'},
                                  d_weak_order_ballot={'a~b>c': 'non-existing ballot'}, voting_rule=PLURALITY)
    # ANTI_PLURALITY
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'ab'},
                                  d_weak_order_ballot={'a~b>c': SPLIT}, voting_rule=ANTI_PLURALITY)
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'ab'},
                                  d_weak_order_ballot={'not a weak order': 'a'}, voting_rule=ANTI_PLURALITY)
    with pytest.raises(ValueError):
        strategy = StrategyTwelve({'abc': 'utility-dependent', 'bac': 'ab'},
                                  d_weak_order_ballot={'a>b~c': 'non-existing ballot'}, voting_rule=ANTI_PLURALITY)
