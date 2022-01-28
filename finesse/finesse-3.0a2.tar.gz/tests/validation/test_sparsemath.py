""""""
from finesse.cymath.sparsemath import CSRMatrix
from scipy.sparse import random
import numpy as np


def test_sparse_csr_multiply():
    for i in range(1000):
        N = np.random.randint(1, 10)
        M = np.random.randint(1, 10)
        A = random(M, N, dtype=complex, density=0.25).todense()
        x = np.random.randint(-100, 100, size=N)
        csr = CSRMatrix(A)
        # These should be numerically exact... but apprently not on debian test server
        assert np.max(abs(csr.multiply(x) - (A @ np.atleast_2d(x).T).T)) < 1e-6


def test_sparse_csr_vector_matrix_vector():
    for i in range(1000):
        N = np.random.randint(1, 10)
        M = np.random.randint(1, 10)
        A = random(M, N, dtype=complex, density=0.5).todense()
        x = np.random.randint(-100, 100, size=N) + 1j * np.random.randint(
            -100, 100, size=N
        )
        y = np.random.randint(-100, 100, size=M) + 1j * np.random.randint(
            -100, 100, size=M
        )
        csr = CSRMatrix(A)
        # These should be numerically exact... but apprently not on debian test server
        assert (
            np.max(
                abs(csr.zcsrgevmv(x, y) - np.atleast_2d(y) @ (A @ np.atleast_2d(x).T))
            )
            < 1e-6
        )


def test_sparse_csr_vector_hermitian_matrix_vector():
    for i in range(1000):
        N = np.random.randint(1, 10)
        M = np.random.randint(1, 10)
        A = random(M, N, dtype=complex, density=0.5).todense()
        x = np.random.randint(-100, 100, size=N) + 1j * np.random.randint(
            -100, 100, size=N
        )
        y = np.random.randint(-100, 100, size=M) + 1j * np.random.randint(
            -100, 100, size=M
        )
        csr = CSRMatrix(A)
        # These should be numerically exact... but apprently not on debian test server
        assert (
            np.max(
                abs(
                    csr.zcsrgecmv(x, y)
                    - np.atleast_2d(y).conjugate() @ (A @ np.atleast_2d(x).T)
                )
            )
            < 1e-6
        )
