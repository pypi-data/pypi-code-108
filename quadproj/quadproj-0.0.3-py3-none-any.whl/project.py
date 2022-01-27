#!/usr/bin/env python3

import numpy as np
import fun


class NoFeasibleDirection(Exception):
    pass


eps = pow(10, -10)




def get_poles(Q_std, x0_std):
    poles = []
    for i, lambd in enumerate(Q_std.eig):
        if np.abs(x0_std[i]) > eps:
            poles.append(-1/lambd)
    return poles


def plot_f(Q_std, x0_std):
    assert Q_std.is_standardized, 'please standardize the quadric'
    Q = Q_std
    x0 = x0_std

    
    poles = _get_poles(Q, x0)



def project(Q, x0_not_std, flag_get_all_KKT=False):
    """project -- project a point to a quadric"""

    class ProjectOutput():
        def __init__(self):
            self.min = None
            self.max = None
            self.xd = []
            self.x_roots = []

    x0 = Q.to_standardized(x0_not_std)

    mu_star, x_star = get_KKT_point_root(Q, x0_not_std, flag_get_all_KKT)
    F = fun.Fun(Q, x0)
    Xd = [x_star]
    for k, eig_bar_k in enumerate(Q.eig_bar):
        L_k = [i for i in range(Q.dim) if Q.eig[i] == eig_bar_k]
        K_k = [i for i in L_k if x0[i] == 0]
        squared_radius_k = get_squared_radius_k(Q, x0, L_k, eig_bar_k)
        if len(L_k) == len(K_k) and squared_radius_k > 0:
            xd_k = get_xd_k(Q, x0, K_k, eig_bar_k)
            xd_k_not_std = Q.to_non_standardized(xd_k)
            assert Q.is_feasible(xd_k_not_std)
            Xd.append(xd_k_not_std)
    x_project_not_std = min(Xd, key=(F.dist))
    assert Q.is_feasible(x_project_not_std)
    return x_project_not_std


def get_KKT_point_root(Q, x0_not_std, flag_get_all_KKT=False):
    x0 = Q.to_standardized(x0_not_std)
    F = fun.Fun(Q, x0)
    if F.e1 != -np.inf:
        if F.e2 == np.inf:
            mu_1 = bisection(F, 'right')
            output_newton = my_newton(F, mu_1x_star
        else:
            output_newton = double_newton(F)
        mu_star = output_newton.root


        x_star_not_std = F.x_not_std(mu_star)
        return mu_star, x_star_not_std


def get_squared_radius_k(Q, x0, L_k, eig_bar_k):
    _sum = [Q.eig[j] * (x0[j]/(1-Q.eig[j]/eig_bar_k))**2
            for j in range(Q.dim) if j not in L_k]
    radius_k = 1/eig_bar_k * (1 - sum(_sum))
    return radius_k


def get_xd_k(Q, x0, K_k, eig_bar_k):
    xd_k = np.zeros_like(x0)
    k_prime = K_k[0]
    for i, x0_i in enumerate(x0):
        if i not in K_k:
            xd_k[i] = x0_i / (1 - Q.eig[i]/eig_bar_k)
        elif i == k_prime:
            squared_radius_k = get_squared_radius_k(Q, x0, K_k, eig_bar_k)
            xd_k[i] = np.sqrt(squared_radius_k)
        # else : 0 already preallocated

    return xd_k


def bisection(F, direction='right'):
    k = 1
    if direction == 'right':
        mu = F.e1 + 1
        while F.f(mu) < 0:
            mu = F.e1 + pow(10, -k)
            k += 1
    else:
        mu = F.e2 - 1
        while F.f(mu) > 0:
            mu = F.e2 - pow(10, -k)
            k += 1

    return mu


def my_newton(F, mu_0):
    class Output:
        def __init__(self):
            self.converged = False
            self.message = ''
            self.iteration = 0
            self.root = None
            self.fx = None
            self.dfx = None
            self.rtol = float('inf')
            self.xtol = float('inf')

        def __str__(self):
            output_str = f"""
            converged: {self.converged} \n
            iterations: {self.iteration} \n
            root: {self.root} \n
            message: {self.message} \n
            fx: {self.fx} \n
            dfx: {self.dfx} \n"""
            return output_str

        def is_in_interval(self, interval):
            if interval[0] == interval[1]:
                return True

            if self.root is None or interval is None:
                return True
            else:
                return self.root >= interval[0] and self.root <= interval[1]

    output = Output()
    iteration_max = 100
    eps_rtol = pow(10, -10)
    eps_xtol = pow(10, -14)
    x = mu_0
    new_x = x
    while (output.iteration < iteration_max and output.rtol > eps_rtol and
           output.xtol > eps_xtol and output.is_in_interval(F.interval)):
        output.fx = F.f(x)
        output.dfx = F.d_f(x)
        new_x = x - output.fx/output.dfx
        output.xtol = abs(x-new_x)
        x = new_x
        output.root = new_x
        output.rtol = abs(output.fx)
        output.iteration += 1
    output.converged = False
    if output.iteration == iteration_max:
        output.message = "max number of iteration reached"
    elif output.rtol <= eps_rtol:
        output.message = "converged"
        output.converged = True
    elif output.xtol <= eps_xtol:
        output.message = "weak improvement, stopping the alg early.\
                You may want to check the value of the derivative around the root"
    elif not output.is_in_interval(F.interval):
        output.message = "Point is outside the interval of research"

    output.iteration += 1
    return output


def double_newton(F):

    # Check if Newton starting from 0 works...
    # print('**** Launching first netwon ****')
    output = my_newton(F, 0)
    # print('**** End first netwon ****')
    if output.converged:
        output.message += " starting from mu_s = 0"
        return output

    if F.f(0) < 0:
        # print('*** Bisection right')
        mu_s = bisection(F, 'right')
        assert F.f(mu_s) > 0, 'Check'
    elif F.f(0) > 0:
        # print('*** Bisection left')
        mu_s = bisection(F, 'left')
        assert F.f(mu_s) < 0, 'Check'
    else:
        raise ValueError('Should never happen')

    output = my_newton(F, mu_s)
    output.message += f" starting from mu_s = {mu_s}"
    return output
