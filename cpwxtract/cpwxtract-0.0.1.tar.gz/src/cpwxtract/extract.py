#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT

__all__ = ["Extractor"]

import jax.numpy as np
from jax import grad, jit
from jax.config import config
import numpy as npo
import nlopt
from .constants import *


def mse(a, b):
    return np.mean(np.abs(a - b) ** 2)


def eps2opt(eps):
    return npo.hstack([eps.real, eps.imag])


class Extractor:
    def __init__(
        self,
        frequencies,
        Smeas,
        guess,
        cpw,
        options=None,
        eps_min=-1e9 - 1e9 * 1j,
        eps_max=1e9 + 1e9 * 1j,
        compile=True,
        verbose=True,
        backend="nlopt",
        bounds=None,
    ):

        if backend not in ["scipy", "nlopt"]:
            raise ValueError("backend must be scipy or nlopt")
        self.bounds = bounds
        self.backend = backend
        self.cpw = cpw
        self.frequencies = frequencies
        self.Smeas = Smeas
        self.guess = guess
        self.nfreq = len(frequencies)
        self.nvar = 2 * self.nfreq
        self.verbose = verbose
        self.compile = compile
        default_options = {
            "disp": int(self.verbose),
            "maxcor": 250,
            "ftol": 1e-16,
            "gtol": 1e-16,
            "eps": 1e-16,
            # "eps": 1e-11,
            "maxfun": 15000,
            "maxiter": 1300,
            "iprint": 1,
            "maxls": 200,
            "finite_diff_rel_step": None,
        }

        self.options = options or default_options
        self.options["disp"] = int(self.verbose)

        self.eps_min = eps_min
        self.eps_max = eps_max

        if self.compile:
            self.fun_jit = jit(self.fun)
            self.grad_fun_jit = jit(grad(self.fun_jit))
        else:
            self.fun_jit = self.fun
            self.grad_fun_jit = grad(self.fun_jit)

    def opt2eps(self, x):
        eps_re, eps_im = x[: int(self.nvar / 2)], x[int(self.nvar / 2) :]
        return eps_re + 1j * eps_im

    def fun(self, x):
        epsilon = self.opt2eps(x) * np.ones(self.nfreq)
        self.cpw.epsilon = epsilon
        S = self.cpw.get_S(self.frequencies)
        obj = mse(self.Smeas["S11"], S["S11"])/mse(self.Smeas["S11"], 0)
        obj += mse(self.Smeas["S21"], S["S21"])/mse(self.Smeas["S21"], 0)
        obj += mse(self.Smeas["S12"], S["S12"])/mse(self.Smeas["S12"], 0)
        obj += mse(self.Smeas["S22"], S["S22"])/mse(self.Smeas["S22"], 0)
        # aa =  np.mean(np.abs(np.gradient(epsilon)/np.gradient(self.frequencies)))
        # print(npo.float64(aa))
        # obj += aa * 1e-4
        # obj += mse(self.Smeas["S12"], S["S12"])
        # obj += mse(self.Smeas["S22"], S["S22"])
        return obj

    def init_bounds(self):
        if self.bounds is not None:
            return npo.array(self.bounds)
        else:
            bounds = [
                (self.eps_min.real, self.eps_max.real)
                for i in range(int(self.nvar / 2))
            ]
            bounds += [
                (self.eps_min.imag, self.eps_max.imag)
                for i in range(int(self.nvar / 2))
            ]
            return npo.array(bounds)

    def init_guess(self):
        initial_guess = npo.complex64(self.guess * npo.ones(self.nfreq))
        return eps2opt(initial_guess)

    def run(self):
        bounds = self.init_bounds()
        initial_guess = self.init_guess()
        # print(initial_guess)
        # print(type(initial_guess))
        # print(bounds)
        # print(type(bounds))
        if self.backend == "scipy":
            opt = minimize(
                self.fun_jit,
                initial_guess,
                bounds=bounds,
                tol=1e-12,
                options=self.options,
                jac=self.jacobian,
                method="L-BFGS-B",
            )
        else:

            def fun_nlopt(x, gradn):
                y = self.fun_jit(x)
                y = npo.float64(y)
                if gradn.size > 0:
                    dy = npo.float64(self.jacobian(x))
                    gradn[:] = dy
                if self.verbose:
                    print(f">>> objective = {y}")
                    eps = self.opt2eps(x)
                    print(f"    mean permittivity = {np.mean(eps)}")
                    print(f"    std permittivity  = {np.std(eps)}")
                return y

            opt = nlopt.opt(nlopt.LD_MMA, self.nvar)
            bounds = self.init_bounds()
            opt.set_lower_bounds(bounds[:, 0])
            opt.set_upper_bounds(bounds[:, 1])
            opt.set_maxeval(self.options["maxiter"])
            opt.set_ftol_rel(self.options["ftol"])
            opt.set_xtol_rel(self.options["eps"])
            opt.set_min_objective(fun_nlopt)
            xopt = opt.optimize(initial_guess)
            fopt = opt.last_optimum_value()
            opt.x = xopt
            opt.fun = fopt

        eps_opt = self.opt2eps(opt.x) * np.ones(self.nfreq)
        self.eps_opt = eps_opt
        self.opt = opt
        
        self.cpw.epsilon = npo.array(eps_opt)
        
        return opt

    def jacobian(self, x):
        out = npo.array(self.grad_fun_jit(x))
        out = out.astype(float)
        return out
