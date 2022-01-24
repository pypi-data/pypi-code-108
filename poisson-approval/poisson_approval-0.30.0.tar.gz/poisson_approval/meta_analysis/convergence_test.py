from poisson_approval.profiles.ProfileHistogram import ProfileHistogram
from poisson_approval.utils.Util import one_over_log_t_plus_one


def convergence_test(n_max_episodes, init='sincere',
                     perception_update_ratio=one_over_log_t_plus_one,
                     ballot_update_ratio=one_over_log_t_plus_one,
                     meth='fictitious_play'):
    """
    Create a convergence test.

    Parameters
    ----------
    n_max_episodes : int
        Maximum number of episodes for the fictitious play / iterated voting.
    init : Strategy or TauVector or str
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play`
        or :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    perception_update_ratio,ballot_update_ratio : callable or Number
        Cf. :meth:`~poisson_approval.ProfileCardinal.fictitious_play`
        or :meth:`~poisson_approval.ProfileCardinal.iterated_voting`.
    meth : str
        The name of the method (``'fictitious_play'`` or ``'iterated_voting'``).

    Returns
    -------
    callable
        A callable. Input: a profile. Output: a bool, which is True if the fictitious play / iterated
        voting converges (within the specified number of episodes).

    Examples
    --------
        >>> converges = convergence_test(n_max_episodes=10)
        >>> profile = ProfileHistogram({'abc': 0.7, 'bac': 0.3}, {'abc': [1.], 'bac': [1.]})
        >>> converges(profile)
        False

    This function is especially convenient when a test function is required, for example when using
    :func:`~poisson_approval.utils.Util.probability`.
    """
    def converges(profile):
        results = getattr(profile, meth)(init=init, n_max_episodes=n_max_episodes,
                                         perception_update_ratio=perception_update_ratio,
                                         ballot_update_ratio=ballot_update_ratio)
        return results['converges']
    return converges
