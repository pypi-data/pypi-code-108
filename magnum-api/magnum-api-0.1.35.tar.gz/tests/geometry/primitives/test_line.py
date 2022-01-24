import math
from unittest import TestCase

import dataclasses

from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.primitives.Point import Point


class TestLine(TestCase):
    def test_calc_arc_length_between_two_lines(self):
        # arrange
        radius = 10
        center = Point.of_cartesian(0, 0)
        p_end_first = Point.of_polar(20, 30)
        p_end_second = Point.of_polar(20, 60)

        l_first = Line.of_end_points(center, p_end_first)
        l_second = Line.of_end_points(center, p_end_second)

        # act
        l_arc = Line.calc_arc_length_between_two_lines(radius, l_first, l_second)

        # assert
        self.assertAlmostEqual(radius * math.radians(30), l_arc, places=6)

    def test_calculate_point_orientation_wrt_line_positive_on_left(self):
        # arrange
        p1 = Point.of_cartesian(0, 0)
        p2 = Point.of_polar(20, 30)

        point = Point.of_polar(30, 45)
        line = Line.of_end_points(p1, p2)

        # act
        orientation = Line.calculate_point_orientation_wrt_line(line, point)

        # assert
        self.assertEqual(1, orientation)

    def test_calculate_point_orientation_wrt_line_negative_on_right(self):
        # arrange
        p1 = Point.of_cartesian(0, 0)
        p2 = Point.of_polar(20, 30)

        point = Point.of_polar(30, 15)
        line = Line.of_end_points(p1, p2)

        # act
        orientation = Line.calculate_point_orientation_wrt_line(line, point)

        # assert
        self.assertEqual(-1, orientation)

    def test_calculate_point_orientation_wrt_line_zero_on_line(self):
        # arrange
        p1 = Point.of_cartesian(0, 0)
        p2 = Point.of_polar(20, 30)

        point = Point.of_polar(10, 30)
        line = Line.of_end_points(p1, p2)

        # act
        orientation = Line.calculate_point_orientation_wrt_line(line, point)

        # assert
        self.assertEqual(0, orientation)

    def test_rotate(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)

        line = Line.of_end_points(p1, p2)

        alpha = 30

        # act
        line_rotated = line.rotate(alpha)

        # assert
        self.assertAlmostEqual(Point.of_polar(10, 40).x, line_rotated.p1.x, places=6)
        self.assertAlmostEqual(Point.of_polar(10, 40).y, line_rotated.p1.y, places=6)
        self.assertAlmostEqual(Point.of_polar(20, 60).x, line_rotated.p2.x, places=6)
        self.assertAlmostEqual(Point.of_polar(20, 60).y, line_rotated.p2.y, places=6)

    def test_str(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)

        line = Line.of_end_points(p1, p2)

        # act
        str_act = str(line)

        # assert
        self.assertEqual("(9.848078, 1.736482) -> (17.320508, 10.000000)", str_act)

    def test_immutability_p1(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)


        # act
        line = Line.of_end_points(p1, p2)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('line.p1 = p2')

    def test_immutability_p2(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)


        # act
        line = Line.of_end_points(p1, p2)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('line.p2 = p1')
