from itertools import combinations

import numpy as np


def integral(m, n, h, f):
    if (n - m) % 2 == 0:
        S = (f[m] - f[n]) * h / 3
        for i in range(1, int((n - m) / 2) + 1):
            S += (4 * f[m + 2 * i - 1] + 2 * f[m + 2 * i]) * h / 3
    else:
        S = (f[m] - f[n - 1]) * h / 3
        for i in range(1, int((n - 1 - m) / 2) + 1):
            S += (4 * f[m + 2 * i - 1] + 2 * f[m + 2 * i]) * h / 3
        S += (f[n - 1] + f[n]) * h / 2
    return S


def mldivide(A, B):
    num_vars = A.shape[1]
    rank = np.linalg.matrix_rank(A)
    if rank == num_vars:
        return np.linalg.lstsq(A, B, rcond=None)[0]  # not under-determined
    else:
        for nz in combinations(range(num_vars), rank):  # the variables not set to zero
            try:
                sol = np.zeros((num_vars, 1))
                sol[nz, :] = np.asarray(np.linalg.solve(A[:, nz], B))
                return sol
            except np.linalg.LinAlgError:
                raise ValueError("picked bad variables, can't solve")