from euclidean.constants import pi
from euclidean.exceptions import unexpected_type_error

from .cartesian import P2, V2


class Circle:

    center = property(lambda self: self._center)
    radius = property(lambda self: self._radius)
    diameter = property(lambda self: 2 * self._radius)

    def __init__(self, radius, center=P2(0, 0)):
        """

        (x - center.x) ** 2 + (y - center.y) ** 2 = radius ** 2

        Args:
            radius:
            center (P2):
        """

        if radius <= 0:
            raise ValueError("Radius must be positive.")
        self._center = center
        self._radius = radius

    def _equation(self, point):
        diff = point - self.center
        return diff.dot(diff)

    def on_circumference(self, point, atol=1e-6):
        return abs(self._equation(point) - self.radius ** 2) <= atol

    def circumference(self):
        return pi * self.diameter

    def area(self):
        return pi * self._radius ** 2

    def does_intersect(self, circle):
        if not isinstance(circle, Circle):
            raise unexpected_type_error("circle", Circle, circle)

        if self == circle:
            raise ValueError("Test circles are identical.")

        vector = circle.center - self.center
        magnitude = vector.magnitude()
        if magnitude > self.radius + circle.radius:
            return False
        if magnitude < abs(self.radius - circle.radius):
            return False

        return True

    def intersection(self, circle):
        if not self.does_intersect(circle):
            return set()

        my_c = self.center
        c_c = circle.center

        vector = c_c - my_c
        v_mag = vector.magnitude()

        apothem = (self.radius ** 2 - circle.radius ** 2 + v_mag ** 2) / (2 * v_mag)
        intersect_center = my_c + apothem * vector.unit()
        if apothem == self.radius:
            return {intersect_center}

        h = (self.radius ** 2 - apothem ** 2) ** 0.5
        offset = h / v_mag * V2(c_c.y - my_c.y, my_c.x - c_c.x)

        return {intersect_center + offset, intersect_center - offset}

    def contains(self, point):
        if isinstance(point, P2):
            return self._equation(point) <= self.radius ** 2
        return False
