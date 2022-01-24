from poisson_approval import ProfileOrdinal


def is_not_condorcet(profile):
    """
    Whether a profile has no Condorcet winner.

    Parameters
    ----------
    profile : Profile
        A profile.

    Returns
    -------
    bool
        True if the profile has no Condorcet winner.

    Examples
    --------
        >>> profile = ProfileOrdinal({'abc': 0.3, 'bca': 0.4, 'cab': 0.3})
        >>> is_not_condorcet(profile)
        True

    This is just another syntax for:

        >>> profile.is_profile_condorcet == 0.0
        True

    This function is especially convenient when a test function is required, for example when using
    :func:`~poisson_approval.utils.Util.probability`.
    """
    return profile.is_profile_condorcet == 0.0
