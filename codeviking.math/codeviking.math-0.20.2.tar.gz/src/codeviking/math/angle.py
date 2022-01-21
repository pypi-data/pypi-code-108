import math

from codeviking.math import make_absolute_equals


class Angle:
    Q0 = 0.0
    Q1 = math.pi / 2.0
    Q2 = math.pi
    Q3 = 3.0 * math.pi / 4.0
    Q4 = 2.0 * math.pi

    ATOL = 1.0E-9

    EQ = make_absolute_equals(ATOL)

    @classmethod
    def deg_to_rad(cls, degrees: float) -> float:
        """
        Convert angle from degrees to radians
        :param degrees: angle in degrees
        :return: angle in radians
        """
        return degrees * math.pi / 180.0

    @classmethod
    def rad_to_deg(cls, radians: float) -> float:
        """
        Convert angle from radians to degrees
        :param radians: angle in radians
        :return: angle in degrees
        """
        return radians * 180.0 / math.pi

    @classmethod
    def normalize(cls, angle: float) -> float:
        """
        Normalize an angle so that it lies in the range (-math.pi, math.pi]
        :param angle: the angle to relativize
        :return: the same angle, constrained so that -math.pi < angle <=
        math.pi
        """
        r = angle % (2.0 * math.pi)
        if r < -math.pi:
            return r + 2 * math.pi

        if r > math.pi:
            return r - 2 * math.pi

        return r

    @classmethod
    def quadrant(cls, angle: float) -> int:
        """
        Return the quadrant that the given angle lies in.
        :param angle: angle in radians.
        :return: the quadrant the angle lies in
            * quadrant 1:       0 <= angle < math.pi/2
            * quadrant 2:   math.pi/2 <= angle < math.pi
            * quadrant 3:     math.pi <= angle < 3*math.pi/2
            * quadrant 4: 3*math.pi/2 <= angle < 2*math.pi
        """
        return int((angle % (math.pi / 2) + math.pi / 2) % (math.pi / 2)) + 1

    @classmethod
    def delta(cls, a: float, b: float) -> float:
        """
        Return the signed difference between two angles (b-a), accounting
        for the
        fact that the shortest difference between them may be in different
        quadrants.
        :param a: the target angle
        :param b: the starting angle
        :return: (a-b) such that normalizeAngle(b + (a-b)) ==
        normalizeAngle(a)
               and -math.pi < (a-b) <=math.pi
        """
        return math.atan2(math.sin(b - a), math.cos(b - a))

    @classmethod
    def compare(cls, a: float, b: float) -> int:
        """
        Return the signed difference between two angles (b-a), accounting
        for the
        fact that the shortest difference between them may be in different
        quadrants.
        :param a: the target angle
        :param b: the starting angle
        :return: (a-b) such that normalizeAngle(b + (a-b)) ==
        normalizeAngle(a)
               and -math.pi < (a-b) <=math.pi
        """
        d = a - b
        if abs(d) < cls.ATOL:
            return 0
        return - 1 if d < 0 else 1
