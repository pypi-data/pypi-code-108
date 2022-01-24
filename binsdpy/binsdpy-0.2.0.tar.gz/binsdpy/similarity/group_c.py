import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def sokal_michener(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Michener similarity
    
    Sokal, R. R. (1958).
    A statistical method for evaluating systematic relationships.
    Univ. Kansas, Sci. Bull., 38, 1409-1438.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d) / a + b + c + d


def rogers_tanimoto(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Roges-Tanimoto similarity

    Rogers, D. J., & Tanimoto, T. T. (1960).
    A computer program for classifying plants.
    Science, 132(3434), 1115-1118.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d) / (a + 2 * (b + c) + d)


def sokal_sneath2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Sneath similarity (v2)
    
    Sneath, P. H., & Sokal, R. R. (1973).
    Numerical taxonomy.
    The principles and practice of numerical classification.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (2 * (a + d)) / (2 * a + b + c + 2 * d)


def sokal_sneath3(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Sneath similarity (v3)
    
    Sneath, P. H., & Sokal, R. R. (1973).
    Numerical taxonomy.
    The principles and practice of numerical classification.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d) / (b + c)


def faith(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Faith similarity

    Faith, D. P. (1983).
    Asymmetric binary similarity measures.
    Oecologia, 57(3), 287-290.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + 0.5 * d) / (a + b + c + d)


def gower_legendre(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Gower-Legendre similarity

    Gower, J. C., & Legendre, P. (1986).
    Metric and Euclidean properties of dissimilarity coefficients.
    Journal of classification, 3(1), 5-48.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d) / (a + 0.5 * (b + c) + d)


def gower(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Gower similarity
    
    Gower, J. C. (1971).
    A general coefficient of similarity and some of its properties.
    Biometrics, 857-871.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d) / math.sqrt((a + b) * (a + c) * (b + d) * (c + d))


def austin_colwell(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Austin-Colwell similarity
    
    Austin, B., & Colwell, R. R. (1977).
    Evaluation of some coefficients for use in numerical taxonomy of microorganisms.
    International Journal of Systematic and Evolutionary Microbiology, 27(3), 204-210.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return 2 / math.pi * math.asin(math.sqrt((a + d) / (a + b + c + d)))


def consonni_todeschini1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Consonni and Todeschini similarity (v1)

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

    return math.log(1 + a + d) / math.log(1 + a + b + c + d)


def hamman(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Hamman similarity

    Hamann, U. (1961).
    Merkmalsbestand und verwandtschaftsbeziehungen der farinosae: ein beitrag zum system der monokotyledonen.
    Willdenowia, 639-768.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a + d - b - c) / a + b + c + d