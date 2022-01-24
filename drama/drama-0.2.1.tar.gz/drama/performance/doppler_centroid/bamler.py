# -*- coding: utf-8 -*-
"""
Created on Sat Nov 01 15:16:18 2014

author: Paco Lopez-Dekker
"""

from __future__ import absolute_import, division, print_function

import numpy as np

from drama import constants as const
from drama.orbits import orbit_to_vel
from drama.performance import sar as sar
from drama.utils import db2lin


def stripmap_numerical(
    prf, v_orb, L=None, Lrx=None, snr_db=10.0, f0=1, rx_pat=None, tx_pat=None
):
    """Doppler centroid integrating Doppler spectrum We can compute
        this for any shape of snrd_db, which can be an ndarray, but
        prf should be fixed

    Parameters
    ----------
    prf : float
        Pulse repetition frequency
    v_orb : float
        Orbital velocity
    L : float
         Antenna length (Default value = None)
    Lrx : float
         Antenna length of receiver (Default value = None)
    snr_db : float
         Signal-to-noise ration in dB (Default value = 10.0)
    f0 : float
         Centre frequency (Default value = 1)
    rx_pat : Pattern class object
         Antenna pattern of the receiver (Default value = None)
    tx_pat : Pattern class object
         Antenna pattern of the transmitter (Default value = None)

    Returns
    -------
    float
        Numerical calculation of the Cramer-Rao bound.
    """
    Ns = 1000
    f_D = np.linspace(-prf * 3 / 2, prf * 3 / 2, num=3 * Ns).reshape((3, Ns))
    # fd = 2 v / wl * u -> u = df * wl / 2 / v
    sin_angle = f_D * (const.c / f0 / 2.0) / v_orb
    if tx_pat is None:
        beam_pattern_1 = sar.sinc_bp(sin_angle, L, f0, field=False)
    else:
        beam_pattern_1 = tx_pat(sin_angle, field=False)

    if rx_pat is None:
        if Lrx is None:
            Lrx = L
        beam_pattern_2 = sar.sinc_bp(sin_angle, Lrx, f0, field=False)
    else:
        beam_pattern_2 = rx_pat(sin_angle, field=False)

    beam_pattern_2way = beam_pattern_1 * beam_pattern_2
    dop_spectrum = beam_pattern_2way
    dop_spectrum_al = np.sum(beam_pattern_2way, axis=0)
    if type(snr_db) is np.ndarray:
        snr_db_r = snr_db.reshape(snr_db.shape + (1,))
        noise_density = sum(dop_spectrum[1, :]) / db2lin(snr_db_r) / Ns
    else:
        noise_density = sum(dop_spectrum[1, :]) / db2lin(snr_db) / Ns

    d_spec_df = (
        (dop_spectrum.flatten())[Ns + 1 : 2 * Ns + 1]
        - (dop_spectrum.flatten())[Ns : 2 * Ns]
    ) / (prf / Ns)
    # denominator (13) in Bamler
    k = 1 / np.sum(
        prf / Ns * ((d_spec_df / (dop_spectrum_al + noise_density)) ** 2),
        axis=-1,
    )
    return k


def stripmap(
    La,
    rg_res,
    prod_res=1e3,
    v_ef=None,
    numerical=False,
    snr_db=10,
    La2=None,
    az_ovs=1.1,
    az_res=None,
    rx_pat=None,
    f0=1,
    tx_pat=None,
    prf=None,
):
    """Provides an estimate of the Cramer-Rao bound for the Doppler centroid
       estimation, assuming a stripmap opeation mode and a sinc pattern. For
       reference see Bamler's Doppler Frequency Estimation and the Cramer-Rao
       Bound

    Parameters
    ----------
    La : float
        Antenna length, in m
    rg_res : float
        range resolution, in m
    prod_res : float
        product resolution, assuming isotropic grid, in m (Default value = 1e3)
    v_ef : float
        effective velocity of sensor. If not given LEO is assumed (Default value = None)
    numerical : boolean
        flag for numerical integration, needed for finete SNR (Default value = False)
    snr_db : float
        SNR level, in dB (Default value = 10)
    az_ovs : float
        PRF oversampling (Default value = 1.1)
    prf : float, ndarray
        PRF, if you want to give it explicitly, can be a scalar or an ndarray like snr_db (Default value = None)
    rx_pat : Pattern class object
        Antenna pattern of the receiver (Default value = None)
    tx_pat : Pattern class object
        Antenna pattern of the transmitter (Default value = None)
    La2 : float
        Second antenna length (Default value = None)
    az_res : float
        Azimuth resolution (Default value = None)
    f0 : float
        Centre frequency (Default value = 1)

    Returns
    -------
    float
        Estimate of the Cramer-Rao bound
    """

    if v_ef is None:
        v_ef = orbit_to_vel(600e3)
    if (rx_pat is not None) or (tx_pat is not None):
        numerical = True
    # Coarse but not too bad approximation to Doppler bandwidth
    if az_res is None:
        az_res = La / 2.0

    if prf is None:
        doppler_bw = v_ef / La * 2
        prf = az_ovs * doppler_bw
    # Number of independent samples
    n_samp = (prod_res ** 2) / (az_res * rg_res)
    # FIXME, here something is wrong, increasing PRF leads to worse performance. This should be compensated
    # somewhere somehow
    # delta_f = v_ef / prod_res
    # n_rg_smp = prod_res / rg_res
    sigma_f = 0.2516 * prf / np.sqrt(n_samp)
    # sigma_f = 0.2516 * delta_f / np.sqrt(n_rg_smp)
    if numerical:
        k = stripmap_numerical(
            prf,
            v_ef,
            La,
            snr_db=snr_db,
            Lrx=La2,
            rx_pat=rx_pat,
            f0=f0,
            tx_pat=tx_pat,
        )
        # n_az = prod_res / az_res
        # n_rg = prod_res / rg_res
        # delta_f = v_ef / (N_az * az_res)
        sigma_f_num = np.sqrt(k * prf / n_samp)
        return sigma_f_num
    else:
        return sigma_f
