from poisson_approval import convergence_test, ProfileHistogram


def test_convergence_test_iterated_voting():
    """
        >>> converges = convergence_test(
        ...     n_max_episodes=10,
        ...     perception_update_ratio=1,
        ...     ballot_update_ratio=1,
        ...     meth='iterated_voting',
        ... )
        >>> profile = ProfileHistogram({'abc': 0.7, 'bac': 0.3}, {'abc': [1.], 'bac': [1.]})
        >>> converges(profile)
        True
    """
    pass
