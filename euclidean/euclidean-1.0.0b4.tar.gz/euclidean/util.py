from collections import deque


def normalize_coefficients(*coefficients):
    """Normalize coefficients such that all equivalents can be directly compared.

    :raises ValueError: If all coefficients are 0.

    :param *coefficients: The unnormalized coefficients.
    :rtype: Tuple[float, ...]
    """
    divisor = 0
    normalized = deque()
    for c in reversed(coefficients):
        if divisor:
            normalized.appendleft(c / divisor)
        elif c != 0:
            divisor = c
            normalized.appendleft(1)
        else:
            normalized.appendleft(0)

    if divisor == 0:
        raise ValueError("All coefficients are 0.")

    return tuple(normalized)


def methods(*meths):
    """A class decorator for attaching generic methods to a class.

    .. note:

        The first argument of the function will be bound to self instance.

    :param *meths: Raw functions to be bound to a class.
    """

    def decorator(cls):
        for meth in meths:
            setattr(cls, meth.__name__, meth)
        return cls

    return decorator
