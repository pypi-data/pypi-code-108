#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


__all__ = ["CPW"]

from .constants import *
import jax.numpy as np
from .helpers import kokp



class CPW:
    def __init__(self, L, w, s, h, thickness=None, epsilon=1, grounded=False):
        self.L = L * 1e-3
        self.w = w * 1e-3
        self.h = h * 1e-3
        self.s = s * 1e-3
        self.thickness = thickness if thickness is None else thickness * 1e-3
        self.epsilon = epsilon
        self.grounded = grounded

        if grounded and thickness is None:
            raise ValueError("thinkness must be finite when grounded is True")
        self.k1 = w / (w + 2 * s)
        self.k2 = (
            0
            if self.thickness is None
            else np.sinh(pi * self.w / (4 * self.thickness))
            / np.sinh(pi * (self.w + 2 * self.s) / (4 * self.thickness))
        )
        self.k3 = (
            0
            if self.thickness is None
            else np.tanh(pi * self.w / (4 * self.thickness))
            / np.tanh(pi * (self.w + 2 * self.s) / (4 * self.thickness))
        )

    @property
    def effective_epsilon(self):
        if self.thickness is None:
            return (self.epsilon + 1) / 2
        else:
            if self.grounded:
                q = kokp(self.k3) / (kokp(self.k1) + kokp(self.k3))
                return 1 + q * (self.epsilon - 1)
            else:
                return 1 + (self.epsilon - 1) / 2 * kokp(self.k2) / kokp(self.k1)

    @property
    def impedance(self):
        if self.grounded:
            return (
                60
                * pi
                / (self.effective_epsilon) ** 0.5
                / (kokp(self.k1) + kokp(self.k3))
            )
        else:
            return 30 * pi / (self.effective_epsilon) ** 0.5 / kokp(self.k1)



    def get_S(self,frequency):
        omega = frequency * 2 * pi * 1e9
        k0 = omega / c
        Z0 = 50
        # Zc = 3
        Zc = self.impedance
        # Zc = Z0 * np.real(1 + S11_target) / (1 - S11_target)
        gamma = 1j * (self.effective_epsilon) ** 0.5 * k0
        sh = np.sinh(gamma * self.L)
        ch = np.cosh(gamma * self.L)
        denom = 2 * Zc * Z0 * ch + (Zc ** 2 + Z0 ** 2) * sh
        S11 = (Zc ** 2 - Z0 ** 2) * sh / denom
        S12 = 2 * Zc * Z0 / denom
        S21 = S12
        S22 = S11
        return dict(S11=S11, S12=S12, S21=S21, S22=S22)
