from fractions import Fraction
from poisson_approval import TauVector, BestResponseApproval, isnan, RANKINGS


def test_best_response_approval():
    """
        >>> tau = TauVector({'a': Fraction(9, 15), 'b': Fraction(4, 15), 'ac': Fraction(1, 15), 'bc': Fraction(1, 15)})
        >>> best_response = BestResponseApproval(tau, 'abc')
        >>> print(best_response._str_very_verbose)
        tau = <a: 3/5, ac: 1/15, b: 4/15, bc: 1/15> ==> a
        ranking = abc
        voting_rule  = Approval
        duo_ij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ji = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        duo_ik = <asymptotic = exp(- 0.266667 n - 0.5 log n - 0.460793 + o(1)), phi_a = 0.333333, phi_b = 1, phi_ac = 1, phi_bc = 3>
        duo_ki = <asymptotic = exp(- 0.266667 n - 0.5 log n - 0.460793 + o(1)), phi_a = 0.333333, phi_b = 1, phi_ac = 1, phi_bc = 3>
        duo_jk = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.258061 + o(1)), phi_a = 1, phi_b = 0.5, phi_ac = 2, phi_bc = 1>
        duo_kj = <asymptotic = exp(- 0.0666667 n - 0.5 log n - 0.258061 + o(1)), phi_a = 1, phi_b = 0.5, phi_ac = 2, phi_bc = 1>
        pivot_weak_ij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_weak_ji = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_weak_ik = <asymptotic = exp(- 0.333333 n - log n - 0.0257066 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_weak_ki = <asymptotic = exp(- 0.333333 n - log n - 0.0257066 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_weak_jk = <asymptotic = exp(- 0.333333 n - log n - 0.313389 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_weak_kj = <asymptotic = exp(- 0.333333 n - log n - 0.313389 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_strict_ij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_strict_ji = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.889493 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_strict_ik = <asymptotic = exp(- 0.333333 n - log n - 0.718854 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_strict_ki = <asymptotic = exp(- 0.333333 n - log n - 0.718854 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_strict_jk = <asymptotic = exp(- 0.333333 n - log n - 1.412 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_strict_kj = <asymptotic = exp(- 0.333333 n - log n - 1.412 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tij_ijk = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.354693 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij_ikj = <asymptotic = exp(- 0.333333 n - log n + 0.128444 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tij_jik = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.00811919 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij_jki = <asymptotic = exp(- 0.333333 n - log n - 0.159238 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tij_kij = <asymptotic = exp(- 0.333333 n - log n + 1.36059 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tij_kji = <asymptotic = exp(- 0.333333 n - log n + 0.785224 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tjk_ijk = <asymptotic = exp(- 0.333333 n - log n - 2.10515 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tjk_ikj = <asymptotic = exp(- 0.333333 n - log n - 0.564703 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tjk_jik = <asymptotic = exp(- 0.333333 n - log n - 1.12432 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tjk_jki = <asymptotic = exp(- 0.333333 n - log n + 0.533909 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_tjk_kij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.354693 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tjk_kji = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.00811919 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tij = <asymptotic = exp(- 0.057191 n - 0.5 log n - 0.354693 + o(1)), phi_a = 0.707107, phi_b = 1.41421, phi_ac = 0.707107, phi_bc = 1.41421>
        pivot_tjk = <asymptotic = exp(- 0.333333 n - log n - 2.10515 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio = <asymptotic = exp(- 0.333333 n - log n - 0.718854 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_1t_i = <asymptotic = exp(- 0.333333 n - log n - 1.81747 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_1t_j = <asymptotic = exp(- 0.333333 n - log n - 1.412 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_1t_k = <asymptotic = exp(- 0.333333 n - log n + 1.07291 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_ij = <asymptotic = exp(- 0.333333 n - log n - 2.51061 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_ji = <asymptotic = exp(- 0.333333 n - log n - 2.51061 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_ik = <asymptotic = exp(- 0.333333 n - log n - 0.0257066 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_ki = <asymptotic = exp(- 0.333333 n - log n - 0.0257066 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_jk = <asymptotic = exp(- 0.333333 n - log n + 0.379759 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        trio_2t_kj = <asymptotic = exp(- 0.333333 n - log n + 0.379759 + o(1)), phi_a = 0.333333, phi_b = 0.5, phi_ac = 2, phi_bc = 3>
        pivot_ij_easy_or_tight = True
        pivot_ji_easy_or_tight = True
        pivot_ik_easy_or_tight = False
        pivot_ki_easy_or_tight = False
        pivot_jk_easy_or_tight = False
        pivot_kj_easy_or_tight = False
        utility_threshold = 1
        justification = Easy vs difficult pivot
        ballot = a
    """
    pass


def test_results_limit_pivot_theorem_when_two_consecutive_zeros():
    tau = TauVector({'a': 3 / 5, 'b': 2 / 5})
    best_response = BestResponseApproval(tau, 'abc')
    utility_threshold, justification = best_response.results_limit_pivot_theorem
    assert isnan(utility_threshold)
    assert justification == ''


def test_correct_identification_of_easy_easy_edge_case():
    tau = TauVector({'a': 0.24382716330832704, 'ab': 0.0011384657401753433,
                     'ac': 0.25507268421895707, 'b': 0.2550449552509131,
                     'bc': 0.24379357320990255, 'c': 0.001123158271724989})
    for ranking in RANKINGS:
        # Especially cab
        assert 0 <= tau.d_ranking_best_response[ranking].utility_threshold <= 1


def test_offset_method_with_trio_approximation():
    tau = TauVector({
        'a': 0.2438625672480171, 'ab': 0.0011437146863146892,
        'ac': 0.25503412377742823, 'b': 0.25503005949673074,
        'bc': 0.24380331566218985, 'c': 0.0011262191293193397
    })
    for ranking in RANKINGS:
        # Especially acb
        assert 0 <= tau.d_ranking_best_response[ranking].utility_threshold <= 1
