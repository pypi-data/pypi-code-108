#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of cpwxtract
# License: GPLv3
# See the documentation at benvial.gitlab.io/cpwxtract


__all__ = ["load", "get_Smeas"]

from numpy import interp, loadtxt

from .helpers import meas2complex


def load(filename):

    S = dict(
        S11=dict(A=None, phi=None),
        S21=dict(A=None, phi=None),
        S12=dict(A=None, phi=None),
        S22=dict(A=None, phi=None),
    )
    (
        f,
        S["S11"]["A"],
        S["S11"]["phi"],
        S["S21"]["A"],
        S["S21"]["phi"],
        S["S12"]["A"],
        S["S12"]["phi"],
        S["S22"]["A"],
        S["S22"]["phi"],
    ) = loadtxt(filename, skiprows=9).T

    f *= 1e-9
    return f, S


def _prepSmeas(S, frequencies, f):
    s = meas2complex(S["A"], S["phi"])
    return interp(frequencies, f, s)


def get_Smeas(filename, frequencies):
    f, S = load(filename)
    Smeas = dict()
    Smeas["S11"] = _prepSmeas(S["S11"], frequencies, f)
    Smeas["S21"] = _prepSmeas(S["S21"], frequencies, f)
    Smeas["S12"] = _prepSmeas(S["S12"], frequencies, f)
    Smeas["S22"] = _prepSmeas(S["S22"], frequencies, f)
    return Smeas
