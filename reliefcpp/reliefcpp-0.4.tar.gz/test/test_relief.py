import unittest
import reliefcpp
import numpy as np
from mnist import MNIST
from numpy.testing import assert_allclose


class test_interface(unittest.TestCase):
    def test1(self):
        rr = reliefcpp.Relief(4, 1, 1)
        a = np.array([
            [1, 1, 0, 0],
            [1, 0.2, 1, 0],
            [0, 1, 0.2, 1],
            [0, 0, 1, 1]
        ])
        b = np.array([0, 0, 1, 2])

        rr.fit(a, b)
        xnew = rr.transform(a)
        print('xnew', xnew)

        print('scores', rr.scores)

    def test2(self):
        rr = reliefcpp.ReliefK(4)
        a = np.array([
            [1, 1, 0, 0],
            [1, 0.2, 1, 0],
            [0, 1, 0.2, 1],
            [0, 0, 1, 1]
        ])
        b = np.array([0, 0, 1, 1])

        rr.fit(a, b)
        xnew = rr.transform(a)
        print('xnew', xnew)

        print('scores', rr.scores)

    def test3(self):
        rr = reliefcpp.ReliefF(4)
        a = np.array([
            [1, 1, 0, 0],
            [1, 0.2, 1, 0],
            [0, 1, 0.2, 1],
            [0, 0, 1, 1]
        ])
        b = np.array([0, 0, 1, 2])

        rr.fit(a, b)
        xnew = rr.transform(a)
        print('xnew', xnew)

        print('scores', rr.scores)


if __name__ == "__main__":
    unittest.main()
