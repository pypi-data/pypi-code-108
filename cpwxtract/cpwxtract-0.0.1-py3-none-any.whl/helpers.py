#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT



import jax.numpy as np
from .constants import *



deg2rad = pi / 180
rad2deg = 1 / deg2rad

def complementary(k):
    return (1 - k ** 2) ** 0.5


def kokp(k):
    kp = complementary(k)
    val0 = pi / np.log(2 * (1 + kp ** 0.5) / (1 - kp ** 0.5))
    val1 = np.log(2 * (1 + k ** 0.5) / (1 - k ** 0.5)) / pi
    return np.where(np.abs(k) < 1 / 2 ** 0.5, val0, val1)


def unwrap(phi):
    return np.unwrap(phi * deg2rad) * rad2deg


def meas2complex(A, phi):
    return 10 ** (A / 20) * np.exp(1j * phi * deg2rad)


def complex2aphi(z):
    return np.abs(z), np.unwrap(np.angle(z)) * 180 / pi



# 
# from scipy.special import ellipk
# 
# def K(k):
#     return ellipk(k)
# 
# def Kp(k):
#     return K(complementary(k))
# 
# def kokp_scipy(k):
#     return K(k)/Kp(k)
# 
# 
# k = np.linspace(0.0,1,100)
# 
# plt.figure()
# plt.plot(k,kokp(k))
# plt.plot(k,kokp_scipy(k),"o")
# xsx
