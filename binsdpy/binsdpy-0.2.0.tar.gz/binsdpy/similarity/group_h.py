import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def sokal_sneath4(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Sneath similarity (v4)

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

    return (a / (a + b) + a / (a + c) + d / (b + d) + d / (c + d)) / 4


def sokal_sneath5(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Sneath similarity (v5)

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

    return (a * d) / math.sqrt((a + b) * (a + c) * (b + d) * (c + d))


def rogot_goldberg(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Rogot-Goldberg

    Rogot, E., & Goldberg, I. D. (1966).
    A proposed index for measuring agreement in test-retest studies.
    Journal of chronic diseases, 19(9), 991-1006.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a / (2 * a + b + c)) + (d / (2 * d + b + c))


def baroni_urbani_buser1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Baroni-Urbani similarity (v1)

    Baroni-Urbani, C., & Buser, M. W. (1976).
    Similarity of binary data.
    Systematic Zoology, 25(3), 251-259.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (math.sqrt(a * d) + a) / (math.sqrt(a * d) + a + b + c)


def peirce3(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Peirce similarity (v3)

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

    return (a * b + b * c) / (a * b + 2 * b * c + c * d)


def hawkins_dotson(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Hawkins-Dotson

    Hawkins, R. P., & Dotson, V. A. (1973).
    Reliability Scores That Delude: An Alice in Wonderland Trip Through the Misleading Characteristics of Inter-Observer Agreement Scores in Interval Recording.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return ((a / (a + b + c) + (d / (b + c + d)))) / 2


def tarantula(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Tarantula similarity

    Jones, J. A., & Harrold, M. J. (2005, November).
    Empirical evaluation of the tarantula automatic fault-localization technique.
    In Proceedings of the 20th IEEE/ACM international Conference on Automated software engineering (pp. 273-282).

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (a * (c + d)) / (c * (a + b))


def harris_lahey(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Harris-Lahey similarity

    Harris, F. C., & Lahey, B. B. (1978).
    A method for combining occurrence and nonoccurrence interobserver agreement scores.
    Journal of Applied Behavior Analysis, 11(4), 523-527.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return ((a * (2 * d + b + c)) / (2 * (a + b + c))) + (
        (d * (2 * a + b + c) / (2 * (b + c + d)))
    )


def forbes1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Forbesi similarity (v1)

    Forbes, S. A. (1907).
    On the local distribution of certain Illinois fishes: an essay in statistical ecology (Vol. 7).
    Illinois State Laboratory of Natural History.

    Forbes, S. A. (1925).
    Method of determining and measuring the associative relations of species.
    Science, 61(1585), 518-524.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (n * a) / ((a + b) * (a + c))


def baroni_urbani_buser2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Baroni-Urbani similarity (v1)

    Baroni-Urbani, C., & Buser, M. W. (1976).
    Similarity of binary data.
    Systematic Zoology, 25(3), 251-259.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (math.sqrt(a * d) + a - b - c) / (math.sqrt(a * d) + a + b + c)


def fossum(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Fossum similarity

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (n * math.pow(a - 0.5, 2)) / math.sqrt((a + b) * (a + c))


def forbes2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Forbesi similarity (v2)

    Forbes, S. A. (1907).
    On the local distribution of certain Illinois fishes: an essay in statistical ecology (Vol. 7).
    Illinois State Laboratory of Natural History.

    Forbes, S. A. (1925).
    Method of determining and measuring the associative relations of species.
    Science, 61(1585), 518-524.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (n * a - (a + b) * (a + c)) / (n * min(a + b, a + c) - (a + b) * (a + c))


def eyraud(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Eyraud similarity

    Eyraud, H. (1936).
    Les principes de la mesure des correlations.
    Ann. Univ. Lyon, III. Ser., Sect. A, 1(30-47), 111.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (math.pow(n, 2) + (n * a - (a + b) * (a + c))) / (
        (a + b) * (a + c) * (b + d) * (c + d)
    )


def tarwid(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Tarwid similarity

    Tarwid, K. (1960).
    Szacowanie zbieznosci nisz ekologicznych gatunkow droga oceny prawdopodobienstwa spotykania sie ich w polowach.
    Ecol Polska B (6), 115-130.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return (n * a - (a + b) * (a + c)) / (n * a + (a + b) * (a + c))


def goodman_kruskal1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Goodman-Kruskal similarity (v1)

    Goodman, L. A., & Kruskal, W. H. (1979).
    Measures of association for cross classifications.
    Measures of association for cross classifications, 2-34.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    p1 = max(a, b) + max(c, d) + max(a, c) + max(d, b)
    p2 = max(a + c, b + d) + max(a + b, c + d)

    return (p1 - p2) / (2 * n - p2)


def anderberg(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Anderberg similarity

    Anderberg, M. R. (2014).
    Cluster analysis for applications: probability and mathematical statistics: a series of monographs and textbooks (Vol. 19).
    Academic press.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    p1 = max(a, b) + max(c, d) + max(a, c) + max(d, b)
    p2 = max(a + c, b + d) + max(a + b, c + d)

    return (p1 - p2) / (2 * n)


def goodman_kruskal2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Goodman-Kruskal similarity (v2)

    Goodman, L. A., & Kruskal, W. H. (1979).
    Measures of association for cross classifications.
    Measures of association for cross classifications, 2-34.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    return (2 * min(a, d) - b - c) / (2 * min(a, d) + b + c)


def gilbert_wells(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Gilbert-Wells similarity

    Gilbert, G. K. (1884).
    Finley's tornado predictions. American Meteorological Journal.
    A Monthly Review of Meteorology and Allied Branches of Study (1884-1896), 1(5), 166.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, d = operational_taxonomic_units(x, y)

    n = a + b + c + d

    return math.log(a) - math.log(n) - math.log((a + b) / n) - math.log((a + c) / n)


def consonni_todeschini2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Consonni and Todeschini (v2)

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

    n = a + b + c + d

    return (math.log(1 + n) - math.log(1 + b + c)) / math.log(1 + n)
