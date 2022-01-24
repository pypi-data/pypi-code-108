from fractions import Fraction
from poisson_approval import ProfileOrdinal, StrategyOrdinal, ProfileDiscrete, StrategyThreshold


def test():
    """
    >>> from fractions import Fraction
    >>> profile = ProfileOrdinal({'abc': Fraction(1, 10), 'bac': Fraction(6, 10), 'cab': Fraction(3, 10)})
    >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'}, profile=profile)
    >>> print(strategy)
    <abc: a, bac: ab, cab: c> ==> a
    >>> print(strategy.tau)
    <a: 1/10, ab: 3/5, c: 3/10> ==> a
    >>> print(strategy.τ)
    <a: 1/10, ab: 3/5, c: 3/10> ==> a
    >>> print(strategy.scores)
    {a: 7/10, b: 3/5, c: 3/10}
    >>> print(strategy.winners)
    a
    >>> strategy.share_sincere
    >>> strategy.share_sincere_among_strategic_voters
    >>> strategy.duo_ab
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.duo_ba
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.duo_ac
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.duo_ca
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.duo_bc
    <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.duo_cb
    <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.pivot_weak_ab
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_weak_ba
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_weak_ac
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_weak_ca
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_weak_bc
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.pivot_weak_cb
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = \
0.707107>
    >>> strategy.pivot_strict_ab
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_strict_ba
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_strict_ac
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_strict_ca
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_strict_bc
    <asymptotic = exp(- inf)>
    >>> strategy.pivot_strict_cb
    <asymptotic = exp(- inf)>
    >>> strategy.pivot_tij_abc
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_tij_acb
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_tij_bac
    <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_tij_bca
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.302013 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.pivot_tij_cab
    <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_tij_cba
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.pivot_tjk_abc
    <asymptotic = exp(- inf)>
    >>> strategy.pivot_tjk_acb
    <asymptotic = exp(- inf)>
    >>> strategy.pivot_tjk_bac
    <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_tjk_bca
    <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    >>> strategy.pivot_tjk_cab
    <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.pivot_tjk_cba
    <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    >>> strategy.trio
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.trio_1t_a
    <asymptotic = exp(- inf)>
    >>> strategy.trio_1t_b
    <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.48597 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.trio_1t_c
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.490239 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.trio_2t_ab
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.trio_2t_ac
    <asymptotic = exp(- inf)>
    >>> strategy.trio_2t_bc
    <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.trio_2t_ba
    <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.trio_2t_ca
    <asymptotic = exp(- inf)>
    >>> strategy.trio_2t_cb
    <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.print_weak_pivots()
    pivot_weak_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_weak_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    pivot_weak_bc:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    trio:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, phi_ab = 0.707107>
    >>> strategy.print_all_pivots()
    pivot_weak_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_weak_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_weak_bc:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    pivot_strict_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_strict_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_strict_bc:  <asymptotic = exp(- inf)>
    pivot_tij_abc:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_tij_acb:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_tij_bac:  <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_tij_bca:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.302013 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    pivot_tij_cab:  <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_tij_cba:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    pivot_tjk_abc:  <asymptotic = exp(- inf)>
    pivot_tjk_acb:  <asymptotic = exp(- inf)>
    pivot_tjk_bac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.371758 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_tjk_bca:  <asymptotic = exp(- 0.0834849 n - 0.5 log n + 0.0518905 + o(1)), phi_a = 0.654654, \
phi_c = 1.52753, phi_ab = 0.654654>
    pivot_tjk_cab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    pivot_tjk_cba:  <asymptotic = exp(- 0.1 n + log n - 2.30259 + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    trio:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.836813 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    trio_1t_a:  <asymptotic = exp(- inf)>
    trio_1t_b:  <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.48597 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    trio_1t_c:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 0.490239 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    trio_2t_ab:  <asymptotic = exp(- 0.151472 n - 0.5 log n - 1.18339 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    trio_2t_ac:  <asymptotic = exp(- inf)>
    trio_2t_bc:  <asymptotic = exp(- 0.151472 n + 0.5 log n - 3.1394 + o(1)), phi_a = 0, phi_c = 1.41421, \
phi_ab = 0.707107>
    duo_ab:  <asymptotic = exp(- 0.1 n + o(1)), phi_a = 0, phi_c = 1, phi_ab = 1>
    duo_ac:  <asymptotic = exp(- 0.0834849 n - 0.5 log n - 0.87535 + o(1)), phi_a = 0.654654, phi_c = 1.52753, \
phi_ab = 0.654654>
    duo_bc:  <asymptotic = exp(- 0.0514719 n - 0.5 log n - 0.836813 + o(1)), phi_a = 1, phi_c = 1.41421, \
phi_ab = 0.707107>
    >>> strategy.d_ranking_best_response['abc']
    <ballot = a, utility_threshold = 1, justification = Asymptotic method>
    >>> strategy.is_equilibrium
    EquilibriumStatus.EQUILIBRIUM
    """
    pass


def test_shares():
    """
        >>> profile = ProfileDiscrete({
        ...     ('abc', Fraction(2, 11)): 1,  # Sincere vote: a
        ... }, ratio_fanatic=Fraction(1, 3))
        >>> strategy = StrategyOrdinal({'abc': 'ab'}, profile=profile)
        >>> strategy.tau
        TauVector({'a': Fraction(1, 3), 'ab': Fraction(2, 3)})
        >>> strategy.share_single_votes
        Fraction(1, 3)
        >>> strategy.share_double_votes
        Fraction(2, 3)
        >>> strategy.share_sincere_among_strategic_voters
        0
        >>> strategy.share_sincere
        Fraction(1, 3)
    """
    pass
