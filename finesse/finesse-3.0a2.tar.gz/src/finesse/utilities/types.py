import typing


def issubtype(cls, annotation):
    """Check that `cls` is compatible with typing annotation `annotation`.

    Parameters
    ----------
    cls : type
        The type to check for membership of `annotation`.

    annotation : :mod:`typing` type
        The annotation to check.
    """
    if typing.get_origin(annotation) is None:
        # This is not a typing type, but a normal Python type.
        return annotation is cls
    # Maybe a generic.
    return any(issubtype(cls, arg) for arg in typing.get_args(annotation))
