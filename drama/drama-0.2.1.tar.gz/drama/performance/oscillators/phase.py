# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 12:48:52 2015

@author: Paco Lopez-Dekker
"""
from __future__ import absolute_import, division, print_function
import numpy as np
import scipy as sp
import drama.utils as utils
from matplotlib import pyplot as plt


def measured2coef(f=None, S_meas=None, floor=-160, type="SAOCOM", alpha=-3):
    """

    Parameters
    ----------
    f :
         (Default value = None)
    S_meas :
         (Default value = None)
    floor :
         (Default value = -160)
    type :
         (Default value = 'SAOCOM')
    alpha :
         (Default value = -3)

    Returns
    -------

    """
    if (f is None) or (S_meas is None):
        if type == "SAOCOM":
            f = np.array([1, 10, 100, 1000.0])
            S_meas = np.array([-100, -120, -135, -150])
            floor = -155
        elif type == "astrium_ocxo":
            f = np.array([1, 10, 100, 1000.0])
            S_meas = np.array([-105, -140, -150, -156])
            floor = -160
        elif type == "ap_com16":
            f = np.array([1, 10, 100, 1000.0])
            S_meas = np.array([-105, -135, -145, -153])
            floor = -155
        elif type == "TSX":
            f = np.array([10, 100, 1000, 1e4])
            S_meas = np.array([-118, -138, -155, -158])
            floor = -160

    f_e = np.append(f, [np.max(f) * 10, np.max(f) * 100])
    S_m_l = np.append(
        utils.db2lin(S_meas), utils.db2lin(np.array([floor, floor]))
    )
    f_p = 10 ** (np.arange(np.log10(f_e.min()), np.log10(f_e.max()), 0.1))
    S_spl = sp.interpolate.interp1d(np.log10(f_e), utils.db(S_m_l), "linear")
    coef1 = sp.polyfit(f_e, (f_e ** 4) * S_m_l, deg=4, w=f_e ** alpha)
    coef2 = sp.polyfit(
        f_p,
        (f_p ** 4) * utils.db2lin(S_spl(np.log10(f_p))),
        deg=4,
        w=f_p ** alpha,
    )
    coef1_ = np.where(coef1 > 0, coef1, 0)
    coef2_ = np.where(coef2 > 0, coef2, 0)
    plt.figure()
    plt.plot(f_e, utils.db(S_m_l), "b--")
    plt.xscale("log")
    plt.plot(f_p, utils.db(f_p ** -4 * sp.polyval(coef1_, f_p)), "r")
    plt.plot(f_p, utils.db(f_p ** -4 * sp.polyval(coef2_, f_p)), "g")
    return coef2_
