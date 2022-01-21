#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


"""
From :cite:p:`Zhou2017`.
"""
# Zhou, L., Ju, Y., Wang, P. & Pei,  and Y.
# Fast and Stable Integration Method for the Aperture Admittance of an
# Open-Ended Coaxial Probe Terminated into Low-Loss Dielectrics.
# Progress In Electromagnetics Research M 55, 211–219 (2017)

from jax.config import config

# config.update("jax_debug_nans", True)
config.update("jax_debug_nans", False)

import jax.numpy as jnp
import numpy as np
import scipy.integrate as si
from jax import ops

from .constants import *


def path_integral(
    integrand,
    eps,
    path="complex",
    alpha=0.5,
    int_method="trapz",
    n_int=100,
    divmax=5,
):

    if int_method not in ["trapz", "romberg", "romberg_jax"]:
        raise ValueError('int_method must be one of "trapz", "romberg", "romberg_jax"')

    if path not in ["complex", "real"]:
        raise ValueError('path must be one of "complex", "real"')

    _A0 = (eps.real) ** 0.5
    if jnp.isscalar(_A0):
        n = 1
    else:
        n = len(_A0)

    def broadcast(t):
        if int_method == "trapz":
            A0 = jnp.broadcast_to(_A0, (len(t), n))
            t1 = jnp.broadcast_to(t, (n, len(t))).T
            return A0, t1
        else:
            return _A0, t

    def y1(t):

        A0, t = broadcast(t)
        return 2 * A0 * integrand(2 * A0 * t)

    def y2(t):
        A0, t = broadcast(t)
        if jnp.isscalar(t) and t == 0:
            return 0
        else:
            epstol = 1e-14
            result = jnp.where(
                t == 0.0,
                0.0,
                2 * A0 / (t + epstol) ** 2 * integrand(2 * A0 / (t + epstol)),
            )

            # return result
            # return jnp.where(
            #     t == 0.0, 0.0, 2 * s0 / (t + 1e-16) ** 2 * f(2 * s0 / (t + 1e-16))
            # )
            return jnp.where(jnp.isfinite(result), result, 0)

    ### integration along an elliptical path in the complex plane
    def elliptical_path(theta, alpha=alpha):
        A0, theta = broadcast(theta)
        return A0 + A0 * (jnp.cos(theta) + 1j * alpha * jnp.sin(theta))

    def yc(z, alpha=alpha):
        A0, t = broadcast(z)
        result = (
            pi
            * A0
            * (jnp.sin(t * pi) - 1j * alpha * jnp.cos(t * pi))
            * integrand(elliptical_path(pi * z))
        )
        return result  # jnp.where(jnp.isfinite(result), result, 0)

    def ytot(t, path=path):
        if path == "complex":
            return yc(t) + y2(t)
        else:
            return y1(t) + y2(t)

    # t0, t1 = 1e-9, 1.0
    t0, t1 = 0.0, 1.0
    if int_method == "romberg":
        return si.romberg(ytot, t0, t1, vec_func=False, show=False, divmax=divmax)
    elif int_method == "romberg_jax":
        if n == 1:
            return romberg(ytot, t0, t1, divmax=divmax)
        else:
            return romberg_vect(n, ytot, t0, t1, divmax=divmax)
    else:
        t = jnp.linspace(t0, t1, n_int)
        return jnp.trapz(ytot(t), t, axis=0)


def trapezcomp(f, a, b, n):
    """
    Composite trapezoidal function integration

    INPUTS:
    f:  the function to integrate
    a:  lower bound of integration
    b:  upper bound
    n:  number of panels to create between ``a`` and ``b``
    """

    # Initialization
    h = (b - a) / n
    x = a

    # Composite rule
    In = f(a)
    for k in range(1, n):
        x = x + h
        In += 2 * f(x)

    return (In + f(b)) * h * 0.5


def romberg(f, a, b, divmax=5, err=False):
    """
    Romberg integration

    INPUTS:
    f:  the function to integrate
    a:  lower bound of integration
    b:  upper bound
    jnp:  number of rows in the Romberg table
    """

    I = jnp.zeros((divmax, divmax), complex)
    error = 0
    for k in range(0, divmax):
        # Composite trapezoidal rule for 2^k panels
        I = ops.index_update(I, ops.index[k, 0], trapezcomp(f, a, b, 2 ** k))

        # Romberg recursive formula
        for j in range(0, k):
            q = (4 ** (j + 1) * I[k, j] - I[k - 1, j]) / (4 ** (j + 1) - 1)
            I = ops.index_update(I, ops.index[k, j + 1], q)
        error = jnp.abs(I[k, -1] - I[k - 1, -2])

    result = I[k, -1]
    if err:
        return result, error
    else:
        return result


def romberg_numpy(f, a, b, eps=1.48e-8, divmax=5):
    """
    Romberg integration

    INPUTS:
    f:  the function to integrate
    a:  lower bound of integration
    b:  upper bound
    jnp:  number of rows in the Romberg table
    """

    I = np.zeros((divmax, divmax), complex)
    error = 0
    for k in range(0, divmax):
        print("k=", k)
        # Composite trapezoidal rule for 2^k panels
        I[k, 0] = trapezcomp(f, a, b, 2 ** k)

        # Romberg recursive formula
        for j in range(0, k):
            q = (4 ** (j + 1) * I[k, j] - I[k - 1, j]) / (4 ** (j + 1) - 1)
            I[k, j + 1] = q
        error = np.abs(I[k, -1] - I[k - 1, -2])
    print(f"error {k} = ", error)
    return I[k, -1]


# import numpy as np
# from jax import lax

# def romberg(f, a, b, eps=1.48e-8, divmax=10):
#     """
#     Romberg integration
#
#     INPUTS:
#     f:  the function to integrate
#     a:  lower bound of integration
#     b:  upper bound
#     divmax:  number of rows in the Romberg table
#     """
#
#     def cond_fun(val):
#         I, k = val
#         error = jnp.where(k > 0, jnp.abs(I[k, -1] - I[k, -2]), jnp.inf)
#         return jnp.where(error > eps,True,False) #and k < divmax
#
#     def body_fun(val):
#         I, k = val
#         # Composite trapezoidal rule for 2^k panelss
#         divmax=1
#         xi = jnp.linspace(a, b, 2 ** divmax +1)
#
#
#
#         def trapezoid(xi,k):
#             h = xi[1]-xi[0]
#             fi = f(xi)
#             s = jnp.sum(fi[1:-1])
#             s = (h / 2) * (fi[0] + fi[-1]) + h * s
#             return s
#
#
#         I = ops.index_update(I, ops.index[k, 0], trapezoid(xi,k))
#         # Romberg recursive formula
#         for j in range(0, k):
#             q = (4 ** (j + 1) * I[k, j] - I[k - 1, j]) / (4 ** (j + 1) - 1)
#             I = ops.index_update(I, ops.index[k, j + 1], q)
#
#         k += 1
#         return I, k
#
#     I = jnp.zeros((divmax, divmax), complex)
#     k = 0
#     init_val =I,k
#     I,k = lax.while_loop(cond_fun, body_fun, init_val)
#
#     return I[k,-1]
#


# while error > eps and k < divmax:
#     # Composite trapezoidal rule for 2^k panels
#     I = ops.index_update(I, ops.index[k, 0], trapezoid(f, a, b, 2 ** k))
#     # Romberg recursive formula
#     for j in range(0, k):
#         q = (4 ** (j + 1) * I[k, j] - I[k - 1, j]) / (4 ** (j + 1) - 1)
#         I = ops.index_update(I, ops.index[k, j + 1], q)
#     if k > 0:
#         error = jnp.abs(I[k, j + 1] - I[k, j])
#     k += 1

# return I[k, j + 1]


def romberg_vect(N, f, *args, **kwargs):
    res = []
    for i in range(N):

        def f_(x):
            return f(x)[i]

        res.append(romberg(f_, *args, **kwargs))
    return jnp.array(res)


if __name__ == "__main__":

    from jax import grad, jit, vmap

    #
    # def f(x):
    #     # return 3 * x ** 2
    #     return jnp.sin(x ** 3)
    #
    # exact = 1
    # bounds = 0, 1
    # npts = 1001
    # Nvec = 3
    #
    # x = jnp.linspace(bounds[0], bounds[1], npts)
    # # param = jnp.linspace(1, 2, 3)
    # # xvec, paramvec = jnp.meshgrid(x, param)
    #
    # def fvec(x):
    #     return jnp.array([x ** 2 + i ** 2 for i in range(Nvec)])
    #
    # def myinteg():
    #     return romberg_vect(Nvec, fvec, *bounds)
    # # N = 10
    # # print(trapezoid(f, *bounds, N))
    # print(romberg(f, *bounds))
    # print(jnp.trapz(f(x), x))
    # print(exact)
    #
    # # num_rombergvect_jax = romberg_vect(Nvec, fvec, *bounds)
    # # print(num_rombergvect_jax)
    # print(myinteg())
    # myintegjit = jit(myinteg)
    # print(myintegjit())
    from coaxtract import CoaxProbe, Layer, Setup, Stack

    h = 430e-6

    def myfunc(eps):

        air = Layer(epsilon=1.0001 - 0.1j, thickness=100e-6)
        substrate = Layer(epsilon=eps - 0.0001j, thickness=h)

        layers = [air, substrate]
        stack = Stack(layers, termination="PEC")
        probe = CoaxProbe()
        setup = Setup(stack, probe)

        freqs = jnp.array([5e9])  # jnp.linspace(5,10,100)*1e9
        k0 = 2 * jnp.pi * freqs / c

        # Npts=10000
        # s=jnp.linspace(0,100,Npts)

        def I(s):
            q = setup.integrand(s, k0)
            return q

        # q = I(s)
        return jnp.sum(path_integral(I, eps, n_int=10)).real

    # import matplotlib.pyplot as plt
    # plt.ion()
    # plt.close("all")
    # plt.plot(s, jnp.abs(q))

    eps = jnp.array([11.2])

    print(myfunc(eps))
    print(grad(myfunc)(eps))

    # def f(s):
    #     return setup.integrand(s, k0)
    #
    # import matplotlib.pyplot as plt
    #
    # plt.ion()
    # plt.close("all")
    # a, b = 0, 110
    #
    # npts = 100000
    #
    # s = jnp.linspace(a, b, npts)
    #
    # fs = f(s)
    #
    # plt.plot(s, jnp.abs(fs))
    # eps = substrate.epsilon
    # s0 = (eps.real) ** 0.5
    # t = jnp.linspace(0, 1, npts)
    #
    # def y1(t):
    #     return 2 * s0 * f(2 * s0 * t)
    #
    # def y2(t):
    #     # return np.where(t==0.0,0.0,1./(t+1e-16))
    #     return jnp.where(
    #         t == 0.0, 0.0, 2 * s0 / (t + 1e-16) ** 2 * f(2 * s0 / (t + 1e-16))
    #     )
    #
    # plt.figure()
    # plt.plot(t, jnp.abs(y1(t)))
    # plt.plot(t, jnp.abs(y2(t)), "--")
    #
    # divmax = 1
    #
    # print("y1")
    # print("--------")
    # print(">>> trapz")
    # print(jnp.trapz(y1(t), t))
    # print(">>> romberg scipy")
    # print(si.romberg(y1, 0, 1, divmax=divmax, vec_func=True))
    # # print(">>> romberg jax")
    # # print(romberg(y1, 0, 1, eps=1e-12, divmax=divmax))
    # print(">>> romberg numpy")
    # print(romberg_numpy(y1, 0, 1, eps=1e-12, divmax=divmax))
    #
    # print("y2")
    # print("--------")
    # print(">>> trapz")
    # print(jnp.trapz(y2(t), t))
    # print(">>> romberg scipy")
    # print(si.romberg(y2, 0, 1, divmax=divmax, vec_func=True))
    # print(">>> romberg jax")
    # print(romberg(y2, 0, 1, eps=1e-12, divmax=divmax))
    #

    # def setup(epsilon):
    #     h = 1
    #     substrate = Layer(epsilon=epsilon, thickness=h)
    #     layers = [substrate]
    #     stack = Stack(layers, termination="PEC")
    #     probe = CoaxProbe()
    #     setup = Setup(stack, probe)
    #
    #     lamb = 0.5
    #     k0 = 2 * jnp.pi / lamb
    #
    #     def f(s):
    #         return setup.integrand(s, k0)
    #
    #     eps = substrate.epsilon
    #     s0 = (eps.real) ** 0.5
    #     t = jnp.linspace(0, 1, npts)
    #
    #     def y1(t):
    #         return 2 * s0 * f(2 * s0 * t)
    #
    #     def y2(t):
    #         return jnp.where(
    #             t == 0.0, 0.0, 2 * s0 / (t + 1e-6) ** 2 * f(2 * s0 / (t + 1e-6))
    #         )
    #
    #     return y2, t
    #     # return jnp.trapz(y2(t), t)
    #
    # #
    #
    # def fun_trapz(epsilon):
    #     y2, t = setup(epsilon)
    #     return jnp.trapz(y2(t), t)
    #
    # #
    #
    # def fun_romberg(epsilon, divmax=3):
    #     y2, t = setup(epsilon)
    #     return romberg(y2, 0, 1, divmax=divmax)
    #
    # #
    # # print(jnp.trapz(y2(t), t))
    # # for divmax in range(1,10):
    # #     print(romberg(y2, 0, 1, divmax=divmax))
    #
    # eps = 12 - 4j
    # I = fun_trapz(eps)
    # print(I)
    # I = fun_romberg(eps)
    # print(I)
    #
    # fun_trapz_jit = jit(fun_trapz)
    # fun_romberg_jit = jit(fun_romberg, static_argnums=(1,))
    # fun_trapz_jit(eps)
    # # fun_trapz_jit(5-7j)
    # fun_romberg_jit(eps)
    # # fun_romberg_jit(5-7j)

    #
    #
    #
    # from jax import jit
    # from functools import partial
    #
    # # @partial(jit, static_argnums=(3,))
    # def trapezoid(f, a, b, N):
    #     h = (b - a) / N
    #     xi = jnp.linspace(a, b, N + 1)
    #     fi = f(xi)
    #     s = jnp.sum(fi[1:-1])
    #     s = (h / 2) * (fi[0] + fi[N]) + h * s
    #     return s
    #
    #
    #
    # def romberg(f, a, b, eps=1.48e-8, divmax=10):
    #     """
    #     Romberg integration
    #
    #     INPUTS:
    #     f:  the function to integrate
    #     a:  lower bound of integration
    #     b:  upper bound
    #     divmax:  number of rows in the Romberg table
    #     """
    #
    #     I = jnp.zeros((divmax, divmax), complex)
    #     for k in range(0, divmax):
    #         # Composite trapezoidal rule for 2^k panels
    #         I = ops.index_update(I, ops.index[k, 0], trapezoid(f, a, b, 2 ** k))
    #         # Romberg recursive formula
    #         for j in range(0, k):
    #             q = (4 ** (j + 1) * I[k, j] - I[k - 1, j]) / (4 ** (j + 1) - 1)
    #             I = ops.index_update(I, ops.index[k, j + 1], q)
    #         if k > 0:
    #             error = jnp.abs(I[k, -1] - I[k, -2])
    #             converged = jnp.where(error < eps, True, False)
    #             if converged:
    #                 break
    #             # return I[k, j+1]
    #         # print(I[k,0:k+1])   # display intermediate results
    #
    #     return I[k, j + 1]
    #
    #
