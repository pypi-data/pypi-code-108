from fractions import Fraction
from poisson_approval import ProfileDiscrete, StrategyOrdinal, PLURALITY, ANTI_PLURALITY, StrategyThreshold


def test_normalization():
    profile = ProfileDiscrete({('abc', 0.2): 1, ('acb', 0.4): 1})
    assert profile.abc == 0.5


def test_plurality():
    """
        >>> profile = ProfileDiscrete({('abc', 0.2): 1, ('acb', 0.4): 1}, voting_rule=PLURALITY)
        >>> profile
        ProfileDiscrete({'abc': {0.2: Fraction(1, 2)}, 'acb': {0.4: Fraction(1, 2)}}, voting_rule='Plurality')
        >>> print(profile)
        <abc 0.2: 1/2, acb 0.4: 1/2> (Condorcet winner: a) (Plurality)
    """
    pass


def test_anti_plurality():
    """
        >>> profile = ProfileDiscrete({('abc', 0.2): 1, ('acb', 0.4): 1}, voting_rule=ANTI_PLURALITY)
        >>> profile
        ProfileDiscrete({'abc': {0.2: Fraction(1, 2)}, 'acb': {0.4: Fraction(1, 2)}}, voting_rule='Anti-plurality')
        >>> print(profile)
        <abc 0.2: 1/2, acb 0.4: 1/2> (Condorcet winner: a) (Anti-plurality)
    """
    pass


def test_misc_forms_of_input():
    """
        >>> profile = ProfileDiscrete({('abc', 0.2): 0, ('abc', 0): Fraction(3, 7), ('bca', 1): Fraction(4, 7)})
        >>> profile
        ProfileDiscrete({}, d_weak_order_share={'a>b~c': Fraction(3, 7), 'b~c>a': Fraction(4, 7)})
        >>> print(profile)
        <a>b~c: 3/7, b~c>a: 4/7> (Condorcet winner: b, c)
    """
    pass


def test_strategy_weak_order():
    """
        >>> profile = ProfileDiscrete({('abc', 0.3): Fraction(1, 7), 'a~b>c': Fraction(2, 7), 'c>a~b': Fraction(4, 7)})
        >>> strategy = StrategyOrdinal({'abc': 'a'}, profile=profile)
        >>> print(strategy.tau)
        <a: 1/7, ab: 2/7, c: 4/7> ==> c
    """
    pass


def test_mixed_strategy():
    """
        >>> profile = ProfileDiscrete({('abc', 0.2): Fraction(1, 7), ('acb', 0.4): Fraction(6, 7)})
        >>> strategy = StrategyThreshold({'abc': (0.2, Fraction(1, 3)), 'acb': 0}, profile=profile)
        >>> print(strategy.tau)
        <a: 1/21, ab: 2/21, ac: 6/7> ==> a
    """
    pass


def test_welfare():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(3, 10)): Fraction(26, 100), ('bac', Fraction(1, 10)): Fraction(21, 100),
        ...     'a~b>c': Fraction(23, 100), 'a>b~c': Fraction(30, 100)
        ... })
        >>> profile.d_candidate_welfare
        {'a': Fraction(811, 1000), 'b': Fraction(259, 500), 'c': 0}
    """
    pass


def test_relative_welfare():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(1, 2)): Fraction(1, 3),
        ...     ('bca', Fraction(1, 2)): Fraction(1, 3),
        ...     ('cab', Fraction(1, 2)): Fraction(1, 3)
        ... })
        >>> profile.d_candidate_relative_welfare
        {'a': 1, 'b': 1, 'c': 1}
    """
    pass


def test_share_sincere_among_strategic_voters_weak_orders():
    """
        >>> profile = ProfileDiscrete({'a~b>c': 1})
        >>> strategy = StrategyOrdinal({})
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
    """
    pass


def test_share_sincere_among_strategic_voters_approval():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),   # Sincere vote: a
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),   # Sincere vote: a
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),   # Sincere vote: ab
        ... })
        >>> strategy = StrategyThreshold({'abc': 0})
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(4, 7)
        >>> strategy = StrategyThreshold({'abc': Fraction(2, 11)}, ratio_optimistic=Fraction(1, 3))
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(13, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(1, 2)}, ratio_optimistic=Fraction(1, 3))
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(17, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(9, 11)}, ratio_optimistic=Fraction(1, 3))
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(17, 21)
        >>> strategy = StrategyThreshold({'abc': 1})
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(3, 7)
    """
    pass


def test_share_sincere_among_strategic_voters_plurality():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),
        ... }, voting_rule=PLURALITY)
        >>> strategy = StrategyThreshold({'abc': 0}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
        >>> strategy = StrategyThreshold({'abc': Fraction(2, 11)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(1, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(1, 2)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(5, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(9, 11)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(13, 21)
        >>> strategy = StrategyThreshold({'abc': 1}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
    """
    pass


def test_share_sincere_among_strategic_voters_anti_plurality():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),
        ... }, voting_rule=ANTI_PLURALITY)
        >>> strategy = StrategyThreshold({'abc': 0}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
        >>> strategy = StrategyThreshold({'abc': Fraction(2, 11)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(20, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(1, 2)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(16, 21)
        >>> strategy = StrategyThreshold({'abc': Fraction(9, 11)}, ratio_optimistic=Fraction(1, 3), profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(8, 21)
        >>> strategy = StrategyThreshold({'abc': 1}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
    """
    pass


def test_share_sincere_among_fanatic_voters_weak_orders():
    """
        >>> profile = ProfileDiscrete({'a~b>c': 1})
        >>> profile.share_sincere_among_fanatic_voters
        1
    """
    pass


def test_share_sincere_among_fanatic_voters_approval():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),   # Sincere vote: a
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),   # Sincere vote: a
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),   # Sincere vote: ab
        ... })
        >>> profile.share_sincere_among_fanatic_voters
        Fraction(3, 7)
    """
    pass


def test_share_sincere_among_fanatic_voters_plurality():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),
        ... }, voting_rule=PLURALITY)
        >>> profile.share_sincere_among_fanatic_voters
        1
    """
    pass


def test_share_sincere_among_fanatic_voters_anti_plurality():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)):   Fraction(1, 7),
        ...     ('abc', Fraction(1, 2)):    Fraction(2, 7),
        ...     ('abc', Fraction(9, 11)):   Fraction(4, 7),
        ... }, voting_rule=ANTI_PLURALITY)
        >>> profile.share_sincere_among_fanatic_voters
        1
    """
    pass


def test_share_sincere():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)): 1,   # Sincere vote: a
        ... }, ratio_fanatic=Fraction(1, 3))
        >>> strategy = StrategyOrdinal({'abc': 'ab'})
        >>> profile.share_sincere_among_fanatic_voters
        1
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
        >>> profile.share_sincere(strategy)
        Fraction(1, 3)

        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)): 1,   # Sincere vote: a
        ... }, ratio_sincere=Fraction(1, 5))
        >>> strategy = StrategyOrdinal({'abc': 'ab'})
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
        >>> profile.share_sincere(strategy)
        Fraction(1, 5)
    """
    pass
