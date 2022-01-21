import math
from unittest import TestCase
from unittest.mock import patch

import dataclasses
import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Point import Point


class TestPoint(TestCase):
    def test_of_cartesian(self):
        # arrange
        x = 1
        y = 5

        # act
        p = Point.of_cartesian(x, y)

        # assert
        self.assertEqual(x, p.x)
        self.assertEqual(y, p.y)

    def test_of_polar(self):
        # arrange
        r = 1
        phi = 60

        # act
        p = Point.of_polar(r, phi)

        # assert
        self.assertAlmostEqual(r, p.get_r(), places=6)
        self.assertAlmostEqual(phi, p.get_phi(), places=6)

    def test_copy(self):
        # arrange
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        # act
        p_copy = p.copy()

        # assert
        self.assertNotEqual(id(p), id(p_copy))
        self.assertEqual(id(p), id(p))
        self.assertEqual(id(p_copy), id(p_copy))

    def test_x(self):
        # arrange
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        # act
        x_act = p.x

        # assert
        self.assertEqual(x, x_act)

    def test_get_phi(self):
        # arrange
        r = 1
        phi = 60

        # act
        p = Point.of_polar(r, phi)

        # assert
        self.assertAlmostEqual(phi, p.get_phi(), places=6)

    def test_get_phi_in_rad(self):
        # arrange
        r = 1
        phi = 60

        # act
        p = Point.of_polar(r, phi)

        # assert
        self.assertAlmostEqual(2 * math.pi * phi / 360, p.get_phi_in_rad(), places=6)

    def test_get_r(self):
        # arrange
        r = 1
        phi = 60

        # act
        p = Point.of_polar(r, phi)

        # assert
        self.assertAlmostEqual(r, p.get_r(), places=6)

    def test_rotate(self):
        # arrange
        r = 1
        phi = 60
        p = Point.of_polar(r, phi)
        alpha = 15

        # act
        p_rotated = p.rotate(alpha)

        # assert
        self.assertAlmostEqual(phi + alpha, p_rotated.get_phi(), places=6)
        self.assertAlmostEqual(r, p_rotated.get_r(), places=6)

    def test_translate(self):
        # arrange
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        x_trans = 2
        y_trans = 2
        p_trans = Point.of_cartesian(x_trans, y_trans)

        # act
        p_new = p.translate(p_trans)

        # assert
        self.assertEqual(x + x_trans, p_new.x)
        self.assertEqual(y + y_trans, p_new.y)

    @patch("matplotlib.pyplot.show")
    def test_plot(self, mock_show=None):
        # arrange
        fig, ax = plt.subplots(figsize=(15, 15))
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        # act
        p.plot(ax)
        plt.show()

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_det(self):
        # arrange
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        # act
        det = p.det()

        # assert
        self.assertAlmostEqual(math.sqrt(x ** 2 + y ** 2), det, places=6)

    def test_dot(self):
        # arrange
        x = 1
        y = 5
        p = Point.of_cartesian(x, y)

        x_trans = 2
        y_trans = 2
        p2 = Point.of_cartesian(x_trans, y_trans)

        # act
        dot = p.dot(p2)

        #
        self.assertEqual(12, dot)

    def test_unit(self):
        # arrange
        x = 3
        y = 4
        p = Point.of_cartesian(x, y)

        # act
        unit = p.unit()

        # assert
        self.assertEqual(x / 5, unit.x)
        self.assertEqual(y / 5, unit.y)

    def test_unit_zero_length(self):
        # arrange
        x = 0
        y = 0
        p = Point.of_cartesian(x, y)

        # act
        unit = p.unit()

        # assert
        self.assertEqual(0, unit.x)
        self.assertEqual(0, unit.y)

    def test_str_int_int(self):
        # arrange
        x = 3
        y = 4
        p = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertEqual('(3, 4)', str(p))

    def test_str_int_float(self):
        # arrange
        x = 3
        y = 4.0
        p = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertEqual('(3, 4.000000)', str(p))

    def test_str_float_int(self):
        # arrange
        x = 3.0
        y = 4
        p = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertEqual('(3.000000, 4)', str(p))

    def test_str_float_float(self):
        # arrange
        x = 3.0
        y = 4.0
        p = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertEqual('(3.000000, 4.000000)', str(p))

    def test_repr(self):
        # arrange
        x = 3
        y = 4
        p = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertEqual('Point(3.000000, 4.000000)', repr(p))

    def test_equality(self):
        # arrange
        x = 3
        y = 4
        p1 = Point.of_cartesian(x, y)
        p2 = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertTrue(p1 == p2)

    def test_non_equality(self):
        # arrange
        x = 3
        y = 4
        p1 = Point.of_cartesian(x, y)
        x = 3
        y = 5
        p2 = Point.of_cartesian(x, y)

        # act
        # assert
        self.assertFalse(p1 == p2)

    def test_immutability_x(self):
        # arrange
        x = 3
        y = 4
        p1 = Point.of_cartesian(x, y)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('p1.x = 5')

    def test_immutability_y(self):
        # arrange
        x = 3
        y = 4
        p1 = Point.of_cartesian(x, y)

        # act
        with self.assertRaises(dataclasses.FrozenInstanceError):
            exec('p1.y = 5')
