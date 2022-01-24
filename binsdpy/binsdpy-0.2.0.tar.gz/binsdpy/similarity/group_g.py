from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def loevinger_h(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Loevinger's H

    Loevinger, J. (1948).
    The technic of homogeneous tests compared with some aspects of" scale analysis" and factor analysis.
    Psychological bulletin, 45(6), 507.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    p1 = max(a, b) + max(c, d) + max(a, c) + max(d, b)
    p2 = max(a + c, b + d) + max(a + b, c + d)

    return 1 - (b / ((a + b + c + d) * p1 * p2))
