#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file


import numpy as np
import scipy.special as sp


def compute_beta_S(R0, R1, lcur, sph):
    """
    Compute coefficients usefull to account spherical waves in cone

    For a pipe of length :math:`\\ell` and with\
    :math:`L = \\sqrt{\\ell^2 + \\Delta R^2}`

    :math:`\\beta` can be seen as the inverse of the distance to the apex:

    - if spherical waves :math:`\\beta = \\frac{\\Delta R}{L R_0}`
    - if plane waves :math:`\\beta = \\frac{\\Delta R}{\\ell R_0}`

    The area is generally assumed to be :math:`S = \\pi R_0^2`, except if
    ``sph='spherical_tmm'``, in that case it is the surface of the spherical cap:
    :math:`S = \\pi (R_0^2 + h^2)`

    Parameters
    ----------
    R0 : float
        upstream end radius.
    R1 : float
        dowstream end radius.
    lcur : float
        length of the pipe (along its main axis)
    sph : bool or str
        spherical waves or not.

    Returns
    -------
    beta : float
        the coef beta
    S : float
        Front wave area

    """
    DR = R1 - R0
    L = np.sqrt(lcur**2 + DR**2)
    if sph in [True]:
        beta = DR / L / R0
        S = np.pi * R0**2
    elif sph in ['spherical_tmm']:
        beta = DR / L / R0
        h = DR * R0 / (L + lcur)
        S = np.pi * (R0**2 + h**2)
    else:
        beta = DR / lcur / R0
        S = np.pi * R0**2
    return beta, S

def cone_lossy(physics, lpart, R0, R1, omegas, nbSub=1, sph=False, loss_type='bessel'):
    """
    Compute the transfer of a lossy cone.

    .. math::
        T = \\begin{pmatrix} A & B \\\\ C & D \\end{pmatrix}

    The :math:`A, B, C, D` are the coefficients given by [Chaigne_TMMconelossy]_ for a
    a cone (eq.(7.83), p.325), reformulated in a clearer way in [Ernoult_TMMlossy]_.

    For a conical pipe of radius :math:`R_0, R_1`:

    .. math::
        \\begin{align}
        A & = \\frac{R_1}{R_0} \\cosh(\\Gamma \\ell) -  \\frac{\\beta}{\\Gamma}\
            \\sinh(\\Gamma \\ell) \\\\
        B & = \\frac{R_1}{R_0} Z_c \\sinh(\\Gamma \\ell) \\\\
        C & = \\frac{1}{Z_c} \\left( (\\frac{R_1}{R_0} - \\frac{\\beta^2}{\\Gamma^2}) \\sinh(\\Gamma \\ell)
            + \\frac{\\ell \\beta^2}{\\Gamma \\cosh(\\Gamma \\ell))} \\right) \\\\
        D & = \\frac{R_1}{R_0} \\cosh(\\Gamma \\ell) + \\frac{\\beta}{\\Gamma} \\sinh(\\Gamma \\ell))
        \\end{align}

    with :math:`S, \\beta` depending if spherical waves are taken into account
    or not (see :py:func:`compute_beta_S`). The length :math:`\\ell` is the
    main axis length of the pipe in case of plane waves or the "wall" length
    (hypothenuse) in case of spherical waves.

    To include the losses :math:`Z_c, \\Gamma` are taken equals to the one
    of an equivalent cylinder with a radius : :math:`R_{eq}=(2 R_{min} + R_{max})/3`.
    It is possible to subdivise the cone to improve the accuracy of the losses

    Parameters
    ----------
    physics : :py:class:`Physics<openwind.continuous.physics.Physics>`
        The object with the physical quantities values.
    lpart : float
        The length of the pipe (main axis).
    R0 : float
        upstream end radius.
    R1 : float
        dowstream end radius.
    omegas : float
        The angular frequency.
    nbSub : int, optional
        The number of subdivision to improve losses computation. The default is 1.
    sph : bool or str, optional
        Spherical (true or 'spherical_tmm') or plane waves.. The default is False.
    loss_type : {'bessel', 'keefe', 'minikeefe'}, optional
        The losses model. The default is 'bessel'.

    Returns
    -------
    mat : tuple of float
        The value of A, B, C, D.

    References
    ----------
    .. [Chaigne_TMMconelossy] Chaigne, Antoine, and Jean Kergomard. 2016. "Acoustics \
        of Musical Instruments. Modern Acoustics and Signal Processing. New \
        York: Springer. https://doi.org/10.1007/978-1-4939-3679-3.

    .. [Ernoult_TMMlossy] Ernoult, Augustin, and Jean Kergomard. 2020. “Transfer \
        Matrix of a Truncated Cone with Viscothermal Losses: Application of \
        the WKB Method.” Acta Acustica 4 (2): 7. https://doi.org/10.1051/aacus/2020005.

    """
    assert physics.uniform # constant temperature only

    Rbeg = R0
    Rend = R1
    if Rbeg == Rend:  # test cylindrique
        subPart = 1
    else:
        subPart = nbSub
    lcur = lpart / subPart
    for i in range(subPart):
        R0 = Rend + (Rbeg - Rend) * (lpart - i * lcur) / lpart
        R1 = Rend + (Rbeg - Rend) * (lpart - (i + 1) * lcur) / lpart

        L = np.sqrt(lcur ** 2 + (R0 - R1) ** 2)
        beta, S = compute_beta_S(R0,R1,lcur,sph)
        Zc = physics.rho(0) * physics.c(0) / S

        Rmin = min(R0, R1)
        Rmax = max(R0, R1)
        # Req = (rmin + rmax) / 2  # half
        Req = (2*Rmin + Rmax) / 3  # first third, better according to Jean-Pierre Dalmont
        # version pafi (equivalent to eq.7.106, p333 of Chaigne and Kergomard 2016)
        # if Rmax==Rmin:
        #     Req = Rmin
        # else:
        #     Req = (Rmax-Rmin)/np.log1p((Rmax-Rmin)/Rmin)

        Zv, Yt = zv_yt_TMM(Req, S, omegas, physics, loss_type)
        Gamma = np.sqrt(Zv * Yt)
        Zcc = np.sqrt(Zv / Yt)
        if sph:
            length = L
        else:
            length = lcur
        A = R1 / R0 * np.cosh(Gamma * length) - \
            beta / Gamma * np.sinh(Gamma * length)
        B = R0 / R1 * Zcc * np.sinh(Gamma * length)
        C = 1 / Zcc * ((R1 / R0 - beta ** 2 / Gamma ** 2) *
                       np.sinh(Gamma * length) + length * beta ** 2 /
                       Gamma * np.cosh(Gamma * length))
        D = R0 / R1 * (np.cosh(Gamma * length) + (beta / Gamma) *
                       np.sinh(Gamma * length))

        matrixLocal = A, B, C, D
        if i == 0:
            mat = matrixLocal
        else:
            mat = multmat(mat, matrixLocal)
    return mat


def cone_lossless(physics, lpart, R0, R1, omegas, sph=False):
    """
    Compute the transfer of a lossless cone.

    .. math::
        T = \\begin{pmatrix} A & B \\\\ C & D \\end{pmatrix}

    The :math:`A, B, C, D` are the coefficients given by [Chaigne_TMMcone]_ for a
    a cone (eq.(7.83), p.325), reformulated in a clearer way in [Ernoult_TMM]_.

    For a conical pipe of radius :math:`R_0, R_1`:

    .. math::
        \\begin{align}
        A & = \\frac{R_1}{R_0} \\cos(k \\ell) -  \\frac{\\beta}{k}\
            \\sin(k \\ell) \\\\
        B & = \\frac{R_1}{R_0} Z_c \\sin(k \\ell) \\\\
        C & = \\frac{1}{Z_c} \\left( (\\frac{R_1}{R_0} - \\frac{\\beta^2}{k^2}) \\sin(k \\ell)
            + \\frac{\\ell \\beta^2}{k \\cos(k \\ell))} \\right) \\\\
        D & = \\frac{R_1}{R_0} \\cos(k \\ell) + \\frac{\\beta}{k} \\sin(k \\ell))
        \\end{align}

    with :math:`S, \\beta` depending if spherical waves are taken into account
    or not (see :py:func:`compute_beta_S`). The length :math:`\\ell` is the
    main axis length of the pipe in case of plane waves or the "wall" length
    (hypothenuse) in case of spherical waves.

    Parameters
    ----------
    physics : :py:class:`Physics<openwind.continuous.physics.Physics>`
        The object with the physical quantities values.
    lpart : float
        The length of the pipe (main axis).
    R0 : float
        upstream end radius.
    R1 : float
        dowstream end radius.
    omegas : float
        The angular frequency.
    sph : bool or str, optional
        Spherical (true or 'spherical_tmm') or plane waves.. The default is False.

    Returns
    -------
    mat : tuple of float
        The value of A, B, C, D.

    References
    ----------
    .. [Chaigne_TMMcone] Chaigne, Antoine, and Jean Kergomard. 2016. "Acoustics \
        of Musical Instruments. Modern Acoustics and Signal Processing. New \
        York: Springer. https://doi.org/10.1007/978-1-4939-3679-3.

    .. [Ernoult_TMM] Ernoult, Augustin, and Jean Kergomard. 2020. “Transfer \
        Matrix of a Truncated Cone with Viscothermal Losses: Application of \
        the WKB Method.” Acta Acustica 4 (2): 7. https://doi.org/10.1051/aacus/2020005.

    """
    assert physics.uniform # constant temperature only
    ks = omegas/physics.c(0)
    L = np.sqrt(lpart ** 2 + (R0 - R1) ** 2)
    beta, S = compute_beta_S(R0,R1,lpart,sph)

    if sph:
        length = L
    else:
        length = lpart

    Zc = physics.rho(0) * physics.c(0) / S
    A = R1 / R0 * np.cos(ks * length) - beta / ks * np.sin(ks * length)
    B = R0 / R1 * 1j * Zc * np.sin(ks * length)
    C = 1j / Zc * ((R1 / R0 + beta ** 2 / ks ** 2) * np.sin(ks * length) -
                   length * beta ** 2 / ks * np.cos(ks * length))
    D = R0 / R1 * (np.cos(ks * length) + (beta / ks) * np.sin(ks * length))
    return A, B, C, D


def multmat(mguide, matrix):
    """
    Multiply two matrices in format (A, B, C, D)

    Parameters
    ----------
    mguide : tuple of 4 floats
        The left matrix of the product.
    matrix : tuple of 4 floats
        The right hand matrix of the product.

    Returns
    -------
    tuple of 4 floats
        The resulting matrix

    """
    A1, B1, C1, D1 = mguide
    A2, B2, C2, D2 = matrix
    A = A1*A2 + B1*C2
    B = A1*B2 + B1*D2
    C = C1*A2 + D1*C2
    D = C1*B2 + D1*D2
    return A, B, C, D

def impedance_TMM(mguide, Zr):
    """
    deprecated
    """
    N = int(mguide.shape[0] / 4)
    return (mguide[0:N] * Zr +
            mguide[N:2 * N]) / (mguide[2 * N:3 * N] * Zr + mguide[3 * N:4 * N])

def zv_yt_TMM(Req, S, omega, physics, loss_type):
    """
    The lossy term Zv and Yt

    Zv has the dimension of :math:`j \\omega \\rho /S`.
    Yt has the dimension of :math:`j \\omega S / (\\rho c^2)`.

    Following the option given, the formule used is:

    - 'bessel', (Zwikker and Kosten): eq.(5.133), (5.134) p.239 of [Chaigne_TMMlosses]_
    - 'keefe' 2nd order approximaiton: eq.(5.143), p.142 of [Chaigne_TMMlosses]_
    - 'minikeefe' 1st order approximation of these equations


    Parameters
    ----------
    Req : float
        The radius of the equivalent cylinder.
    S : float
        the area of the front wave at the entrence of the pipe.
    omega : float
        angular frequency.
    physics : :py:class:`Physics<openwind.continuous.physics.Physics>`
        The object with the physical quantities values.
    loss_type : {'bessel', 'keefe', 'minikeefe'}, optional
        The losses model. The default is 'bessel'..

    Returns
    -------
    Zv : float
        The value of Zv.
    Yt : float
        The value of Yt.

    References
    ----------
    .. [Chaigne_TMMlosses] Chaigne, Antoine, and Jean Kergomard. 2016. "Acoustics \
        of Musical Instruments. Modern Acoustics and Signal Processing. New \
        York: Springer. https://doi.org/10.1007/978-1-4939-3679-3.

    """
    rv = Req * np.sqrt(physics.rho(0) * omega / physics.mu(0))
    rt = Req * np.sqrt(omega * physics.rho(0) * physics.Cp / physics.kappa(0))
    if loss_type in ['bessel']:
        kvr = rv / np.sqrt(1j)
        ktr = rt / np.sqrt(1j)
        #    jv = 2 * sp.jve(1, kvr) / (kvr * sp.jve(0, kvr))
        Zv = (1j * omega * physics.rho(0) / S) * (1 / ( 1 - 2 * sp.jve(1, kvr) / (kvr * sp.jve(0, kvr))))
        #    jt = 2 * sp.jve(1, ktr) / (ktr * sp.jve(0, ktr))
        Yt = 1j * omega * S / (physics.rho(0) * physics.c(0)**2) * (1 + (physics.gamma - 1) * 2 * sp.jve(1, ktr) / (ktr * sp.jve(0, ktr)))
    elif loss_type in ['keefe']:
        Zv = (1j * omega * physics.rho(0) / S) * (1 + 2*np.sqrt(-1j)/rv - 3*1j/(rv**2))
        Yt = 1j * omega * S / (physics.rho(0) * physics.c(0)**2) * (1 + (physics.gamma - 1)*(2*np.sqrt(-1j)/rt + 1j/(rt**2)))
    elif loss_type in ['minikeefe']:
        Zv = (1j * omega * physics.rho(0) / S) * (1 + 2*np.sqrt(-1j)/rv )
        Yt = 1j * omega * S / (physics.rho(0) * physics.c(0)**2) * (1 + (physics.gamma - 1)*(2*np.sqrt(-1j)/rt ))
    return Zv, Yt
