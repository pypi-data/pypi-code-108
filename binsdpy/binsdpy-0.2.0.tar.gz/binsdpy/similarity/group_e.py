import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def scott(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Scott similarity

    Scott, W. A. (1955).
    Reliability of content analysis: The case of nominal scale coding.
    Public opinion quarterly, 321-325.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (4 * a * d - math.pow(b + c, 2)) / ((2 * a + b + c) * (2 + d + b + c))


def tetrachoric(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Tetrachoric similarity

    Peirce, C. S. (1884).
    The numerical measure of the success of predictions.
    Science, (93), 453-454.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return math.cos(180 / (1 + math.sqrt((a * d) / (b * c))))


def odds_ratio(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Odds ratio
    
    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a * d) / (b * c)



