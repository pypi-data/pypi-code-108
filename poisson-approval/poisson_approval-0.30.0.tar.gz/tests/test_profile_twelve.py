import pytest
from pytest import fixture
from fractions import Fraction
from poisson_approval import ProfileTwelve, StrategyTwelve, StrategyOrdinal, EquilibriumStatus, \
    APPROVAL, PLURALITY, ANTI_PLURALITY, TauVector, initialize_random_seeds, UTILITY_DEPENDENT, SPLIT


def test_iterative_voting_verbose():
    """
    >>> from fractions import Fraction
    >>> profile = ProfileTwelve(d_type_share={'a_bc': Fraction(1, 2), 'ab_c': Fraction(1, 2)})
    >>> strategy = StrategyTwelve(d_ranking_ballot={'abc': 'ab'})
    >>> result = profile.iterated_voting(init=strategy, n_max_episodes=100,
    ...                                  ballot_update_ratio=1, verbose=True)
    t = 0
    strategy: <abc: ab> ==> a, b
    tau_actual: <ab: 1> ==> a, b
    t = 1
    tau_perceived: <ab: 1> ==> a, b
    mu_ab > mu_ac = mu_bc
    strategy: <abc: a> ==> a
    tau_full_response: <a: 1> ==> a
    tau_actual: <a: 1> ==> a
    t = 2
    tau_perceived: <a: 1> ==> a
    mu_ab = mu_ac = mu_bc
    strategy: <abc: a> ==> a
    tau_full_response: <a: 1> ==> a
    tau_actual: <a: 1> ==> a
    t = 3
    tau_perceived: <a: 1> ==> a
    mu_ab = mu_ac = mu_bc
    strategy: <abc: a> ==> a
    tau_full_response: <a: 1> ==> a
    tau_actual: <a: 1> ==> a
    >>> result = profile.fictitious_play(init=strategy, n_max_episodes=100,
    ...                                  perception_update_ratio=1, ballot_update_ratio=1, verbose=True)
    t = 0
    strategy: <abc: ab> ==> a, b
    tau_actual: <ab: 1> ==> a, b
    t = 1
    tau_perceived: <ab: 1> ==> a, b
    mu_ab > mu_ac = mu_bc
    strategy: <abc: a> ==> a
    tau_full_response: <a: 1> ==> a
    tau_actual: <a: 1> ==> a
    t = 2
    tau_perceived: <a: 1> ==> a
    mu_ab = mu_ac = mu_bc
    strategy: <abc: a> ==> a
    tau_full_response: <a: 1> ==> a
    tau_actual: <a: 1> ==> a
    """
    pass


@fixture()
def my_profile():
    return ProfileTwelve(d_type_share={'a_bc': 1, 'ab_c': 1})


@fixture()
def my_strategy():
    return StrategyTwelve(d_ranking_ballot={'abc': 'ab'})


def test_normalization(my_profile):
    assert my_profile.a_bc == 0.5


def test_not_equilibrium(my_profile, my_strategy):
    assert my_profile.is_equilibrium(my_strategy) == EquilibriumStatus.NOT_EQUILIBRIUM


def test_iterated_voting_with_cycle():
    """
        >>> my_profile = ProfileTwelve(d_type_share={'a_bc': 1, 'ab_c': 1}, voting_rule=ANTI_PLURALITY)
        >>> my_strategy = StrategyTwelve(d_ranking_ballot={'abc': 'ab'})
        >>> def share_double_votes_t(tau):
        ...     return tau.ab + tau.ac + tau.bc
        >>> def share_double_votes_s(strategy):
        ...     return strategy.share_double_votes
        >>> result = my_profile.iterated_voting(
        ...     init=my_strategy, n_max_episodes=10, ballot_update_ratio=1,
        ...     other_statistics_tau={'share_double_votes_t': share_double_votes_t},
        ...     other_statistics_strategy={'share_double_votes_s': share_double_votes_s})
        >>> result['cycle_taus_actual']
        [TauVector({'ab': 1}, voting_rule='Anti-plurality'), TauVector({'ac': 1}, voting_rule='Anti-plurality')]
        >>> result['d_candidate_winning_frequency']
        {'a': Fraction(1, 2), 'b': Fraction(1, 4), 'c': Fraction(1, 4)}
        >>> result['share_double_votes_t']
        1.0
        >>> result['share_double_votes_s']
        1.0
    """
    pass


def test_iterated_voting_without_convergence():
    """
        >>> my_profile = ProfileTwelve(
        ...     d_type_share={'ab_c': Fraction(2, 5), 'c_ba': Fraction(2, 5), 'ca_b': Fraction(1, 5)})
        >>> my_strategy = StrategyTwelve(d_ranking_ballot={'abc': 'a', 'cab': 'ac', 'cba': 'bc'})
        >>> def share_double_votes_t(tau):
        ...     return tau.ab + tau.ac + tau.bc
        >>> def share_double_votes_s(strategy):
        ...     return strategy.share_double_votes
        >>> result = my_profile.iterated_voting(
        ...     init=my_strategy, n_max_episodes=4, ballot_update_ratio=1,
        ...     other_statistics_tau={'share_double_votes_t': share_double_votes_t},
        ...     other_statistics_strategy={'share_double_votes_s': share_double_votes_s})
        >>> result['cycle_taus_actual']
        []
        >>> result['d_candidate_winning_frequency']
        {'a': Fraction(1, 8), 'c': Fraction(7, 8)}
        >>> result['share_double_votes_t']  # doctest: +ELLIPSIS
        0.4499999...
        >>> result['share_double_votes_s']
        Fraction(9, 20)
    """
    pass


def test_fictitious_play_without_convergence():
    """
        >>> my_profile = ProfileTwelve(d_type_share={'a_bc': 1, 'ab_c': 1}, voting_rule=ANTI_PLURALITY)
        >>> my_strategy = StrategyTwelve(d_ranking_ballot={'abc': 'ab'})
        >>> def share_double_votes_t(tau):
        ...     return tau.ab + tau.ac + tau.bc
        >>> def share_double_votes_s(strategy):
        ...     return strategy.share_double_votes
        >>> result = my_profile.fictitious_play(
        ...     init=my_strategy, n_max_episodes=10,
        ...     other_statistics_tau={'share_double_votes_t': share_double_votes_t},
        ...     other_statistics_strategy={'share_double_votes_s': share_double_votes_s})
        >>> print(result['tau'])
        None
        >>> result['d_candidate_winning_frequency']
        {'a': Fraction(1, 2), 'b': Fraction(1, 4), 'c': Fraction(1, 4)}
        >>> result['share_double_votes_t']
        Fraction(1, 1)
        >>> result['share_double_votes_s']
        Fraction(1, 1)
    """
    pass


def test_plurality():
    """
        >>> profile = ProfileTwelve(
        ...     d_type_share={'a_bc': Fraction(1, 5), 'ba_c': Fraction(3, 5), 'c_ab': Fraction(1, 5)},
        ...     voting_rule=PLURALITY)
        >>> profile
        ProfileTwelve({'a_bc': Fraction(1, 5), 'ba_c': Fraction(3, 5), 'c_ab': Fraction(1, 5)}, voting_rule='Plurality')
        >>> print(profile)
        <a_bc: 1/5, ba_c: 3/5, c_ab: 1/5> (Condorcet winner: b) (Plurality)
        >>> profile.tau_sincere
        TauVector({'a': Fraction(1, 5), 'b': Fraction(3, 5), 'c': Fraction(1, 5)}, voting_rule='Plurality')
        >>> profile.tau_fanatic
        TauVector({'a': Fraction(1, 5), 'b': Fraction(3, 5), 'c': Fraction(1, 5)}, voting_rule='Plurality')
        >>> strategy = StrategyTwelve({'abc': 'a', 'bac': 'b', 'cab': 'c'}, profile=profile)
        >>> strategy.is_equilibrium
        EquilibriumStatus.EQUILIBRIUM
    """
    pass


def test_anti_plurality():
    """
        >>> profile = ProfileTwelve(
        ...     d_type_share={'ab_c': Fraction(2, 5), 'b_ca': Fraction(2, 5), 'ca_b': Fraction(1, 5)},
        ...     voting_rule=ANTI_PLURALITY)
        >>> profile
        ProfileTwelve({'ab_c': Fraction(2, 5), 'b_ca': Fraction(2, 5), 'ca_b': Fraction(1, 5)}, \
voting_rule='Anti-plurality')
        >>> print(profile)
        <ab_c: 2/5, b_ca: 2/5, ca_b: 1/5> (Anti-plurality)
        >>> profile.tau_sincere
        TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'bc': Fraction(2, 5)}, voting_rule='Anti-plurality')
        >>> profile.tau_fanatic
        TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'bc': Fraction(2, 5)}, voting_rule='Anti-plurality')
        >>> strategy = StrategyTwelve({'abc': 'ab', 'bca': 'bc', 'cab': 'ac'}, profile=profile)
        >>> strategy.is_equilibrium
        EquilibriumStatus.EQUILIBRIUM
    """
    pass


def test_initializer():
    """
        >>> profile = ProfileTwelve(
        ...     d_type_share={'ab_c': Fraction(2, 5), 'b_ca': Fraction(2, 5), 'ca_b': Fraction(1, 5)})
        >>> profile._initializer(init=StrategyTwelve({'abc': 'ab', 'bca': 'bc', 'cab': 'ac'}))
        (StrategyTwelve({'abc': 'ab', 'bca': 'bc', 'cab': 'ac'}), \
TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'bc': Fraction(2, 5)}))
        >>> profile._initializer(TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'bc': Fraction(2, 5)}))
        (None, TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'bc': Fraction(2, 5)}))
        >>> profile._initializer('sincere')
        (None, TauVector({'ab': Fraction(2, 5), 'ac': Fraction(1, 5), 'b': Fraction(2, 5)}))
        >>> profile._initializer('fanatic')
        (None, TauVector({'a': Fraction(2, 5), 'b': Fraction(2, 5), 'c': Fraction(1, 5)}))
        >>> initialize_random_seeds()
        >>> profile._initializer('random_tau')
        (None, TauVector({'a': 0.4236547993389047, 'ab': 0.12122838365799216, 'ac': 0.0039303209304278885, \
'b': 0.05394987214431912, 'bc': 0.1124259903007756, 'c': 0.2848106336275805}))
        >>> initialize_random_seeds()
        >>> profile._initializer('random_tau_undominated')
        (None, TauVector({'a': 0.33776874061001927, 'ab': 0.06223125938998075, 'ac': 0.0977450557262783, \
'b': 0.10356670011718534, 'bc': 0.2964332998828147, 'c': 0.10225494427372171}))

        >>> profile = ProfileTwelve(d_type_share={'ab_c': 1})
        >>> initialize_random_seeds()
        >>> profile._initializer('random_tau_undominated')
        (None, TauVector({'a': 0.8444218515250481, 'ab': 0.15557814847495188}))
    """
    with pytest.warns(Warning):
        ProfileTwelve({'a_bc': 1}, symbolic=True)._initializer(init='random_tau')
    with pytest.raises(ValueError):
        ProfileTwelve({'a_bc': 1})._initializer(init='unexpected argument')


def test_random_tau_undominated_with_weak_orders():
    """
        >>> initialize_random_seeds()
        >>> profile = ProfileTwelve({'a>b~c': Fraction(9, 10), 'b~c>a': Fraction(1, 10)}, voting_rule=APPROVAL)
        >>> profile.random_tau_undominated()
        TauVector({'a': 0.9, 'bc': 0.1})
        >>> profile = ProfileTwelve({'a>b~c': Fraction(9, 10), 'b~c>a': Fraction(1, 10)}, voting_rule=PLURALITY)
        >>> profile.random_tau_undominated()
        TauVector({'a': 0.9, 'b': 0.06183689966753317, 'c': 0.03816310033246684}, voting_rule='Plurality')
        >>> profile = ProfileTwelve({'a>b~c': Fraction(9, 10), 'b~c>a': Fraction(1, 10)}, voting_rule=ANTI_PLURALITY)
        >>> profile.random_tau_undominated()
        TauVector({'ab': 0.6568485734341158, 'ac': 0.24315142656588423, 'bc': 0.1}, voting_rule='Anti-plurality')
    """
    pass


def test_strategy_weak_order():
    """
        >>> profile = ProfileTwelve({'ab_c': Fraction(1, 7), 'a~b>c': Fraction(2, 7), 'c>a~b': Fraction(4, 7)})
        >>> strategy = StrategyOrdinal({'abc': 'a'}, profile=profile)
        >>> print(strategy.tau)
        <a: 1/7, ab: 2/7, c: 4/7> ==> c
    """
    pass


def test_welfare():
    """
        >>> profile = ProfileTwelve({'a~b>c': Fraction(1, 3), 'a>b~c': Fraction(2, 3)})
        >>> profile.d_candidate_welfare
        {'a': Fraction(1, 1), 'b': Fraction(1, 3), 'c': 0}
    """
    pass


def test_share_sincere_among_strategic_voters_approval():
    """
        >>> profile = ProfileTwelve({'a_bc': Fraction(1, 3), 'ab_c': Fraction(2, 3)})
        >>> strategy = StrategyTwelve({'abc': 'a'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(1, 3)
        >>> strategy = StrategyTwelve({'abc': UTILITY_DEPENDENT}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
        >>> strategy = StrategyTwelve({'abc': 'ab'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(2, 3)
    """
    pass


def test_share_sincere_among_strategic_voters_plurality():
    """
        >>> profile = ProfileTwelve({'a_bc': Fraction(1, 3), 'ab_c': Fraction(2, 3)}, voting_rule=PLURALITY)
        >>> strategy = StrategyTwelve({'abc': 'a'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
        >>> strategy = StrategyTwelve({'abc': UTILITY_DEPENDENT}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(1, 3)
        >>> strategy = StrategyTwelve({'abc': 'b'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
    """
    pass


def test_share_sincere_among_strategic_voters_anti_plurality():
    """
        >>> profile = ProfileTwelve({'a_bc': Fraction(1, 3), 'ab_c': Fraction(2, 3)}, voting_rule=ANTI_PLURALITY)
        >>> strategy = StrategyTwelve({'abc': 'ab'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        1
        >>> strategy = StrategyTwelve({'abc': UTILITY_DEPENDENT}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        Fraction(2, 3)
        >>> strategy = StrategyTwelve({'abc': 'ac'}, profile=profile)
        >>> profile.share_sincere_among_strategic_voters(strategy)
        0
    """
    pass


def test_d_ballot_share_weak_voters_strategic():
    """
        >>> profile = ProfileTwelve({}, d_weak_order_share={'a~b>c': 0.5, 'a~c>b': 0.3, 'b>a~c': 0.2},
        ...                                                 voting_rule=PLURALITY)
        >>> strategy = StrategyTwelve({}, d_weak_order_ballot={'a~b>c': 'a', 'a~c>b': SPLIT}, profile=profile)
        >>> profile.d_ballot_share_weak_voters_strategic(strategy)
        {'a': 0.65, 'b': 0.2, 'c': 0.15, 'ab': 0, 'ac': 0, 'bc': 0}

        >>> profile = ProfileTwelve({}, d_weak_order_share={'a>b~c': 0.5, 'b>a~c': 0.3, 'a~c>b': 0.2},
        ...                                                 voting_rule=ANTI_PLURALITY)
        >>> strategy = StrategyTwelve({}, d_weak_order_ballot={'a>b~c': 'ab', 'b>a~c': SPLIT}, profile=profile)
        >>> profile.d_ballot_share_weak_voters_strategic(strategy)
        {'a': 0, 'b': 0, 'c': 0, 'ab': 0.65, 'ac': 0.2, 'bc': 0.15}
    """
    pass


def test_best_responses_to_strategy():
    """
        >>> profile = ProfileTwelve({}, d_weak_order_share={'a~b>c': 0.5, 'a~c>b': 0.3, 'b~c>a': 0.2},
        ...                                                 voting_rule=PLURALITY)
        >>> tau = TauVector({'a': 0.4, 'b': 0.2, 'c': 0.4}, voting_rule=PLURALITY)
        >>> profile.best_responses_to_strategy(tau)
        StrategyThreshold({}, d_weak_order_ballot={'a~b>c': 'a', 'a~c>b': 'Split', 'b~c>a': 'c'}, voting_rule='Plurality')

        >>> profile = ProfileTwelve({}, d_weak_order_share={'a>b~c': 0.5, 'b>a~c': 0.3, 'c>a~b': 0.2},
        ...                                                 voting_rule=ANTI_PLURALITY)
        >>> tau = TauVector({'ab': 0.2, 'ac': 0.6, 'bc': 0.2}, voting_rule=ANTI_PLURALITY)
        >>> profile.best_responses_to_strategy(tau)
        StrategyThreshold({}, d_weak_order_ballot={'a>b~c': 'ab', 'b>a~c': 'Split', 'c>a~b': 'bc'}, voting_rule='Anti-plurality')
    """
    pass
