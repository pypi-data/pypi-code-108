import math

from binsdpy.utils import operational_taxonomic_units, BinaryFeatureVector


def dice1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Dice 1 similarity (v1)

    Dice, L. R. (1945).
    Measures of the amount of ecologic association between species.
    Ecology, 26(3), 297-302    

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, _, _ = operational_taxonomic_units(x, y)

    return a / (a + b)


def dice2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Dice 2 similarity (v2)

    Dice, L. R. (1945).
    Measures of the amount of ecologic association between species.
    Ecology, 26(3), 297-302    

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, _, c, _ = operational_taxonomic_units(x, y)

    return a / (a + c)


def jaccard(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Jaccard similarity

    Same as:
        Tanimoto coefficient
    
    Jaccard, P. (1908).
    Nouvelles recherches sur la distribution florale.
    Bull. Soc. Vaud. Sci. Nat., 44, 223-270.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / (a + b + c)


def sw_jaccard(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """SW Jaccard similarity

    Jaccard, P. (1908).
    Nouvelles recherches sur la distribution florale.
    Bull. Soc. Vaud. Sci. Nat., 44, 223-270.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (3 * a) / (3 * a + b + c)


def gleason(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Gleason similarity

    Gleason, H. A. (1920). 
    Some applications of the quadrat method. 
    Bulletin of the Torrey Botanical Club, 47(1), 21-33.  

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (2 * a) / (2 * a + b + c)


def kulczynski1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Kulczynski similarity (v1)

    Stanisław Kulczynśki. (1927).
    Die pflanzenassoziationen der pieninen.
    Bulletin International de l'Academie Polonaise des Sciences et des Lettres, Classe des Sciences Mathematiques et Naturelles, B (Sciences Naturelles), pages 57–203.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / (b + c)


def kulczynski2(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Kulczynski similarity (v2)

    Stanisław Kulczynśki. (1927).
    Die pflanzenassoziationen der pieninen.
    Bulletin International de l'Academie Polonaise des Sciences et des Lettres, Classe des Sciences Mathematiques et Naturelles, B (Sciences Naturelles), pages 57–203.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return 1/2 * (a / (a + b) + a / (a + c))


def ochiai(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Ochiai similarity

    Same as:
        Cosine similarity
        Otsuka similarity
    
    Ochiai, A. (1957).
    Zoogeographic studies on the soleoid fishes found in Japan and its neighbouring regions.
    Bulletin of Japanese Society of Scientific Fisheries, 22, 526-530.
        
    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """

    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / math.sqrt((a + b) * (a + c))


def braun_blanquet(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Braun-Banquet similarity

    Braun-Blanquet, J. (1932).
    Plant sociology. The study of plant communities. Plant sociology.
    The study of plant communities. First ed.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / max(a + b, a + c)


def simpson(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Simpson similarity

    Simpson, E. H. (1949).
    Measurement of diversity.
    Nature, 163(4148), 688-688.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / min(a + b, a + c)


def sorgenfrei(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sorgenfrei similarity

    Sorgenfrei, T. (1958).
    Molluscan Assemblages from the Marine Middle Miocene of South Jutland and their Environments. Vol. II.
    Danmarks Geologiske Undersøgelse II. Række, 79, 356-503.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return math.pow(a, 2) / ((a + b) * (a + c))


def mountford(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Mountford similarity

    Mountford, M. D. (1962).
    An index of similarity and its application to classificatory problem.
    Progress in soil zoology"(ed. Murphy, PW), 43-50.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (2 * a) / (a * b + a * c + 2 * b * c)


def fager_mcgowan(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Fager-McGowan similarity

    Fager, E. W. (1957).
    Determination and analysis of recurrent groups.
    Ecology, 38(4), 586-595.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / math.sqrt((a + b) * (a + c)) - max(a + b, a + c) / 2


def sokal_sneath1(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Sokal-Sneath similarity (v1)
    
    Sneath, P. H., & Sokal, R. R. (1973).
    Numerical taxonomy.
    The principles and practice of numerical classification.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / (a + 2 * b + 2 * c)


def mcconnaughey(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """McConnaughey similarity

    McConnaughey, B. H. (1964).
    The determination and analysis of plankton communities.
    Lembaga Penelitian Laut.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (math.pow(a, 2) - b * c) / ((a + b) * (a + c))


def johnson(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Johnson similarity

    Johnson, S. C. (1967).
    Hierarchical clustering schemes.
    Psychometrika, 32(3), 241-254.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return a / (a + b) + a / (a + c)


def van_der_maarel(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Van der Maarel similarity

    Van der Maarel, E. (1969).
    On the use of ordination models in phytosociology.
    Vegetatio, 19(1), 21-46.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (2 * a - b - c) / (2 * a + b + c)


def consonni_todeschini4(x: BinaryFeatureVector, y: BinaryFeatureVector) -> float:
    """Consonni and Todeschini (v4)

    Consonni, V., & Todeschini, R. (2012).
    New similarity coefficients for binary data.
    Match-Communications in Mathematical and Computer Chemistry, 68(2), 581.

    Args:
        x (BinaryFeatureVector): binary feature vector
        y (BinaryFeatureVector): binary feature vector

    Returns:
        float: similarity of given vectors
    """
    a, b, c, _ = operational_taxonomic_units(x, y)

    return (2 * a - b - c) / (2 * a + b + c)