#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


"""
Calculation of integrand for a multilayer :cite:p:`Bakhtiari1994`.

"""
# See: Bakhtiari, S., Ganchev, S. I. & Zoughi, R. Analysis of radiation
# from an open-ended coaxial line into stratified dielectrics.
# IEEE Transactions on Microwave Theory and Techniques 42, 1261–1267 (1994)

__all__ = ["Layer", "Stack", "Setup"]

import jax.numpy as jnp

from coaxtract.constants import *
from coaxtract.integ import path_integral
from coaxtract.special import *


class Layer:
    def __init__(self, epsilon, thickness=None, name="layer"):
        self.epsilon = epsilon
        self.thickness = thickness
        self.name = name


class Stack:
    def __init__(self, layers, termination="PEC"):
        if termination not in ["PEC", "infinite"]:
            raise ValueError("termination must be PEC or infinite")
        self.layers = layers
        self.N = len(self.layers)
        self.termination = termination
        self.thicknesses = [l.thickness for l in self.layers]
        self.epsilons = [l.epsilon for l in self.layers]
        if termination == "infinite":
            if self.thicknesses[-1] is not None:
                raise ValueError(
                    "last layer must have None thickness for PEC termination"
                )

    def thickness(self, n):
        thicknesses = [l.thickness for l in self.layers]
        # if self.termination == "infinite":
        #     return sum(self.thicknesses[:n-1])
        # else:
        return sum(self.thicknesses[: (n + 1)])

    def rhoN(self, s, k0):
        if self.termination == "infinite":
            return 0  # jnp.zeros_like(k0)
        else:
            zn = self.thickness(self.N)
            epsN = self.epsilons[-1]
            return jnp.exp(-2 * 1j * k0 * zn * jnp.sqrt(epsN - s ** 2))

    # def beta(self, s, k0, z, rho, eps):
    #     ph = jnp.exp(2 * 1j * k0 * z * jnp.sqrt(eps - s ** 2))
    #     return (1 - rho * ph) / (1 + rho * ph)
    #

    def beta(self, s, k0, z, rho, eps):
        ph = jnp.exp(-2 * 1j * k0 * z * jnp.sqrt(eps - s ** 2))
        return (ph - rho) / (ph + rho + 1e-15)

    def kappa(self, s, eps1, eps2):
        return eps1 / eps2 * jnp.sqrt(eps2 - s ** 2) / jnp.sqrt(eps1 - s ** 2)

    def rho(self, s, k0, z, kappa, beta, eps):
        return (
            (1 - kappa * beta)
            / (1 + kappa * beta)
            * jnp.exp(-2 * 1j * k0 * z * jnp.sqrt(eps - s ** 2))
        )

    def recurrence(self, s, k0):
        n = self.N - 1
        rhos = []
        for i in range(self.N):
            if i == 0:
                rho = self.rhoN(s, k0)
            else:
                z = self.thickness(n)
                beta = self.beta(s, k0, z, rhos[i - 1], self.epsilons[n + 1])
                kappa = self.kappa(s, self.epsilons[n], self.epsilons[n + 1])
                rho = self.rho(s, k0, z, kappa, beta, self.epsilons[n])
            rhos.append(rho)
            n -= 1
        return rhos

    def rho1(self, s, k0):
        return self.recurrence(s, k0)[-1]

    def F(self, s, k0):
        eps = self.epsilons[0]
        rho1 = self.rho1(s, k0)
        result = 1 / jnp.sqrt(eps - s ** 2) * (1 + rho1) / (1 - rho1)
        return result  # jnp.where(jnp.isfinite(result), result, 0)


class Setup:
    def __init__(
        self,
        stack,
        probe,
        bessel="jax",
    ):
        self.stack = stack
        self.probe = probe
        self.bessel = bessel
        if bessel not in ["scipy", "jax"]:
            raise ValueError('bessel must be one of ["scipy", "jax"]')

        def j0app(z):
            return j0_approx(z, N=100)

        self.j0 = j0_scipy if bessel == "scipy" else j0

    def integrand(self, s, k0):
        zout = k0 * s * self.probe.rout
        zin = k0 * s * self.probe.rin
        jout = self.j0(zout)
        jin = self.j0(zin)
        F = self.stack.F(s, k0)
        out = (jout - jin) ** 2 * F / s
        small = F * s * (k0 * (self.probe.rout - self.probe.rin) / 4.0) ** 2
        return jnp.where(s <= 1.0e-5, small, out)

        # return jnp.where(s == 0, 0, out)

    def admittance(
        self,
        freq,
        path="complex",
        alpha=0.5,
        int_method="trapz",
        n_int=700,
        divmax=10,
        iopt=0,
    ):

        if int_method not in ["trapz", "romberg", "romberg_jax"]:
            raise ValueError(
                'bessel must be one of ["trapz", "romberg", "romberg_jax"]'
            )
        k0 = 2 * pi * freq / c
        # eps = jnp.array([jnp.max(jnp.array(self.stack.epsilons).real)])*jnp.ones_like(freq)
        eps = self.stack.epsilons[iopt]

        def _integrand(s):
            return self.integrand(s, k0)

        I = path_integral(
            _integrand,
            eps,
            path,
            alpha,
            int_method,
            n_int,
            divmax,
        )

        y = (
            I
            * eps
            / (self.probe.epsilon ** 0.5 * jnp.log(self.probe.rout / self.probe.rin))
        )
        return y

    def reflection(self, *args, **kwargs):
        y = self.admittance(*args, **kwargs)
        return (1 - y) / (1 + y)


if __name__ == "__main__":

    # Probe
    # Teflon with complex dielectric constant εrc = 2.08 · (1 − 0.0006j).
    # Dimensions for the coax are chosen as a = 0.52 mm and b = 1.2 mm
    from coaxtract import CoaxProbe

    probe = CoaxProbe(epsilon=2.08 * (1 - 0.0006j), rin=0.52e-3, rout=1.2e-3)

    # MUT in Fig. 1 is assumed to have
    # a dielectric constant of εr1 = 2.08 with a thickness of 2.0 mm.

    def myfunc(epsilon):

        layer = Layer(epsilon=epsilon, thickness=2e-3)
        stack = Stack([layer], termination="PEC")
        setup = Setup(stack, probe)
        nconv = 0
        acc = 1e-4
        err = jnp.inf
        n_int = 100

        divmax = 1
        while err > acc:
            y = setup.admittance(
                10e9,
                path="complex",
                alpha=0.5,
                int_method="trapz",
                n_int=n_int,
                divmax=divmax,
            )
            # print(y)
            if nconv > 0:
                err = abs(y - yold)
            nconv += 1
            yold = y
            # print(err)
            n_int *= 2
            divmax += 1

        print(y)
        print(err)
        return y

    from jax import jit

    # fast = jit(myfunc)

    epsr1 = 2.08
    for j in range(-7, 2):
        tand = 10 ** (j)
        epsilon = epsr1 * (1 - 1j * tand)
        myfunc(epsilon)

    # layer = Layer(epsilon=11 - 0.1j, thickness=13e-3)
    # layers = [layer]
    # stack = Stack(layers, termination="PEC")
    # probe = CoaxProbe()
    # setup = Setup(stack, probe)
    # r = setup.reflection(freq=10e9)

    # # from top to bottom
    #
    # air = Layer(epsilon=1 - 0.01j, thickness=1e-2)
    # film = Layer(epsilon=11 - 0.01j, thickness=0.01)
    # substrate = Layer(epsilon=3 - 0.01j, thickness=0.4)
    #
    # # layers = [air, film, substrate]
    #
    # layers = [substrate]
    #
    # stack = Stack(layers, termination="PEC")
    #
    # # # print(stack.tickness(0))
    # #
    # # # rhos = stack.recurrence(1, 1)
    # # # print()
    # # #
    # # s = jnp.linspace(0, 1, 10)
    # # k0 = jnp.linspace(1, 3, 15)
    #
    # s = 0.5
    # k0 = 2
    #
    # from coaxtract import Calibration, CoaxProbe
    #
    # probe = CoaxProbe()
    # cal = Calibration(
    #     probe, epsilon_load=substrate.epsilon, thickness_load=substrate.thickness
    # )
    #
    # #
    # print(">>> one layer")
    # print(stack.F(s, k0))
    # print(cal._integrand_function_load(s, k0))
    #
    # def _integrand_function_tw0_layers(
    #     s, k0, epsilon, thickness, epsilon_substrate, thickness_substrate
    # ):
    #     eps1, eps2 = epsilon, epsilon_substrate
    #     d1, d2 = thickness, thickness_substrate
    #     q1 = jnp.sqrt(eps1 - s ** 2)
    #     q2 = jnp.sqrt(eps2 - s ** 2)
    #     kappa1 = (eps2 * q1) / (eps1 * q2)
    #     t1 = jnp.tan(k0 * d1 * q1)
    #     t2 = jnp.tan(k0 * d2 * q2)
    #     f = (t1 * t2 - kappa1) / (kappa1 * t1 + t2)
    #     return 1j * f / q1
    #
    # air = Layer(epsilon=1 - 0.0j, thickness=1e-62)
    # film = Layer(epsilon=11 - 0.0j, thickness=0.01)
    # substrate = Layer(epsilon=3 - 0.0j, thickness=0.4)
    #
    # layers = [air, substrate]
    #
    # stack = Stack(layers, termination="PEC")
    #
    # i2 = _integrand_function_tw0_layers(
    #     s, k0, air.epsilon, air.thickness, substrate.epsilon, substrate.thickness
    # )
    #
    # print(">>> two layers")
    # print(stack.F(s, k0))
    # print(i2)
    #
    # layer = Layer(epsilon=11 - 0.1j, thickness=13e-3)
    # layers = [layer]
    # stack = Stack(layers, termination="PEC")
    # probe = CoaxProbe()
    # setup = Setup(stack, probe)
    # r = setup.reflection(freq=10e9)
    # print(r)
    # print(jnp.abs(r))
    #
    # film = Layer(epsilon=100 - 0.1j, thickness=10e-6)
    # sublayer = Layer(epsilon=11 - 0.01j, thickness=1e-3)
    # substrate = Layer(epsilon=11 - 0.1j, thickness=0.5e-3)
    # layers = [film, sublayer, substrate]
    # stack = Stack(layers, termination="PEC")
    # probe = CoaxProbe(rin=0.5e-3, rout=3e-3, epsilon=2.1 * (1 - 0.0004j))
    # probe = CoaxProbe()
    # setup = Setup(stack, probe)
    # r = setup.reflection(freq=10e9)
    # print(r)
    # print(jnp.abs(r))
    #
    # cal = Calibration(
    #     probe,
    #     int_method="jax",
    #     epsilon_load=substrate.epsilon,
    #     thickness_load=substrate.thickness,
    # )
    #
    # r = cal.reflection(10e9, "open")
    # print(r)
    #
    # layer = Layer(epsilon=cal.epsilon_open, thickness=None)
    # layers = [layer]
    # stack = Stack(layers, termination="infinite")
    # probe = CoaxProbe()
    # setup = Setup(stack, probe)
    # r = setup.reflection(freq=10e9)
    # print(r)
    #
    # cal = Calibration(
    #     probe,
    #     int_method="trapz",
    #     epsilon_load=substrate.epsilon,
    #     thickness_load=substrate.thickness,
    #     air_gap=0,
    # )
    #
    # r = cal.reflection(10e9, "short")
    # print(r)
