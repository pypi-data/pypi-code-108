"""

This module contains types useful in 2D geometry.


"""
import math
from typing import NamedTuple, Sequence, Tuple, TypeVar, Union, Optional
from copy import copy
from math import sqrt

from codeviking.math.interval import RI, RICompat

V2Compat = Union['V2', Tuple[float, float]]
__V2 = NamedTuple('__V2', (('x', float), ('y', float)))

__all__ = ['V2', 'ClipLine', 'Box2', 'Segment2', 'Shape2', 'ConvPoly2',
           'Tri2']


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class V2(__V2):
    """
    2D Euclidean vector type.

    Several operations are supported.  In the following, *u* is a V2,
    *v* is either a V2 or a tuple of length 2, and *a* is a number.

    *  *u* == *v* : standard equality test.
    *  *u* + *v* :        vector addition
    *  *u* - *v* :        vector subtraction
    *  *u* * *a* or *a* * *u* :        scalar multiplication
    *  *u* / *a* :        scalar division
    *  *u* // *a* :        scalar floor division
    *  *u* @ *v* :        dot product
    """

    @property
    def length(self) -> float:
        """
        Euclidean length of this vector.
        """
        if not hasattr(self, '_length'):
            self._length = sqrt(self.x ** 2 + self.y ** 2)
        return self._length

    def __eq__(self, other: V2Compat) -> bool:
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other: V2Compat) -> 'V2':
        assert isinstance(other, tuple)
        return V2(self.x + other[0], self.y + other[1])

    def __neg__(self) -> 'V2':
        return V2(-self.x, -self.y)

    def __sub__(self, other: V2Compat) -> 'V2':
        assert isinstance(other, tuple)
        return V2(self.x - other[0], self.y - other[1])

    def __mul__(self, scalar) -> 'V2':
        return V2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar) -> 'V2':
        return V2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar) -> 'V2':
        return V2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar) -> 'V2':
        """Scalar floor division."""
        return V2(self.x // scalar, self.y // scalar)

    def __matmul__(self, other: V2Compat) -> float:
        """Dot product"""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def dot(self, other: V2Compat) -> float:
        """Dot product (other can be a V2 or a tuple)."""
        assert isinstance(other, tuple)
        return self.x * other[0] + self.y * other[1]

    def rdot(self, other: V2Compat) -> float:
        """Dot product of the right-facing normal vector with other."""
        assert isinstance(other, tuple)
        return self.y * other[0] - self.x * other[1]

    def ldot(self, other: V2Compat) -> float:
        """Dot product of the left-facing normal vector with other."""
        assert isinstance(other, tuple)
        return self.x * other[1] - self.y * other[0]

    def cross(self, other: V2Compat) -> float:
        """Cross product of this verctor with other"""
        assert isinstance(other, tuple)
        return self.x * other[1] - self.y * other[0]

    @property
    def unit(self) -> 'V2':
        """Returns a normalized version of this vector (unit vector)."""
        if not hasattr(self, '_unit'):
            self._unit = V2(self.x / self.length, self.y / self.length)
        return self._unit

    @property
    def angle(self):
        """Returns the angle that this vector makes with the x-axis,
        in radians.  Counterclockwise is positive."""
        if not hasattr(self, '_angle'):
            self._angle = math.atan2(self.y, self.x)
            if self._angle <= 0:
                self._angle += 2 * math.pi
        return self._angle

    @property
    def angle_deg(self):
        """Returns the angle that this vector makes with the x-axis,
        in degrees.  Counterclockwise is positive."""
        return self.angle * 180 / math.pi

    def __str__(self) -> str:
        return "({0},{1})".format(self.x, self.y)

    @classmethod
    def from_angle(cls, radians: float) -> 'V2':
        """Create a unit vector pointing in direction of radians"""
        return V2(math.cos(radians), math.sin(radians))

    @classmethod
    def from_angle_deg(cls, degrees: float) -> 'V2':
        radians = math.pi * degrees / 180.0
        return V2(math.cos(radians), math.sin(radians))

    @classmethod
    def from_polar(cls, radius: float, radians: float):
        return V2(radius * math.cos(radians), radius * math.sin(radians))

    @classmethod
    def from_polar_deg(cls, radius: float, degrees: float):
        radians = math.pi * degrees / 180.0
        return V2(radius * math.cos(radians), radius * math.sin(radians))

    def project_onto(self, vector: V2Compat):
        s = self.x * vector[0] + self.y * vector[1]
        d2 = vector[0] ** 2 + vector[1] ** 2
        return (s / d2) * vector

    def rotate(self, radians: float) -> 'V2':
        cs, sn = math.cos(radians), math.sin(radians)
        return V2(cs * self.x - sn * self.y, sn * self.x + self.y * cs)

    def rotate_deg(self, degrees: float) -> 'V2':
        radians = math.pi * degrees / 180.0
        cs, sn = math.cos(radians), math.sin(radians)
        return V2(cs * self.x - sn * self.y, sn * self.x + self.y * cs)

    def left(self) -> 'V2':
        """
        A vector with the same length pointing 90 degrees to the left of this
        vector.
        """
        return V2(-self.y, self.x)

    def right(self) -> 'V2':
        """
        A vector with the same length pointing 90 degrees to the right of this
        vector.
        """
        return V2(self.y, -self.x)


V2.ZERO = V2(0.0, 0.0)
V2.X = V2(1.0, 0.0)
V2.Y = V2(0.0, 1.0)
V2.NaN = V2(float('NaN'), float('NaN'))

__Box2 = NamedTuple('__BBox', (('xr', RI), ('yr', RI)))


class Box2(__Box2):
    """
    Axis-aligned bounding box.
    :members:
    :undoc-members:
    :inherited-members:

    .. attribute:: xr, yr

        x and y intervals (instances of class RI) of this bounding box.  These
        attributes are read-only.

    .. describe::  p in box

         True if the point p lies inside box.   p can be a V2 or tuple.
         A p is inside box if box.xr.min <= p.x <= box.xr.max and box.yr.min
         <= p.y <= box.yr.max

    """

    def __new__(cls, xr: RICompat, yr: RICompat):
        if not isinstance(xr, RI):
            xr = RI(*xr)
        if not isinstance(yr, RI):
            yr = RI(*yr)
        # noinspection PyArgumentList
        return super(Box2, cls).__new__(cls, xr, yr)

    def __contains__(self, p: V2Compat) -> bool:
        return p[0] in self.xr and p[1] in self.yr

    def expand(self, item: Union['Box2', V2Compat]) -> 'Box2':
        """
        return a Box2 that contains both this box and item.

        :param item: can be either a V2, a Box2, or a tuple of length 2
        """
        if isinstance(item, Box2):
            return Box2(self.xr.expand(item.xr), self.yr.expand(item.yr))
        if not isinstance(item, V2):
            item = V2(*item)
        if item in self:
            return self
        if self.is_empty:
            return Box2(RI(item.x, item.x), RI(item.y, item.y))
        return Box2(self.xr.expand(item.x), self.yr.expand(item.y))

    @property
    def is_empty(self) -> bool:
        """
        return True if this box is empty.
        """
        return self.xr.is_empty or self.yr.is_empty

    @property
    def bbox(self) -> 'Box2':
        return self

    @property
    def is_point(self) -> bool:
        """is this box a single point?"""
        return self.xr.is_point and self.yr.is_point

    @property
    def size(self) -> V2:
        """The size of this box (xsize,ysize)"""
        if not hasattr(self, '_size'):
            self._size = V2(self.xr.length, self.yr.length)
        return self._size

    def interpolate(self, alpha: float) -> V2:
        return V2(self.xr.interpolate(alpha), self.yr.interpolate(alpha))

    def intersects(self, other: 'Box2') -> bool:
        return self.xr.intersects(other.xr) and self.yr.intersects(other.yr)

    def intersection(self, other: 'Box2'):
        return Box2(self.xr.intersection(other.xr),
                    self.yr.intersection(other.yr))

    @classmethod
    def from_points(cls, a: V2, b: V2) -> 'Box2':
        """
        Construct a new Box2 from two points.  The two points can represent
        any two corners of the box.
        :param a: a corner of the box
        :param b: another corner of the box
        :return: a new box containing both corners
        """
        return Box2(RI(min(a.x, b.x), max(a.x, b.x)),
                    RI(min(a.y, b.y), max(a.y, b.y)))


Box2.empty = Box2(RI.empty, RI.empty)


class Shape2:
    """
    This is an interface for a generic 2d shape.  It only supports one
    operation:

    .. describe p in shape::

        True if the point p lies inside this shape.

    subclasses need to implement the __contains__ member function.
    """

    def __contains__(self, p: V2Compat) -> bool:
        pass


__Tri2 = NamedTuple('__Tri2', (('v0', V2), ('v1', V2), ('v2', V2),
                               ('n0', V2), ('n1', V2), ('n2', V2),
                               ('bbox', Box2)))


# noinspection PyUnresolvedReferences
class Tri2(__Tri2, Shape2):
    """
    2d Triangle.
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: v0, v1, v2

        Triangle vertices in counter clockwise order.  These are read-only
        attributes

    .. attribute:: n0, n1, n2

        Outward-facing edge normal vectors.  These are read-only attributes

    .. describe:: p in triangle

        True if point *p* lies inside *triangle*.  *p* can be a V2 or a
        tuple.

    """

    def __new__(cls,
                v0: V2Compat,
                v1: V2Compat,
                v2: V2Compat):
        if not isinstance(v0, V2):
            v0 = V2(*v0)
        if not isinstance(v1, V2):
            v1 = V2(*v1)
        if not isinstance(v2, V2):
            v2 = V2(*v2)
        ax, ay = [v0.x, v1.x, v2.x], [v0.y, v1.y, v2.y]

        # noinspection PyArgumentList
        return super(Tri2, cls).__new__(cls, v0, v1, v2,
                                        (v1 - v0).right(),
                                        (v2 - v1).right(),
                                        (v0 - v2).right(),
                                        Box2(RI(min(ax), max(ax)),
                                             RI(min(ay), max(ay))))

    def __contains__(self, p: V2Compat) -> bool:
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        if self.n0.dot(p - self.v0) > 0:
            return False
        if self.n1.dot(p - self.v1) > 0:
            return False
        if self.n2.dot(p - self.v2) > 0:
            return False
        return True


_ConvPoly2 = NamedTuple('_ConvPoly2', (('vertices', Sequence[V2]),
                                       ('onorms', Sequence[V2]),
                                       ('bbox', Box2)))


class ClipLine(NamedTuple('ClipLine', (('a', V2), ('b', V2), ('n', V2)))):
    pass


"""
sa - which side of clipping line is point a on.
sb - which side of clipping line is point b on.
i - intersection point with clipping line.
"""
ClipResult = NamedTuple('ClipResult',
                        (('sa', float), ('sb', float), ('i', V2Compat)))


# noinspection PyAttributeOutsideInit


class Segment2(NamedTuple('Segment', (('a', V2), ('b', V2)))):
    @property
    def v(self):
        if not hasattr(self, '_v'):
            self._v = self.b - self.a
        return self._v

    def point(self, alpha):
        """Calculate a point on the segment that is a fraction alpha between a
         and b.  point(0) == a   point(1) == b  point(0.5) == midpoint of a,
         b."""
        return V2(self.a.x + alpha * self.v.x, self.a.y + alpha * self.v.y)

    def alpha(self, point):
        """Calculate the alpha value for point.  This is the inverse of the
        .point(alpha) memberfunction
        :param point:
        :return: alpha value for the point on this segment that is closest
        to point.
        """
        q = (point - self.a)
        s = q.dot(self.v)
        d2 = self.v.length ** 2
        return s / d2

    def side(self, point):
        """Which side of this line segment is point on?
            > 0 => point is on the right side.
            < 0 => point is on the left side.
        """
        d = point - self.a
        return self.v.rdot(d)

    def intersect(self, other, epsilon=1e-8) -> Optional[
        Union[V2, 'Segment2']]:
        k = self.v.x * other.v.y - self.v.y * other.v.x
        if abs(k) < epsilon:
            # lines are (roughly) parallel
            aa = self.alpha(other.a)
            ab = self.alpha(other.b)
            if aa < 0 and ab < 0:
                return None
            if aa > 1 and ab > 1:
                return None

            pa = self.point(aa)
            pb = self.point(ab)

            da = (pa - other.a).length
            db = (pb - other.b).length

            if (pa - other.a).length > epsilon or (
                    pb - other.b).length > epsilon:
                return None

            # intersection is a segment.
            # order the points
            if aa > ab:
                aa, ab = ab, aa
            ia = max(0.0, aa)
            ib = min(1.0, ab)

            pa = self.point(ia)
            pb = self.point(ib)
            return Segment2(pa, pb)

        # intersection between lines is a point
        # find out if point is on the segments

        u = self.a - other.a
        s = ((u.y * other.v.x - u.x * other.v.y) / k)
        t = ((u.y * self.v.x - u.x * self.v.y) / k)

        if s <= -epsilon or s >= 1.0 + epsilon:
            return None
        if t <= -epsilon or t >= 1.0 + epsilon:
            return None

        return self.point(s)


# noinspection PyAttributeOutsideInit
class ConvPoly2(_ConvPoly2, Shape2):
    """
    2d Convex Polygon
    Vertices must be supplied in counter clockwise (CCW) order.

    .. attribute:: vertices

        Triangle vertices in counter clockwise order.

    .. attribute:: onorms

        Outward-facing edge normal vectors.

    .. describe:: p in poly

        True if point *p* lies inside *poly*.  *p* can be a V2 or a tuple.


    """

    def __new__(cls, vertices: Sequence[V2Compat]):
        n = len(vertices)
        vertices = tuple(
                (p if isinstance(p, V2) else V2(*p)) for p in vertices)
        ax, ay = ([p.x for p in vertices], [p.y for p in vertices])
        bbox = Box2(RI(min(ax), max(ax)), RI(min(ay), max(ay)))
        onorms = tuple((vertices[(i + 1) % n] - vertices[i]).right()
                       for i in range(n))
        # noinspection PyArgumentList
        return super(ConvPoly2, cls).__new__(cls,
                                             vertices,
                                             onorms,
                                             bbox)

    def __contains__(self, p):
        if not isinstance(p, V2):
            p = V2(*p)
        if p not in self.bbox:
            return False
        for i in range(len(self.vertices)):
            if self.onorms[i].dot(p - self.vertices[i]) > 0:
                return False
        return True

    def vertex(self, idx):
        return self.vertices[idx % len(self.vertices)]

    @property
    def segments(self):
        if not hasattr(self, '_segments'):
            self._segments = tuple(Segment2(self.vertices[i + 1],
                                            self.vertices[i]) for i in
                                   range(len(self.vertices)))
        return self._segments

        # def intersection(self, other: ConvPoly2):
        #     output_list = list(other.vertices)
        #     for (p, n) in self.clip_edges():
        #         input_list = copy(output_list)
        #         output_list.clear()
        #         s = input_list[-1]
        #         for e in input_list:
        #             if n.dot(e - p) > 0:
