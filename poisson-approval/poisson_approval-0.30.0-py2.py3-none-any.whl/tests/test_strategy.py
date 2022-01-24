from poisson_approval import ProfileTwelve, StrategyTwelve


def test_deepcopy_with_attached_profile():
    """
    >>> strategy = StrategyTwelve(d_ranking_ballot={'abc': 'ab'})
    >>> print(strategy)
    <abc: ab>
    >>> profile = ProfileTwelve(d_type_share={'a_bc': 1, 'ab_c': 1})
    >>> strategy_with_profile = strategy.deepcopy_with_attached_profile(profile)
    >>> print(strategy_with_profile)
    <abc: ab> ==> a, b
    """
    pass
