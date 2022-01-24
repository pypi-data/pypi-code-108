from fractions import Fraction
from poisson_approval import TauVector


def test_limit_pivot():
    """
        >>> tau = TauVector({'a': Fraction(1, 3), 'b': Fraction(1, 3), 'c': Fraction(1, 3)})
        >>> tau.pivot_weak_ab.asymptotic
        Asymptotic(mu=0, nu=-0.5, xi=-1.4093531597105358)
    """
    pass
