from itertools import chain

from euclidean.R2.cartesian import P2, V2, cross2
from euclidean.R2.line import LineSegment

from .hull import convex_hull
from .line_sweep import shamos_hoey


class Polygon:
    """

    """

    @classmethod
    def ConvexHull(cls, points):
        return cls(convex_hull(points), is_convex=True)

    def __init__(self, points, is_convex=None):
        self._points = tuple(points)
        if len(self._points) < 3:
            raise ValueError("At least 3 points are required to define a polygon.")
        self._min_index = _min_idx(self._points)
        self.__is_convex = is_convex

    def __len__(self):
        return len(self._points)

    def standard_form(self):
        """Normalize point order to begin traversal from minimum point.

        #todo: also detect if CW -> iterate backwards, ie. CCW?
        #todo: make this the default __iter__ method?

        Returns:

        """
        return self._rolled(self._min_index)

    def _rolled(self, offset):
        return _rolled(self._points, offset)

    def _cross_products(self):
        return map(cross2, self._points, self._rolled(1))

    def area(self):
        """Find the area of this polygon.

        Notes:

            This will return an incorrect value if the polygon is complex.

        Returns:

        """
        return 0.5 * abs(sum(self._cross_products()))

    def centroid(self):
        """Find the centroid of this polygon.

        Notes:

            This will return an incorrect value if the polygon is complex.

        Returns:

        """
        cx, cy, a = 0, 0, 0
        for p1, p2 in zip(self._points, self._rolled(1)):
            cross = cross2(p1, p2)
            cx += (p1.x + p2.x) * cross
            cy += (p1.y + p2.y) * cross
            a += cross
        a *= 3
        return P2(cx / a, cy / a)

    def translate(self, vector):
        return Polygon(p + vector for p in self._points)

    def centered_at(self, new_center_point):
        """Copy this polygon centered at the provided point.

        Returns:
            (Polygon):
        """
        vector = new_center_point - self.centroid()
        return Polygon(p + vector for p in self._points)

    def rotate(self, radians, center_point=None):
        """Rotate the polygon by radians around a center point or the centroid if none is provided.

        Args:
            radians:
            center_point:

        Returns:
            (Polygon)
        """
        center_point = center_point if center_point else self.centroid()
        return Polygon(p.rotate(radians, center_point) for p in self._points)

    def points(self):
        return self._points

    def xs(self):
        return (p.x for p in self._points)

    def ys(self):
        return (p.y for p in self._points)

    def __ccws(self):
        return map(P2.CCW, self._rolled(0), self._rolled(1), self._rolled(2))

    def __maybe_convex(self):
        return all(c <= 0 for c in self.__ccws()) or all(c >= 0 for c in self.__ccws())

    def is_convex(self):
        if self.__is_convex is None:
            self.__is_convex = len(self._points) < 4 or (
                self.__maybe_convex() and self.is_simple()
            )
        return self.__is_convex

    def is_simple(self):
        return shamos_hoey(self.edges())

    def edges(self):
        return map(LineSegment, self._points, chain(self._points[1:], self._points[:1]))

    def contains(self, test_point, atol=1e-6, closed=True):
        if self.winding_number(test_point) > 0:
            return True
        if closed:
            return self.on_perimeter(test_point, atol)
        return False

    def perimeter(self):
        return sum(edge.length() for edge in self.edges())

    def on_perimeter(self, point, atol=1e-6):
        return any(edge.contains(point, atol) for edge in self.edges())

    def winding_number(self, test_point):
        order = sum(self._cross_products())
        wn = 0
        for edge in self.edges():
            if edge._p1.y <= test_point.y:
                if edge._p2.y > test_point.y:
                    if order * P2.CCW(edge._p1, edge._p2, test_point) > 0:
                        wn += 1
            else:
                if edge._p2.y <= test_point.y:
                    if order * P2.CCW(edge._p1, edge._p2, test_point) < 0:
                        wn -= 1
        return wn

    def __eq__(self, other):
        if not isinstance(other, Polygon):
            return NotImplemented
        if len(self._points) != len(other._points):
            return False
        for p1, p2 in zip(self.standard_form(), other.standard_form()):
            if p1 != p2:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def plot(self, **kwargs):
        xs = list(self.xs())
        xs.append(xs[0])
        ys = list(self.ys())
        ys.append(ys[0])
        return plt.plot(xs, ys, **kwargs)


def _rolled(points, offset):
    return chain(points[offset:], points[:offset])


def _standard_form(points):
    return tuple(_rolled(points, _min_idx(points)))


def _min_idx(points):
    min_idx = 0
    for idx, point in enumerate(points):
        if point._coords < points[min_idx]._coords:
            min_idx = idx
    return min_idx
