import operator

from euclidean.R2.cartesian import P2
from euclidean.R2.line import Line


def convex_hull(point_cloud):
    if len(point_cloud) < 3:
        return None

    return _divide_and_conquer_convex_hull(sorted(point_cloud)).points()


def _jarvis_convex_hull(points):
    """Find the convex hull of a point cloud using the jarvis march algorithm.

    Notes:

        O(n * h) for n points in point cloud, h points in hull

    Args:
        points (List[P2]):

    Returns:
        (List[P2]):
    """
    count = len(points)
    hull = []
    last_idx = 0
    while True:
        hull.append(points[last_idx])

        next_idx = (last_idx + 1) % count
        for test_idx, test_point in enumerate(points):
            if P2.CCW(points[last_idx], test_point, points[next_idx]) > 0:
                next_idx = test_idx

        last_idx = next_idx

        if last_idx == 0:
            return hull


def _divide_and_conquer_convex_hull(points):
    """

    Notes:

        O(n * log(n))

    Args:
        points:

    Returns:

    """
    count = len(points)
    if count < 6:
        return Hull(_jarvis_convex_hull(points))

    midpoint = count // 2
    min_cloud, max_cloud = points[:midpoint], points[midpoint:]

    min_hull = _divide_and_conquer_convex_hull(min_cloud)
    max_hull = _divide_and_conquer_convex_hull(max_cloud)

    return __merge_convex_hulls(min_hull, max_hull)


class Hull:
    class Vertex:
        __slots__ = ("cw", "point", "ccw")

        def __init__(self, point):
            self.point = point

    def __init__(self, points):
        p_iter = iter(points)
        first = Hull.Vertex(next(p_iter))
        last = Hull.Vertex(next(p_iter))
        first.cw = first.ccw = last
        last.cw = last.ccw = first
        self.__min = first

        for point in p_iter:
            self.__append(point)

    def __append(self, point):
        first = self.__min
        last = self.__min.cw
        new_vertex = Hull.Vertex(point)
        first.cw = new_vertex
        new_vertex.ccw = first
        last.ccw = new_vertex
        new_vertex.cw = last

    def points(self):
        current = self.__min
        while True:
            yield current.point
            current = current.ccw
            if current == self.__min:
                break

    def min(self):
        return self.__min

    def max(self):
        current = self.__min
        while current.point < current.ccw.point:
            current = current.ccw
        return current


def __merge_convex_hulls(min_hull, max_hull):

    (min_h_max_vtx, max_h_max_vtx) = __tangent(min_hull, max_hull, Tangent.MAX)
    (min_h_min_vtx, max_h_min_vtx) = __tangent(min_hull, max_hull, Tangent.MIN)

    min_h_max_vtx.cw = max_h_max_vtx
    max_h_max_vtx.ccw = min_h_max_vtx

    min_h_min_vtx.ccw = max_h_min_vtx
    max_h_min_vtx.cw = min_h_min_vtx

    return min_hull


import enum


class Tangent(enum.Enum):
    MAX = 1
    MIN = -1


def __tangent(min_hull, max_hull, dir):
    min_hull_vtx = min_hull.max()
    max_hull_vtx = max_hull.min()

    op = operator.gt if dir == Tangent.MAX else operator.lt

    while True:
        test_line = Line.ByPoints(min_hull_vtx.point, max_hull_vtx.point)

        cmp_vtx = min_hull_vtx.ccw if dir == Tangent.MAX else min_hull_vtx.cw
        if op(test_line.on_side(cmp_vtx.point), 0):
            min_hull_vtx = cmp_vtx
            continue

        cmp_vtx = max_hull_vtx.cw if dir == Tangent.MAX else max_hull_vtx.ccw
        if op(test_line.on_side(cmp_vtx.point), 0):
            max_hull_vtx = cmp_vtx
            continue

        return min_hull_vtx, max_hull_vtx
