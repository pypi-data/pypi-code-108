from unittest import TestCase

import dataclasses

from magnumapi.geometry.primitives.Area import Area
from magnumapi.geometry.primitives.Point import Point
from magnumapi.geometry.primitives.Line import Line


class TestArea(TestCase):

    def test_get_line(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)
        p3 = Point.of_polar(15, 45)


        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p1)

        area = Area.of_lines((l1, l2, l3))

        # act
        # assert
        with self.assertRaises(IndexError) as context:
            area.get_line(5)

        self.assertTrue('The requested line index 5 is out of range for a list of length 3' in str(context.exception))

    def test_get_line_negative(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)
        p3 = Point.of_polar(15, 45)


        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p1)

        area = Area.of_lines((l1, l2, l3))

        # act
        # assert
        with self.assertRaises(IndexError) as context:
            area.get_line(-5)

        self.assertTrue('The requested line index -5 is out of range for a list of length 3' in str(context.exception))

    def test_rotate(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)
        p3 = Point.of_polar(15, 45)


        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p1)

        alpha = 30

        area = Area.of_lines((l1, l2, l3))

        # act
        area_rotated = area.rotate(alpha)

        # assert
        # # line 1
        self.assertAlmostEqual(Point.of_polar(10, 40).x, area_rotated.get_line(0).p1.x, places=6)
        self.assertAlmostEqual(Point.of_polar(10, 40).y, area_rotated.get_line(0).p1.y, places=6)
        self.assertAlmostEqual(Point.of_polar(20, 60).x, area_rotated.get_line(0).p2.x, places=6)
        self.assertAlmostEqual(Point.of_polar(20, 60).y, area_rotated.get_line(0).p2.y, places=6)

        # # line 2
        self.assertAlmostEqual(Point.of_polar(20, 60).x, area_rotated.get_line(1).p1.x, places=6)
        self.assertAlmostEqual(Point.of_polar(20, 60).y, area_rotated.get_line(1).p1.y, places=6)
        self.assertAlmostEqual(Point.of_polar(15, 75).x, area_rotated.get_line(1).p2.x, places=6)
        self.assertAlmostEqual(Point.of_polar(15, 75).y, area_rotated.get_line(1).p2.y, places=6)

        # # line 3
        self.assertAlmostEqual(Point.of_polar(15, 75).x, area_rotated.get_line(2).p1.x, places=6)
        self.assertAlmostEqual(Point.of_polar(15, 75).y, area_rotated.get_line(2).p1.y, places=6)
        self.assertAlmostEqual(Point.of_polar(10, 40).x, area_rotated.get_line(2).p2.x, places=6)
        self.assertAlmostEqual(Point.of_polar(10, 40).y, area_rotated.get_line(2).p2.y, places=6)

    def test_str(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)
        p3 = Point.of_polar(15, 45)


        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p1)

        alpha = 30

        area = Area.of_lines((l1, l2, l3))

        # act
        str_act = str(area)

        # assert
        self.assertEqual('(9.848078, 1.736482) -> (17.320508, 10.000000),(17.320508, 10.000000) -> '
                         '(10.606602, 10.606602),(10.606602, 10.606602) -> (9.848078, 1.736482)', str_act)

    def test_find_trapezoid_shift_to_intercept_with_radius_no_interception(self):
        # arrange
        p1 = Point.of_cartesian(10, 10)
        p2 = Point.of_cartesian(20, 10)
        p3 = Point.of_cartesian(20, 20)
        p4 = Point.of_cartesian(10, 20)

        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p4)
        l4 = Line.of_end_points(p4, p1)

        area = Area.of_lines((l1, l2, l3, l4))

        # act
        shift = Area.find_trapezoid_shift_to_intercept_with_radius(1, area)

        # assert
        self.assertAlmostEqual(0.0, shift, places=1)

    def test_immutability(self):
        # arrange
        p1 = Point.of_polar(10, 10)
        p2 = Point.of_polar(20, 30)
        p3 = Point.of_polar(15, 45)


        l1 = Line.of_end_points(p1, p2)
        l2 = Line.of_end_points(p2, p3)
        l3 = Line.of_end_points(p3, p1)

        area = Area.of_lines((l1, l2, l3))

        # assert
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('area.lines = (l3, l2, l1)')
