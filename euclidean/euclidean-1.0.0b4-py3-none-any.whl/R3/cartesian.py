import math
import numbers

from functools import total_ordering

from euclidean.R2.cartesian import V2
from euclidean.exceptions import unexpected_type_error


class Cartesian3:
    __slots__ = ("_coords",)

    def __init__(self, x, y, z):
        self._coords = (x, y, z)

    x = property(lambda self: self._coords[0])
    y = property(lambda self: self._coords[1])
    z = property(lambda self: self._coords[2])

    def __iter__(self):
        return iter(self._coords)

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.x, self.y, self.z)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._coords == other._coords
        return NotImplemented


class V3(Cartesian3):
    __slots__ = ()

    def dot(self, other):
        if not isinstance(other, V3):
            raise unexpected_type_error("other", V3, other)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return V3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def magnitude(self):
        return self.dot(self) ** 0.5

    __abs__ = magnitude

    def unit(self):
        return self / self.magnitude()

    def angle(self, other):
        return math.acos(self.dot(other) / self.magnitude() / other.magnitude())

    def xy(self):
        return V2(self.x, self.y)

    def xz(self):
        return V2(self.x, self.z)

    def yz(self):
        return V2(self.y, self.z)

    def manhattan_distance(self):
        return sum(self._coords)

    def approx(self, other, atol=1e-6):
        if not isinstance(other, V3):
            raise unexpected_type_error("other", V3, other)
        return abs(self - other) <= atol

    def __add__(self, other):
        if isinstance(other, V3):
            return V3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    __iadd__ = __add__

    def __sub__(self, other):
        if isinstance(other, V3):
            return V3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    __isub__ = __sub__

    def __mul__(self, other):
        if isinstance(other, numbers.Real):
            return V3(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    __imul__ = __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, numbers.Real):
            return V3(self.x / other, self.y / other, self.z / other)
        return NotImplemented

    __itruediv__ = __truediv__

    def __floordiv__(self, other):
        if isinstance(other, numbers.Real):
            return V3(self.x // other, self.y // other, self.z // other)
        return NotImplemented

    def __neg__(self):
        return V3(-self.x, -self.y, -self.z)


@total_ordering
class P3(Cartesian3):
    __slots__ = ()

    def __add__(self, other):
        if isinstance(other, V3):
            return P3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    __radd__ = __iadd__ = __add__

    def approx(self, other, atol=1e-6):
        if not isinstance(other, P3):
            raise unexpected_type_error("other", P3, other)
        return abs(self - other) < atol

    def __sub__(self, other):
        if isinstance(other, V3):
            return P3(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, P3):
            return V3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    def vector(self):
        return V3(self.x, self.y, self.z)

    def __lt__(self, other):
        if not isinstance(other, P3):
            return NotImplemented
        return self._coords < other._coords
