import math
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Point import Point


@dataclass(frozen=True)
class Line:
    """ A Line class implementing a 2D line made of two end points along with basic geometric transformations

   Attributes:
       p1 (Point): start point of a line
       p2 (Point): end point of a line
    """
    p1: Point
    p2: Point

    @staticmethod
    def of_end_points(p1: Point, p2: Point) -> "Line":
        """ Static method initiating a line from two end points

        :param p1: start point of a line
        :param p2: end point of a line
        :return: Initialized line object with copies of both lines
        """
        return Line(p1=p1.copy(), p2=p2.copy())

    def translate(self, vector: Point) -> "Line":
        """ Method translating line by an input vector

        :param vector: vector by which the line is translated
        :return: translated line
        """
        return Line.of_end_points(self.p1.translate(vector), self.p2.translate(vector))

    def rotate(self, angle: float) -> "Line":
        """ Method rotating line by a given angle w.r.t. origin of the coordinate system (0, 0)

        :param angle: rotation angle in degrees
        :return: rotated line
        """
        return Line.of_end_points(self.p1.rotate(angle), self.p2.rotate(angle))

    def unit(self) -> Point:
        """ Method calculating a unit vector along the line

        :return: Unit vector along the line with start at the origin of the coordinate system
        """
        vector = self.p1.copy() - self.p2.copy()
        return vector.copy().unit()

    def is_constant(self) -> bool:
        """ Method checking whether the line is constant (y values are equal)

        :return: True if y values are equal, otherwise False
        """
        return self.p1.y == self.p2.y

    def find_line_parameters(self) -> Tuple[float, float]:
        """ Method finding line parametrization as y = m*x + n
        p1.y = m*p1.x + n
        p2.y = m*p2.x + n
        subtracting both sides
        p1.y - p2.y = m*p1.x - m*p2.x
        m = (p1.y - p2.y) / (p1.x - p2.x)
        n = p1.y - m*p1.x

        :return: a Tuple with the first element being m and the second being n
        """
        m = (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)
        n = self.p1.y - m * self.p1.x
        return m, n

    def __str__(self) -> str:
        """ Method returning a string representation of a Line for a user

        :return: string representation of a Line instance
        """
        return "%s -> %s" % (self.p1, self.p2)

    def to_df(self) -> pd.DataFrame:
        """ Method converting a line object into a dataframe with end point coordinates

        :return: a DataFrame with x1, y1, x2, y2 columns
        """
        return pd.DataFrame(columns=['x1', 'y1', 'x2', 'y2'],
                            data=[[self.p1.x, self.p1.y, self.p2.x, self.p2.y]],
                            index=[0])

    @staticmethod
    def find_intersection_with_circle(r: float, m: float, n: float) -> Union[None, Point]:
        """ Method finding intersection of a circle given by radius and line given by y = m*x + n parametrization
        (x-x_0)^2 + (y-y_0)^2 = r^2
        y = m*x+n
        for simplicity, x_0 = 0, y_0 = 0
        x^2 + y^2 = r^2
        x^2 + (mx+n)^2 = r^2
        x^2 + m^2*x^2 + 2*m*n*x + n^2 - r^2 = 0
        (1 + m^2) * x^2 + 2*m*n*x + n^2 - r^2 = 0
        Let, a = 1 + m^2, b = 2*m*n, c = n^2 - r^2
        delta = b^2 - 4*a*c
        if delta < 0 - a real valued solution does not exist
        otherwise, there are two solution exist, one with negative x and the other with positive,
        we take positive one assuming that we are in the first quadrant
        x = (-b + sqrt(delta)) / 2a
        y = m*x + n
        :param r: radius of a circle
        :param m: m line coefficient
        :param n: n line coefficient
        :return: If there is an intersection, then Point is returned, otherwise None
        """

        a = 1 + m ** 2
        b = 2 * m * n
        c = n ** 2 - r ** 2

        delta = b ** 2 - 4 * a * c
        if delta < 0:
            return None
        else:
            x = (-b + delta ** 0.5) / (2 * a)
            y = m * x + n
            return Point.of_cartesian(x, y)

    def copy(self) -> "Line":
        """ Method returning a copy of a current Line instance

        :return: a copy of a Line instance
        """
        return Line.of_end_points(p1=self.p1.copy(), p2=self.p2.copy())

    def det(self) -> float:
        """ Method calculating line length

        :return: lenght of the line
        """
        return (self.p2 - self.p1).det()

    @staticmethod
    def calc_arc_length_between_two_lines(radius: float, line_low: "Line", line_up: "Line") -> float:
        """ Static method calculating arc lenght between two lines. The method is used to compute wedge length at
        its tip between two blocks. The method uses the law of cosines in order to compute the length. It is assumed
        that both lines are defined with the same unit.

        :param radius: radius with which the lines are intercepting
        :param line_low: lower line
        :param line_up: upper line
        :return: arc length in units determined from the line definitions
        """
        # find crossing points of both lines with the radius
        m_low, n_low = line_low.find_line_parameters()
        p_low = Line.find_intersection_with_circle(radius, m_low, n_low)
        m_up, n_up = line_up.find_line_parameters()
        p_up = Line.find_intersection_with_circle(radius, m_up, n_up)
        # calculate d
        d = (p_low - p_up).det()
        # calculate theta from the law of cosines
        theta = math.acos(1 - d ** 2 / (2 * radius ** 2))
        l_arc = radius * theta
        return l_arc

    @staticmethod
    def calculate_point_orientation_wrt_line(line: "Line", point: Point, eps=1e-12) -> int:
        """ Method calculating orientation of a point w.r.t a line
        The orientation is obtained from the sign of a matrix (http://www.cs.cmu.edu/~quake/robust.html)
        - if the sign is positive, then the point is on the left side
        - if the sign is negative, then the point is on the right sied
        - if the sign equal to 0 (with eps tolerance), then it is assumed that the point is on the line

        :param line: reference line
        :param point: point for which the orientation is checked
        :return: -1 (on the right), +1 (on the left), 0 (on the line)
        """
        matrix = np.array([[line.p1.x - point.x, line.p1.y - point.y],
                          [line.p2.x - point.x, line.p2.y - point.y]])
        det = np.linalg.det(matrix)
        if abs(det) < eps:
            return 0
        else:
            return np.sign(det)

    @staticmethod
    def is_line_intercepting_radius(radius: float, line: "Line") -> bool:
        """ Method calculating whether a line is intercepting a radius.

        :param radius: radius to check
        :param line: line to calculate the interception
        :return: True if at least one point is within the radius, otherwise False
        """
        return (line.p1.get_r() < radius) or (line.p2.get_r() < radius)

    @staticmethod
    def find_interception_parameter(r: float, line: "Line") -> Union[None, float]:
        """ Method finding an interception parameter of a line with a radius
        Assuming that the center of the circle is at 0,0
        The segment S form p1 to p2 is parameterised as
        S = p1 + t(p2-p1) = p1 + t*v for v = p2-p1, and t = [0, 1]
        The segment intercepts the circle when
        |S - q| = r, with our assumption:
        |S| = r, |p1 + t*v| = r
        Squaring both sides we obtain:
        |p1 + t*v|^2 = r^2
        (p1 + t*v)^2 = r^2
        p1^2 + 2*t*v*p1 + (t*v)^2 - r^2 = 0
        (t*v)^2 + 2*t*v + p1^2 - r^2 = 0
        then, a = v^2, b = 2*v, c = p1^2 - r^2
        Then, delta is equal to b**2 - 4*a*c . For negative delta, the line does not intercept radius. Otherwise,
        t1 and t2 can be computed. Only if one of the solutions is in [0, 1] range, then the line segment intercepts a
        radius. Values outside of this range indicate that the segment would need to be extended in order to cross a
        radius.

        :param r: radius with center at 0, 0
        :param line: line for which the interception parameter is calculated
        :return: None if there is no intersection
        """

        v = line.p2 - line.p1
        a = v.dot(v)
        b = 2 * v.dot(line.p1)
        c = line.p1.dot(line.p1) - r ** 2

        delta = b ** 2 - 4 * a * c

        if delta < 0:
            return None

        t1 = (-b + delta ** (0.5)) / (2 * a)
        t2 = (-b - delta ** (0.5)) / (2 * a)

        if 0 <= t1 <= 1:
            return t1
        elif 0 <= t2 <= 1:
            return t2
        else:
            return None

    def plot(self, ax: plt.Axes, color="black") -> None:
        """ Method plotting an Area instance on an input axis

        :param ax: input axis for plot
        :param color: color for line plotting, black by default
        """
        ax.plot([self.p1.x, self.p2.x], [self.p1.y, self.p2.y], color=color)

    @staticmethod
    def calculate_positioning_angle(line_ref: "Line", radius: float) -> float:
        """ Method calculating the positioning angle from the point of line crossing a radius

        :param line_ref: reference line for which the positioning angle is calculated
        :param radius: radius for which the positioning angle is calculated
        :return: positioning angle in degrees
        """
        if line_ref.is_constant():
            y = line_ref.p1.y
            p_cross = Point.of_cartesian(x=math.sqrt(radius ** 2 - y ** 2), y=y)
        else:
            m, n = line_ref.find_line_parameters()
            p_cross = Line.find_intersection_with_circle(radius, m, n)

        return p_cross.get_phi()

    @staticmethod
    def calculate_relative_alpha_angle(line_ref: "Line") -> float:
        """ Static method calculating the inclination angle of a line, i.e., its slope angle in degrees.
        There are three cases:
        - 0 degrees if the line is constant,
        - 90 degrees if the x coordinates are the same,
        - arcus tangent of the slope coefficient
        The method is used to calculate block inclination angle

        :param line_ref: a Line instance for which the angle is calculated
        :return: slope angle in degrees
        """
        if line_ref.is_constant():
            alpha_ref = 0
        elif line_ref.p1.x == line_ref.p2.x and (line_ref.p1.y < line_ref.p2.y):
            alpha_ref = 90
        elif line_ref.p1.x == line_ref.p2.x and (line_ref.p1.y > line_ref.p2.y):
            alpha_ref = 270
        else:
            m, _ = line_ref.find_line_parameters()
            alpha_ref = math.degrees(math.atan(m))

        return alpha_ref
