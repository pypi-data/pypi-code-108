#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


__all__ = ["Calibration"]

import warnings

import jax.numpy as jnp

from .constants import *
from .special import *
from .stack import *

# def j0(z):
#     return j0_approx(z, N=100)


# warnings.filterwarnings("ignore")


class Calibration:
    def __init__(
        self,
        probe,
        epsilon_load=4 * (1 - 0.01j),
        thickness_load=1.3e-3,
        epsilon_open=1 - 0j,
        air_gap=0,
        bessel="jax",
    ):

        self.cases = ["open", "short", "load"]
        self.epsilon_load = epsilon_load
        self.thickness_load = thickness_load

        self.air_gap = air_gap
        self.epsilon_open = epsilon_open
        load_layer = Layer(epsilon_load, thickness_load)
        if self.air_gap == 0:
            load = Stack([load_layer], termination="PEC")
        else:
            air_layer = Layer(epsilon_open, air_gap)
            load = Stack([air_layer, load_layer], termination="PEC")
        self.load_setup = Setup(
            load,
            probe,
            bessel=bessel,
        )

        short_layer = Layer(epsilon_open, air_gap)
        short = Stack([short_layer], termination="PEC")
        self.short_setup = Setup(
            short,
            probe,
            bessel=bessel,
        )

        open_layer = Layer(epsilon=epsilon_open, thickness=None)
        open = Stack([open_layer], termination="infinite")
        self.open_setup = Setup(
            open,
            probe,
            bessel=bessel,
        )

        self.probe = probe
        self.bessel = bessel

        # self.S11 = dict(theory=None, measured=None)

    def reflection(self, freqs, case, **kwargs):
        if case not in self.cases:
            raise ValueError(f"case must be in {self.cases}")

        if case == "short":
            if self.air_gap == 0:
                return -jnp.ones_like(freqs)
            else:
                return self.short_setup.reflection(freqs, **kwargs)

        elif case == "load":
            iopt = 0 if self.air_gap == 0 else 1
            kwargs["iopt"] = iopt
            return self.load_setup.reflection(freqs, **kwargs)
        else:
            return self.open_setup.reflection(freqs, **kwargs)

    def get_theoretical_reflection(self, freqs, **kwargs):
        R = {}
        for case in self.cases:
            R[case] = self.reflection(freqs, case, **kwargs)
        return R

    def run(self, freqs, Rmeasured, **kwargs):
        nfreq = len(freqs)
        Id = jnp.eye(nfreq)
        R = self.get_theoretical_reflection(freqs, **kwargs)
        b = [
            [jnp.diag(R[case]), Id, -jnp.diag(R[case] * Rmeasured[case])]
            for case in self.cases
        ]
        B = jnp.block(b)
        v = jnp.hstack(list(Rmeasured.values()))
        sol = jnp.linalg.inv(B) @ v
        a, b, c = sol[:nfreq], sol[nfreq : 2 * nfreq], sol[-nfreq:]
        self.coefficients = dict(a=a, b=b, c=c)
        return self.coefficients

    def apply(self, Rmeas, freqspan=None):
        if freqspan is None:
            freqspan = range(len(Rmeas))
        return (Rmeas - self.coefficients["b"][freqspan]) / (
            -self.coefficients["c"][freqspan] * Rmeas + self.coefficients["a"][freqspan]
        )
