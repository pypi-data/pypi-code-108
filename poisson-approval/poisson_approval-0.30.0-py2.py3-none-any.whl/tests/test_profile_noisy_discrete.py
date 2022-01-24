import pytest
from fractions import Fraction
from poisson_approval import ProfileNoisyDiscrete, StrategyOrdinal, PLURALITY, ANTI_PLURALITY


def test_normalization():
    profile = ProfileNoisyDiscrete({('abc', 0.2, 0.01): 1, ('acb', 0.4, 0.01): 1})
    assert profile.abc == 0.5


def test_epsilon_zero():
    with pytest.raises(ValueError):
        profile = ProfileNoisyDiscrete({('abc', 0.2): .5, ('acb', 0.4): .5}, noise=0)


def test_plurality():
    """
        >>> profile = ProfileNoisyDiscrete({('abc', 0.2, 0.01): 1, ('acb', 0.4, 0.01): 1}, voting_rule=PLURALITY)
        >>> profile
        ProfileNoisyDiscrete({'abc': {(0.2, 0.01): Fraction(1, 2)}, 'acb': {(0.4, 0.01): Fraction(1, 2)}}, \
voting_rule='Plurality')
        >>> print(profile)
        <abc 0.2 ± 0.01: 1/2, acb 0.4 ± 0.01: 1/2> (Condorcet winner: a) (Plurality)
    """
    pass


def test_anti_plurality():
    """
        >>> profile = ProfileNoisyDiscrete({('abc', 0.2, 0.01): 1, ('acb', 0.4, 0.01): 1}, voting_rule=ANTI_PLURALITY)
        >>> profile
        ProfileNoisyDiscrete({'abc': {(0.2, 0.01): Fraction(1, 2)}, 'acb': {(0.4, 0.01): Fraction(1, 2)}}, \
voting_rule='Anti-plurality')
        >>> print(profile)
        <abc 0.2 ± 0.01: 1/2, acb 0.4 ± 0.01: 1/2> (Condorcet winner: a) (Anti-plurality)
    """
    pass


def test_misc_forms_of_input():
    """
        >>> profile = ProfileNoisyDiscrete({('abc', 0.2, 0.01): 0, ('abc', 0, 0.01): Fraction(3, 7)})
        >>> profile
        ProfileNoisyDiscrete({'abc': {(0, 0.01): 1}})
        >>> print(profile)
        <abc 0 ± 0.01: 1> (Condorcet winner: a)
    """
    pass


def test_strategy_weak_order():
    """
        >>> profile = ProfileNoisyDiscrete({('abc', 0.3, 0.01): Fraction(1, 7),
        ...                                 'a~b>c': Fraction(2, 7), 'c>a~b': Fraction(4, 7)})
        >>> strategy = StrategyOrdinal({'abc': 'a'}, profile=profile)
        >>> print(strategy.tau)
        <a: 1/7, ab: 2/7, c: 4/7> ==> c
    """
    pass


def test_welfare():
    """
        >>> profile = ProfileNoisyDiscrete({'a~b>c': Fraction(1, 3), 'a>b~c': Fraction(2, 3)})
        >>> profile.d_candidate_welfare
        {'a': Fraction(1, 1), 'b': Fraction(1, 3), 'c': 0}
    """
    pass
