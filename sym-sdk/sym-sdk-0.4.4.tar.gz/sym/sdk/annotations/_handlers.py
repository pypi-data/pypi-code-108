def reducer(fn):
    """Reducers take in an Event and return a single value.py

    Reducer names are always prefixed with ``get_``."""
    return fn


def hook(fn):
    """Hooks allow you to alter control flow by overriding default implementations of Template steps.
    Hook names may be prefixed with ``on_`` or ``after_``.

    If a Hook name is prefixed with ``on_``, it will be executed after the :class:`~sym.sdk.events.Event` is fired
    but before the default implementation.

    If a Hook name is prefixed with ``after_``, it will be executed after the default implementation.
    """
    return fn
