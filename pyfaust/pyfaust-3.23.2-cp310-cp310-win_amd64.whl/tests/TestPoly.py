import unittest
from pyfaust.poly import basis, poly, expm_multiply
from numpy.random import randint
import numpy as np
from scipy.sparse import csr_matrix, random
from scipy.sparse.linalg import expm_multiply as scipy_expm_multiply
import tempfile
import os

dev = 'cpu'
field = 'real'


class TestPoly(unittest.TestCase):

    def __init__(self, methodName='runTest', dev='cpu', field='real'):
        super(TestPoly, self).__init__(methodName)
        self.dev = dev
        self.field = field

    def setUp(self):
        self.d = 50
        self.density = 0.02
        if self.field == 'complex':
            self.dtype = 'complex'
        else:
            self.dtype = 'double'
        self.L = random(self.d, self.d, .02, format='csr', dtype=self.dtype)
        self.K = 5

    def test_basis(self):
        print("Test basis()")
        d = self.d
        L = self.L
        K = self.K
        density = self.density
        F = basis(L, K, 'chebyshev', dev=self.dev)
        # assert the dimensions are consistent to L
        self.assertEqual(F.shape[0], (K+1)*L.shape[0])
        self.assertEqual(F.shape[1], L.shape[0])
        # assert the 0-degree polynomial matrix is the identity
        last_fac = F.factors(F.numfactors()-1).toarray()
        Id = np.eye(d)
        self.assertTrue(np.allclose(Id, last_fac))
        if K >= 1:
            # assert the 1-degree polynomial matrix is in the form [Id ; L]
            deg1_fac = F.factors(F.numfactors()-2).toarray()
            self.assertTrue(np.allclose(deg1_fac[:d, :], Id))
            self.assertTrue(np.allclose(deg1_fac[d:2*d, :], L.toarray()))
            if K >= 2:
                # assert the 2-degree polynomial matrix is in the form [Id ; [-Id, L]]
                I2d = np.eye(2*d)
                deg2_fac = F.factors(F.numfactors()-3).toarray()
                self.assertTrue(np.allclose(deg2_fac[:2*d, :], I2d))
                self.assertTrue(np.allclose(deg2_fac[2*d:, :d], -Id))
                self.assertTrue(np.allclose(deg2_fac[2*d:, d:], 2*L.toarray()))
                if K >= 3:
                    # assert the n-degree polynomial matrix is in the form
                    # [I_nd ; [0 , -Id, 2L]]
                    for n in range(3, K):
                        Ind = np.eye(n*d)
                        degn_fac = F.factors(F.numfactors()-n-1).toarray()
                        self.assertTrue(np.allclose(degn_fac[:n*d, :], Ind))
                        self.assertTrue(np.allclose(degn_fac[n*d:, -2*d:-d], -Id))
                        self.assertTrue(np.allclose(degn_fac[n*d:, -d:],
                                                    2*L.toarray()))
                        zero_part = degn_fac[n*d:, :-2*d]
                        self.assertTrue(np.linalg.norm(zero_part) == 0)


    def test_basisT0(self):
        print("Test basis(T0)")
        d = self.d
        L = self.L
        K = self.K
        density = self.density
        T0 = random(d, 2, density, format='csr', dtype=self.dtype)
        F = basis(L, K, 'chebyshev', dev=self.dev, T0=T0)
        print(F)
        # assert the dimensions are consistent to L and TO
        self.assertEqual(F.shape[0], (K+1)*L.shape[0])
        self.assertEqual(F.shape[1], T0.shape[1])
        # assert the 0-degree polynomial matrix is T0
        last_fac = F.factors(F.numfactors()-1).toarray()
        self.assertTrue(np.allclose(T0.toarray(), last_fac))

    def test_poly(self):
        print("Test poly()")
        d = self.d
        L = self.L
        K = self.K
        density = self.density
        F = basis(L, K, 'chebyshev', dev=self.dev)
        coeffs = np.random.rand(K+1).astype(L.dtype)
        G = poly(coeffs, F)
        # Test polynomial as Faust
        poly_ref = np.zeros((d,d))
        for i,c in enumerate(coeffs[:]):
            poly_ref += c * F[d*i:(i+1)*d, :]
        self.assertAlmostEqual((G-poly_ref).norm(), 0)
        # Test polynomial as array
        GM = poly(coeffs, F.toarray())
        self.assertTrue(isinstance(GM, np.ndarray) and np.allclose(GM,
                                                                  poly_ref.toarray()))
        # Test polynomial-vector product
        x = np.random.rand(F.shape[1], 1).astype(L.dtype)
        # Three ways to do (not all as efficient as each other)
        Fx1 = poly(coeffs, F, dev=self.dev)@x
        Fx2 = poly(coeffs, F@x, dev=self.dev)
        Fx3 = poly(coeffs, F, X=x, dev=self.dev)
        self.assertTrue(np.allclose(Fx1, Fx2))
        self.assertTrue(np.allclose(Fx1, Fx3))
        # Test polynomial-matrix product
        X = np.random.rand(F.shape[1], 18).astype(L.dtype)
        FX1 = poly(coeffs, F, dev=self.dev)@X
        FX2 = poly(coeffs, F@X, dev=self.dev)
        FX3 = poly(coeffs, F, X=X, dev=self.dev)
        self.assertTrue(np.allclose(FX1, FX2))
        self.assertTrue(np.allclose(FX2, FX3))
        # Test creating the polynomial basis on the fly
        G2 = poly(coeffs, 'chebyshev', L)
        self.assertAlmostEqual((G-G2).norm(), 0)
        GX = poly(coeffs, 'chebyshev', L, X=X, dev=self.dev)
        self.assertTrue(np.allclose(GX, FX1))
        # Test polynomial-matrix product with arbitrary T0
        F_ = basis(L, K, 'chebyshev', dev=self.dev, T0=csr_matrix(X))
        GT0eqX = poly(coeffs, F_, dev=self.dev).toarray()
        self.assertTrue(np.allclose(GT0eqX, FX1))

    def test_expm_multiply(self):
        print("Test expm_multiply()")
        L = self.L
        L = L@L.T
        # test expm_multiply on a vector
        x = np.random.rand(L.shape[1]).astype(L.dtype)
        pts_args = {'start':-.5, 'stop':-0.1, 'num':3, 'endpoint':True}
        t = np.linspace(**pts_args).astype(L.dtype)
        y = expm_multiply(L, x, t)
        y_ref = scipy_expm_multiply(L, x, **pts_args)
        self.assertTrue(np.allclose(y, y_ref))
        # test expm_multiply on a matrix
        X = np.random.rand(L.shape[1], 32).astype(L.dtype)
        pts_args = {'start':-.5, 'stop':-0.1, 'num':3, 'endpoint':True}
        t = np.linspace(**pts_args)
        y = expm_multiply(L, X, t)
        y_ref = scipy_expm_multiply(L, X, **pts_args)
        self.assertTrue(np.allclose(y, y_ref))
        # test expm_multiply with (non-default) tradeoff=='memory'
        X = np.random.rand(L.shape[1], 32).astype(L.dtype)
        pts_args = {'start':-.5, 'stop':-0.1, 'num':3, 'endpoint':True}
        t = np.linspace(**pts_args)
        y = expm_multiply(L, X, t, tradeoff='memory')
        y_ref = scipy_expm_multiply(L, X, **pts_args)
        self.assertTrue(np.allclose(y, y_ref))
