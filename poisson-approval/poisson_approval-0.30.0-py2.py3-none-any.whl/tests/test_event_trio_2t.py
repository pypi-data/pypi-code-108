from fractions import Fraction
from poisson_approval import TauVector, EventTrio2t


def test():
    """
        >>> tau = TauVector({'a': 2, 'b': 3, 'c': 5, 'ab': 7, 'ac': 11, 'bc':13}, normalization_warning=False)
        >>> tau.trio_2t_ab
        <asymptotic = exp(- 0.0392799 n + ? log n + ? + o(1)), phi_a = 1.35481, phi_b = 1.08479, phi_c = 0.680414, \
phi_ab = 1.46969, phi_ac = 0.921834, phi_bc = 0.738109>
    """
    pass


def test_flower_diagram_3():
    """
        >>> tau = TauVector({'ac': Fraction(1, 3), 'bc': Fraction(1, 3), 'c': Fraction(1, 3)})
        >>> tau.trio_2t_ab
        <asymptotic = exp(- 0.845299 n - 0.5 log n - 1.54017 + o(1)), phi_c = 0, phi_ac = 0, phi_bc = 0>
    """
    pass
