#!/usr/bin/env python3


import numpy as np

eps = pow(10, -14)


def _f(Q, mu, x0):
    # Q_std and x0_std
    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            if abs(mu + 1 / Q.eig[i]) < eps:
                return -np.sign(mu) * np.inf
            else:
                _sum += Q.eig[i] * pow(x0[i]/(1+mu*Q.eig[i]), 2)

    return _sum - 1  # self.c_std = - 1 !


def _d_f(Q, mu, x0):

    # Q_std and x0_std
    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            _sum += -2 * (Q.eig[i] * x0[i])**2 / (1+mu*Q.eig[i])**3
    return _sum


def _d2_f(Q, mu, x0):
    # Q_std and x0_std
    _sum = 0
    for i in range(Q.dim):
        if abs(x0[i]) > eps:
            _sum += 6 * (Q.eig[i]**3 * x0[i]**2) / (1+mu*Q.eig[i])**4
    return _sum


def _get_e1(Q, x0):
    for i, x in enumerate(x0):
        if abs(x) > eps and Q.eig[i] > eps:
            return -1/Q.eig[i]
    return -np.inf


def _get_e2(Q, x0):
    for i, _ in enumerate(x0):
        if abs(x0[-i]) > eps and Q.eig[-i] < 0:
            return -1/Q.eig[-i]
    return np.inf


class Fun():
    def __init__(self, Q, x0):
        E = np.ones(Q.dim)
        self.inv_I_lA = lambda l: np.dot(np.dot(Q.V, np.diag(1/(E+l*Q.eig))), Q.V.T)
        self.inv_I_lA = lambda mu: np.diag(1/(E+mu*Q.eig))
        self.x_std = lambda mu: self.inv_I_lA(mu) @ x0
        self.x_not_std = lambda mu: Q.to_non_standardized(self.x_std(mu))

        self.f = lambda mu: _f(Q, mu, x0)
        self.d_f = lambda mu: _d_f(Q, mu, x0)
        self.d2_f = lambda mu: _d2_f(Q, mu, x0)

        self.e1 = _get_e1(Q, x0)
        self.e2 = _get_e2(Q, x0)
        self.interval = self.e1, self.e2
        x0_not_std = Q.to_non_standardized(x0)

        self.dist = lambda _x: np.linalg.norm(_x - x0_not_std)
