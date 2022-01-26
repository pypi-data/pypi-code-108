from math import radians, cos, sin, asin, sqrt
from typing import Union

import numpy as np
import scipy.interpolate as si
from numpy.linalg import norm


def calc_unit_vector(v: Union[list, np.ndarray]) -> np.ndarray:
    """ Returns the unit vector of the given vector v

    Parameters
    ----------
    v : array_like
        Vector of which the unit vector should be calculated
    """
    return v / np.linalg.norm(v)


def calc_angle_between(v1: Union[list, np.ndarray], v2: Union[list, np.ndarray]) -> np.ndarray:
    """ Returns the angle in radians between vectors v1 and v2

    Parameters
    ----------
    v1 : array_like
        First vector
    v2 : array_like
        Second vector
    """
    v1_u = calc_unit_vector(v1)
    v2_u = calc_unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def bspline(cv, n=10000, degree=3, periodic=False):
    """ Calculate n samples on a bspline

        Parameters
        ----------
        cv: array_like
            Array ov control vertices
        n: int
            Number of samples to return
        degree: int
            Curve degree
        periodic: bool
            True - Curve is closed, False - Curve is open
        Returns
        -------
        np.ndarray

        """

    # If periodic, extend the point array by count+degree+1
    cv = np.asarray(cv)
    count = len(cv)

    if periodic:
        factor, fraction = divmod(count + degree + 1, count)
        cv = np.concatenate((cv,) * factor + (cv[:fraction],))
        count = len(cv)
        degree = np.clip(degree, 1, degree)

    # If opened, prevent degree from exceeding count-1
    else:
        degree = np.clip(degree, 1, count - 1)

    # Calculate knot vector
    kv = None
    if periodic:
        kv = np.arange(0 - degree, count + degree + degree - 1, dtype='int')
    else:
        kv = np.concatenate(([0] * degree, np.arange(count - degree + 1), [count - degree] * degree))

    # Calculate query range
    u = np.linspace(periodic, (count - degree), n)

    # Calculate result
    return np.array(si.splev(u, (kv, cv.T, degree))).T


def project_point_onto_line(line: Union[np.ndarray, list], point: Union[np.ndarray, list]) -> tuple:
    """

    Parameters
    ----------
    line: np.ndarray
        List of two points defining the line in the form of [[x1, y1],[x2, y2]]
    point: np.ndarray
        Point of which the distance perpendicular from the line should be calculated to
    Returns
    -------
    tuple
        Returns a tuple with the point where the orthogonal projections of the given points intersects the given the
        line and secondly the (perpendicular) distance to this point

    """
    if type(line) is list:
        line = np.array(line)

    if type(point) is list:
        point = np.array(point)

    p1 = line[0]
    p2 = line[1]
    p3 = point

    if np.array_equal(p1, p2):
        raise ValueError("Given line consists of two identical points!")

    d = norm(np.cross(p2 - p1, p1 - p3)) / norm(p2 - p1)

    n = p2 - p1
    n = n / norm(n, 2)

    p = p1 + n * np.dot(p3 - p1, n)

    return p, d


def is_point_within_line_projection(line: Union[np.ndarray, list], point: Union[np.ndarray, list]) -> bool:
    """ Checks whether a given points line projection falls within the points that the define the line

    Parameters
    ----------
    line: np.ndarray
        List of two points defining the line in the form of [[x1, y1],[x2, y2]]
    point: np.ndarray
        Point of which it should be determined whether the projection onto the line falls within the points that
        define the line
    Returns
    -------

    """
    if type(line) is list:
        line = np.array(line)

    if type(point) is list:
        point = np.array(point)

    p1 = line[0]
    p2 = line[1]
    p3 = point

    s = p2 - p1
    v = p3 - p1

    b = (0 <= np.inner(v, s) <= np.inner(s, s))

    return b


def haversine(lon1: float, lat1: float, lon2: float, lat2: float):
    """ Calculate the great circle distance in kilometers between two points on the earth (specified in decimal degrees)
        Source: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    Parameters
    ----------
    lon1 : float
        Longitude of first point
    lat1 : float
        Latitude of first point
    lon2 : float
        Longitude of second point
    lat2 : float
        Latitude of second point
    Returns
    -------
    float
        Distance between the points in meters

    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of earth in meters
    return c * r
