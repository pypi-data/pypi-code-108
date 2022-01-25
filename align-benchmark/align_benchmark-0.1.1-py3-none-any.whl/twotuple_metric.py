"""Calculate two two-tuples ali-metric."""
# pylint: disable=

from typing import Tuple

# import math


def twotuple_metric(vec1: Tuple[int, int], vec2: Tuple[int, int]) -> float:
    """Calculate two two-tuples ali-metric.

    Args:
        vec1: two-tuples of int
        vec2: two-tuples of int

    Return:
        float metric: 1, 0.5 or 0

    >>> twotuple_metric([0, 1], [0, 1])
    1.0

    >>> twotuple_metric([0, 1], [0, 2])
    0.5

    >>> twotuple_metric([0, 1], [1, 2])
    0.0

    >>> twotuple_metric([0, 1], [0, ""])
    0.0

    return 1. * float(vec1[0] == vec2[0] and vec1[1] == vec2[1]) or 0.5 * float(vec1[0] == vec2[0] or vec1[1] == vec2[1])
    """
    # if any of vec[:2], vec2[:2] cant be cast to int, return -.0
    try:
        int(vec1[0])
        int(vec1[1])
        int(vec2[0])
        int(vec2[1])
    except ValueError:
        return 0.0

    # if vec1 == vec2:
    if vec1[0] == vec2[0] and vec1[1] == vec2[1]:
        return 1.0

    # if vec1[0] == vec2[0] or vec1[1] == vec2[1]:
    if (
        vec1[0] == vec2[0]
        and abs(vec1[1] - vec2[1]) <= 1
        or vec1[1] == vec2[1]
        and abs(vec1[0] - vec2[0]) <= 1
    ):
        return 0.5

    return 0.0
