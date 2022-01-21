#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


__all__ = ["CoaxProbe"]

import numpy as np

from .constants import Z0, pi


class CoaxProbe:
    def __init__(
        self, rin=0.994e-3 / 2, rout=5.909e-3 / 2, epsilon=2.25 * (1 - 0.001j)
    ):
        self.rin = rin
        self.rout = rout
        self.epsilon = epsilon
        self.geom_factor = np.log(self.rout / self.rin) / (2 * pi)
        self.impedance = Z0 * self.geom_factor / self.epsilon ** 0.5
