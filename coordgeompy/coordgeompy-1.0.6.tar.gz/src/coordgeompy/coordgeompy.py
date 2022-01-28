import numpy as np


def dist_pll_lines_2d(m, b1, b2):
    """Finding the distance between two parallel lines.
    The distance between two parallel lines is the distance between the points where a perpendicular line intersects.
    This function will find that distance (d). The parameters of the function can be obtained from the equation of a parallel
    line y = mx + b.
    Parameters
    ----------
    m  : float
        slope of two parallel lines which are the same, i.e., slope of
        line 1, m1 = -(1/m2)
    b1 : float
        intercept of line 1 where y = mx + b1
    b2 : float
        intercept of line 2 where y = mx + b2
    Returns
    -------
    float
        The distance d between two parallel lines.
    Examples
    --------
    >>> dist_pll_lines_2d(3.0, 4.5, 2.5)
    0.6324
    >>> dist_pll_lines_2d(-4, 11, 23)
    2.9104
    """
    # apply corresponding values from the two parallel line equations to
    # the equation below
    if not isinstance(m, (int, float)):
        raise TypeError("m must be an integer or float")

    if not isinstance(b1, (int, float)):
        raise TypeError("b1 must be an integer or float")

    if not isinstance(b2, (int, float)):
        raise TypeError("b2 must be an integer or float")


    d = abs(b2 - b1) / np.sqrt(m ** 2 + 1)
    return d


def get_distance(x1, x2, metric="Euclidean", p=None):
    """Calculates the distance between two n dimensional vectors.
    Possible metrics include: Euclidean, Manhattan, Chebyshev, or Minkowski.
    Parameters
    ----------
    x1 : list of int or float
        The first n dimensional vector.
    x2 : list of int or float
        The second n dimensional vector.
    metric : str, default="Euclidean"
        The distance metric, must be one of "Euclidean", "Manhattan", Chebyshev,
        or "Minkowski"
    p : int, default=None
        The order of Minkowski distance to calculate.  Only required if `metric` is
        set to "Minkowski".
    Returns
    -------
    float
        The relevant distance between the two vectors.
    Examples
    --------
    >>> x1 = [1, 2, 3, 4]
    >>> x2 = [5, 6, 7, 8]
    >>> get_distance(x1, x2, metric="Euclidean")
    8
    >>> get_distance(x1, x2, metric="Manhattan")
    16
    >>> get_distance(x1, x2, metric="Chebyshev")
    4
    >>> get_distance(x1, x2, metric="Minkowski", 3)
    6.3496
    """

    # cast to lower for flexibility
    metric = metric.lower()

    # verify distance metric
    if metric not in ["euclidean", "manhattan", "chebyshev", "minkowski"]:
        raise ValueError(f"Invalid distance metric: {metric}")

    # verify that vectors are passed as python lists
    if not isinstance(x1, list) or not isinstance(x2, list):
        raise TypeError("x1 and x2 must be Python lists")

    # verify dimensions of vectors match
    if len(x1) != len(x2):
        raise TypeError("x1 and x2 must be the same length")

    # verify p if minkowski distance is metric
    if metric.lower() == "minkowski":
        if not isinstance(p, (int, float)):
            raise TypeError("p must be int or float")

    # convert to numpy arrays
    x1 = np.array(x1)
    x2 = np.array(x2)

    # check if arrays are equal if so distance is 0
    if np.array_equal(x1, x2):
        return 0
    elif metric == "euclidean":
        return np.sqrt(np.sum((np.square(x1 - x2))))
    elif metric == "manhattan":
        return np.sum(np.abs(x1 - x2))
    elif metric == "chebyshev":
        return np.max(np.abs(x1 - x2))
    elif metric == "minkowski":
        return np.power(np.sum(np.power(np.abs(x1 - x2), p)), 1 / p)


def is_intersection_3d(m1, b1, m2, b2):
    """Determines whether two infinite lines intersect in 3-dimensional space.
    Note that if two parallel lines are provided, they will be considered as NOT intersecting.
    Also note that this function expects integer values for x, y, z coordinates. Values will be rounded
    if integer values are not provided.
    This algorithm uses the following idea to test for intersection: Two (non parallel) lines intersect
    in 3d space if and only if they are coplanar.
    Parameters
    ----------
    m1 : list or tuple of floats
        This list corresponds to a 3-dimensional vector ⟨𝑚𝑥1,𝑚𝑦1,𝑚𝑧1⟩ describing the
        direction vector (or slope) of line 2. List or tuple must be of length 3.
    b1 : list or tuple of floats
        Any point on line 1. This list corresponds to a point (x1, y1, z1) that lies on line 1.
        This point must lie on line 2.
    m2 : list or tuple of floats
        This list corresponds to a 3-dimensional vector ⟨𝑚𝑥2,𝑚𝑦2,𝑚𝑧2⟩ describing the
        direction vector (or slope) of line 2.
    b2 : list or tuple of floats
        Any point on line 2. This list corresponds to a point (x2, y2, z2) that lies on line 2.
        This point must lie on line 2.
    Returns
    -------
    bool
        True if there is intersection, False if not.
    Examples
    --------
    >>> m1 = (1, 0, 0)
    >>> m2 = (0, 1, 0)
    >>> b1 = (0, 0, 0)
    >>> b2 = (0, 0, 0)
    >>> is_intersection_3d(m1, b1, m2, b2)
    True
    >>> m3 = (1, 3, -1)
    >>> m4 = (2, 1, 4)
    >>> b3 = (0, -2, 4)
    >>> b4 = (0, 3, -3)
    >>> is_intersection_3d(m3, m4, b3, b4)
    False
    """

    # Validate input
    if not isinstance(m1, (list, tuple) or not isinstance(m2, (list, tuple))):
        raise TypeError(
            "Only lists or tuples are supported. Please provide m1 & m2 as lists or tuples"
        )

    if not isinstance(b1, (list, tuple)) or not isinstance(b1, (list, tuple)):
        raise TypeError(
            "Only lists or tuples are supported. Please provide b1 & b2 as lists or tuples."
        )

    if len(m1) != 3 or len(m2) != 3 or len(b1) != 3 or len(b2) != 3:
        raise ValueError("All tuples should of length 3. Please check your inputs")

    # Ensure all values are integers
    m1 = (round(m1[0]), round(m1[1]), round(m1[2]))
    m2 = (round(m2[0]), round(m2[1]), round(m2[2]))
    b1 = (round(b1[0]), round(b1[1]), round(b1[2]))
    b2 = (round(b2[0]), round(b2[1]), round(b2[2]))

    m1 = np.array(m1)
    m2 = np.array(m2)
    b1 = np.array(b1)
    b2 = np.array(b2)

    # Check if lines are parallel
    if (m1 == m2).all():
        return False

    # Lines intersect if and only if they lie on the same plane (and are not parallel).
    x = np.cross(m1, m2)
    disp = np.array(b2) - np.array(b1)
    if np.dot(x, disp) == 0:
        return True
    else:
        return False


def is_orthogonal(m1, m2):
    """Determines whether two infinite lines are perpendicular in n-dimensional space.
    Parameters
    ----------
    m1 : list or tuple of floats
        This list corresponds to a n-dimensional vector ⟨mx1, my1, mz1, ...⟩ describing the
        direction vector of line 1.
    m2 : list or tuple of floats
        This list corresponds to a n-dimensional vector ⟨mx2, my2, mz2, ...⟩ describing the
        direction vector of line 2. Demensions of line 1 and line 2 must be equal.
    Returns
    -------
    bool
        True if there is orthogonal, False if not.
    Examples
    --------
    >>> m1 = (1, 0)
    >>> m2 = (0, 1)
    >>> is_orthogonal(m1, m2)
    True
    >>> m3 = (0, 0, 1)
    >>> m4 = (1, 1, 1)
    >>> is_orthogonal(m3, m4)
    False
    """
    # Validate input
    if not isinstance(m1, (list, tuple) or not isinstance(m2, (list, tuple))):
        raise TypeError("m1 and m2 must be lists or tuples")

    if len(m1) < 1 or len(m2) < 1:
        raise ValueError("The dimension of inputs must be at least 2")

    # Checking if m1 and m2 have the same dimension
    if len(m1) != len(m2):
        raise ValueError("m1 and m2 must be the same length")

    line1 = np.array(m1)
    line2 = np.array(m2)
    if round(np.dot(line1, line2), 10) == 0:
        return True
    else:
        return False