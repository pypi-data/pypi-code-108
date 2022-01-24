from typing import Tuple, Union
from dataclasses import dataclass

import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Arc import Arc
from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.primitives.Point import Point


@dataclass(frozen=True)
class Area:
    """ An Area class implementing a 2D area made of connected lines/arcs

   Attributes:
       lines (Tuple): tuple of Line/Arc objects
    """
    lines: Tuple[Union[Line, Arc], ...]

    @staticmethod
    def of_lines(lines: Tuple[Union[Line, Arc], ...]) -> "Area":
        """ Static method creating an Area object from a tuple of Line objects. Line objects are copied to preserve
        static behaviour and avoid side effects.

        :param lines: tuple of Line objects
        :return: An area with copy of input Line objects
        """
        return Area(lines=tuple(line.copy() for line in lines))

    @staticmethod
    def of_closed_ordered_list_of_points(points: Tuple[Point, ...]) -> "Area":
        #ToDo: add test
        #ToDo: add docstring
        lines = []
        for ix in range(len(points) - 1):
            lines.append(Line.of_end_points(points[ix], points[ix + 1]))

        lines.append(Line.of_end_points(points[-1], points[0]))

        return Area.of_lines(tuple(lines))

    def get_line(self, index: int) -> Line:
        """ Method returning a line at a given index.

        :param index: index of line to be returned
        :return: Line at the given index
        """
        if abs(index) >= len(self.lines):
            raise IndexError('The requested line index %d is out of range for a list of length %d' %
                             (index, len(self.lines)))
        return self.lines[index].copy()

    def copy(self) -> "Area":
        """ Method returning a copy of an Area instance

        :return: a new Area instance with copy of lines
        """
        return Area(lines=tuple(line.copy() for line in self.lines))

    def translate(self, vector: Point) -> "Area":
        """ Method translating an Area instance by a given vector

        :param vector: vector by which an area is translated
        :return: a translated area
        """
        return Area(lines=tuple(line.translate(vector) for line in self.lines))

    def rotate(self, angle: float) -> "Area":
        """ Method rotating area by a given angle w.r.t. origin of the coordinate system (0, 0)

        :param angle: rotation angle in degrees
        :return: rotated area
        """
        return Area(lines=tuple(line.rotate(angle) for line in self.lines))

    def plot(self, ax: plt.Axes) -> None:
        """ Method plotting an Area instance on an input axis

        :param ax: input axis for plot
        """
        for line in self.lines:
            line.plot(ax)

    def __str__(self):
        """ Method returning a string representation of an Area for a user

        :return: string representation of an Area instance
        """
        return ",".join([str(line) for line in self.lines])

    def to_df(self):
        """ Method converting a line object into a dataframe with end point coordinates of each line. Lines are
        distinguished by 1-based index.

        :return: a DataFrame with x1_i, y1_i, x2_i, y2_i columns, where i is the line index (1-based)
        """
        return pd.concat([line.to_df().add_suffix('_%d' % (i + 1)) for i, line in enumerate(self.lines)], axis=1)

    @staticmethod
    def find_trapezoid_shift_to_intercept_with_radius(radius: float, area: "Area", eps=1e-6) -> float:
        """ Method finding a shift for a trapezoidal area to get in contact with a radius.
        The method works as follows:

        - for lower (index 0) line of an area, find an intersection point with a radius
        - for upper (index 2) line of an area, find an intersection point with a radius

        - find distance between the intersection point and lower line end point closest to the radius (p2)
        - find distance between the intersection point and upper line end point closest to the radius (p1)

        - take the shortest distance

        - shift the line closes to the radius (index 3) and shift according to the bisection method between 0 and the
        shortest distance

        :param radius: radius for which the shift is calculated
        :param area: area which is shifted in order to get in contact with a radius
        :param eps: bisection method accuracy
        :return: shift distance by which a trapezoidal area needs to be shifted in order to get in contact with radius
        (up to the eps accuracy)
        """
        # find point of crossing radial segment extension with radius
        # # lower line
        line_low = area.get_line(0)

        m_low, n_low = line_low.find_line_parameters()
        p_cross_low = Line.find_intersection_with_circle(radius, m_low, n_low)

        ## upper line
        line_up = area.get_line(2)
        m_up = m_low
        n_up = line_up.p2.y - m_up * line_up.p2.x
        p_cross_up = Line.find_intersection_with_circle(radius, m_up, n_up)

        if p_cross_low is None and p_cross_up is None:
            return 0.0

        # find maximum distance from the circle
        v_dir_low = p_cross_low - line_low.p1.copy()
        det_v_dir_l = v_dir_low.det()

        if abs(det_v_dir_l) <= 1e-12:
            return 0.0

        if p_cross_up is None:
            det_v_dir_u = 0
        else:
            v_dir_up = p_cross_up - line_up.p2.copy()
            det_v_dir_u = v_dir_up.det()

        # # take the maximum
        max_v_dir = max(det_v_dir_l, det_v_dir_u)

        # shift along this axis
        v_dir_l_unit = v_dir_low.unit()

        # lower point
        p_low = p_low_transl = area.get_line(0).p1.copy()
        # upper point
        line_left = area.get_line(3)
        det_line_left = line_left.det()
        alpha_left = Line.calculate_relative_alpha_angle(line_left)
        delta_alpha = 0 if alpha_left == 90 else 180
        p_up_transl = p_low.copy().translate(Point.of_polar(det_line_left, delta_alpha + alpha_left))

        start = 0
        end = max_v_dir
        shift = eps
        while (end - start) > eps:
            shift = (end + start) / 2
            p_low_transl = p_low.translate(v_dir_l_unit * shift)
            p_up_transl = p_low_transl.copy().translate(Point.of_polar(det_line_left, delta_alpha + alpha_left))

            if Line.find_interception_parameter(radius, Line.of_end_points(p_low_transl, p_up_transl)) is not None or \
                    Line.is_line_intercepting_radius(radius, Line.of_end_points(p_low_transl, p_up_transl)):
                end = shift
            else:
                start = shift

        if Line.find_interception_parameter(radius, Line.of_end_points(p_low_transl, p_up_transl)) is not None or \
            Line.is_line_intercepting_radius(radius, Line.of_end_points(p_low_transl, p_up_transl)):
            shift = start

        return shift

    @staticmethod
    def is_outside_of_first_quadrant(area: "Area", eps=1e-30) -> bool:
        """ Method checking whether an area is fully positioned in the first quadrant.

        :param area: an Area instance for which the check is performed
        :param eps: a machine precision for comparison of 0 value
        :return: True if an Area instance is in the first quadrant, False otherwise
        """
        is_x_nonegative = all([(line.p1.x >= -eps) and (line.p2.x >= -eps) for line in area.lines])
        is_y_nonegative = all([(line.p1.y >= -eps) and (line.p2.y >= -eps) for line in area.lines])
        return not (is_x_nonegative and is_y_nonegative)

    @staticmethod
    def are_areas_overlapping(area_a: "Area", area_b: "Area") -> True:
        line_a = area_a.get_line(2)
        line_a_rev = Line.of_end_points(line_a.p2, line_a.p1)
        orient_p1 = Line.calculate_point_orientation_wrt_line(line_a_rev, area_b.get_line(0).p1)
        orient_p2 = Line.calculate_point_orientation_wrt_line(line_a_rev, area_b.get_line(0).p2)

        return orient_p1 == -1 or orient_p2 == -1
