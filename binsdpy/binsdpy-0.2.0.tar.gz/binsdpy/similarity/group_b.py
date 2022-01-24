import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def russell_rao(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Russel-Rao similarity

    Russell, P. F., & Rao, T. R. (1940).
    On habitat and association of species of anopheline larvae in south-eastern Madras.
    Journal of the Malaria Institute of India, 3(1).

    Rao, C. R. (1948).
    The utilization of multiple measurements in problems of biological classification.
    Journal of the Royal Statistical Society. Series B (Methodological), 10(2), 159-203.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return a / (a + b + c + d)


def consonni_todeschini3(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Consonni and Todeschini (v3)

    Consonni, V., & Todeschini, R. (2012).
    New similarity coefficients for binary data.
    Match-Communications in Mathematical and Computer Chemistry, 68(2), 581.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return math.log(1 + a) / math.log(1 + a + b + c + d)