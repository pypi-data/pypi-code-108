import AutoFeedback.varchecks as vc
import sympy as sp
import unittest
import numpy as np
from AutoFeedback.utils import check_module
check_module("sympy")


class tmod:
    x = sp.symbols("x")
    y = sp.Array([1, 2, x])
    z = sp.Matrix([[1, 2, 3], [1, 3, 2], [3, 1, 2]])
    d = {"a": 1, "b": 2}


class UnitTests(unittest.TestCase):
    def test_matrixshape(self):
        myz = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert(vc._check_size(tmod.z, myz))

    def test_notmatrixshape(self):
        myz = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9]])
        assert(not vc._check_size(tmod.z, myz))

    def test_arraysize(self):
        assert(vc._check_size(tmod.y, [1, 2, 3]))

    def test_notarraysize(self):
        assert(not vc._check_size(tmod.y, [1, 2, 3, 4]))

    def test_dictequal(self):
        assert(vc.check_value(tmod.d, {"b": 2, "a": 1}))

    def test_notdictequal(self):
        assert(not vc.check_value(tmod.d, {"b": 2, "a": 2}))

    def test_expr(self):
        assert(vc.check_value(tmod.x*tmod.x, sp.symbols("x")**2))

    def test_notexpr(self):
        assert(not vc.check_value(tmod.x*tmod.x, sp.symbols("x")**3))

    def test_matrix(self):
        assert(vc.check_value(tmod.z*tmod.z**(-1), sp.eye(3)))

    def test_notmatrix(self):
        assert(not vc.check_value(tmod.z, sp.eye(3)))


class SystemTests(unittest.TestCase):
    def test_mod_vard(self):
        assert(vc.check_vars('d', {"a": 1, "b": 2},
                             modname=tmod, output=False))

    def test_mod_varx(self):
        assert(vc.check_vars('x', sp.symbols("x"), modname=tmod, output=False))

    def test_mod_vary(self):
        assert(vc.check_vars('y', sp.Array(
            [1, 2, sp.symbols("x")]), modname=tmod, output=False))

    def test_mod_varz(self):
        assert(vc.check_vars('z', sp.Matrix(
            [[1, 2, 3], [1, 3, 2], [3, 1, 2]]), modname=tmod, output=False))

    def test_notmod_varx(self):
        assert(not vc.check_vars('x', [2, 3], modname=tmod, output=False))

    def test_notmod_vary(self):
        assert(not vc.check_vars('y', [1, 2, "x"], modname=tmod, output=False))
