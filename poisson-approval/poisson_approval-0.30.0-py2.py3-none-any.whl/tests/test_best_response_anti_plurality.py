from fractions import Fraction
from poisson_approval import TauVector, BestResponseAntiPlurality, ANTI_PLURALITY, UTILITY_DEPENDENT


def test_best_response_anti_plurality():
    """
        >>> tau = TauVector({'ab': Fraction(9, 15), 'ac': Fraction(4, 15), 'bc': Fraction(2, 15)},
        ...                 voting_rule=ANTI_PLURALITY)
        >>> best_response = BestResponseAntiPlurality(tau, 'abc')
        >>> print(best_response._str_very_verbose)
        tau = <ab: 3/5, ac: 4/15, bc: 2/15> ==> a (Anti-plurality)
        ranking = abc
        voting_rule  = Anti-plurality
        duo_ij = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ij = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ji = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ik = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_ab = 0.471405, phi_ac = 1, phi_bc = 2.12132>
        duo_ki = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_ab = 0.471405, phi_ac = 1, phi_bc = 2.12132>
        duo_jk = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_ab = 0.666667, phi_ac = 1.5, phi_bc = 1>
        duo_kj = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_ab = 0.666667, phi_ac = 1.5, phi_bc = 1>
        pivot_weak_ij = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_weak_ji = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_weak_ik = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_weak_ki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_weak_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_weak_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_strict_ij = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_strict_ji = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_strict_ik = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_strict_ki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_strict_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_strict_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tij_ijk = <asymptotic = exp(- 0.0228764 n - 0.5 log n + 0.103453 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij_ikj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tij_jik = <asymptotic = exp(- 0.0228764 n - 0.5 log n + 0.450026 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij_jki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tij_kij = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tij_kji = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tjk_ijk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tjk_ikj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tjk_jik = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tjk_jki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_tjk_kij = <asymptotic = exp(- 0.0228764 n - 0.5 log n + 0.103453 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tjk_kji = <asymptotic = exp(- 0.0228764 n - 0.5 log n + 0.450026 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij = <asymptotic = exp(- 0.0228764 n - 0.5 log n + 0.103453 + o(1)), phi_ab = 1, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tjk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_1t_i = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_1t_j = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_1t_k = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_ij = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_ji = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_ik = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_ki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        trio_2t_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_ab = 0.462241, phi_ac = 1.04004, phi_bc = 2.08008>
        pivot_ij_easy_or_tight = True
        pivot_ji_easy_or_tight = True
        pivot_ik_easy_or_tight = False
        pivot_ki_easy_or_tight = False
        pivot_jk_easy_or_tight = False
        pivot_kj_easy_or_tight = False
        utility_threshold = 1
        justification = Anti-plurality analysis
        ballot = ac
    """
    pass


def test_best_response_is_ij():
    tau = TauVector({'ab': Fraction(4, 15), 'ac': Fraction(9, 15), 'bc': Fraction(2, 15)}, voting_rule=ANTI_PLURALITY)
    best_response = BestResponseAntiPlurality(tau, 'abc')
    assert best_response.ballot == 'ab'


def test_best_response_is_utility_dependent():
    tau = TauVector({'ab': Fraction(7, 15), 'ac': Fraction(1, 15), 'bc': Fraction(7, 15)}, voting_rule=ANTI_PLURALITY)
    best_response = BestResponseAntiPlurality(tau, 'abc')
    assert best_response.utility_threshold == Fraction(1, 2)
    assert best_response.ballot == UTILITY_DEPENDENT
