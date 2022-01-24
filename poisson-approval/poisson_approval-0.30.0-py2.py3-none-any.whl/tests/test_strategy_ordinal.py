from poisson_approval import StrategyOrdinal, PLURALITY, ANTI_PLURALITY


def test_strategy_ordinal_plurality():
    """
        >>> strategy = StrategyOrdinal({'abc': 'a', 'cba': 'b'}, voting_rule=PLURALITY)
        >>> strategy
        StrategyOrdinal({'abc': 'a', 'cba': 'b'}, voting_rule='Plurality')
        >>> print(strategy)
        <abc: a, cba: b> (Plurality)
    """
    pass


def test_strategy_ordinal_anti_plurality():
    """
        >>> strategy = StrategyOrdinal({'abc': 'ab', 'cba': 'ac'}, voting_rule=ANTI_PLURALITY)
        >>> strategy
        StrategyOrdinal({'abc': 'ab', 'cba': 'ac'}, voting_rule='Anti-plurality')
        >>> print(strategy)
        <abc: ab, cba: ac> (Anti-plurality)
    """
    pass
