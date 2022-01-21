#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT

__all__ = ["Extractor"]

import jax.numpy as jnp
import nlopt
import numpy as np
from jax import grad, jit
from jax.config import config
from scipy.optimize import minimize

from coaxtract.constants import *
from coaxtract.stack import Stack


def mse(a, b):
    return jnp.mean(jnp.abs(a - b) ** 2)


def eps2opt(eps):
    return np.hstack([eps.real, eps.imag])


class Extractor:
    def __init__(
        self,
        setup,
        frequencies,
        Rmeas,
        scale=True,
        guess="random",
        options=None,
        eps_min=-1e9 * (1 + 1j),
        eps_max=1e9 * (1 + 1j),
        single_layer=False,
        compile=False,
        verbose=False,
        n_int=700,
        alpha=0.5,
        model="constant",
        bounds=None,
        constraints=False,
        backend="scipy",
    ):
        self.setup = setup
        self.constraints = constraints
        self.bounds = bounds
        self.backend = backend
        if backend not in ["scipy", "nlopt"]:
            raise ValueError("backend must be scipy or nlopt")
        if model not in ["constant", "wideband", "cole-cole"]:
            raise ValueError("model must be wideband, constant or cole-cole")
        self.film = None
        for i, lay in enumerate(setup.stack.layers):
            if lay.name == "unknown":
                self.film = lay
                self.film_index = i
        if self.film is None:
            raise ValueError("layer named unknown must be contained in the setup stack")

        self.frequencies = frequencies
        self.Rmeas = Rmeas
        self.probe = setup.probe
        self.guess = guess
        self.nfreq = len(Rmeas)

        self.model = model
        if self.model == "constant":
            self.nvar = 2
        elif self.model == "wideband":
            self.nvar = 2 * self.nfreq
        else:
            self.nvar = 4
        self.verbose = verbose
        self.scale = scale
        self.single_layer = single_layer
        self.compile = compile
        self.alpha = alpha

        self.n_int = n_int
        default_options = {
            "disp": int(self.verbose),
            "maxcor": 250,
            "ftol": 1e-16,
            "gtol": 1e-16,
            "eps": 1e-12,
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

    def thin_film_approx(self):
        Zc = self.probe.impedance
        Zmeas = Zc * (1 + self.Rmeas) / (1 - self.Rmeas)
        out = 1 / (
            1j * 2 * pi * self.frequencies * self.film.thickness * Zmeas * epsilon_0
        )
        # out[np.isnan(out)] = 0
        return out

    def opt2eps(self, x):
        if self.model == "cole-cole":
            omega = 2 * pi * self.frequencies * 1e-9
            return cole_cole(omega, *x) - 1e-6
        else:
            eps_re, eps_im = x[: int(self.nvar / 2)], x[int(self.nvar / 2) :]
            return eps_re + 1j * eps_im

    def reflection(self, eps_film):
        self.setup.stack.layers[self.film_index].epsilon = eps_film
        stack = self.setup.stack
        layers = stack.layers
        layers[self.film_index].epsilon = eps_film
        self.setup.stack = Stack(layers, stack.termination)
        r = self.setup.reflection(
            self.frequencies, n_int=self.n_int, alpha=self.alpha, iopt=self.film_index
        )
        return jnp.array(r)

    def fun(self, x):
        eps_film = self.opt2eps(x) * jnp.ones(self.nfreq)
        R_ana = self.reflection(eps_film)
        obj = mse(self.Rmeas, R_ana)
        if self.scale:
            obj /= self.film.thickness
        return obj

    def init_bounds(self):
        if self.bounds is not None:
            return np.array(self.bounds)
        else:
            if self.model == "cole-cole":
                bounds = [(self.eps_min.real, self.eps_max.real)]
                bounds += [(self.eps_min.real, self.eps_max.real)]
                bounds += [(-1e6, -1e-16)]
                bounds += [(0, 1)]
            else:
                bounds = [
                    (self.eps_min.real, self.eps_max.real)
                    for i in range(int(self.nvar / 2))
                ]
                bounds += [
                    (self.eps_min.imag, self.eps_max.imag)
                    for i in range(int(self.nvar / 2))
                ]
            return np.array(bounds)

    def init_guess(self):
        re = np.array(self.thin_film_approx().real)
        im = np.array(self.thin_film_approx().imag)
        eps_approx = re.astype(float) + 1j * im.astype(float)

        if self.guess == "random":
            eps_random = self.eps_min + (self.eps_max - self.eps_min) * np.random.rand(
                self.nvar
            )
            return eps_random
        elif self.guess == "approx":
            return eps2opt((eps_approx))
        elif self.guess == "approx mean":
            guess = eps2opt((np.mean(eps_approx) * np.ones(self.nfreq)))
            return guess
        elif self.guess == "approx low freq":
            guess = eps2opt((eps_approx[0] * np.ones(self.nfreq)))
            return guess
        elif not isinstance(self.guess, str):
            if np.isscalar(self.guess):
                guess = self.guess
                if self.model == "constant":
                    return eps2opt(guess)
                else:
                    initial_guess = np.complex64(guess * np.ones(self.nfreq))
                    return eps2opt(initial_guess)
            elif len(self.guess) == self.nfreq:
                guess = self.guess
                return eps2opt(np.complex64(guess))
            elif self.model == "cole-cole":
                return self.guess
            else:
                raise ValueError("Wrong initial guess")

    def run(self):
        bounds = self.init_bounds()
        initial_guess = self.init_guess()
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
                y = np.float64(y)
                # y = np.array(y.astype(float))
                if gradn.size > 0:
                    dy = np.float64(self.jacobian(x))
                    # dy = dy.astype(float)
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

            if self.model == "cole-cole" and self.constraints:

                def _fc(x, i):
                    eps = self.opt2eps(x)
                    c1 = -eps.real + self.eps_min.real
                    c2 = eps.imag - self.eps_max.imag
                    return jnp.hstack([c1, c2])[i]

                _grad_fc = jit(grad(_fc))

                def fc(result, x, gradn):
                    if gradn.size > 0:
                        gradn[:] = [_grad_fc(x, i) for i in range(2 * self.nfreq)]

                    result[:] = [_fc(x, i) for i in range(2 * self.nfreq)]
                    return result

                tols = np.ones(2 * self.nfreq) * 1e-6
                opt.add_inequality_mconstraint(fc, tols)

            xopt = opt.optimize(initial_guess)
            fopt = opt.last_optimum_value()
            opt.x = xopt
            opt.fun = fopt

        eps_opt = self.opt2eps(opt.x) * jnp.ones(self.nfreq)
        self.eps_opt = eps_opt
        self.opt = opt
        return opt

    def jacobian(self, x):
        out = np.array(self.grad_fun_jit(x))
        out = out.astype(float)
        return out


#### permittivity models


def cole_cole(omega, eps_inf, eps_static, tau, alpha):
    return eps_inf + (eps_static - eps_inf) / (1 + (1j * omega * tau) ** (1 - alpha))


if __name__ == "__main__":

    import coaxtract as cx

    probe = cx.CoaxProbe()
    freqs = np.linspace(1, 2, 10) * 1e9
    Rmeas_cal = np.ones_like(freqs)
    t_film = 0.5e-3
    layopt = cx.Layer(1, t_film, name="unknown")
    opt = cx.Stack([layopt])
    exp = cx.Setup(opt, probe)

    for l in exp.stack.layers:
        if l.name == "opt":
            film = l

    self = cx.Extractor(
        exp,
        freqs,
        Rmeas_cal,
    )
