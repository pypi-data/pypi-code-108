import math
from unittest import TestCase

import dataclasses

from magnumapi.geometry.primitives.Arc import Arc
from magnumapi.geometry.primitives.Point import Point


class TestArc(TestCase):
    def test_calculate_theta_in_rad(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        # assert
        self.assertAlmostEqual(math.radians(90), Arc.calculate_theta_in_rad(p_start, p_end), places=6)

    def test_get_start_angle_in_rad(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)
        # assert
        self.assertAlmostEqual(math.radians(0), arc.get_start_angle_in_rad(), places=6)

    def test_get_start_angle(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)
        # assert
        self.assertAlmostEqual(0, arc.get_start_angle(), places=6)

    def test_get_end_angle_in_rad(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)
        # assert
        self.assertAlmostEqual(math.radians(90), arc.get_end_angle_in_rad(), places=6)

    def test_get_end_angle(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)
        # assert
        self.assertAlmostEqual(90, arc.get_end_angle(), places=6)

    def test_get_radius(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)
        # assert
        self.assertAlmostEqual(10, arc.get_radius(), places=6)

    def test_describe_ellipse_arc_open(self):
        # arrange
        # act
        arc_str = Arc.describe_ellipse_arc(x_center=0.0, y_center=0.0, a=1.0, b=1.0, start_angle=0.0,
                                           end_angle=2 * math.pi, N=3,
                                           closed=False)

        # assert
        arc_str_ref = 'M 1.0, 0.0L-1.0, 1.2246467991473532e-16L1.0, -2.4492935982947064e-16'
        self.assertEqual(arc_str_ref, arc_str)

    def test_describe_ellipse_arc_closed(self):
        # arrange
        # act
        arc_str = Arc.describe_ellipse_arc(x_center=0.0, y_center=0.0, a=1.0, b=1.0, start_angle=0.0,
                                           end_angle=2 * math.pi, N=3,
                                           closed=True)

        # assert
        arc_str_ref = 'M 1.0, 0.0L-1.0, 1.2246467991473532e-16L1.0, -2.4492935982947064e-16 Z'
        self.assertEqual(arc_str_ref, arc_str)

    def test_immutability_p_start(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('arc.p_start = p_end')

    def test_immutability_p_center(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('arc.p_center = p_end')

    def test_immutability_theta(self):
        # arrange
        p_start = Point.of_cartesian(10, 0)
        p_end = Point.of_cartesian(0, 10)

        # act
        arc = Arc.of_end_points_center(p_start, p_end)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('arc.theta = 90')