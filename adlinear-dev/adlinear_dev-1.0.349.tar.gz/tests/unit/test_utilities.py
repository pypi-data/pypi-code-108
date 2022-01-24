import numpy as np
from adlinear import utilities as utl

epsilon = 1e-10


def almost_eq(x, y):
    return abs(x-y) <= epsilon


def test_hhi():
    res = utl.hhi_1([0, 1, 0, 1, 0, 1])
    assert (almost_eq(res, 3))
    res = utl.hhi_1([-1] * 100)
    assert (almost_eq(res, 100))
    res = utl.hhi_1([0])
    assert (res == 0)


def test_mean_square():

    for i in range(2, 10):
        mytab = np.arange(start=1, stop=i+1)
        res = utl.mean_square(mytab)
        assert (almost_eq(res, (i+1)*(2*i+1)/6.0))
