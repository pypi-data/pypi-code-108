import typing

STR_BOOL = {
    'y': True,
    'yes': True,
    't': True,
    'true': True,
    'on': True,
    '1': True,

    'n': False,
    'no': False,
    'f': False,
    'false': False,
    'off': False,
    '0': False,
}


def to_bool(val: typing.Any) -> bool:
    """Convert a representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    >>> to_bool(True)
    True

    >>> to_bool('y')
    True

    >>> to_bool('yes')
    True

    >>> to_bool('t')
    True

    >>> to_bool('true')
    True

    >>> to_bool('on')
    True

    >>> to_bool('1')
    True

    >>> to_bool(1)
    True

    >>> to_bool(False)
    False

    >>> to_bool('n')
    False

    >>> to_bool('no')
    False

    >>> to_bool('f')
    False

    >>> to_bool('false')
    False

    >>> to_bool('off')
    False

    >>> to_bool('0')
    False

    >>> to_bool(0)
    False

    >>> to_bool(None)
    False

    >>> to_bool('other')
    Traceback (most recent call last):
    ...
    ValueError: invalid truth value 'other'


    """
    if val is None:
        return False
    if isinstance(val, (int, float, bool)):
        return bool(val)

    val = str(val).lower()
    try:
        return STR_BOOL[val]
    except KeyError:
        raise ValueError(f"invalid truth value {val!r}")