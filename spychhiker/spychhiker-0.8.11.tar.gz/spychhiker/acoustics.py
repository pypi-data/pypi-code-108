#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 09:32:12 2020

@author: benjamin
"""

import copy
import numpy as np
from ._set import timestruct, struct
from .electricterms import AcousticsElem, DerivTerms, IntegrTerms

class AcousticsTime:
    """ contains acoustic terms of the vocal tract """

    parent = None
    pressure_freq = None
    flow_freq = None
    areasensitivity = None
    lengthsensitivity = None
    norder = 1
    pressure_time = None
    flow_time = None
    elements = None
    derivative_terms = None
    intergation_terms = None
    noise_matrix = None
    flow_time_matrix = None
    pressure_time_matrix = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        """ returns a deep copy of the instance"""

        return copy.deepcopy(self)

    def initderiv(self):
        """ Initialisation of the derivative and integration terms
        Nx is the number of tubelets of the considered pipe"""

        nTube = self.parent.area_function.area.shape[0]
        Vc = np.zeros(nTube)
        Q = np.zeros(nTube + 1)
        V = np.zeros(nTube + 1)
        Qwl = np.zeros(nTube)
        Qwc = np.zeros(nTube)
        if self.parent.child_wvg is not None:
            nChild = len(self.parent.child_wvg)
        else:
            nChild = 0
        Qnc = np.zeros(nChild)

        deriv_terms = DerivTerms('Q', Q,
                                 'Qwl', Qwl,
                                 'Qwc', Qwc,
                                 'Qnc', Qnc,
                                 'parent', self.parent)
        integr_terms = IntegrTerms('V', V,
                                   'Vc', Vc,
                                   'parent', self.parent)

        self.derivative_terms = deriv_terms
        self.integration_terms = integr_terms

    def acou2elec(self, Const=None, ujm1=0, aglot=0, isSub=False):
        """Computes the electric components values of the vocal tract"""
        
        if Const is None:
            Const = timestruct()

        Xj = self.parent.area_function.length
        Aj = self.parent.area_function.area

        if hasattr(Const, 'k_iter'):
            Xj = Xj[:, Const.k_iter].reshape(-1, 1)
            Aj = Aj[:, Const.k_iter].reshape(-1, 1)

        nTube, nFrame = Aj.shape
        A_lip = Aj[-1, :]
        rad = np.sqrt(Aj/np.pi)
        aprec = np.diff(np.append(aglot, Aj.squeeze()))
        asucc = np.sign(np.diff(np.append(Aj.squeeze(), 1e10)))

        Gw = np.zeros(Xj.shape)
        Udj = np.zeros(Xj.shape)
        Rcm = np.zeros(Xj.shape)
        Rcp = np.zeros(Xj.shape)

        if Const.dynterm and sum(abs(ujm1)) != 0:
            idx = [x for x in range(len(aprec)) if aprec[x] < 0]
            Rcm[idx, :] = abs(ujm1[idx].reshape(-1, 1))*Const.rho/(2*Aj[idx, :]**2)
            idx = [x for x in range(len(asucc)) if asucc[x] < 0]
            idx2 = [x + 1 for x in idx]
            Rcp[idx, :] = -abs(ujm1[idx2].reshape(-1, 1))*Const.rho/(2*Aj[idx, :]**2)

        Lj = 0.5*Const.rho*Xj/Aj
        Rj = Const.rmlt * np.pi * Const.mu * Xj / Aj**2
        Cj = Xj*Aj/(Const.rho*Const.c**2)
        Srad = 0.5*Const.T*Const.S*np.pi*np.sqrt(np.pi)/Const.rho
        Grad = Const.G*np.pi**2/Const.rho/Const.c
        if isSub:
            xtrach = np.cumsum(Aj) / sum(Aj)
            wr = 0.33/(1.30**(xtrach/4))*1.6e3/(2*np.pi*(rad**3)*Xj)
            wl = 0.33/(1.30**(xtrach/4))*1.1e-3/(2*np.pi*rad*Xj)
            wc = (2*np.pi*(rad**3)*Xj)/(0.33/(1.30**(xtrach/4))*0.392e6)
        else:
            wr = Const.wr/(2*np.sqrt(np.pi))/Xj/np.sqrt(Aj)
            wl = 2/Const.T*Const.wm/(2*np.sqrt(np.pi))/Xj/np.sqrt(Aj)
            wc = 0.5*Const.T/(Const.wc/(2*np.sqrt(np.pi))/Xj/np.sqrt(Aj))

        if Const.wallyield:
            Gw = 1 / (wr + wl + wc)

        #### Compute linear system coefficients
        bj = np.zeros((nTube+1, nFrame))
        Hj = np.zeros((nTube+1, nFrame))
        bj[0:nTube, :] = 1./(2*Cj/Const.T+Gw)
        Hj[1:nTube, :] = -2*(Lj[0:nTube-1, :]+Lj[1:nTube, :])/Const.T \
            -Rj[0:nTube-1, :]-Rj[1:nTube, :]-Rcm[0:nTube-1, :]-Rcp[1:nTube, :] \
            -bj[0:nTube-1, :]-bj[1:nTube, :]
        bj[nTube, :] = 1./(Srad*np.sqrt(A_lip)+Grad*A_lip)
        Hj[nTube, :] = -(2/Const.T*Lj[nTube-1, :]+Rj[nTube-1, :] + \
                         bj[nTube-1, :]+bj[nTube, :]+Rcp[nTube-1])
        elements = AcousticsElem('Lj', Lj.squeeze(),
                                 'Rj', Rj.squeeze(),
                                 'Cj', Cj.squeeze(),
                                 'Gw', Gw.squeeze(),
                                 'wl', wl.squeeze(),
                                 'wc', wc.squeeze(),
                                 'Udj', Udj.squeeze(),
                                 'bj', bj.squeeze(),
                                 'Hj', Hj.squeeze(),
                                 'Rcm', Rcm.squeeze(),
                                 'Rcp', Rcp.squeeze(),
                                 'Ns', np.zeros((nTube+1, nFrame)).squeeze(),
                                 'parent', self)
        self.elements = elements

class AcousticsFreq:
    """ contains the acoustics terms of the vocal tract in the frequency domain"""

    parent = None
    pressure_freq = None
    flow_freq = None
    areasensitivity = None
    lengthsensitivity = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        """ returns a deep copy of the instance"""

        return copy.deepcopy(self)

    def af2acoustics(self, freq, param=None):
        """Compute the pressure and air flow inside the vocal and nasal tracts
        defined by area function A and l.
        The constant values are stocked in param.
        After the chain matrix paradigm by Sondhi and Schroeter
        in "A hybrid time-frequency domain articulatory speech synthesizer",
        IEEE TASSP, 1987)."""

        if param is None:
            param = struct()

        af = self.parent.area_function.area
        lf = self.parent.area_function.length
        if len(af.shape) == 1:
            nFrame = 1
            af = af.reshape((af.shape[0], nFrame), order='F')
            lf = lf.reshape((af.shape[0], nFrame), order='F')
        else:
            nFrame = af.shape[1]
        shapeFreq = freq.shape
        nFreq = shapeFreq[0]
        if len(shapeFreq) == 1:
            freq = np.matlib.repmat(freq, nFreq, nFrame)

        w = 2 * np.pi * freq
        alp = np.sqrt(1j*w * param.c1)
        bet = 1j*w * param.wo2/((1j*w + param.a) * 1j*w + param.b) + alp
        gam = np.sqrt((param.alp + 1j*w) / (bet + 1j*w))
        sig = gam * (bet + 1j*w)

        P = np.zeros((af.shape[0], nFrame, nFreq)) + 1j*np.zeros((af.shape[0], nFrame, nFreq))
        U = np.zeros((af.shape[0], nFrame, nFreq)) + 1j*np.zeros((af.shape[0], nFrame, nFreq))

        for kframe in range(nFrame):

            af_tmp = af[:, kframe]
            lf_tmp = lf[:, kframe]
            freqtmp = freq[:, kframe]
            sigtmp = sig[:, kframe]
            gamtmp = gam[:, kframe]
            wTmp = 2*np.pi*freqtmp

            Grad = 0.5 * param.rho * wTmp**2 / np.pi / param.c_s
            Jrad = 8 * param.rho * wTmp / 3 / np.pi**(1.5) * af_tmp[-1]**(-0.5)
            Zrad = Grad + 1j*Jrad
            P1 = Zrad
            U1 = np.ones(P1.shape)
            for ktube in range(af.shape[0]-1, -1, -1): # Compute the chain matrix
                Argh = sigtmp * lf_tmp[ktube] / param.c_s
                A = np.cosh(Argh)
                B = -param.rho*param.c_s / af_tmp[ktube] * gamtmp * np.sinh(Argh)
                C = -af_tmp[ktube] / param.rho/param.c_s / gamtmp * np.sinh(Argh)
                det_k = 1 / (A**2 - B * C)
                P1tmp = (A * P1 - B * U1) / det_k
                U1tmp = (-C * P1 + A * U1) / det_k
                P[ktube, kframe, :] = P1tmp.reshape((1, 1, np.size(P1tmp)),
                                                    order='F')
                U[ktube, kframe, :] = U1tmp.reshape((1, 1, np.size(U1tmp)),
                                                    order='F')
                P1 = P1tmp
                U1 = U1tmp

        self.pressure_freq = P
        self.flow_freq = U
        return P, U

    def areasensitivityfunction(self, freq, param=struct()):
        """Compute the sensitivity function Sn along the vocal tract"""

        af = self.parent.area_function.area
        lf = self.parent.area_function.length
        if len(af.shape) == 1:
            nFrame = 1
            af = af.reshape((af.shape[0], nFrame), order='F')
            lf = lf.reshape((af.shape[0], nFrame), order='F')
        else:
            nFrame = af.shape[1]
        nFreq, _ = freq.shape

        Sn_x = np.zeros((af.shape[0], nFrame, nFreq * nFrame)) + \
            1j*np.zeros((af.shape[0], nFrame, nFreq * nFrame))

        P, U = self.af2acoustics(freq, param)

        for kframe in range(nFrame):
            for kfreq in range(nFreq):
                Pn = np.squeeze(abs(P[:, kframe, kfreq])**2)
                Un = np.squeeze(abs(U[:, kframe, kfreq])**2)
                lftmp = np.squeeze(lf[:, kframe])
                aftmp = np.squeeze(af[:, kframe])
                idx = kframe*nFreq+kfreq
                cst1 = param.rho/aftmp*Un-aftmp/param.rho/param.c_s**2*Pn
                argsum1 = param.rho/aftmp*Un+aftmp/param.rho/param.c_s**2*Pn
                Sn_x[:, kframe, idx] = lftmp * cst1 / np.sum(lftmp * argsum1)

        self.areasensitivity = Sn_x
        return Sn_x

    def lengthsensitivityfunction(self, freq, param):
        """Compute the sensitivity function Sn along the vocal tract for the
        length function"""

        af = self.parent.area_function.area
        lf = self.parent.area_function.length

        if len(af.shape) == 1:
            nFrame = 1
            af = af.reshape((af.shape[0], nFrame),
                            order='F')
            lf = lf.reshape((af.shape[0], nFrame),
                            order='F')
        else:
            nFrame = af.shape[1]

        Sn_x = np.zeros((af.shape[0], nFrame, freq.shape[0] * nFrame)) + \
            1j*np.zeros((af.shape[0], nFrame, freq.shape[0] * nFrame))
        rho = param.rho
        cs = param.c_s

        P, U = self.af2acoustics(freq, param)
        for kframe in range(nFrame):
            for kfreq in range(freq.shape[0]):
                Pn = np.squeeze(abs(P[:, kframe, kfreq])**2)
                Un = np.squeeze(abs(U[:, kframe, kfreq])**2)
                lftmp = np.squeeze(lf[:, kframe])
                aftmp = np.squeeze(af[:, kframe])
                idx = kframe * freq.shape[0] + kfreq
                Sn_x[:, kframe, idx] = lftmp*(rho/aftmp*Un+aftmp/rho/cs**2*Pn)/ \
                    np.sum(lftmp*(rho/aftmp*Un+aftmp/rho/cs**2*Pn))

        self.lengthsensitivity = Sn_x
        return Sn_x
