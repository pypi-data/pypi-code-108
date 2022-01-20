"""util.py -- Utility module for the buildtools project."""


def is_nonempty_str(obj):
    return isinstance(obj, str) and len(obj) > 0


def hasattr_nonempty_str(obj, attribute):
    return hasattr(obj, attribute) and is_nonempty_str(getattr(obj, attribute))
