from poisson_approval import NiceStatsProfileOrdinal, initialize_random_seeds, ProfileOrdinal


def test():
    # Test when rejection is indeed necessary.
    initialize_random_seeds()
    nice_stats = NiceStatsProfileOrdinal(
        tests_profile=[
            (lambda profile: any([strategy for strategy in profile.analyzed_strategies_ordinal.equilibria
                                  if strategy.profile.condorcet_winners == strategy.winners]),
             'There exists a true equilibrium electing the CW'),
        ],
        conditional_on=lambda profile: profile.has_majority_ranking)
    nice_stats.run(n_samples=2)
    profile = nice_stats.find_example(0, False)
    assert isinstance(profile, ProfileOrdinal)


def test_misc_options():
    """
        >>> initialize_random_seeds()
        >>> nice_stats = NiceStatsProfileOrdinal(
        ...     tests_profile=[
        ...         (lambda profile: any([strategy for strategy in profile.analyzed_strategies_ordinal.equilibria
        ...                               if strategy.profile.condorcet_winners == strategy.winners]),
        ...          'There exists a true equilibrium electing the CW'),
        ...     ],
        ...     tests_strategy=[
        ...         (lambda strategy: strategy.profile.condorcet_winners == strategy.winners,
        ...          'There exists an equilibrium that elects the CW')
        ...     ],
        ...     tests_strategy_dist=[
        ...         (lambda strategy: strategy.profile.condorcet_winners == strategy.winners,
        ...          'There exists an equilibrium that elects the CW')
        ...     ],
        ...     tests_strategy_winners = [
        ...         (lambda sigma: True, 'Number of possible winners')
        ...     ],
        ...     conditional_on=lambda profile: profile.is_profile_condorcet == 1.
        ... )
        >>> nice_stats.run(n_samples=10)
        >>> nice_stats.plot_test_strategy(test=0, ylabel=False, legend=True, replacement_name='foobar')
        >>> nice_stats.plot_cutoff(test=0)
    """
    pass
