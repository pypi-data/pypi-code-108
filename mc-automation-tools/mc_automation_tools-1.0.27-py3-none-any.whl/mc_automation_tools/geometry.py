"""This module provide geometry functionality utils"""
from shapely.geometry import Polygon


def get_polygon_area(coordinates):
    """
    This method calculate area
    :param coordinates: list of points represented as list [x.y]
    :return: float in meters
    """
    polygon = process_polygon(coordinates)
    area = polygon.area
    return area


def bounding_box(points):
    """
    The function calculates bounding_box from the coordinates. XY - Min , XY - Max
    :param points: coordinates list
    :return: List of bounding box.
    """
    x_coordinates, y_coordinates = zip(*points)
    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]


def get_polygon_perimeter(coordinates):
    """
    This method calculate perimeter
    :param coordinates: list of points represented as list [x.y]
    :return: float in meters
    """
    polygon = process_polygon(coordinates)
    perimeter = polygon.length
    return perimeter


def process_polygon(coordinates):
    """Pass list of co-ordinates to Shapely Polygon function and get polygon object"""

    return Polygon(coordinates)
