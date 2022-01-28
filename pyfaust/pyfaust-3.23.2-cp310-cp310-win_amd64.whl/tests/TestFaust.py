import unittest
from pyfaust import (rand as frand, Faust, vstack, hstack, isFaust, dot,
                     concatenate, pinv, eye, dft, wht, is_gpu_mod_enabled)
from numpy.random import randint
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import aslinearoperator
import tempfile
import os
import random


class TestFaust(unittest.TestCase):

    MIN_NUM_FACTORS = 1
    MAX_NUM_FACTORS = 4
    MAX_DIM_SIZE = 256
    MIN_DIM_SIZE = 3

    def __init__(self, methodName='runTest', dev='cpu', field='real'):
        super(TestFaust, self).__init__(methodName)
        self.dev = dev
        self.field = field

    def setUp(self):
        """
        """
#        self.dev = 'cpu'
#        self.field = 'real'
#        if 'dev' in os.environ:
#            self.dev = os.environ['dev']
#        if 'field' in os.environ:
#            self.field = os.environ['field']
        nrows = randint(TestFaust.MIN_DIM_SIZE,
                        TestFaust.MAX_DIM_SIZE+1)
        ncols = randint(TestFaust.MIN_DIM_SIZE,
                        TestFaust.MAX_DIM_SIZE+1)
        nfacts = randint(TestFaust.MIN_NUM_FACTORS,
                         TestFaust.MAX_NUM_FACTORS+1)
        self.F = frand(nrows, ncols, num_factors=nfacts, dev=self.dev, field=self.field)
        self.nrows = nrows
        self.ncols = ncols
        self.nfacts = nfacts

    def test_toarray(self):
        print("Faust.toarray")
        # this test of toarray depends (and tests) Faust.factors() and
        # numfactors()
        factors = [self.F.factors(i) for i in range(self.F.numfactors())]
        fullF = np.eye(self.ncols)
        for fac in reversed(factors):
            fullF = fac @ fullF
        self.assertTrue(np.allclose(self.F.toarray(), fullF))

    def test_nbytes(self):
        print("Faust.nbytes")
        # this test of nbytes depends (and tests) Faust.factors() and
        # numfactors()

        def sparse_fac_size(sfac):
            int_size = 4
            double_size = 8
            cplx_size = 16
            nnz = sfac.nnz
            nrows = sfac.shape[0]
            size = nnz*int_size+(nrows+1)*int_size
            if sfac.dtype == np.complex:
                size += cplx_size*nnz
            elif sfac.dtype == np.float:
                size += double_size*nnz
            return size
        Fsize = 0
        for i in range(0, self.F.numfactors()):
            fac = self.F.factors(i)
            if isinstance(fac, np.ndarray):
                Fsize += fac.nbytes
            elif isinstance(fac, csr_matrix):
                Fsize += sparse_fac_size(fac)
        self.assertEqual(Fsize, self.F.nbytes)

    def test_shape(self):
        print("Faust.shape")
        self.assertEqual(self.nrows, self.F.shape[0])
        self.assertEqual(self.ncols, self.F.shape[1])

    def test_ndim(self):
        print("Faust.ndim")
        self.assertEqual(self.F.ndim, 2)

    def test_size(self):
        print("Faust.size")
        self.assertEqual(self.F.size, self.nrows*self.ncols)

    def test_device(self):
        print("Faust.device")
        self.assertEqual(self.F.device, self.dev)

    def test_transpose(self):
        print("Faust.transpose")
        self.assertTrue(np.allclose(self.F.T.toarray().T, self.F.toarray()))
        self.assertTrue(np.allclose(self.F.transpose().toarray().T,
                                    self.F.toarray()))

    def test_conj(self):
        print("Faust.conj")
        self.assertTrue(np.allclose(self.F.conj().toarray(),
                                    self.F.toarray().conj()))
        self.assertTrue(np.allclose(self.F.conjugate().toarray(),
                                    self.F.toarray().conjugate()))

    def test_transconj(self):
        print("Faust.H")
        self.assertTrue(np.allclose(self.F.H.toarray().conj().T,
                                    self.F.toarray()))
        self.assertTrue(np.allclose(self.F.getH().toarray().conj().T,
                                    self.F.toarray()))

    def test_pruneout(self):
        print("Faust.pruneout")
        self.assertLessEqual(self.F.pruneout().nbytes, self.F.nbytes)
        self.assertTrue(np.allclose(self.F.pruneout().toarray(),
                                    self.F.toarray()))

    def test_add(self):
        print("Faust.__add__, __radd__")
        G = frand(self.nrows, self.ncols, dev=self.dev)
        self.assertTrue(np.allclose((self.F+G).toarray(),
                                    self.F.toarray()+G.toarray()))
        self.assertTrue(np.allclose((self.F+G.toarray()).toarray(),
                                    self.F.toarray()+G.toarray()))

    def test_sub(self):
        print("Faust.__sub__, __rsub__")
        G = frand(self.nrows, self.ncols, dev=self.dev)
        self.assertTrue(np.allclose((self.F-G).toarray(),
                                    self.F.toarray()-G.toarray()))
        self.assertTrue(np.allclose((self.F-G.toarray()).toarray(),
                                    self.F.toarray()-G.toarray()))

    def test_div(self):
        print("Faust.__truediv__")
        self.assertTrue(np.allclose((self.F/2).toarray(), self.F.toarray()/2))

    def test_matmul(self):
        print("Faust.__matmul__, dot, __rmatmul__")
        G = frand(self.ncols, self.nrows, dev=self.dev)
        self.assertTrue(np.allclose((self.F@G).toarray(),
                                    self.F.toarray()@G.toarray()))
        self.assertTrue(np.allclose((self.F@G.toarray()),
                                    self.F.toarray()@G.toarray()))
        self.assertTrue(np.allclose((self.F.dot(G)).toarray(),
                                    self.F.toarray().dot(G.toarray())))
        self.assertTrue(np.allclose((dot(self.F, G)).toarray(),
                                    np.dot(self.F.toarray(), G.toarray())))
        self.assertTrue(np.allclose((self.F.matvec(G.toarray()[:, 1])),
                                    aslinearoperator(self.F.toarray()).matvec(G.toarray()[:, 1])))


    def test_concatenate(self):
        print("Faust.concatenate, pyfaust.vstack, pyfaust.hstack")
        G = frand(self.nrows, self.ncols, dev=self.dev)
        self.assertTrue(np.allclose((self.F.concatenate(G)).toarray(),
                                    np.concatenate((self.F.toarray(),
                                                    G.toarray()))))
        self.assertTrue(np.allclose((self.F.concatenate(G.toarray())).toarray(),
                                    np.concatenate((self.F.toarray(),
                                                    G.toarray()))))
        self._assertAlmostEqual(concatenate((self.F, G)), np.concatenate((self.F.toarray(),
                                                    G.toarray())))
        self._assertAlmostEqual(concatenate((self.F, G), axis=1), np.concatenate((self.F.toarray(),
                                                    G.toarray()), axis=1))
        self.assertTrue(np.allclose(vstack((self.F, G.toarray())).toarray(),
                                    np.vstack((self.F.toarray(),
                                                    G.toarray()))))
        self.assertTrue(np.allclose(hstack((self.F, G.toarray())).toarray(),
                                    np.hstack((self.F.toarray(),
                                                    G.toarray()))))

    def test_isFaust(self):
        print("test pyfaust.isFaust")
        self.assertTrue(isFaust(self.F))
        self.assertFalse(isFaust(object()))

    def test_nnz_sum(self):
        print("Faust.nnz_sum")
        nnz_sum = 0
        for i in range(0, self.F.numfactors()):
            nnz_sum += self.F.factors(i).nnz
        self.assertEqual(nnz_sum, self.F.nnz_sum())

    def test_density(self):
        print("Faust.density")
        self.assertEqual(self.F.density(), self.F.nnz_sum()/self.F.size)

    def test_rcg(self):
        print("Faust.rcg")
        self.assertEqual(self.F.density(), self.F.nnz_sum()/self.F.size)
        self.assertEqual(self.F.rcg(), 1/self.F.density())

    def test_norm(self):
        print("Faust.norm")
        for nt in ['fro', 1, 2, np.inf]:
            print("norm",nt)
            print(self.F.norm(nt),
                                        np.linalg.norm(self.F.toarray(), nt))
            self.assertTrue(np.allclose(self.F.norm(nt),
                                        np.linalg.norm(self.F.toarray(), nt),
                                        rtol=1e-2))

    def test_normalize(self):
        print("Faust.normalize")
        FA = self.F.toarray()
        for nt in ['fro', 1, 2, np.inf]:
            NF = self.F.normalize(nt)
            NFA = NF.toarray()
            for j in range(NFA.shape[1]):
                n = np.linalg.norm(FA[:, j],  2
                                   if nt ==
                                   'fro' else
                                   nt, )
                self.assertTrue(n == 0 or np.allclose(FA[:, j]/n, NFA[:, j], rtol=1e-3))

    def test_numfactors(self):
        print("Faust.numfactors")
        self.assertEqual(self.nfacts, self.F.numfactors())
        self.assertEqual(self.nfacts, self.F.__len__())

    def test_factors(self):
        print("Faust.factors")
        Fc = Faust([self.F.factors(i) for i in range(self.F.numfactors())])
        self.assertTrue(np.allclose(Fc.toarray(), self.F.toarray()))
        i = randint(0, self.F.numfactors())
        j = randint(0, self.F.numfactors())
        if self.F.numfactors() > 1:
            if i > j:
                tmp = i
                i = j
                j = tmp
            elif i == j:
                if j < self.F.numfactors()-1:
                    j += 1
                elif i > 0:
                    i -= 1
                else:
                    return # irrelevant test factors(i) already tested above
            Fp = self.F.factors(range(i, j+1))
            print(Fp)
            for k in range(i, j+1):
                # self.assertTrue(np.allclose(self.F.factors(k), Fp.factors(k)))
                self._assertAlmostEqual(self.F.factors(k), Fp.factors(k-i))


    def _assertAlmostEqual(self, a, b):
        if not isinstance(a, np.ndarray):
            a = a.toarray()
        if not isinstance(b, np.ndarray):
            b = b.toarray()
        self.assertTrue(np.allclose(a, b))

    def test_left_right(self):
        print("Faust.right, Faust.left")
        i = randint(0, self.F.numfactors())
        left = self.F.left(i)
        for k in range(0, i+1):
            if isFaust(left):
                fac = left.factors(k)
            else:
                fac = left
            if not isinstance(fac, np.ndarray):
                fac = fac.toarray()
            Ffac = self.F.factors(k)
            if not isinstance(Ffac, np.ndarray):
                Ffac = Ffac.toarray()
            self.assertTrue(np.allclose(fac, Ffac))

    def test_save(self):
        print("Faust.save")
        tmp_dir = tempfile.gettempdir()+os.sep
        rand_suffix = random.Random().randint(1, 1000)
        test_file = tmp_dir+"A"+str(rand_suffix)+".mat"
        self.F.save(test_file)
        Fs = Faust(test_file)
        self._assertAlmostEqual(Fs, self.F)

    def test_astype(self):
        print("test Faust.astype, Faust.dtype")
        try:
            if self.F.dtype == np.float:
                self.assertEqual(self.F.astype(np.complex).dtype, np.complex)
            else:
                self.assertEqual(self.F.astype(np.float).dtype, np.float)
        except ValueError:
            # complex > float not yet supported
            pass

    def test_pinv(self):
        print("Faust.pinv")
        self._assertAlmostEqual(self.F.pinv(), np.linalg.pinv(self.F.toarray()))
        self._assertAlmostEqual(pinv(self.F), np.linalg.pinv(self.F.toarray()))

    def test_issparse(self):
        print("Faust.issparse")
        self.assertEqual(self.F.issparse(), np.all([isinstance(self.F.factors(i),
                                                        csr_matrix) for i in
                                             range(0, self.F.numfactors())]))

    def test_swap_cols(self):
        print("Faust.swap_cols")
        j1 = randint(0, self.F.shape[1])
        j2 = randint(0, self.F.shape[1])
        sF = self.F.swap_cols(j1, j2)
        Fa = self.F.toarray()
        sFa = sF.toarray()
        self._assertAlmostEqual(sFa[:, j1], Fa[:, j2])
        self.assertAlmostEqual(sF.norm(), self.F.norm())

    def test_swap_rows(self):
        print("Faust.swap_rows")
        i1 = randint(0, self.F.shape[0])
        i2 = randint(0, self.F.shape[0])
        sF = self.F.swap_rows(i1, i2)
        Fa = self.F.toarray()
        sFa = sF.toarray()
        self._assertAlmostEqual(sFa[i1, :], Fa[i2, :])
        self.assertAlmostEqual(sF.norm(), self.F.norm())

    def test_optimize_memory(self):
        print("Faust.optimize_memory")
        self.assertLessEqual(self.F.optimize_memory().nbytes, self.F.nbytes)

    def test_optimize_time(self):
        print("Faust.optimize_time")
        # test only if CPU and no gpu_mod enabled
        # anyway the method is not yet implemented for GPU
        if self.dev == 'cpu' and not is_gpu_mod_enabled():
           oF = self.F.optimize_time()
           self._assertAlmostEqual(oF, self.F)

    def test_clone(self):
        print("Faust.clone")
        if self.dev =='cpu':
            Fc = self.F.clone()
        elif self.dev == 'gpu':
            Fc = self.F.clone()
            self._assertAlmostEqual(Fc, self.F)
            Fc_cpu = self.F.clone(dev='cpu')
            self._assertAlmostEqual(Fc_cpu, self.F)
            Fc_gpu = Fc_cpu.clone(dev='gpu')
            self._assertAlmostEqual(Fc_gpu, Fc_cpu)

    def test_sum(self):
        print("Faust.sum")
        for i in [0, 1]:
            self._assertAlmostEqual(self.F.sum(axis=i).toarray().reshape(1, self.F.shape[(i+1)%2]),
                                    np.sum(self.F.toarray(), axis=i))

    def test_average(self):
        print("Faust.average")
        weights = [ np.random.rand(self.F.shape[0]), np.random.rand(self.F.shape[1])]
        for i in [0, 1]:
            self._assertAlmostEqual(self.F.average(axis=i).toarray().reshape(1, self.F.shape[(i+1)%2]),
                                    np.average(self.F.toarray(), axis=i))
            self._assertAlmostEqual(self.F.average(axis=i,
                                                   weights=
                                                   weights[i]).toarray().reshape(1, self.F.shape[(i+1) % 2]),
                                    np.average(self.F.toarray(), axis=i,
                                               weights=weights[i]))

    def test_wht(self):
        print("test pyfaust.wht")
        pow2_exp = random.Random().randint(1, 10)
        n = 2**pow2_exp
        H = wht(n, False)
        fH = H.toarray()
        self.assertEqual(np.count_nonzero(fH), fH.size)
        for i in range(0, n-1):
            for j in range(i+1, n):
                self.assertTrue((fH[i, ::].dot(fH[j, ::].T) == 0).all())
        self._assertAlmostEqual(wht(n), wht(n, False).normalize())

    def test_dft(self):
        print("test pyfaust.dft")
        from numpy.fft import fft
        pow2_exp = random.Random().randint(1, 10)
        n = 2**pow2_exp
        F = dft(n, False)
        fF = F.toarray()
        ref_fft = fft(np.eye(n))
        self._assertAlmostEqual(fF, ref_fft)
        self._assertAlmostEqual(dft(n), dft(n, False).normalize())

    def test_eye(self):
        print("test pyfaust.eye")
        self._assertAlmostEqual(eye(self.nrows, self.ncols),
                                np.eye(self.nrows,
                                       self.ncols))
