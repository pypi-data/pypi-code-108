import unittest
import numpy as np

import AutoFeedback.funcchecks as fc


class tmod:
    def f1(x):
        return(x**2)

    def f2(x, y):
        print(np.sqrt(tmod.f1(x)))


def f4(x):
    return x**2


def f3(x):
    return(np.sqrt(f4(x)))


class UnitTests(unittest.TestCase):
    def test_exists(self):
        assert(fc._exists('f1', modname=tmod))

    def test_notexists(self):
        assert(not fc._exists('f3', modname=tmod))

    def test_1input_vars(self):
        assert(fc._input_vars(tmod.f1, 10))

    def test_2input_vars(self):
        assert(fc._input_vars(tmod.f2, (10, 11)))

    def test_not1input_vars(self):
        assert(not fc._input_vars(tmod.f1, (10, 11, 12)))

    def test_not2input_vars(self):
        assert(not fc._input_vars(tmod.f2, (10,)))

    def test_returns(self):
        assert(fc._returns(tmod.f1, (10,)))

    def test_notreturns(self):
        assert(not fc._returns(tmod.f2, (10, 11)))

    def test_check_outputs(self):
        assert(fc._check_outputs(tmod.f1, (4,), 16))

    def test_2check_outputs(self):
        assert(fc._check_outputs(tmod.f1, (-10,), 100))

    def test_array_check_outputs(self):
        assert(fc._check_outputs(tmod.f1, (np.array([1, 2, 3]),), [1, 4, 9]))

    def test_notcheck_outputs1(self):
        assert(not fc._check_outputs(tmod.f1, (3,), 10))

    def test_notcheck_outputs2(self):
        assert(not fc._check_outputs(tmod.f2, (10, 11), 10))

    def test_calls(self):
        assert(fc._check_calls(f3, (10,), 'f4'))

    def test_notcalls(self):
        assert(not fc._check_calls(f3, (10,), 'f1'))


class SystemTests(unittest.TestCase):
    def test_f1(self):
        assert (fc.check_func('f1', [(3,), (-4,)], [9, 16],
                              modname=tmod, output=False) and
                not fc.check_func('f2', [(3,), (-4,)], [9, 16],
                                  modname=tmod, output=False))
