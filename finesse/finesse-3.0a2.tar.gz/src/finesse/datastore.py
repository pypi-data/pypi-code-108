"""Finesse datastore tools.

The datastore is intended for objects that should be cached during the execution of the
current Python kernel. Code typically uses this instead of the more bug-prone singleton
pattern (see #260).
"""

_DATASTORE = {}


def invalidate(key=None):
    """Invalidate the datastore.

    Parameters
    ----------
    key : str, optional
        The datastore key to invalidate. If None, the whole datastore is invalidated.
    """
    if key is None:
        _DATASTORE.clear()
    else:
        del _DATASTORE[key]


def getfield(key):
    """Get value with key `key`.

    Parameters
    ----------
    key : any
        The key.

    Returns
    -------
    any
        The value.
    """
    return _DATASTORE[key]


def setfield(key, value, overwrite=False):
    """Initialize a field with key `key` and value `value`.

    Parameters
    ----------
    key : any
        The key. If it already exists in the datastore,
    value : any
        The value.

    Returns
    -------
    any
        The value.
    """
    if not overwrite and hasfield(key):
        raise ValueError(
            f"{repr(key)} already exists in datastore. Set overwrite=True to force."
        )
    _DATASTORE[key] = value
    return getfield(key)


def hasfield(key):
    """Determine if the datastore key `key` exists.

    Parameters
    ----------
    key : any
        The singeton class to check.

    Returns
    -------
    bool
        True if `key` exists, False otherwise.
    """
    return key in _DATASTORE


def init_singleton(cls, *args, **kwargs):
    """Instantiate `cls` and return the object for the current and future calls.

    Parameters
    ----------
    cls : type
        The singeton class to retrieve. If `cls` has already been instantiated, the
        existing instance is returned and `args` and `kwargs` are ignored.

    Other Parameters
    ----------------
    args, kwargs
        Positional and keyword arguments to pass to the `cls` call, to use if `cls` is
        not yet instantiated.

    Returns
    -------
    object
        The instantiated singleton.
    """
    if not hasfield(cls):
        setfield(cls, cls(*args, **kwargs))
    return _DATASTORE[cls]
