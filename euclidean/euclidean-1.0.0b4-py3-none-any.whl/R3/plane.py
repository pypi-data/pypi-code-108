from euclidean.util import normalize_coefficients
from euclidean.exceptions import unexpected_type_error

from .cartesian import P3, V3


class Plane:

    cx = property(lambda self: self._coeffs[0])
    cy = property(lambda self: self._coeffs[1])
    cz = property(lambda self: self._coeffs[2])
    c = property(lambda self: self._coeffs[3])

    @staticmethod
    def PointNormal(point, normal_vector):
        c = (
            normal_vector.x * point.x
            + normal_vector.y * point.y
            + normal_vector.z * point.z
        )
        return Plane(normal_vector.x, normal_vector.y, normal_vector.z, c)

    def __init__(self, cx, cy, cz, c):
        self._coeffs = normalize_coefficients(cx, cy, cz, c)

    def _equation(self, point):
        if not isinstance(point, P3):
            raise unexpected_type_error("point", P3, point)
        return self.cx * point.x + self.cy * point.y + self.cz * point.z

    def normal(self):
        return V3(self.cx, self.cy, self.cz).unit()

    def contains(self, point, atol=1e-6):
        return abs(self._equation(point) - self.c) <= atol

    def __eq__(self, other):
        if not isinstance(other, Plane):
            return NotImplemented
        return self._coeffs == other._coeffs

    def __ne__(self, other):
        return not self == other
