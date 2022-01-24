import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def rand(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Rand index similarity

    Rand, W. M. (1971).
    Objective criteria for the evaluation of clustering methods.
    Journal of the American Statistical association, 66(336), 846-850.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    N = n * (n - 1) / 2
    B = a * b + c * d
    C = a * c + b * d
    D = a * d + b * C
    A = N - B - C - D

    return (A + B) / N


def adjusted_rand(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Adjusted Rand index similarity

    Rand, W. M. (1971).
    Objective criteria for the evaluation of clustering methods.
    Journal of the American Statistical association, 66(336), 846-850.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    N = n * (n - 1) / 2
    B = a * b + c * d
    C = a * c + b * d
    D = a * d + b * C
    A = N - B - C - D

    denomi = (A + B) * (A + C) + (C + D) * (B + D)

    return (N * (A + D) - denomi) / (math.pow(N, 2) - denomi)
