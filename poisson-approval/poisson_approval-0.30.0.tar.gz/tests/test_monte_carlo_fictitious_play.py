from poisson_approval import monte_carlo_fictitious_play, RandProfileHistogramUniform, \
    MCS_PROFILE, MCS_TAU_INIT, MCS_N_EPISODES, MCS_CANDIDATE_WINNING_FREQUENCY, MCS_CONVERGES, MCS_FREQUENCY_CW_WINS, \
    MCS_WELFARE_LOSSES, MCS_UTILITY_THRESHOLDS, MCS_BALLOT_STATISTICS, MCS_DECREASING_SCORES, VOTING_RULES, \
    one_over_t


def test_no_mcs():
    """
        >>> meta_results = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ... )
        >>> meta_results
        {'': {'n_samples': 1}}
    """
    pass


def test_with_save_file():
    """
        >>> import pickle
        >>> file_save = 'zzz_test_monte_carlo_with_save_file.sav'
        >>> _ = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ...     file_save=file_save,
        ... )
        >>> with open(file_save, "rb") as f:
        ...     meta_results = pickle.load(f)
        >>> meta_results
        {'': {'n_samples': 1}}
    """
    pass


def test_monte_carlo_iterated_voting():
    """
        >>> meta_results = monte_carlo_fictitious_play(
        ...     factory=RandProfileHistogramUniform(n_bins=1),
        ...     n_samples=1,
        ...     n_max_episodes=10,
        ...     voting_rules=VOTING_RULES,
        ...     monte_carlo_settings=[
        ...         MCS_PROFILE,
        ...         MCS_TAU_INIT,
        ...         MCS_N_EPISODES,
        ...         MCS_CANDIDATE_WINNING_FREQUENCY,
        ...         MCS_CONVERGES,
        ...         MCS_FREQUENCY_CW_WINS,
        ...         MCS_WELFARE_LOSSES,
        ...         MCS_UTILITY_THRESHOLDS,
        ...         MCS_BALLOT_STATISTICS,
        ...         MCS_DECREASING_SCORES,
        ...     ],
        ...     meth='iterated_voting',
        ...     perception_update_ratio=1,
        ...     ballot_update_ratio=1,
        ...     statistics_update_ratio=one_over_t,
        ... )
    """
    pass
