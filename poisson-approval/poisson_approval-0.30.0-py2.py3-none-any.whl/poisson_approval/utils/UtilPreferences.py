def is_hater(weak_order):
    """Whether a weak order represents a "hater".

    Parameters
    ----------
    weak_order : str
        A weak order, e.g. ``'a>b~c'``, ``'a~b>c'``, etc.

    Returns
    -------
    bool
        True iff the weak order is of the form ``'a~b>c'``.

    Examples
    --------
        >>> is_hater('a~b>c')
        True
    """
    return weak_order[3] == '>'


def is_lover(weak_order):
    """Whether a weak order represents a "lover".

    Parameters
    ----------
    weak_order : str
        A weak order, e.g. ``'a>b~c'``, ``'a~b>c'``, etc.

    Returns
    -------
    bool
        True iff the weak order is of the form ``'a>b~c'``.

    Examples
    --------
        >>> is_lover('a>b~c')
        True
    """
    return weak_order[1] == '>'


def is_weak_order(o):
    """Whether an object is a weak order.

    Parameters
    ----------
    o : object

    Returns
    -------
    bool
        True iff `o` is a string that represent a weak order, i.e. of the form ``'a>b~c'`` (lover) or ``'a~b>c'``
        (hater).

    Examples
    --------
        >>> is_weak_order('a>b~c')
        True
        >>> is_weak_order('a>b~')
        False
        >>> is_weak_order(42)
        False
    """
    return isinstance(o, str) and len(o) == 5 and {o[1], o[3]} == {'>', '~'}


def sort_weak_order(weak_order):
    """Put a weak order in normalized format (with the indifferent candidates sorted alphabetically).

    Parameters
    ----------
    weak_order : str
        A weak order, e.g. ``'a>b~c'``, ``'a~b>c'``, etc.

    Returns
    -------
    str
        The same weak order in normalized format.

    Examples
    --------
        >>> sort_weak_order('a>c~b')
        'a>b~c'
        >>> sort_weak_order('b~a>c')
        'a~b>c'
    """
    if is_lover(weak_order):
        return weak_order[0] + '>' + '~'.join(sorted([weak_order[2], weak_order[4]]))
    else:
        return '~'.join(sorted([weak_order[0], weak_order[2]])) + '>' + weak_order[4]


def d_candidate_ordinal_utility(order):
    """Ordinal utilities of the candidates.

    Parameters
    ----------
    order : str
        For example ``'abc'`` (ranking) or ``'a~b>c'`` (weak order).

    Returns
    -------
    dict
        Key: candidate. Value: an ordinal utility.

    Examples
    --------
        >>> d_candidate_ordinal_utility('abc')
        {'a': 1, 'b': 0.5, 'c': 0}
        >>> d_candidate_ordinal_utility('a>b~c')
        {'a': 1, 'b': 0, 'c': 0}
        >>> d_candidate_ordinal_utility('a~b>c')
        {'a': 1, 'b': 1, 'c': 0}
    """
    if is_weak_order(order):
        if is_lover(order):
            return {order[0]: 1, order[2]: 0, order[4]: 0}
        else:
            return {order[0]: 1, order[2]: 1, order[4]: 0}
    else:
        return {order[0]: 1, order[1]: .5, order[2]: 0}
