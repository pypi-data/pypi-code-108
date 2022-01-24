from poisson_approval.constants.basic_constants import APPROVAL, PLURALITY, ANTI_PLURALITY, \
    CANDIDATES, PAIRS_WITHOUT_INVERSIONS, BALLOTS_WITHOUT_INVERSIONS_SORTED_ALPHABETICAL


def allowed_ballots(voting_rule=APPROVAL):
    """Allowed ballots in a voting rule.

    Parameters
    ----------
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.

    Returns
    -------
    list
        The list of all allowed ballots.

    Examples
    --------
        >>> allowed_ballots(APPROVAL)
        ['a', 'ab', 'ac', 'b', 'bc', 'c']
        >>> allowed_ballots(PLURALITY)
        ['a', 'b', 'c']
        >>> allowed_ballots(ANTI_PLURALITY)
        ['ab', 'ac', 'bc']
    """
    if voting_rule == APPROVAL:
        return BALLOTS_WITHOUT_INVERSIONS_SORTED_ALPHABETICAL
    elif voting_rule == PLURALITY:
        return CANDIDATES
    elif voting_rule == ANTI_PLURALITY:
        return PAIRS_WITHOUT_INVERSIONS
    else:
        raise NotImplementedError


def ballot_one(ranking):
    """Ballot for the voter's preferred candidate.

    Parameters
    ----------
    ranking : str
        A ranking.

    Returns
    -------
    str
        The first candidate.

    Examples
    --------
        >>> ballot_one('abc')
        'a'
    """
    return ranking[0]


def ballot_two(ranking):
    """Ballot for the voter's second most-liked candidate.

    Parameters
    ----------
    ranking : str
        A ranking.

    Returns
    -------
    str
        The second candidate.

    Examples
    --------
        >>> ballot_two('abc')
        'b'
    """
    return ranking[1]


def ballot_one_two(ranking):
    """Ballot for the voter's two preferred candidates.

    Parameters
    ----------
    ranking : str
        A ranking.

    Returns
    -------
    str
        The ballot with the two first candidates.

    Examples
    --------
        >>> ballot_one_two('abc')
        'ab'
        >>> ballot_one_two('bac')
        'ab'
    """
    return sort_ballot(ranking[:2])


def ballot_one_three(ranking):
    """Ballot for the voter's first and third candidates.

    Parameters
    ----------
    ranking : str
        A ranking.

    Returns
    -------
    str
        The ballot with the first and third candidates.

    Examples
    --------
        >>> ballot_one_three('abc')
        'ac'
        >>> ballot_one_three('cba')
        'ac'
    """
    return sort_ballot(ranking[0] + ranking[2])


def ballot_low_u(ranking, voting_rule):
    """Ballot chosen by the voters who have a low utility for their middle candidate.

    Parameters
    ----------
    ranking : str
        A ranking.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.

    Returns
    -------
    str
        The ballot chosen by the voters with this ranking and a low utility for their middle candidate, in case
        the response is utility-dependent.

    Examples
    --------
        >>> ballot_low_u('abc', APPROVAL)
        'a'
        >>> ballot_low_u('abc', PLURALITY)
        'a'
        >>> ballot_low_u('abc', ANTI_PLURALITY)
        'ac'
    """
    if voting_rule in {APPROVAL, PLURALITY}:
        return ballot_one(ranking)
    elif voting_rule == ANTI_PLURALITY:
        return ballot_one_three(ranking)
    else:
        raise NotImplementedError


def ballot_high_u(ranking, voting_rule):
    """Ballot chosen by the voters who have a high utility for their middle candidate.

    Parameters
    ----------
    ranking : str
        A ranking.
    voting_rule : str
        The voting rule. Possible values are ``APPROVAL``, ``PLURALITY`` and ``ANTI_PLURALITY``.

    Returns
    -------
    str
        The ballot chosen by the voters with this ranking and a high utility for their middle candidate, in case
        the response is utility-dependent.

    Examples
    --------
        >>> ballot_high_u('abc', APPROVAL)
        'ab'
        >>> ballot_high_u('abc', PLURALITY)
        'b'
        >>> ballot_high_u('abc', ANTI_PLURALITY)
        'ab'
    """
    if voting_rule in {APPROVAL, ANTI_PLURALITY}:
        return ballot_one_two(ranking)
    elif voting_rule == PLURALITY:
        return ballot_two(ranking)
    else:
        raise NotImplementedError


def sort_ballot(ballot):
    """Put a ballot in alphabetical order.

    Parameters
    ----------
    ballot : str
        A ballot, e.g. ``'a'``, ``'ab'``, ``'ba'``, etc.

    Returns
    -------
    str
        The same ballot in alphabetical order.

    Examples
    --------
        >>> sort_ballot('a')
        'a'
        >>> sort_ballot('ab')
        'ab'
        >>> sort_ballot('ba')
        'ab'
    """
    return ''.join(sorted(ballot))
