"""
A geometry module for the SymPy library. This module contains all of the
entities and functions needed to construct basic geometrical data and to
perform simple informational queries.

Usage:
======

Examples
========

"""
from .point import Point, Point2D, Point3D
from .line import Line, Ray, Segment, Line2D, Segment2D, Ray2D, \
    Line3D, Segment3D, Ray3D
from .plane import Plane
from .ellipse import Ellipse, Circle
from .polygon import Polygon, RegularPolygon, Triangle, rad, deg
from .util import are_similar, centroid, convex_hull, idiff, \
    intersection, closest_points, farthest_points
from .exceptions import GeometryError
from .curve import Curve
from .parabola import Parabola
