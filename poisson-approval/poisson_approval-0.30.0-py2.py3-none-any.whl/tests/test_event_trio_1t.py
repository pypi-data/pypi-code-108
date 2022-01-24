from poisson_approval import TauVector, EventTrio1t


def test():
    """
        >>> tau = TauVector({'a': 2, 'b': 3, 'c': 5, 'ab': 7, 'ac': 11, 'bc':13}, normalization_warning=False)
        >>> tau.trio_1t_a
        <asymptotic = exp(- 0.0392799 n + ? log n + ? + o(1)), phi_a = 1.35481, phi_b = 1.08479, phi_c = 0.680414, \
phi_ab = 1.46969, phi_ac = 0.921834, phi_bc = 0.738109>
    """
    pass
