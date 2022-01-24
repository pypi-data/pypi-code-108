from fractions import Fraction
from poisson_approval import SimplexToProfile, ProfileNoisyDiscrete


def test_without_fixed_voters():
    """
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete, left_type=('abc', 0.5, 0.01), right_type=('bac', 0.5, 0.01), top_type='c>a~b')
        >>> profile = simplex_to_profile(left=Fraction(11, 80), top=Fraction(52, 80), right=Fraction(17, 80))
        >>> print(profile)
        <abc 0.5 ± 0.01: 11/80, bac 0.5 ± 0.01: 17/80, c>a~b: 13/20> (Condorcet winner: c)

    """
    pass


def test_profile_noisy_discrete_without_noise():
    """
        >>> simplex_to_profile = SimplexToProfile(
        ...     ProfileNoisyDiscrete, left_type=('abc', 0.5), right_type=('bac', 0.5), top_type='c>a~b', noise=0.01)
        >>> profile = simplex_to_profile(left=Fraction(11, 80), top=Fraction(52, 80), right=Fraction(17, 80))
        >>> print(profile)
        <abc 0.5 ± 0.01: 11/80, bac 0.5 ± 0.01: 17/80, c>a~b: 13/20> (Condorcet winner: c)
    """
    pass
