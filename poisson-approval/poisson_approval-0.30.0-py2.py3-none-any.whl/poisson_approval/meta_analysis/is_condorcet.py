from poisson_approval import ProfileOrdinal


def is_condorcet(profile):
    """
    Whether a profile has one Condorcet winner.

    Parameters
    ----------
    profile : Profile
        A profile.

    Returns
    -------
    bool
        True if the profile has one Condorcet winner.

    Examples
    --------
        >>> profile = ProfileOrdinal({'abc': 0.3, 'bac': 0.4, 'cab': 0.3})
        >>> is_condorcet(profile)
        True

    This is just another syntax for:

        >>> profile.is_profile_condorcet == 1.0
        True

    This function is especially convenient when a test function is required, for example when using
    :func:`~poisson_approval.utils.Util.probability`.
    """
    return profile.is_profile_condorcet == 1.0
