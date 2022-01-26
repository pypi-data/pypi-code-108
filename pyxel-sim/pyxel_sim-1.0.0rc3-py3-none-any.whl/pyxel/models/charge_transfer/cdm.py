#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Charge Distortion Model for :term:`CCDs<CCD>`.

============================
This is a function to run the upgraded :term:`CDM` :term:`CTI` model developed by Alex Short (ESA).

:requires: NumPy

:author: Alex Short
:author: Sami-Matias Niemi
:author: David Lucsanyi

Descriptions of model quantities in the paper:

Ne - number of electrons in a pixel
ne - electron density in the vicinity of the trap
Vc - volume of the charge cloud
Pr - the probability that the trap will release the electron into the sample
tau_c - capture time constant
Pc - capture probability (per vacant trap) as a function of the number of sample electrons Ne
NT - number of traps in the column,
NT = 2*nt*Vg*x  where x is the number of TDI transfers or the column length in pixels.
Nc - number of electrons captured by a given trap species during the transit of an integrating signal packet
N0 - initial trap occupancy
Nr - number of electrons released into the sample during a transit along the column
vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
t: constant TDI period (parallel)
st: constant TDI period (serial)
"""

import typing
from enum import Enum

import astropy.constants as const
import numba
import numpy as np
from typing_extensions import Literal

from pyxel.detectors import CCD


class CDMdirection(Enum):
    """:term:`CDM` direction class."""

    Parallel = "parallel"
    Serial = "serial"


def cdm(
    detector: CCD,
    direction: Literal["parallel", "serial"],
    beta: float,
    trap_release_times: typing.Sequence[float],
    trap_densities: typing.Sequence[float],
    sigma: typing.Sequence[float],
    full_well_capacity: typing.Optional[float] = None,
    max_electron_volume: float = 0.0,
    transfer_period: float = 0.0,
    charge_injection: bool = False,
    electron_effective_mass: float = 0.5,
) -> None:
    r"""Charge Distortion Model (CDM) model wrapper.

    Parameters
    ----------
    detector: CCD
        Pyxel CCD detector object.
    direction: literal
        Set ``"parallel"`` for :term:`CTI` in parallel direction or ``"serial"`` for :term:`CTI` in serial register.
    beta: float
        Electron cloud expansion coefficient :math:`\beta`.
    trap_release_times: sequence of float
        Trap release time constants :math:`\tau_r`. Unit: :math:`s`.
    trap_densities: sequence of float
        Absolute trap densities :math:`n_t`. Unit: :math:`cm^{-3}`.
    sigma: sequence of float
        Trap capture cross section :math:`\sigma`. Unit: :math:`cm^2`.
    full_well_capacity: float
        Full well capacity :math:`FWC`. Unit: :math:`e^-`.
    max_electron_volume: float
        Maximum geometrical volume :math:`V_g` that electrons can occupy within a pixel. Unit: :math:`cm^3`.
    transfer_period: float
        Transfer period :math:`t` (TDI period). Unit: :math:`s`.
    charge_injection: bool
        Enable charge injection (only used in ``"parallel"`` mode).
    electron_effective_mass: float
        Electron effective mass in the semiconductor lattice. Unit: 1 electron mass
    """

    e_effective_mass = electron_effective_mass * const.m_e.value

    if full_well_capacity is None:
        fwc_final = detector.characteristics.full_well_capacity
    else:
        fwc_final = full_well_capacity

    mode = CDMdirection(direction)

    if not isinstance(detector, CCD):
        # Later, this will be checked in when YAML configuration file is parsed
        raise TypeError("Expecting a `CCD` object for 'detector'.")

    if not (0.0 <= max_electron_volume <= 1.0):
        raise ValueError("'max_electron_volume' must be between 0.0 and 1.0.")
    if not (0.0 <= beta <= 1.0):
        raise ValueError("'beta' must be between 0.0 and 1.0.")
    if not (0.0 <= fwc_final <= 1.0e7):
        raise ValueError("'full_well_capacity' must be between 0 and 1e7.")
    if not (0.0 <= transfer_period <= 10.0):
        raise ValueError("'transfer_period' must be between 0.0 and 10.0.")
    if not (len(trap_densities) == len(trap_release_times) == len(sigma)):
        raise ValueError(
            "Length of 'sigma', 'trap_densities' and 'trap_release_times' not the same!"
        )
    if len(trap_release_times) == 0:
        raise ValueError("Expecting inputs for at least one trap species.")

    e_thermal_velocity = np.sqrt(
        3 * const.k_B.value * detector.environment.temperature / e_effective_mass
    )

    if mode == CDMdirection.Parallel:
        detector.pixel.array = run_cdm_parallel(
            array=detector.pixel.array,
            vg=max_electron_volume,
            t=transfer_period,
            fwc=fwc_final,
            vth=e_thermal_velocity,
            charge_injection=charge_injection,
            chg_inj_parallel_transfers=detector.geometry.row,
            beta=beta,
            tr=np.array(trap_release_times),
            nt=np.array(trap_densities),
            sigma=np.array(sigma),
        )

    elif mode == CDMdirection.Serial:
        detector.pixel.array = run_cdm_serial(
            array=detector.pixel.array,
            vg=max_electron_volume,
            t=transfer_period,
            fwc=fwc_final,
            vth=e_thermal_velocity,
            beta=beta,
            tr=np.array(trap_release_times),
            nt=np.array(trap_densities),
            sigma=np.array(sigma),
        )


@numba.njit(nogil=True)
def run_cdm_parallel(
    array: np.ndarray,
    beta: float,
    vg: float,
    t: float,
    fwc: float,
    vth: float,
    tr: np.ndarray,
    nt: np.ndarray,
    sigma: np.ndarray,
    charge_injection: bool = False,
    chg_inj_parallel_transfers: int = 0,
) -> np.ndarray:
    r"""Run :term:`CDM` in parallel direction.

    Parameters
    ----------
    array: ndarray
        Input array.
    beta: float
        Electron cloud expansion coefficient :math:`\beta`.
    vg: float
        Maximum geometrical volume :math:`V_g` that electrons can occupy within a pixel. Unit: :math:`cm^3`.
    t: float
        Transfer period :math:`t` (TDI period). Unit: :math:`s`.
    fwc: float
        Full well capacity :math:`FWC`. Unit: :math:`e^-`.
    vth: float
        Electron thermal velocity.
    tr: sequence of float
        Trap release time constants :math:`\tau_r`. Unit: :math:`s`.
    nt: sequence of float
        Absolute trap densities :math:`n_t`. Unit: :math:`cm^{-3}`.
    sigma: sequence of float
        Trap capture cross section :math:`\sigma`. Unit: :math:`cm^2`.
    charge_injection: bool
        Enable charge injection (only used in "parallel" mode).
    chg_inj_parallel_transfers: int
        Number of parallel transfers for charge injection.

    Returns
    -------
    array: ndarray
        Output array.
    """
    ydim, xdim = array.shape  # full signal array we want to apply cdm for
    kdim_p = len(nt)
    # np.clip(s, 0., fwc, s)      # full well capacity
    nt = nt / vg  # parallel trap density (traps / cm**3)
    # nt_p *= rdose             # absolute trap density [per cm**3]

    # IMAGING (non-TDI) MODE
    # Parallel direction
    no = np.zeros((xdim, kdim_p))
    alpha_p = t * sigma * vth * fwc ** beta / (2.0 * vg)  # type: np.ndarray
    g_p = 2.0 * nt * vg / fwc ** beta  # type: np.ndarray
    for i in range(0, ydim):
        if charge_injection:
            gamma_p = (
                g_p * chg_inj_parallel_transfers
            )  # number of all transfers in parallel dir.
        else:
            gamma_p = g_p * i  # TODO: (i+1) ?????????????
        for k in range(kdim_p):
            for j in range(xdim):
                nc = 0.0
                if array[i, j] > 0.01:
                    nc = max(
                        (gamma_p[k] * array[i, j] ** beta - no[j, k])
                        / (gamma_p[k] * array[i, j] ** (beta - 1.0) + 1.0)
                        * (1.0 - np.exp(-1 * alpha_p[k] * array[i, j] ** (1.0 - beta))),
                        0.0,
                    )
                    no[j, k] += nc
                nr = no[j, k] * (1.0 - np.exp(-t / tr[k]))
                array[i, j] += -1 * nc + nr
                no[j, k] -= nr
                if array[i, j] < 0.01:
                    array[i, j] = 0.0

    return array


@numba.njit(nogil=True)
def run_cdm_serial(
    array: np.ndarray,
    beta: float,
    vg: float,
    t: float,
    fwc: float,
    vth: float,
    tr: np.ndarray,
    nt: np.ndarray,
    sigma: np.ndarray,
) -> np.ndarray:
    r"""Run :term:`CDM` in serial direction.

    Parameters
    ----------
    array: ndarray
        Input array.
    beta: float
        Electron cloud expansion coefficient :math:`\beta`.
    vg: float
        Maximum geometrical volume :math:`V_g` that electrons can occupy within a pixel. Unit: :math:`cm^3`.
    t: float
        Transfer period :math:`t` (TDI period). Unit: :math:`s`.
    fwc: float
        Full well capacity :math:`FWC`. Unit: :math:`e^-`.
    vth: float
        Electron thermal velocity.
    tr: sequence of float
        Trap release time constants :math:`\tau_r`. Unit: :math:`s`.
    nt: sequence of float
        Absolute trap densities :math:`n_t`. Unit: :math:`cm^{-3}`.
    sigma: sequence of float
        Trap capture cross section :math:`\sigma`. Unit: :math:`cm^2`.

    Returns
    -------
    array: ndarray
    """
    ydim, xdim = array.shape  # full signal array we want to apply cdm for
    kdim_s = len(nt)
    # np.clip(s, 0., fwc, s)      # full well capacity
    nt = nt / vg  # serial trap density (traps / cm**3)
    # nt_s *= rdose             # absolute trap density [per cm**3]

    # IMAGING (non-TDI) MODE
    # Serial direction

    sno = np.zeros((ydim, kdim_s))
    alpha_s = t * sigma * vth * fwc ** beta / (2.0 * vg)  # type: np.ndarray
    g_s = 2.0 * nt * vg / fwc ** beta
    for j in range(0, xdim):
        gamma_s = g_s * j  # TODO: (j+1) ?????????????
        for k in range(kdim_s):
            for i in range(ydim):
                nc = 0.0
                if array[i, j] > 0.01:
                    nc = max(
                        (gamma_s[k] * array[i, j] ** beta - sno[i, k])
                        / (gamma_s[k] * array[i, j] ** (beta - 1.0) + 1.0)
                        * (1.0 - np.exp(-1 * alpha_s[k] * array[i, j] ** (1.0 - beta))),
                        0.0,
                    )
                    sno[i, k] += nc
                nr = sno[i, k] * (1.0 - np.exp(-t / tr[k]))
                array[i, j] += -1 * nc + nr
                sno[i, k] -= nr
                if array[i, j] < 0.01:
                    array[i, j] = 0.0

    return array


#
# def plot_serial_profile(
#     data: np.ndarray, row: int, data2: t.Optional[np.ndarray] = None
# ) -> None:
#     """TBW.
#
#     :param data:
#     :param row:
#     :param data2:
#     """
#     ydim, xdim = data.shape
#     profile_x = list(range(ydim))
#     profile_y = data[row, :]
#     plt.title("Serial profile")
#     plt.plot(profile_x, profile_y, color="blue")
#     if data2 is not None:
#         profile_y_2 = data2[row, :]
#         plt.plot(profile_x, profile_y_2, color="red")
#
#
# def plot_parallel_profile(
#     data: np.ndarray, col: int, data2: t.Optional[np.ndarray] = None
# ) -> None:
#     """TBW.
#
#     :param data:
#     :param col:
#     :param data2:
#     """
#     ydim, xdim = data.shape
#     profile_x = list(range(xdim))
#     profile_y = data[:, col]
#     plt.title("Parallel profile")
#     plt.plot(profile_x, profile_y, color="blue")
#     if data2 is not None:
#         profile_y_2 = data2[:, col]
#         plt.plot(profile_x, profile_y_2, color="red")
#
#
# def plot_1d_profile(
#     array: np.ndarray, offset: int = 0, label: str = "", m: str = "-"
# ) -> None:
#     """Plot profile on log scale.
#
#     :param array:
#     :param offset:
#     :param label:
#     :param m:
#     """
#     x = list(range(offset, offset + len(array)))
#     # plt.title('Parallel profile, charge injection')
#     plt.semilogy(x, array, m, label=label)
#     if label:
#         plt.legend()
#
#
# def plot_1d_profile_lin(
#     array: np.ndarray,
#     offset: int = 0,
#     label: str = "",
#     m: str = "-",
#     col: t.Optional[str] = None,
# ) -> None:
#     """TBW.
#
#     :param array:
#     :param offset:
#     :param label:
#     :param m:
#     :param col:
#     """
#     x = list(range(offset, offset + len(array)))
#     # plt.title('Parallel profile, charge injection')
#     plt.plot(x, array, m, label=label, color=col)
#     if label:
#         plt.legend()
#
#
# def plot_1d_profile_with_err(
#     array: np.ndarray, error: np.ndarray, offset: int = 0, label: str = ""
# ) -> None:
#     """TBW.
#
#     :param array:
#     :param error:
#     :param offset:
#     :param label:
#     """
#     x = list(range(offset, offset + len(array)))
#     plt.title("Parallel profile with error, charge injection")
#     plt.errorbar(x, array, error, label=label, linestyle="None", marker=".")
#     if label:
#         plt.legend()
#
#
# def plot_residuals(
#     data: np.ndarray, data2: np.ndarray, label: str = ""
# ) -> None:  # col='magenta',
#     """TBW.
#
#     :param data:
#     :param data2:
#     # :param col:
#     :param label:
#     """
#     x = list(range(len(data)))
#     # plt.title('Residuals of fitted and target parallel CTI profiles')
#     residuals = np.around(data - data2, decimals=5)
#     # residuals = data-data2
#     # plt.plot(x, residuals, '.', color=col, label=label)
#     plt.plot(x, residuals, ".", label=label)
#     plt.legend()
#
#
# def plot_image(data: np.ndarray) -> None:
#     """TBW.
#
#     :param data:
#     """
#     plt.imshow(data, cmap=plt.gray())  # , interpolation='nearest')
#     plt.xlabel("x - serial direction")
#     plt.ylabel("y - parallel direction")
#     plt.title("CCD image with CTI")
#     plt.colorbar()


# # @numba.jit(nopython=True, nogil=True, parallel=True)
# def optimized_cdm(
#     s: np.ndarray,
#     beta_p: float,
#     beta_s: float,
#     vg: float,
#     svg: float,
#     t: float,
#     st: float,
#     fwc: float,
#     sfwc: float,
#     vth: float,
#     tr_p: np.ndarray,
#     tr_s: np.ndarray,
#     nt_p: np.ndarray,
#     nt_s: np.ndarray,
#     sigma_p: np.ndarray,
#     sigma_s: np.ndarray,
#     charge_injection: bool = False,
#     chg_inj_parallel_transfers: int = 0,
#     parallel_cti: bool = True,
#     serial_cti: bool = True,
# ) -> np.ndarray:
#     """CDM model.
#
#     Done by Patricia Liebing. Not yet test or compared to the original 'run_cdm' function.
#
#     :param s: np.ndarray
#     :param dob:
#     :param beta_p: electron cloud expansion coefficient (parallel)
#     :param beta_s: electron cloud expansion coefficient (serial)
#     :param vg: assumed maximum geometrical volume electrons can occupy within
#                a pixel (parallel)
#     :param svg: assumed maximum geometrical volume electrons can occupy within
#                 a pixel (serial)
#     :param t: constant TDI period (parallel)
#     :param st: constant TDI period (serial)
#     :param fwc:
#     :param sfwc:
#     :param vth:
#     :param charge_injection:
#     :param chg_inj_parallel_transfers:
#     :param sigma_p:
#     :param sigma_s:
#     :param tr_p:
#     :param tr_s:
#     :param nt_p: number of traps per electron cloud (and not pixel!)
#                  in parallel direction
#     :param nt_s: number of traps per electron cloud (and not pixel!)
#                  in serial direction
#     :param parallel_cti:
#     :param serial_cti:
#     :return:
#     """
#     ydim, xdim = s.shape  # full signal array we want to apply cdm for
#
#     kdim_p = len(nt_p)
#     kdim_s = len(nt_s)
#
#     # np.clip(s, 0., fwc, s)      # full well capacity
#
#     nt_p = nt_p / vg  # parallel trap density (traps / cm**3)
#     nt_s = nt_s / svg  # serial trap density (traps / cm**3)
#
#     # nt_p *= rdose             # absolute trap density [per cm**3]
#     # nt_s *= rdose             # absolute trap density [per cm**3]
#
#     # IMAGING (non-TDI) MODE
#     # Parallel direction
#     if parallel_cti:
#         no = np.zeros((xdim, kdim_p))
#         alpha_p = t * sigma_p * vth * fwc ** beta_p / (2.0 * vg)  # type: np.ndarray
#         g_p = 2.0 * nt_p * vg / fwc ** beta_p  # type: np.ndarray
#         for i in range(0, ydim):
#             if charge_injection:
#                 gamma_p = (
#                     g_p * chg_inj_parallel_transfers
#                 )  # number of all transfers in parallel dir.
#             else:
#                 gamma_p = g_p * (i + 1)
#             for k in range(kdim_p):
#                 nc = np.zeros(xdim)
#                 nctest = np.zeros(xdim)
#                 sclm = s[i, :]
#                 idx = np.where(sclm > 0.01)
#                 nok = no[:, k]
#                 nc[idx] += (
#                     (gamma_p[k] * sclm[idx] ** beta_p - nok[idx])
#                     / (gamma_p[k] * sclm[idx] ** (beta_p - 1.0) + 1.0)
#                     * (1.0 - np.exp(-1 * alpha_p[k] * sclm[idx] ** (1.0 - beta_p)))
#                 )
#                 no[:, k] += np.fmax(nctest, nc)
#                 nr = no[:, k] * (1.0 - np.exp(-t / tr_p[k]))
#                 s[i, :] += -1 * nc + nr
#                 no[:, k] -= nr
#
#     # IMAGING (non-TDI) MODE
#     # Serial direction
#     if serial_cti:
#         sno = np.zeros((ydim, kdim_s))
#         alpha_s = st * sigma_s * vth * sfwc ** beta_s / (2.0 * svg)  # type: np.ndarray
#         g_s = 2.0 * nt_s * svg / sfwc ** beta_s  # type: np.ndarray
#         for j in range(0, xdim):
#             gamma_s = g_s * (j + 1)
#             for k in range(kdim_s):
#                 ncs = np.zeros(ydim)
#                 ncstest = np.zeros(ydim)
#                 srow = s[:, j]
#                 idxs = np.where(srow > 0.01)
#                 snok = sno[:, k]
#                 ncs[idxs] += (
#                     (gamma_s[k] * srow[idxs] ** beta_s - snok[idxs])
#                     / (gamma_s[k] * srow[idxs] ** (beta_s - 1.0) + 1.0)
#                     * (1.0 - np.exp(-1 * alpha_s[k] * srow[idxs] ** (1.0 - beta_s)))
#                 )
#                 sno[:, k] += np.fmax(ncstest, ncs)
#                 nrs = sno[:, k] * (1.0 - np.exp(-st / tr_s[k]))
#                 s[:, j] += -1 * ncs + nrs
#                 sno[:, k] -= nrs
#
#     return s
