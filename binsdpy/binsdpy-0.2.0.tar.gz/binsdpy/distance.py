import math

from .utils import operational_taxonomic_units, BinaryFeatureVector


def hamming(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Hamming distance

    Hamming, R. W. (1950).
    Error detecting and error correcting codes.
    The Bell system technical journal, 29(2), 147-160.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return b + c


def euclid(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Euclidean distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return math.sqrt(b + c)


def squared_euclid(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Squared euclidean distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return math.sqrt(math.pow(b + c, 2))


def canberra(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Canberra distance

    Lance, G. N., & Williams, W. T. (1966).
    Computer programs for hierarchical polythetic classification (“similarity analyses”).
    The Computer Journal, 9(1), 60-64.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return b + c


def manhattan(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Manhattan distance

    Same as:
        Cityblock distance
        Minkowski distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return b + c


def cityblock(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Cityblock distance

    Same as:
        Manhattan distance
        Minkowski distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """

    _, b, c, _ = operational_taxonomic_units(x, y)

    return b + c


def minkowski(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Minkowski distance

    Same as:
        Manhattan distance
        Cityblock distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    _, b, c, _ = operational_taxonomic_units(x, y)

    return b + c


def mean_manhattan(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Mean manhattan distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (b + c) / (a + b + c + d)


def vari(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Vari distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (b + c) / (4 * (a + b + c + d))


def size_difference(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Size difference distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return math.pow(b + c, 2) / math.pow(a + b + c + d, 2)


def shape_difference(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Shape difference distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (n * (b + c) - math.pow(b + c, 2)) / math.pow(n, 2)


def pattern_difference(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Pattern difference distance

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (4 * b * c) / math.pow(a + b + c + d, 2)


def lance_williams(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Lance-Williams distance

    Same as:
        Bray-Curtis distance

    Lance, G. N., & Williams, W. T. (1967).
    A general theory of classificatory sorting strategies: 1. Hierarchical systems.
    The computer journal, 9(4), 373-380.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (b + c) / (2 * a + b + c)


def bray_curtis(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Bray-Curtis distance

    Same as:
        Lance-Williams distance

    Bray, J. R., & Curtis, J. T. (1957).
    An ordination of the upland forest communities of southern Wisconsin.
    Ecological monographs, 27(4), 326-349.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (b + c) / (2 * a + b + c)


def hellinger(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Hellinger distance

    Hellinger, E. (1909).
    Neue begründung der theorie quadratischer formen von unendlichvielen veränderlichen.
    Journal für die reine und angewandte Mathematik, 1909(136), 210-271.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return 2 * math.sqrt((1 - (a / (math.sqrt((a + b) * (a + c))))))


def chord(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Hellinger distance

    Orlóci, L. (1967).
    An agglomerative method for classification of plant communities.
    The Journal of Ecology, 193-206.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return math.sqrt(2 * (1 - (a / (math.sqrt((a + b) * (a + c))))))


def yuleq(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Yule Q distance

    Yule, G. U., & Kendall, M. G. (1958).
    An introduction to the theory of statistics (No. 311 Y85).

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: distance of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (2 * b * c) / (a * d + b * c)



