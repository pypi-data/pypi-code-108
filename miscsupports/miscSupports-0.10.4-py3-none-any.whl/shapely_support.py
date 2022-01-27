import numpy as np


def meters_to_km_miles(area):
    """
    Meters are recorded as Cartesian Square Miles within shapely and this method will return both the square km and
    square Miles as a list

    :param area: Cartesian Square Miles area
    :return: list of [km_sq, Miles_sq]
    :rtype: list[float, float]
    """
    kmsq = area / 1000000
    return [kmsq, kmsq / 2.59]


def shapely_points_to_array(points_list):
    """Convert Shapely cords to a ContourObject readable numpy array"""
    return np.array([[cord] for cord in points_list])
