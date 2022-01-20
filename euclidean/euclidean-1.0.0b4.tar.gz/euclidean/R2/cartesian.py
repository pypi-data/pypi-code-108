import numbers
import math

from functools import total_ordering

from euclidean.exceptions import unexpected_type_error


def cross2(v1, v2):
    return v1.x * v2.y - v1.y * v2.x


def dot2(v1, v2):
    return v1.x * v2.x + v1.y * v2.y


class Cartesian2:
    __slots__ = ("_coords",)

    coords = property(lambda self: self._coords)

    x = property(lambda self: self._coords[0])
    y = property(lambda self: self._coords[1])

    @classmethod
    def Polar(cls, r, theta):
        return cls(r * math.cos(theta), r * math.sin(theta))

    def __init__(self, x, y):
        self._coords = (x, y)

    def __iter__(self):
        return iter(self._coords)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._coords == other._coords
        return NotImplemented

    def __hash__(self):
        return hash((self.__class__.__name__, self._coords))

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)


class V2(Cartesian2):
    __slots__ = ()

    def unit(self):
        return self / self.magnitude()

    def dot(self, other):
        if not isinstance(other, V2):
            raise unexpected_type_error("other", V2, other)
        return dot2(self, other)

    def cross(self, other):
        if not isinstance(other, V2):
            raise unexpected_type_error("other", V2, other)
        return cross2(self, other)

    def is_parallel(self, other, atol=1e-6):
        return abs(self.cross(other)) <= atol

    def is_orthogonal(self, other, atol=1e-6):
        return abs(self.dot(other)) <= atol

    def magnitude(self):
        return self.dot(self) ** 0.5

    def manhattan_distance(self):
        return self.x + self.y

    __abs__ = magnitude

    def angle(self, other):
        return math.acos(self.dot(other) / self.magnitude() / other.magnitude())

    def rotate(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        return V2(self.x * cos - self.y * sin, self.x * sin + self.y * cos)

    def approx(self, other, atol=1e-6):
        if not isinstance(other, V2):
            raise unexpected_type_error("other", V2, other)
        return abs(self - other) < atol

    def __add__(self, other):
        if isinstance(other, V2):
            return V2(self.x + other.x, self.y + other.y)
        return NotImplemented

    __iadd__ = __add__

    def __sub__(self, other):
        if isinstance(other, V2):
            return V2(self.x - other.x, self.y - other.y)
        return NotImplemented

    __isub__ = __sub__

    def __mul__(self, other):
        if not isinstance(other, numbers.Real):
            return NotImplemented
        return V2(self.x * other, self.y * other)

    __imul__ = __rmul__ = __mul__

    def __truediv__(self, other):
        if not isinstance(other, numbers.Real):
            return NotImplemented
        return V2(self.x / other, self.y / other)

    __itruediv__ = __truediv__

    def __floordiv__(self, other):
        if not isinstance(other, numbers.Real):
            return NotImplemented
        return V2(self.x // other, self.y // other)

    __ifloordiv__ = __floordiv__

    def __neg__(self):
        return V2(-self.x, -self.y)


@total_ordering
class P2(Cartesian2):
    __slots__ = ()

    @staticmethod
    def CCW(p1, p2, p3):
        return (p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)

    @staticmethod
    def AcuteAngle(p1, p2, p3):
        v1 = p1 - p2
        v2 = p3 - p2
        return v1.angle(v2)

    def vector(self):
        return V2(self.x, self.y)

    def rotate(self, radians, center_point=None):
        center_point = center_point if center_point else P2(0, 0)
        vector = self - center_point
        return center_point + vector.rotate(radians)

    def quadrant(self):
        if self.x >= 0 and self.y >= 0:
            return 1
        if self.x <= 0 and self.y >= 0:
            return 2
        if self.x <= 0 and self.y <= 0:
            return 3
        return 4

    def approx(self, other, atol=1e-6):
        if not isinstance(other, P2):
            raise unexpected_type_error("other", P2, other)
        return (self - other).magnitude() < atol

    def __lt__(self, other):
        if not isinstance(other, P2):
            return NotImplemented
        return self._coords < other._coords

    def __add__(self, other):
        if isinstance(other, V2):
            return P2(self.x + other.x, self.y + other.y)
        return NotImplemented

    __radd__ = __iadd__ = __add__

    def __sub__(self, other):
        if isinstance(other, V2):
            return P2(self.x - other.x, self.y - other.y)
        if isinstance(other, P2):
            return V2(self.x - other.x, self.y - other.y)
        return NotImplemented

    __isub__ = __sub__
