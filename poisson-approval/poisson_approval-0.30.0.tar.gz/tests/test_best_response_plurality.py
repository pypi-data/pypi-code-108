from fractions import Fraction
from poisson_approval import TauVector, BestResponsePlurality, PLURALITY, UTILITY_DEPENDENT


def test_best_response_plurality():
    """
        >>> tau = TauVector({'a': Fraction(9, 15), 'b': Fraction(4, 15), 'c': Fraction(2, 15)}, voting_rule=PLURALITY)
        >>> best_response = BestResponsePlurality(tau, 'abc')
        >>> print(best_response._str_very_verbose)
        tau = <a: 3/5, b: 4/15, c: 2/15> ==> a (Plurality)
        ranking = abc
        voting_rule  = Plurality
        duo_ij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        duo_ij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        duo_ji = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        duo_ik = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        duo_ki = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        duo_jk = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_a = 1, phi_b = 0.707107, phi_c = 1.41421>
        duo_kj = <asymptotic = exp(- 0.0228764 n - 0.5 log n - 0.431347 + o(1)), phi_a = 1, phi_b = 0.707107, phi_c = 1.41421>
        pivot_weak_ij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_weak_ji = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_weak_ik = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_weak_ki = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_weak_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_weak_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_strict_ij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_strict_ji = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.807367 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_strict_ik = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_strict_ki = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.63408 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_strict_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_strict_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_tij_ijk = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.296541 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_tij_ikj = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.247863 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_tij_jik = <asymptotic = exp(- 0.0666667 n - 0.5 log n + 0.108924 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_tij_jki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_tij_kij = <asymptotic = exp(- 0.167648 n - 0.5 log n + 0.504176 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_tij_kji = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_tjk_ijk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_tjk_ikj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_tjk_jik = <asymptotic = exp(- 0.167648 n - 0.5 log n - 0.247863 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_tjk_jki = <asymptotic = exp(- 0.167648 n - 0.5 log n + 0.504176 + o(1)), phi_a = 0.471405, phi_b = 1, phi_c = 2.12132>
        pivot_tjk_kij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.296541 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_tjk_kji = <asymptotic = exp(- 0.0666667 n - 0.5 log n + 0.108924 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_tij = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.296541 + o(1)), phi_a = 0.666667, phi_b = 1.5, phi_c = 1>
        pivot_tjk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_1t_i = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_1t_j = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_1t_k = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_ij = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_ji = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_ik = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_ki = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_jk = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        trio_2t_kj = <asymptotic = exp(- 0.167966 n + ? log n + ? + o(1)), phi_a = 0.462241, phi_b = 1.04004, phi_c = 2.08008>
        pivot_ij_easy_or_tight = True
        pivot_ji_easy_or_tight = True
        pivot_ik_easy_or_tight = True
        pivot_ki_easy_or_tight = True
        pivot_jk_easy_or_tight = False
        pivot_kj_easy_or_tight = False
        utility_threshold = 1
        justification = Plurality analysis
        ballot = a
    """
    pass


def test_best_response_is_j():
    tau = TauVector({'a': 1 / 5, 'b': 2 / 5, 'c': 2 / 5}, voting_rule=PLURALITY)
    best_response = BestResponsePlurality(tau, 'abc')
    assert best_response.ballot == 'b'


def test_best_response_is_utility_dependent():
    tau = TauVector({'a': 1 / 5, 'b': 3 / 5, 'c': 1 / 5}, voting_rule=PLURALITY)
    best_response = BestResponsePlurality(tau, 'abc')
    assert best_response.utility_threshold == Fraction(1, 2)
    assert best_response.ballot == UTILITY_DEPENDENT


def test_best_response_is_not_utility_dependent():
    tau = TauVector({'a': 0, 'b': 1, 'c': 0}, voting_rule=PLURALITY)
    best_response = BestResponsePlurality(tau, 'abc')
    assert best_response.ballot == 'a'
