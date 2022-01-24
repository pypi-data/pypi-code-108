from fractions import Fraction
from poisson_approval import XyyToProfile, ProfileNoisyDiscrete


def test_without_fixed_voters():
    """
        >>> xyy_to_profile = XyyToProfile(
        ...     ProfileNoisyDiscrete, left_ranking='abc', right_ranking='bac', noise=0.01)
        >>> profile = xyy_to_profile(x=Fraction(3, 10), y1=0.42, y2=0.51)
        >>> print(profile)
        <abc 0.42 ± 0.01: 7/10, bac 0.51 ± 0.01: 3/10> (Condorcet winner: a)
    """
    pass
