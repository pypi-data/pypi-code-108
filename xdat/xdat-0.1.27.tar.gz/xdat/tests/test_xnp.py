import unittest
from ..xnp import *
from ..xchecks import *

monkey_patch()


class TestXNP(unittest.TestCase):
    def test_x_sum(self):
        a = numpy.array([2, 4, 6])
        self.assertEqual(a.sum(), numpy.x_sum(a))

    def test_x_dot(self):
        a = numpy.array([2, 4, 6]).reshape((3, 1))
        a2 = a.reshape((1, 3))
        check_equals(numpy.dot(a, a2), numpy.x_dot(a, a2))


