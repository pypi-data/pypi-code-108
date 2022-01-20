import math

from multipledispatch import dispatch

from euclidean.constants import tau

from euclidean.R2.cartesian import V2
from euclidean.R2.line import LineSegment
from euclidean.R2.circle import Circle
from euclidean.R2.polygon import Polygon


@dispatch(LineSegment)
def rasterize(line_segment, n=100):
    step_vec = line_segment.vector() / (n - 1)
    return [line_segment._p1 + i * step_vec for i in range(n)]


@rasterize.register(Circle)
def _(circle, n=360):
    rot_theta = tau / n
    radius_vector = circle.radius * V2(1, 0)
    return [circle.center + radius_vector.rotate(rot_theta * i) for i in range(n)]


@rasterize.register(Polygon)
def _(polygon, n=1000):
    n = int(n)
    assert n >= len(polygon)
    poly_points = list(polygon.points())
    poly_points.append(poly_points[0])
    return __rasterize_points(poly_points, n)


def __rasterize_points(points, n):
    print(points)

    count = len(points)
    if count == 2:
        (a, b) = points
        return __rasterize_pair(a, b, n)

    midpoint = count // 2
    n1 = n // 2
    raster = __rasterize_points(points[: midpoint + 1], n1)
    raster.extend(__rasterize_points(points[midpoint:], n - n1))
    return raster


def __rasterize_pair(p1, p2, n):
    assert n >= 1
    step_v = (p2 - p1) / n
    return [p1 + i * step_v for i in range(n)]
