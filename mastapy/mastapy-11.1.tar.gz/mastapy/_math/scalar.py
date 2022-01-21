import math
from typing import Union


NUM = Union[float, int]


def clamp(n: NUM, nmin: NUM, nmax: NUM) -> NUM:
    '''Clamp a value to between a minimum and maximum.

    Equivalent to min(vmax, max(vmin, v))

    Args:
        n (Iterable[NUM]): value to clamp
        nmin (NUM): Lower end of the range into which to constrain n
        nmax (NUM): Upper end of the range into which to constrain n

    Returns:
        NUM
    '''

    return min(nmax, max(nmin, n))


def sign(n: NUM) -> float:
    ''' Extract the sign from a number.

    Returns -1.0 if n is less than 0.0, 0.0 if n is equal to 0.0,
    and +1.0 if n is greater than 0.0.

    Args:
        n (NUM): Number from which to extract the sign.

    Returns:
        float
    '''

    if n < 0.0:
        return -1.0
    elif n > 0.0:
        return 1.0
    else:
        return 0.0


def fract(n: float) -> float:
    ''' Extraction of the fractional part of a number.

    Args:
        n (float): Number to evaluate.

    Returns:
        float
    '''

    return n - math.floor(n)


def step(edge: NUM, n: NUM) -> float:
    ''' Step function.

    0.0 is returned if n < edge, and 1.0 is returned otherwise.

    Args:
        edge (NUM): Edge of the step function.
        n (NUM): Number to evaluate.

    Returns:
        float
    '''

    return 0.0 if edge > n else 1.0


def smoothstep(edge0: NUM, edge1: NUM, n: NUM) -> float:
    ''' Hermite interpolation between two values.

    Args:
        edge0 (NUM): Lower edge of the hermite function.
        edge1 (NUM): Upper edge of the hermite function.
        n (NUM): Number to interpolate.

    Returns:
        float
    '''

    t = clamp((float(n) - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def approximately_equal(n: NUM, m: NUM, epsilon: NUM = 0.001) -> bool:
    ''' Approximately equal comparison.

    Args:
        n (NUM): First number to compare
        m (NUM): Second number to compare
        epsilon (NUM, default=0.001): Sensitivity of the equals operation

    Returns:
        bool
    '''

    return abs(n - m) < epsilon
