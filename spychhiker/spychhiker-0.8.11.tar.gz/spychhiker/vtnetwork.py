# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 09:06:31 2020

@author: benjamin
"""

import numpy as np
import scipy.signal as ssg
# import statsmodels.api as sm
from ._set import timestruct
from .utils import *
from .plottools import subplot_param, addplot, openfig, plot_tf
from tqdm import tqdm

class VtNetwork:
    """ Class for analysis of the whole vocal apparatus"""

    waveguide = None
    oscillators = None
    force_vector = None
    esmf_matrix = None
    number_tubes = None
    isChink = False
    isSubGlott = False
    isGlott = False
    isSupOscill = False
    whereChink = None
    whereSubGlott = None
    whereGlott = None
    whereSupOscill = None
    input_area = None
    flow_inst = None
    radiation_position = None
    subglottal_control = None
    phonetic_label = None
    phonetic_instant = None
    abduction = None
    simulation_frequency = None
    freq = None

    #### Output
    pressure_radiated = None
    network_transfer_function = None
    network_transfer_function_constriction = None

     # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def computetransferfunction(self, param, meth='tmm', loc=-1):
        """returns the transfer function of the vocal tract"""

        param.freq[param.freq <= 1e-11] = 1e-11
        freq = param.freq.reshape(-1)
        w = 2*np.pi*freq
        lw = len(w)

        if meth.lower() == 'cmp':
            param.alp = np.sqrt(1j*w * param.c1)
            param.bet = 1j*w * param.wo2 / ((1j*w + param.a) * 1j*w + param.b) + param.alp
            param.gam = np.sqrt((param.alp + 1j*w) / (param.bet + 1j*w))
            param.sig = param.gam*(param.bet + 1j*w)

        Nwave = len(self.waveguide)
        aftmp = self.waveguide[0].area_function.area
        if len(aftmp.shape) == 1:
            nframe = 1
            aftmp = aftmp.reshape(-1, 1)
            loc = [loc]
        else:
            nframe = aftmp.shape[1]
        transFun = np.zeros((lw, nframe), dtype='complex')
        Hf_cstr = np.zeros((lw, nframe), dtype='complex')

        for kf in range(nframe):
            for kw in range(Nwave-1, -1, -1):
                objtmp = self.waveguide[kw]
                if nframe == 1:
                    objtmp.area_function.area = objtmp.area_function.area.reshape(-1, 1)
                    objtmp.area_function.length = objtmp.area_function.length.reshape(-1, 1)

                if type(objtmp) != 'GlottalChink' and type(objtmp) != 'SubGlottalTract':

                    Avt = objtmp.area_function.area[:, kf]
                    lvt = objtmp.area_function.length[:, kf]
                    Grad = param.rho * w**2 / 2 / np.pi / param.c
                    Lrad = 1j*8 * param.rho * w / 3 / np.pi**(1.5) * Avt[-1]**(-0.5)
                    Zrad = Grad + Lrad

                    if objtmp.child_wvg is None:
                        A, B, C, D, dum1 = ChainMatrix(Avt, lvt, freq, param, meth)
                        objtmp.A = A
                        objtmp.B = B
                        objtmp.C = C
                        objtmp.D = D
                        objtmp.Zin = (D * Zrad - B) / (-C * Zrad + A)
                        if loc[kf] > 0 and kw == 0:
                            param.lg = 0.03
                            param.Ag0 = 0.4e-4
                            Zg = 12 * param.mu * param.lg**3 / param.Ag0**3 + \
                            0.875 * param.rho / 2 / param.Ag0**2 + \
                            1j*freq * 2 * np.pi * param.rho * param.lg / param.Ag0
                            k_tmp = int(loc[kf])
                            aup = Avt[k_tmp::-1]
                            adown = Avt[k_tmp+1:]
                            lup = lvt[k_tmp::-1]
                            ldown = lvt[k_tmp+1:]
                            Aup, Bup, Cup, Dup, _ = ChainMatrix(aup, lup,
                                                                freq, param, meth)
                            Adown, Bdown, Cdown, Ddown, _ = ChainMatrix(adown,
                                                                        ldown,
                                                                        freq,
                                                                        param,
                                                                        meth)
                            Tf_front = 1 / (Cdown * Zrad + Ddown)
                            Z_front = (Adown * Zrad + Bdown) / (Cdown * Zrad + Ddown)
                            Z_back = (Aup * Zg + Bup) / (Cup * Zg + Dup)
                            Hf_cstr[:, kf] = Tf_front * Z_back / (Z_front + Z_back)
                    else:
                        if type(objtmp.child_point) is int:
                            objtmp.child_point = [objtmp.child_point]
                        kn_list = [x-1 for x in objtmp.child_point]
                        
                        if objtmp.anabranch_wvg is None:
                            child = objtmp.child_wvg
                            if not isinstance(child, list):
                                child = [child]
                            if len(kn_list) > 1:
                                idx = np.argsort(kn_list)[::-1]
                                child = [child[x] for x in idx]
                                kn_list = [kn_list[x] for x in idx]
                                
                            kn_list.insert(0, len(Avt))
                            if loc[kf] <= 0:
                                for n_wvg, k_wvg in enumerate(kn_list[:-1]):
                                    if n_wvg == 0:
                                        _, _, _, _, Tf = ChainMatrix(Avt[kn_list[n_wvg+1]:k_wvg],
                                                                     lvt[kn_list[n_wvg+1]:k_wvg],
                                                                     freq, param, meth)
                                    else:
                                        _, _, _, _, Tf = ChainMatrix(Avt[kn_list[n_wvg+1]:k_wvg],
                                                                     lvt[kn_list[n_wvg+1]:k_wvg],
                                                                     freq, param, meth, Tf)
                                    
                                    Acoup = np.ones((1, 1, len(Zrad)), dtype='complex')
                                    Bcoup = np.zeros((1, 1, len(Zrad)), dtype='complex')
                                    Ccoup = -1 / child[n_wvg].Zin
                                    Ccoup = Ccoup.reshape(1, 1, -1)
                                    Tn = np.concatenate((np.concatenate((Acoup, Bcoup), 1),
                                                         np.concatenate((Ccoup, Acoup), 1)),
                                                        0)
                                    Tf = ProdMat3D(Tf, Tn)
                                A, _, C, _, _ = ChainMatrix(Avt[:kn_list[-1]-1], lvt[:kn_list[-1]-1],
                                                            freq, param, meth, Tf)
                            else:
                                param.lg = 0.03
                                param.Ag0 = 0.4e-4
                                Zg = 12 * param.mu * param.lg**3 / param.Ag0**3 + \
                                0.875 * param.rho / 2 / param.Ag0**2 + \
                                1j*freq * 2 * np.pi * param.rho * param.lg / param.Ag0
                                k_tmp = int(loc[kf])
                                if loc[kf] < kn:
                                    _, _, _, _, Tf = ChainMatrix(Avt[kn:], lvt[kn:],
                                                                 freq, param, meth)
                                    Acoup = np.ones((1, 1, len(Zrad)), dtype='complex')
                                    Bcoup = np.zeros((1, 1, len(Zrad)), dtype='complex')
                                    Ccoup = -1 / child.Zin
                                    Ccoup = Ccoup.reshape(1, 1, -1)
                                    Tn = np.concatenate((np.concatenate((Acoup, Bcoup), 1),
                                                         np.concatenate((Ccoup, Acoup), 1)),
                                                        0)
                                    Tf = ProdMat3D(Tf, Tn)

                                    aup = Avt[k_tmp::-1]
                                    adown = Avt[k_tmp+1:kn]
                                    lup = lvt[k_tmp::-1]
                                    ldown = lvt[k_tmp+1:kn]
                                    Aup, Bup, Cup, Dup, _ = ChainMatrix(aup, lup,
                                                                        freq, param, meth)
                                    Adown, Bdown, Cdown, Ddown, _ = ChainMatrix(adown,
                                                                                ldown,
                                                                                freq,
                                                                                param,
                                                                                meth,
                                                                                Tf)
                                    Tf_front = 1 / (Cdown * Zrad + Ddown)
                                    Z_front = (Adown * Zrad + Bdown) / (Cdown * Zrad + Ddown)
                                    Z_back = (Aup * Zg + Bup) / (Cup * Zg + Dup)
                                    Hf_cstr[:, kf] = Tf_front * Z_back / (Z_front + Z_back)

                        else:
                            anabranch = objtmp.anabranch_wvg
                            afTmp = anabranch.area_function.area[:, kf]
                            lfTmp = anabranch.area_function.length[:, kf]
                            A_ana, B_ana, C_ana, D_ana, _ = ChainMatrix(afTmp, lfTmp,
                                                                        freq, param, meth)

                            _, _, _, _, Tf = ChainMatrix(Avt[kn[1]:], lvt[kn[1]:],
                                                         freq, param, meth)
                            Atmp, Btmp, Ctmp, Dtmp, _ = ChainMatrix(Avt[kn[0]-1:kn[1]],
                                                                    lvt[kn[0]-1:kn[1]],
                                                                    freq, param, meth)

                            A_coup = (Atmp * B_ana + A_ana * Btmp) / (Btmp + B_ana)
                            B_coup = (Btmp * B_ana) / (Btmp + B_ana)
                            C_coup = Ctmp + C_ana - (Atmp - A_ana) * (Dtmp - D_ana) / (Btmp + B_ana)
                            D_coup = (Dtmp * B_ana + D_ana * Btmp) / (Btmp + B_ana)
                            Tn_coup = np.zeros((2, 2, lw)) + 1j*np.zeros((2, 2, lw))
                            Tn_coup[0, 0, :] = A_coup
                            Tn_coup[0, 1, :] = B_coup
                            Tn_coup[1, 0, :] = C_coup
                            Tn_coup[1, 1, :] = D_coup
                            Tf = ProdMat3D(Tf, Tn_coup)
                            A, _, C, _, _ = ChainMatrix(Avt[:kn[0]-1], lvt[:kn[0]-1],
                                                        freq, param, meth, Tf)

            Hf = 1 / (-C * Zrad + A)
            transFun[:, kf] = Hf

        self.network_transfer_function = transFun.squeeze()
        self.network_transfer_function_constriction = Hf_cstr.squeeze()
        self.freq = freq

        return transFun, freq

    def plottransferfunction(self, sl=None, hf=None):
        """ plot the transfer function of the waveguide"""

        if hasattr(self, "transfer_function"):
            if self.transfer_function is None:
                print('Warning: No transfer function computed for this waveguide!'
                      ' Please compute the transfer function first')
                return None
            tf = self.transfer_function
            
        if hasattr(self, "network_transfer_function") and isinstance(self, VtNetwork):
            if self.network_transfer_function is None:
                print('Warning: No transfer function computed for this network!'
                      ' Please compute the transfer function first')
                return None
            tf = self.network_transfer_function
            
        freq = self.freq

        return plot_tf(freq, tf, sl, hf)

    def searchchinkandsubglott(self):
        """search if there is a glottal chink or a subglottal tract"""
        nPipe = len(self.waveguide)
        isChink = False
        isSubGlott = False
        idxChink = []
        idxSubGlott = []
        # check for chink or subglottal pressure
        for k in range(nPipe):
            wvg_tmp = self.waveguide[k]
            if hasattr(wvg_tmp, 'chink_length'):
                isChink = True
                idxChink.append(k)
            if hasattr(wvg_tmp, 'connection_pressure_vector '):
                isSubGlott = True
                idxSubGlott.append(k)

        # if idxChink == []:
        #     idxChink = None
        # if idxSubGlott == []:
        #     idxSubGlott = None

        self.whereChink = idxChink
        self.whereSubGlott = idxSubGlott
        self.isChink = isChink
        self.isSubGlott = isSubGlott
        return isChink, isSubGlott, idxChink, idxSubGlott

    def searchoscillators(self):
        """ search for oscillators"""
        nOscill = len(self.oscillators)
        isGlott = False
        isSupOscill = False
        idxGlott = []
        idxSupOscill = []
        # check for chink or subglottal pressure
        for k in range(nOscill):
            oscill_tmp = self.oscillators[k]
            if hasattr(oscill_tmp, 'DC_vector'):
                isGlott = True
                idxGlott.append(k)
            if hasattr(oscill_tmp, 'position'):
                isSupOscill = True
                idxSupOscill.append(k)

        if idxGlott == []:
            idxGlott = None
        if idxSupOscill == []:
            idxSupOscill = None

        self.isGlott = isGlott
        self.isSupOscill = isSupOscill
        self.whereGlott = idxGlott
        self.whereSupOscill = idxSupOscill
        return isGlott, isSupOscill, idxGlott, idxSupOscill

    def computenumtubes(self):
        """returns the number of tubes for each waveguide"""
        nPipe = len(self.waveguide)
        nTubes = np.zeros(nPipe)
        for k in range(nPipe):
            nTubes[k] = self.waveguide[k].area_function.area.shape[0]
            self.waveguide[k].norder = k

        self.number_tubes = nTubes
        return nTubes

    def initoscill(self, numIter):
        """initialization of the oscillators"""
        nOscill = len(self.oscillators)
        for k in range(nOscill):
            oscill_tmp = self.oscillators[k]
            oscill_tmp.mass_position_matrix = np.zeros((2, 2, numIter))
            oscill_tmp.height_vector_output = np.zeros((5, numIter))
            oscill_tmp.mass_matrix = np.zeros((2, 2, numIter))
            oscill_tmp.stiffness_matrix = np.zeros((2, 2, numIter))
            oscill_tmp.damping_matrix = np.zeros((2, 2, numIter))
            oscill_tmp.coupling_stiffness_matrix = np.zeros((2, 2, numIter))

    def esmfmatrix(self, T):
        """Solve acoustic equations along the vocal tract for one time step.
        Structures should be sorted according to the following order :
        1 = oral tract, 2 = nasal tract, n>2 = various cavities.
        If they exist: N-1 = subglottal tract, N = glottal chink."""

        OralTract = self.waveguide[0]
        ot_ta_e = OralTract.time_acoustics.elements
        ot_ta_dt = OralTract.time_acoustics.derivative_terms
        ot_ta_it = OralTract.time_acoustics.integration_terms
        Ps = OralTract.subglottal_pressure
        b_eq = OralTract.glottal_resistance

        nPipe = len(self.waveguide)
        Nx = self.number_tubes.astype(int)

        sgbool = self.isSubGlott
        chbool = self.isChink
        isg = self.whereSubGlott
        ich = self.whereChink

        for k in range(nPipe):
            if hasattr(self.waveguide[k], 'chink_length'):
                Chink = self.waveguide[k]
                chink_ta_e = Chink.time_acoustics.elements
                chink_ta_de = Chink.time_acoustics.derivative_terms
                Hch = -(ot_ta_e.bj[0]+ot_ta_e.Rj[0]+2*ot_ta_e.Lj[0]/T+ot_ta_e.Rcm[0])
                H1_ch = -(chink_ta_e.bj[0] * 2 + ot_ta_e.bj[0] + chink_ta_e.Rj + \
                          ot_ta_e.Rj[0] + 2 * (chink_ta_e.Lj + ot_ta_e.Lj[0]) / T)
            if hasattr(self.waveguide[k], 'connection_pressure_inst'):
                SubGlott = self.waveguide[k]
                sg_ta_e = SubGlott.time_acoustics.elements
                sg_ta_dt = SubGlott.time_acoustics.derivative_terms
                sg_ta_it = SubGlott.time_acoustics.integration_terms
                H1_sg = -(2/T*sg_ta_e.Lj[0]+sg_ta_e.Rj[0]+sg_ta_e.bj[0]+sg_ta_e.Rcm[0])
                Hsg = -(2/T*sg_ta_e.Lj[Nx[k]] + sg_ta_e.Rj[Nx[k]] +
                        sg_ta_e.bj[Nx[k]]+sg_ta_e.Rcp[Nx[k]])
                SubGlott.connection_impedance = Hsg

        nspipe = chbool+sgbool

        if chbool and sgbool:
            Fch = ot_ta_e.bj[0]*(ot_ta_e.Udj[0]+ot_ta_it.V[0])-chink_ta_de.Q[0]+chink_ta_e.Ns[0]
        elif chbool and not sgbool:
            Fch = ot_ta_e.bj[0]*(ot_ta_e.Udj[0]+ot_ta_it.V[0])-Ps-chink_ta_de.Q[0]+chink_ta_e.Ns[0]

        Ft = np.zeros((int(np.sum(Nx+1))-chbool, 1))
        Wont = np.zeros((int(np.sum(Nx+1))-chbool, int(np.sum(Nx+1))-chbool))
        W = None
        idx1Ft = 0

        for k in range(nPipe):
            if k == 0:
                Fj = np.zeros(int(Nx[k]+1))
                ot_ta_it.V[:Nx[k]] = ot_ta_it.Vc-ot_ta_e.Gw*(ot_ta_dt.Qwl-ot_ta_dt.Qwc)
                Fj[1:Nx[k]] = (-ot_ta_e.bj[0:-2]*(ot_ta_e.Udj[:-1] + ot_ta_it.V[:-2]) +
                               ot_ta_e.bj[1:-1]*(ot_ta_e.Udj[1:] +
                                                 ot_ta_it.V[1:-1]) - ot_ta_dt.Q[1:-1] +
                               ot_ta_e.Ns[1:Nx[k]]-ot_ta_e.Ns[2:Nx[k]+1])

                Fj[-1] = (-ot_ta_e.bj[Nx[k]-1]*(ot_ta_e.Udj[Nx[k]-1] + ot_ta_it.V[Nx[k]-1]) +
                          ot_ta_e.bj[Nx[k]]*ot_ta_it.V[Nx[k]] - ot_ta_dt.Q[Nx[k]] +
                          ot_ta_e.Ns[Nx[k]])

                ot_ta_e.Hj[0] = -b_eq - ot_ta_e.bj[0]
                if sgbool:
                    Fj[0] = ot_ta_e.bj[0]*(ot_ta_e.Udj[0]+ot_ta_it.V[0]) - \
                        ot_ta_dt.Q[0]+ot_ta_e.Ns[0]-ot_ta_e.Ns[1]
                else:
                    Fj[0] = ot_ta_e.bj[0]*(ot_ta_e.Udj[0]+ot_ta_it.V[0]) - Ps - \
                        ot_ta_dt.Q[0] + ot_ta_e.Ns[0] - ot_ta_e.Ns[1]
            elif k in ich:

                chink_ta_e.Hj[0] = H1_ch
                Fj = Fch
                Wont[0, -1] = Hch
                Wont[1, -1] = ot_ta_e.bj[0]
                Wont[-1, 1] = ot_ta_e.bj[0]
                Wont[-1, 0] = Hch
            elif k in isg:
                Fj = np.zeros(int(Nx[k]+1))
                sg_ta_it.V[:Nx[k]] = sg_ta_it.Vc - sg_ta_e.Gw * (sg_ta_dt.Qwl -
                                                                 sg_ta_dt.Qwc)
                Fj[1:Nx[k]] = -sg_ta_e.bj[:-2]*(sg_ta_e.Udj[:-1]+sg_ta_it.V[:-2]) + \
                    sg_ta_e.bj[1:-1]*(sg_ta_e.Udj[1:]+sg_ta_it.V[1:-1]) - \
                        sg_ta_dt.Q[1:-1] + sg_ta_e.Ns[1:Nx[k]]-sg_ta_e.Ns[2:Nx[k]+1]
                sg_ta_e.Hj[0] = H1_sg
                sg_ta_e.Hj[-1] = -1
                Fj[0] = sg_ta_e.bj[0]*(sg_ta_e.Udj[0]+sg_ta_e.V[0])-Ps-sg_ta_e.Q[0]+sg_ta_e.Ns[0]-sg_ta_e.Ns[1]
                Fj[-1] = -sg_ta_e.bj[Nx[k]]*(sg_ta_e.Udj[Nx[k]-1]+sg_ta_e.V[Nx[k]-1])-sg_ta_e.Q[Nx[k]]
                Wont[0, -chbool-1] = 1
                Wont[-nspipe-1, 0] = sg_ta_e.bj[Nx[k]-1]
                Wont[-chbool-1, 0] = Hsg
                if chbool:
                    Wont[-3, -1] = sg_ta_e.bj[Nx[k]-1]
                    Wont[-2, -1] = Hsg
                    Wont[-1, -2] = 1
            else:
                PipeTmp = self.waveguide[k]
                Parent = PipeTmp.parent_wvg[0]
                nParent = Parent.norder
                ncoup = PipeTmp.parent_point[0] - 1
                Fj = np.zeros(Nx[k]+1)
                PipeTmp.V[:Nx[k]] = PipeTmp.Vc-PipeTmp.Gw*(PipeTmp.Qwl-PipeTmp.Qwc)
                Fj[1:Nx[k]] = -PipeTmp.bj[:-2]*(PipeTmp.Udj[:-1]+PipeTmp.V[:-2]) + \
                    PipeTmp.bj[1:-1]*(PipeTmp.Udj[1:]+PipeTmp.V[1:-1])-PipeTmp.Q[1:-1] + \
                    PipeTmp.Ns[1:Nx[k]]-PipeTmp.Ns[2:Nx[k]+1]
                Fj[-1] = -PipeTmp.bj[Nx[k]-1]*(PipeTmp.Udj[Nx[k]-1]+PipeTmp.V[Nx[k]-1]) + \
                    PipeTmp.bj[Nx[k]]*PipeTmp.V[Nx[k]]-PipeTmp.Q[Nx[k]]+PipeTmp.Ns[Nx[k]]
                Fj[0] = PipeTmp.bj[0]*(PipeTmp.Udj[0]+PipeTmp.V[0])-Parent.bj[ncoup]*(Parent.Udj[ncoup]+Parent.V[ncoup]) - \
                    PipeTmp.Q[0]+PipeTmp.Ns[0]-PipeTmp.Ns[1]
                PipeTmp.Hj[0] = -(2*(PipeTmp.Lj[0]+Parent.Lj[ncoup])/T+PipeTmp.Rj[0] +
                                PipeTmp.Rcm[0]+Parent.Rj[ncoup]+Parent.Rcp[ncoup]+PipeTmp.bj[0]+Parent.bj[ncoup])
                Hnc = -(Parent.bj[ncoup]+Parent.Rj[ncoup]+2*Parent.Lj[ncoup]/T+Parent.Rcp[ncoup])
                Wont[ncoup+(nParent-1)*np.sum(Nx[0:nParent]+1), np.sum(Nx[1:k-1]+1)] = Hnc
                Wont[np.sum(Nx[:k-1]+1), ncoup+(nParent-1)*np.sum(Nx[:nParent]+1)] = Hnc
                Wont[np.sum(Nx[:k-1]+1), ncoup+(nParent-1)*np.sum(Nx[:nParent]+1)-1] = Parent.bj[ncoup]
                Wont[ncoup-1+(nParent-1)*np.sum(Nx[:nParent]+1), np.sum(Nx[:k-1]+1)] = Parent.bj[ncoup]
                if PipeTmp.twin_wvg is not None: # If there is a twin pipe
                    Wont[np.sum(Nx[:k-1]+1), np.sum(Nx[:PipeTmp.twin_wvg-1]+1)] = Hnc
                if len(PipeTmp.parent_wvg) > 1:
                    Parent = PipeTmp.parent_wvg[1]
                    brg = PipeTmp.parent_point[1] - 1
                    nParent = Parent.norder
                    NN = Nx[k]
                    Fj[-1] = -PipeTmp.bj[NN]*(PipeTmp.Udj[NN]+PipeTmp.V[NN])+Parent.bj[brg+1]*(Parent.Udj[brg+1]+
                      Parent.V[brg+1])-PipeTmp.Q[NN+1]+PipeTmp.Ns[Nx[k]]
                    PipeTmp.Hj[NN+1] = -(PipeTmp.bj[NN]+Parent.bj[brg+1]+2/T*(PipeTmp.Lj[NN]+
                              Parent.Lj[brg+1])+PipeTmp.Rj[NN]+PipeTmp.Rcp[NN]+Parent.Rj[brg+1]+Parent.Rcm[brg+1])
                    Hcp1 = -(Parent.bj[brg+1]+Parent.Rj[brg+1]+Parent.Rcm[brg+1]+2*Parent.Lj[brg+1]/T)
                    Wont[brg+(nParent-1)*np.sum(Nx[:nParent]+1), np.sum(Nx[:k-1]+1)+NN] = Hcp1
                    Wont[np.sum(Nx[:k-1]+1)+NN, brg+(nParent-1)*np.sum(Nx[:nParent]+1)] = Hcp1
                    Wont[np.sum(Nx[:k-1]+1)+NN, brg+1+(nParent-1)*np.sum(Nx[:nParent]+1)] = Parent.bj[brg+1]
                    Wont[brg+1+(nParent-1)*np.sum(Nx[:nParent]+1), np.sum(Nx[:k-1]+1)+NN] = Parent.bj[brg+1]

            if k in ich:
                Ft[-1] = Fch
                Wmat = H1_ch.reshape(-1, 1)
                if W is None:
                    W = Wmat[:]
                else:
                    W1 = np.hstack((W, np.zeros((W.shape[0], Wmat.shape[1]))))
                    W2 = np.hstack((np.zeros((Wmat.shape[0], W.shape[1])), Wmat))
                    W = np.vstack((W1, W2))
            else:
                idx2Ft = idx1Ft + len(Fj)
                Ft[idx1Ft:idx2Ft, 0] = Fj
                Wmat = np.diag(self.waveguide[k].time_acoustics.elements.Hj)
                bd = np.diag(self.waveguide[k].time_acoustics.elements.bj[0:-1])
                Wmat[:-1, 1:] += bd
                Wmat[1:, :-1] += bd
                if k == isg:
                    Wmat[-2, -1] = 0

                if W is None:
                    W = Wmat[:]
                else:
                    W1 = np.hstack((W, np.zeros((W.shape[0], Wmat.shape[1]))))
                    W2 = np.hstack((np.zeros((Wmat.shape[0], W.shape[1])), Wmat))
                    W = np.vstack((W1, W2))
            idx1Ft += idx2Ft + 1

        esmfMtx = Wont+W
        self.esmf_matrix = esmfMtx
        self.force_vector = Ft
        return esmfMtx, Ft

    def esmfmtxsolver(self, bool_op, T):
        """solve the esmf matrix"""

        Ft = self.force_vector
        Wont = self.esmf_matrix
        OralTract = self.waveguide[0]
        ot_ta_e = OralTract.time_acoustics.elements
        sgbool = self.isSubGlott
        chbool = self.isChink
        nspipe = chbool+sgbool
        if chbool:
            Hch = -(ot_ta_e.bj[0]+ot_ta_e.Rj[0]+2*ot_ta_e.Lj[0]/T+ot_ta_e.Rcm[0])
        isg = self.whereSubGlott
        Uch = []
        po = []
        a_eq = OralTract.glottal_bernoulli

        # check for chink or subglottal pressure
        for k in range(len(self.waveguide)):
            wvg_tmp = self.waveguide[k]
            if hasattr(wvg_tmp, 'chink_length'):
                Chink = wvg_tmp
            if hasattr(wvg_tmp, 'connection_pressure_inst'):
                SubGlott = wvg_tmp
                Hsg = SubGlott.connection_impedance

        if bool_op:
            Ug = 0 # if contact, airflow is null
            # To be used with a self-oscillating model of the vocal folds
            Ft2 = Ft[1:]
            Wont2 = Wont[1:, 1:]
            Ut = np.linalg.solve(Wont2, Ft2)#linsolve(Wont2,Ft2,opts2);
            if chbool:
                Uch = Ut[-1]
            if sgbool:
                po = Ut[-1-chbool]
        else:
            GSF = np.linalg.solve(Wont, Ft)  # rearrange the system to solve Ug
            F11 = GSF[0][0]
            GSi = np.linalg.inv(Wont)
            a2 = -a_eq*GSi[0, 0]
            if a2 != 0:
                a = solve_pol_2(a2, 1, -F11)
            else:                
                a = F11
            Ug = np.max([a, 0]) # If the solution is negative, keep 0.
            Ft2 = Ft[1:]
            if Ug != 0:
                Ft2[0] = Ft2[0] - ot_ta_e.bj[0] * Ug
                if chbool:
                    Ft2[-1] += - Hch * Ug
                if sgbool:
                    Ft2[-1-nspipe] += -SubGlott.time_acoustics.elements.bj(self.numer_tubes[isg]) * Ug
                    Ft2[-1-chbool] += -Hsg * Ug
            Wont2 = Wont[1:, 1:]
            Ut = np.linalg.solve(Wont2, Ft2)
            if chbool:
                Uch = Ut[-1]
            if sgbool:
                po = Ut[-1-chbool]

        OralTract.glottal_flow_inst = Ug
        if chbool:
            Chink.glottal_flow_inst = Uch
        if sgbool:
            SubGlott.connection_pressure_inst = po
        self.flow_inst = Ut.squeeze()
        return Ut, Ug, Uch, po

    def updateacoustics(self, Const):
        """update the acoustic terms in the network"""
        """May be put in the acoustics class ?????"""

        nPipe = len(self.waveguide)
        Nx = self.number_tubes.astype(int)

        chbool = self.isChink
        isg = self.whereSubGlott
        if chbool:
            ich = self.whereChink[0]
        else:
            ich = -1
        T = Const.T
        Srad = T / 2 * Const.S * np.pi * np.sqrt(np.pi) / Const.rho

        Ut = self.flow_inst
        Uch = 0
        Ug = self.waveguide[0].glottal_flow_inst
        if chbool:
            Uch = self.waveguide[ich].glottal_flow_inst

        for k in range(nPipe): # Store U values in different pipes
            wvg_tmp = self.waveguide[k]
            if k == 0:
                OralTract = wvg_tmp
                ot_ta_e = OralTract.time_acoustics.elements
                ot_ta_dt = OralTract.time_acoustics.derivative_terms
                wvg_tmp.time_acoustics.flow_time[0] = wvg_tmp.glottal_flow_inst
                wvg_tmp.time_acoustics.flow_time[1:Nx[0]+1] = Ut[:Nx[0]]
            elif k == isg:
                wvg_tmp.time_acoustics.flow_time = Ut[np.sum(Nx[:k-1])+k-1:np.sum(Nx[:k])+k-2]
                wvg_tmp.time_acoustics.flow_time[Nx[k]] = Ug+Uch
                SubGlott = wvg_tmp
                sg_ta_e = SubGlott.time_acoustics.elements
                sg_ta_dt = SubGlott.time_acoustics.derivative_terms
            elif k == ich:
                wvg_tmp.time_acoustics.flow_time = Uch
            else:
                wvg_tmp.time_acoustics.flow_time = Ut[np.sum(Nx[:k-1])+k-1:np.sum(Nx[:k])+k-1]

        Lgl = OralTract.glottal_inductance + ot_ta_e.Lj[0]

        for k in range(nPipe):
            Pt = np.zeros(Nx[k]+1)
            wvg_tmp = self.waveguide[k]
            ta_e = wvg_tmp.time_acoustics.elements
            ta_dt = wvg_tmp.time_acoustics.derivative_terms
            ta_it = wvg_tmp.time_acoustics.integration_terms
            ch = []
            child = wvg_tmp.child_wvg
            if child is not None:
                pos_ch = wvg_tmp.child_point - 1
                for kch in range(len(child)):
                    ch[kch] = child[kch].norder

            if k == 0:
                ot_ta_dt.Q[0] = 4*Lgl/T * Ug + 4/T*ot_ta_e.Lj[0]*Uch - ot_ta_dt.Q[0]
            elif k == ich:
                Chink = wvg_tmp
                Chink = self.waveguide[k]
                chink_ta_e = Chink.time_acoustics.elements
                chink_ta_dt = Chink.time_acoustics.derivative_terms
                chink_ta_it = Chink.time_acoustics.integration_terms
                Lch = chink_ta_e.Lj
                chink_ta_dt.Q[0] = 4*(Lch+ot_ta_e.Lj[0])/T*Uch+4/T*ot_ta_e.Lj[0]*Ug-chink_ta_dt.Q[0]
                Pt = chink_ta_e.bj[0]*(Ug + Uch -
                                       OralTract.time_acoustics.flow_time[1]+
                                       chink_ta_e.Udj+chink_ta_it.V[:-1])
                Chink.time_acoustics.pressure_time = Pt
                chink_ta_it.Vc = 4/T*chink_ta_e.Cj*Pt-chink_ta_it.Vc
                u3 = chink_ta_e.Gw * (Pt + chink_ta_dt.Qwl - chink_ta_dt.Qwc)
                chink_ta_dt.Qwc = 2 * chink_ta_e.wc * u3 + chink_ta_dt.Qwc
                chink_ta_dt.Qwl = 2 * chink_ta_e.wl * u3 - chink_ta_dt.Qwl
            elif k == isg:
                sg_ta_dt.Q[0] = 4*(sg_ta_e.Lj[0])/T * SubGlott.time_acoustics.flow_time[0] - sg_ta_dt.Q[0]
            else:
                Parent = wvg_tmp.parent_wvg[0]
                ncoup = wvg_tmp.parent_point[0] - 1
                pr_ta_e = Parent.time_acoustics.elements

                if wvg_tmp.twin_wvg is not None:
                    Twin = wvg_tmp.twin_wvg
                    ta_dt.Q[0] = 4*(ta_e.Lj[0]+pr_ta_e.Lj[ncoup])/T*wvg_tmp.time_acoustics.flow_time[0] + \
                    4*pr_ta_e.Lj[ncoup]/T*(Parent.time_acoustics.flow_time[ncoup+1] + Twin.time_acoustics.flow_time[0]) - ta_dt.Q[0]
                else:
                    ta_dt.Q[0] = 4*(ta_e.Lj[0]+pr_ta_e.Lj[ncoup])/T*wvg_tmp.time_acoustics.flow_time[0] + \
                    4*pr_ta_e.Lj[ncoup]/T*Parent.time_acoustics.flow_time[ncoup+1] - ta_dt.Q[0]


            if k != ich:
                Pt[:-1] = ta_e.bj[:-1]*(wvg_tmp.time_acoustics.flow_time[:-1] -
                                        wvg_tmp.time_acoustics.flow_time[1:] +
                                        ta_e.Udj + ta_it.V[:-1])
                if k == 0:
                    Pt[0] = ta_e.bj[0]*(Ug + Uch - wvg_tmp.time_acoustics.flow_time[1] +
                                        ta_e.Udj[0] + ta_it.V[0])
                ta_dt.Q[1:-1] = 4*(ta_e.Lj[:-1] + \
                     ta_e.Lj[1:])/T * wvg_tmp.time_acoustics.flow_time[1:-1] - \
                    ta_dt.Q[1:-1]
                if ch != []:
                    for Kq in range(len(np.unique(pos_ch))):
                        ncoup = pos_ch[Kq]
                        sumarray = 0
                        idx = ch[pos_ch == ncoup]
                        if idx != []:
                            for kidx in range(len(idx)):
                                xtmp = self.waveguide[idx[kidx]].time_acoustics.flow_time[0]
                                sumarray += xtmp

                        ta_dt.Qnc[Kq] = 4*(ta_e.Lj[ncoup]+ta_e.Lj[ncoup+1])/T*wvg_tmp.time_acoustics.flow_time[ncoup+1] + \
                        4/T*ta_e.Lj[ncoup]*np.sum(sumarray)-ta_dt.Qnc[Kq]
                        ta_dt.Q[ncoup+1] = ta_dt.Qnc[Kq]
                        Pt[ncoup] = ta_e.bj[ncoup]*(wvg_tmp.time_acoustics.flow_time[ncoup]-
                          wvg_tmp.time_acoustics.flow_time[ncoup+1]-np.sum(sumarray)+ta_e.Udj[ncoup]+ta_it.V[ncoup])

                if wvg_tmp.anabranch_wvg is not None:
                    Anabranch = wvg_tmp.anabranch_wvg
                    brg = Anabranch.parent_point[1] - 1
                    ta_dt.Qnc[-1] = 4*(ta_e.Lj[brg]+ta_e.Lj[brg+1])/T*wvg_tmp.time_acoustics.flow_time[brg+1] + \
                    4/T*ta_e.Lj[brg+1]*Anabranch.time_acoustics.flow_time[-1] - ta_dt.Qnc[-1]
                    ta_dt.Q[brg+1] = ta_dt.Qnc[-1]
                    Pt[brg+1] = ta_e.bj[brg+1]*(wvg_tmp.time_acoustics.flow_time[brg+1] -
                                                wvg_tmp.time_acoustics.flow_time[brg+2] +
                      Anabranch.time_acoustics.flow_time[-1] + ta_e.Udj[brg+1] + ta_it.V[brg+1])

                wvg_tmp.time_acoustics.pressure_time[:Nx[k]] = Pt[:-1]
                ta_it.Vc = 4/T*ta_e.Cj*Pt[:-1]-ta_it.Vc
                u3 = ta_e.Gw*(Pt[:-1]+ta_dt.Qwl-ta_dt.Qwc)
                ta_dt.Qwc = 2*ta_e.wc*u3+ta_dt.Qwc
                ta_dt.Qwl = 2*ta_e.wl*u3-ta_dt.Qwl

                if k == 0:
                    ta_dt.Q[Nx[k]] = 4*ta_e.Lj[-1]/T*wvg_tmp.time_acoustics.flow_time[Nx[k]]-ta_dt.Q[Nx[k]]
                if k != 0:
                    if len(wvg_tmp.parent_wvg) > 1:
                        brg = Anabranch.parent_point[1] - 1
                        Anabranch = wvg_tmp.anabranch_wvg
                        ta_dt.Q[Nx[k]] = 4/T*((ta_e.Lj[-1] +
                                               Anabranch.time_acoustics.elements.Lj[brg+1])*wvg_tmp.time_acoustics.flow_time[Nx[k]] +
                                 Anabranch.time_acoustics.elements.Lj[brg+1]*Anabranch.time_acoustics.flow_time[brg+1])-ta_dt.Q[Nx[k]]
                    else:
                        ta_dt.Q[Nx[k]] = 4*ta_e.Lj[-1]/T*wvg_tmp.time_acoustics.flow_time[Nx[k]]-ta_dt.Q[Nx[k]]

                if k != isg:
                    Pt[Nx[k]] = ta_e.bj[Nx[k]]*(wvg_tmp.time_acoustics.flow_time[Nx[k]] + ta_it.V[Nx[k]])
                else:
                    Pt[Nx[k]] = wvg_tmp.connection_pressure_inst
                wvg_tmp.time_acoustics.pressure_time[Nx[k]] = Pt[Nx[k]]
                cstTmp = np.sqrt(wvg_tmp.area_function.area[-1, Const.k_iter])
                ta_it.V[Nx[k]] = -2 * Srad * cstTmp * Pt[Nx[k]] + ta_it.V[Nx[k]]
            else:
                wvg_tmp.time_acoustics.pressure_time = OralTract.time_acoustics.pressure_time[0]

    def initnetwork(self):
        """ Initialisation of the derivative and integration terms
        Nx is the number of tubelets of the considered pipe"""

        nPipe = len(self.waveguide)
        posrad = []

        for k in range(nPipe):
            wvg_tmp = self.waveguide[k]
            wvg_tmp.initacoustics()
            wvg_tmp.time_acoustics.initderiv()

            if wvg_tmp.radiation:
                posrad.append(k)

        if posrad == []:
            posrad = None
        self.radiation_position = posrad

    def writeoutputmatrix(self, k):
        """update the acoustic matrix at the end of iteration"""


        nPipe = len(self.waveguide)
        for kPipe in range(nPipe):
            wvg_tmp = self.waveguide[kPipe]
            wvg_tmp.time_acoustics.pressure_time_matrix[:, k] = wvg_tmp.time_acoustics.pressure_time
            wvg_tmp.time_acoustics.flow_time_matrix[:, k] = wvg_tmp.time_acoustics.flow_time
            if kPipe == 0:
                wvg_tmp.glottal_flow_vector[k] = wvg_tmp.glottal_flow_inst
                wvg_tmp.reynolds_vector[k] = wvg_tmp.reynolds_inst
            elif kPipe == self.whereChink:
                    wvg_tmp.glottal_flow_vector[k] = wvg_tmp.glottal_flow_inst


        nOscill = len(self.oscillators)
        for kOscill in range(nOscill):
            oscill_tmp = self.oscillators[kOscill]
            oscill_tmp.mass_position_matrix[:, :, k] = oscill_tmp.mass_position
            hVec = np.append(oscill_tmp.height_vector, oscill_tmp.separation_height)

            oscill_tmp.height_vector_output[:, k] = hVec

            # \
            #     [[oscill_tmp.height_vector],[ oscill_tmp.separation_height]]
            oscill_tmp.mass_matrix[:, :, k] = oscill_tmp.mass
            oscill_tmp.stiffness_matrix[:, :, k] = oscill_tmp.stiffness
            oscill_tmp.damping_matrix[:, :, k] = oscill_tmp.damping
            oscill_tmp.coupling_stiffness_matrix[:, :, k] = oscill_tmp.coupling_stiffness
            if kOscill == self.whereGlott:
                oscill_tmp.DC_vector[k] = oscill_tmp.DC_flow

    def outputresample(self, fso, fsi):
        """resamples the output parameters"""
        if fso >= fsi:
            print('Warning: the output frequency should be less than the input frequency')
            pass
        else:
            npts = int(len(self.pressure_radiated)*fso/fsi)
            self.pressure_radiated = ssg.resample(self.pressure_radiated, npts)
            self.subglottal_control = ssg.resample(self.subglottal_control, npts)
            self.simulation_frequency = int(fso)
            nPipe = len(self.waveguide)
            for kPipe in range(nPipe):
                wvg_tmp = self.waveguide[kPipe]
                ptmp = wvg_tmp.time_acoustics.pressure_time_matrix
                utmp = wvg_tmp.time_acoustics.flow_time_matrix
                ptmp = ssg.resample(ptmp, npts, axis=1)
                utmp = ssg.resample(utmp, npts, axis=1)
                wvg_tmp.pressure_time_matrix = ptmp
                wvg_tmp.flow_time_matrix = utmp
                if kPipe == 0:
                    wvg_tmp.glottal_flow_vector = ssg.resample(wvg_tmp.glottal_flow_vector, npts)
                    wvg_tmp.reynolds_vector = ssg.resample(wvg_tmp.reynolds_vector, npts)
                    wvg_tmp.area_function.area = ssg.resample(wvg_tmp.area_function.area,
                                                         npts, axis=1)
                    wvg_tmp.area_function.length = ssg.resample(wvg_tmp.area_function.length,
                                                         npts, axis=1)
                elif kPipe in self.whereChink:
                    wvg_tmp.glottal_flow_vector = ssg.resample(wvg_tmp.glottal_flow_vector,
                                                               npts)
                    wvg_tmp.area_function.area = ssg.resample(wvg_tmp.area_function.area.squeeze(),
                                                         npts)
                    wvg_tmp.area_function.length = ssg.resample(wvg_tmp.area_function.length.squeeze(),
                                                         npts)

            nOscill = len(self.oscillators)
            for kOscill in range(nOscill):
               oscill_tmp = self.oscillators[kOscill]
               oscill_tmp.height_vector_output = ssg.resample(oscill_tmp.height_vector_output, npts, axis=1)
               oscill_tmp.fundamental_frequency = ssg.resample(oscill_tmp.fundamental_frequency, npts)
               oscill_tmp.low_frequency_abduction = ssg.resample(oscill_tmp.low_frequency_abduction, npts)
               oscill_tmp.partial_abduction = ssg.resample(oscill_tmp.partial_abduction, npts)
               oscill_tmp.oscillation_factor = ssg.resample(oscill_tmp.oscillation_factor, npts)
               oscill_tmp.output_length = ssg.resample(oscill_tmp.output_length, npts)
               if kOscill == self.whereGlott:
                   oscill_tmp.DC_vector = ssg.resample(oscill_tmp.DC_vector, npts)


    def esmfsynthesis(self, Const=None):
        """ Time-domain speech synthesis. The vocal tract is modeled as a waveguide
        network. The acoustic source is a 2x2 mass model of the
        vocal folds."""
        # import warnings
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        if Const is None:
            Const = timestruct()
        chbool, sgbool, ich, isg = self.searchchinkandsubglott()
        isGlott, isSupOscill, idxGlott, idxSupOscill = self.searchoscillators()
        if isSupOscill:
            nSupOscill = len(idxSupOscill)
        ##### Special objects
        OralTract = self.waveguide[0]
        numIter = OralTract.area_function.area.shape[1]
        if isGlott:
            objGlottis = self.oscillators[idxGlott[0]]
        else:
            if self.input_area is None or len(self.input_area) < numIter \
                    or self.abduction is None or len(self.abduction) < numIter:
                raise Exception('Glottal opening parameters not set properly for parametric glottis based simulation. Use self-oscillations instead');
            else:
                glottalArea = self.input_area
                ag0 = self.abduction
                objGlottis = Glottis()
                objGlottis.partial_abduction = ag0 / objGlottis.max_opening

        if sgbool:
            SubGlottTract = self.waveguide[isg[0]]

        if chbool:
            if isGlott:
                Chink = self.waveguide[ich[0]]
            else:
                self.waveguide[ich] = []
                isGlott = 0
                chbool = 0
                aChink = 0
        else:
            aChink = 0
            if isGlott:
                objGlottis.partial_abduction = np.zeros(numIter)
        Nx = self.computenumtubes()
        nPipe = len(Nx)
        self.initnetwork()
        Uk1 = 0

        ############# Check potential unrealistic pitch values and correct them
        objGlottis.fundamental_frequency[objGlottis.fundamental_frequency <= 60] = 60

        armin = Const.amin
        rho = Const.rho
        co_mu = Const.mu

        ########### Definition of all the constants used during resolution.
        T = Const.T
        fs = Const.fs

        kwb = 0
        if OralTract.actualVT is None:
            OralTract.actualVT = np.arange(OralTract.area_function.shape[0]).astype(int)

        ac = np.min(OralTract.area_function.area[OralTract.actualVT, :],
                    axis=0)
        ic = np.argmin(OralTract.area_function.area,
                       axis=0)
        inputArea = OralTract.area_function.area[0, :]
        # if length(inparam(1).Psub) ~= numIter; inparam(1).Psub = mean(inparam(1).Psub)*ones(size(tvec)); end
        # if length(inparam(1).fo) ~= numIter; inparam(1).fo = 100*ones(size(tvec)); end

        ########## Initialization of glottal parameters
        if isGlott:
            objGlottis.mass_position = objGlottis.rest_position
            objGlottis.mass_position_nm1 = objGlottis.rest_position
            objGlottis.mass_position_nm2 = objGlottis.rest_position
            if sgbool:
                pstmp = 0
                objGlottis.up_height = powtr(SubGlottTract.area_function[-1, :], 1.8, 1.2, 0)
            else:
                asg = 3.1314e-05
                h0 = powtr(asg, 1.8, 1.2, 0)
                objGlottis.up_height = h0 * np.ones(numIter)
                del asg, h0

            objGlottis.down_height = powtr(inputArea, 1.8, 1.2, 0)
            if objGlottis.low_frequency_abduction is None:
                objGlottis.low_frequency_abduction = np.zeros(numIter)

        if not hasattr(Const, 'fso'):
            Const.fso = fs
        Fric_Amp = Const.namp
        Reyn = 0
        fny = fs/2 # Nyquist frequency

        if isSupOscill:
            for ksup in range(nSupOscill):
                objSup = self.oscillators[idxSupOscill[ksup]]
                objwvg = objSup.waveguide
                objSup.mass_position = objSup.rest_position
                objSup.mass_position_nm1 = objSup.rest_position
                objSup.mass_position_nm2 = objSup.rest_position
                objSup.down_height = powtr(objwvg.area_function[objSup.position-1, :], 1.8, 1.2, 0)
                objSup.up_height = powtr(objwvg.area_function[objSup.position+1, :], 1.8, 1.2, 0)


        ########## FIR 1 TO CHECK
        if np.any(ic >= 38):
            if Const.filt == 'fir1':
                Const.hld = ssg.firwin(int(Const.ordl*2), float(1000/fny))
                Const.hld2 = ssg.firwin(1, 1000/fny, pass_zero='highpass')

       ################ Resolution of the system at every

        if objGlottis.partial_abduction is not None:
            lchk = objGlottis.partial_abduction**2
        else:
            lchk = np.zeros(numIter)

        lchk[lchk <= armin] = armin
        lchk[lchk >= 1-armin] = 1-armin
        lgvec = objGlottis.length*(1-lchk)
        objGlottis.output_length = lgvec

        if not isGlott:
            lc = np.zeros(ac.shape)
            for k in range(len(ic)):
                lc[k] = OralTract.length_function[ic[k], k]

            Ag2 = 1/(glottalArea**2);
            Ac2 = 1/(ac**2)
            rv_sum = (12*lgvec*objGlottis.width*Ag2*np.sqrt(Ag2)+8*np.pi*lc*Ac2)*co_mu
            rk_sum = 1.38*rho*(Ac2+Ag2)
            udc = (-rv_sum + np.sqrt(rv_sum*rv_sum + 4*rk_sum*OralTract.subglottal_pressure))/(2*rk_sum)
            udc[np.isnan(udc)] = 0
            rgvec = 12*co_mu*lgvec**2*objGlottis.width/(glottalArea**3)

        self.pressure_radiated = np.zeros(numIter)
        self.initoscill(numIter)

        for k in tqdm(range(numIter)):
            Const.k_iter = k
            objGlottis.length = lgvec[k]
            ain = inputArea[k]
            lc = OralTract.area_function.length[ic[k], k]
            if (not sgbool) or (k == 0):
                pstmp = self.subglottal_control[k]
            if chbool:
                aChink = Chink.area_function.area[0, k]
            objGlottis.upstream_pressure = pstmp
            if isSupOscill:
                for ksup in range(nSupOscill):
                    objSup = self.oscillators[idxSupOscill[ksup]]
                    objwvg = objSup.waveguide
                    objSup.length = powtr(objSup.low_frequency_abduction[k],
                                          1.8, 1.2, 0)
                    dlt = powtr(objSup.length,
                                1.8, 0.2, 1)*1e2
                    ain_tongue = objSup.down_height*dlt
                    ldtt = objwvg.length_function[objSup.position, k]
                    if objSup.model == 'ishi':
                        Qmass = objSup.initial_mass[0, 1]/objSup.initial_mass[0, 0]
                        x1tt = ldtt/(1+Qmass) # 1st mass
                        x2tt = ldtt-1e-11 # 2nd mass
                        x3tt = ldtt
                    else:
                        x1tt = 2e-4
                        x2tt = ldtt-2*x1tt
                        x3tt = ldtt

                    objSup.x_position = [0, x1tt, x2tt, x3tt]
                    objSup.updateimpedance(0, ain_tongue, Const)
                    hsii = objSup.sepration_height
                    objwvg.area_function[objSup.position, k] = max(1e-8,
                                                                   powtr(hsii,
                                                                         1.8,
                                                                         1.2,
                                                                         1))

                ###### Thing to be fixed
                if OralTract.anabranch_wvg is not None:
                    lat = OralTract.anabranch_wvg[0]
                    cp = OralTract.child_wvg

                    ii = np.argwhere(cp[0, :] == lat)
                    af_main[cp[1, ii[0]]:cp[1, ii[1]]] += af[lat].A[:, k]
            if isGlott:
                objGlottis.updateimpedance(Const, aChink, ain, ac[k], lc)
                Lg = objGlottis.inductance
                Udc = objGlottis.DC_flow
                Aglot = objGlottis.area
            else:
                objGlottis.bernoulli = 0
                objGlottis.inductance = 0
                objGlottis.resistance = rgvec[k]
                Udc = udc[k]
                objGlottis.DC_flow = Udc
                Aglot = glottalArea[k]

            # kpc = 100*((k)/(numIter-1))
            # if (kpc >= 10*kwb and Const.dispcomp):
            #     print('Completion: ' + str(10*kwb) + ' %')
            #     kwb += 1
            for kpipe in range(nPipe): # Electric components of each pipe
                wvg_tmp = self.waveguide[kpipe]

                if k == 0:
                    uim1 = np.zeros(int(Nx[kpipe]))
                else:
                    if kpipe > 0:
                        wvg_parent = wvg_tmp.parent_wvg[0]
                        Aglot = wvg_parent.area_function.area[wvg_tmp.parent_point[0] - 1, k]
                    uim1 = wvg_tmp.time_acoustics.flow_time_matrix[:, k-1]

                isSub = wvg_tmp.check_instance('SubGlottalTract')
                wvg_tmp.time_acoustics.acou2elec(Const, uim1, Aglot, isSub)
                namp = Fric_Amp
                if kpipe == 0:
                    if isGlott and chbool and namp > 0:
                        Reyn = wvg_tmp.computereynolds(Udc, Const)

                    ### Check if there is a supraglottal oscillator
                    if isSupOscill:
                        for ksup in range(nSupOscill):
                            objSup = self.oscillators[idxSupOscill[ksup]]
                            ptt = objSup.position
                            wvg_tmp.Lj[ptt] = 0
                            wvg_tmp.Hj[ptt:ptt+1] = -2*(wvg_tmp.Lj[ptt-1:ptt]+wvg_tmp.Lj[ptt:ptt+1])/T \
                            -wvg_tmp.Rj[ptt-1:ptt]-wvg_tmp.Rj[ptt:ptt+1]- \
                            wvg_tmp.bj[ptt-1:ptt]-wvg_tmp.bj[ptt:ptt+1]- \
                            wvg_tmp.Rcm[ptt-1:ptt]-wvg_tmp.Rcp[ptt:ptt+1]

        #             if (~Const.unst && Const.osc_tg)
        #                 wvg_tmp.Lj(ptt) = 0;
        #                 wvg_tmp.Hj[ptt:ptt+1] = -2*(wvg_tmp.Lj[ptt-1:ptt]+wvg_tmp.Lj[ptt:ptt+1])/T ...
        #                     -wvg_tmp.Rj[ptt-1:ptt]-wvg_tmp.Rj[ptt:ptt+1]- ...
        #                     wvg_tmp.bj[ptt-1:ptt]-wvg_tmp.bj[ptt:ptt+1]- ...
        #                     wvg_tmp.Rcm[ptt-1:ptt]-wvg_tmp.Rcp[ptt:ptt+1];
        #             end
                else:
                    namp = 0

                if (Reyn < Const.Rec or hasattr(wvg_tmp, 'chink_length')):
                    namp = 0

                if hasattr(wvg_tmp, 'chink_length'):
                    wvg_tmp.time_acoustics.elements.Lj *= 2
                    wvg_tmp.time_acoustics.elements.Lj *= 2 / (Const.rmlt / 4)
                if isGlott and chbool and namp:
                    wvg_tmp.computenoise(Const, namp, Udc, Aglot)
            if isGlott or isSupOscill:
                for k_oscill in range(len(self.oscillators)):
                    self.oscillators[k_oscill].updateparam(Const)
            else:
                objGlottis.isContact = (glottalArea <= armin)
                if isSupOscill:
                    for k_oscill in range(len(self.oscillators)):
                        self.oscillators[k_oscill].updateparam(Const)

            ot_ta_e = OralTract.time_acoustics.elements
            OralTract.subglottal_pressure = pstmp
            OralTract.glottal_resistance = np.sum(objGlottis.resistance) + \
                ot_ta_e.Rj[0] + 2 * (np.sum(Lg) + ot_ta_e.Lj[0]) / T + ot_ta_e.Rcm[0]
            OralTract.glottal_inductance = np.sum(objGlottis.inductance)
            OralTract.glottal_bernoulli = np.sum(objGlottis.bernoulli)
            self.esmfmatrix(Const.T)
            try:
                self.esmfmtxsolver(objGlottis.isContact, Const.T)
            except:
                break
            self.updateacoustics(Const)
            OralTract.updatesup(Const)
            if sgbool:
                pstmp = SubGlottTract.pressure_time[-2]

            ##### Radiation
            sumarray = 0

            for krad in range(len(self.radiation_position)):
                sumarray += self.waveguide[self.radiation_position[krad]].time_acoustics.flow_time[-1]

            Um = np.sum(sumarray)
            self.pressure_radiated[k] = Um - Uk1
            Uk1 = Um

            if isGlott:
                objGlottis.inst_flow = OralTract.glottal_flow_inst
                if objGlottis.model == 'smooth':
                    objGlottis.appliedforce(Const)
                    objGlottis.updatemassposition(Const)
                else:
                    objGlottis.updatemassishiflan(Const)

            if isSupOscill:
                for ksup in range(len(idxSupOscill)):
                    objSup = self.oscillators[idxSupOscill[ksup]]
                    objwvg = objSup.waveguide
                    objSup.updatepressure(objwvg, Const)

                    if objSup.model == 'smooth':
                        objSup.appliedforce(Const)
                        objSup.updatemassposition(Const)
                    else:
                        objSup.updatemassishiflan(Const)
                    if objSup.num_oscillators == 1:
                        objSup.mass_position[0, :] = 0
                        objSup.mass_position_nm1[0, :] = 0

            self.writeoutputmatrix(k)

        return self.pressure_radiated

    def inputtrim(self, start_time=0, end_time=None):
        sr = self.simulation_frequency
        
        psub = self.subglottal_control
        MOT = self.waveguide[0]
        nb_tubes, nb_frame = MOT.area_function.area.shape
        phl = self.phonetic_label
        inst = self.phonetic_instant
        
        if end_time is not None:
            end_idx = int(end_time * sr)
        else:
            end_idx = nb_frame
        start_idx = int(start_time * sr)
        
        if end_idx < nb_frame:
            self.subglottal_control = self.subglottal_control[start_idx:end_idx]
            for wvg in self.waveguide:
                wvg.area_function.area = wvg.area_function.area[:, start_idx:end_idx]
                wvg.area_function.length = wvg.area_function.length[:, start_idx:end_idx]
            for osc in self.oscillators:
                osc.fundamental_frequency = osc.fundamental_frequency[start_idx:end_idx]
                osc.partial_abduction = osc.partial_abduction[start_idx:end_idx]
                osc.oscillation_factor = osc.oscillation_factor[start_idx:end_idx]
            idx = [x for x in range(len(phl)) if inst[x, 0] < end_time and 
                   inst[x, 0] > start_time]
            self.phonetic_label = [self.phonetic_label[x] for x in idx]
            self.phonetic_instant = self.phonetic_instant[idx,:]

    def plotinputparameters(self):
        """plot the input parameters of the network"""

        sr = self.simulation_frequency
        chbool, sgbool, ich, isg = self.searchchinkandsubglott()
        psub = self.subglottal_control
        MOT = self.waveguide[0]
        ac = np.min(MOT.area_function.area, 0) * 1e4
        nFrame = len(ac)
        tvec = np.arange(nFrame) / sr
        fo = self.oscillators[0].fundamental_frequency

        # Plot Input parameters
        h_handle = openfig()
        ax = subplot_param(311, tvec, ac,
                           self.phonetic_label,
                           self.phonetic_instant,
                           [-1, 1e3],
                           title='Miniminal cross-section area',
                           ylabel='Area (cm\\textsuperscript{2})',
                           xlabel=None,
                           limx=None,
                           ax_share=None)
        
        osc_fact = self.oscillators[0].oscillation_factor
        addplot(ax, tvec, osc_fact,
                    color=(0, 0.498, 0))

        if chbool:
            Chink = self.waveguide[ich[0]]
            addplot(ax, tvec, np.squeeze(Chink.area_function.area * 1e4),
                    color='r')

        ax2 = subplot_param(312, tvec, fo,
                            self.phonetic_label,
                           self.phonetic_instant,
                           [0, 100 * np.ceil(max(fo) / 100)],
                           title='Fundamental frequency',
                           ylabel='$F_0$ (Hz)',
                           xlabel=None,
                           limx=None,
                           ax_share=ax)

        ax3 = subplot_param(313, tvec, psub,
                            self.phonetic_label,
                           self.phonetic_instant,
                           [0, 100 * np.ceil(max(self.subglottal_control) / 100)],
                           title='Subglottal Pressure',
                           ylabel='$P_{Sub}$ (Pa)',
                           xlabel='Time (s)',
                           limx = [0, tvec[-1]],
                           ax_share=ax)

        #h_handle.show()

        return h_handle

    def plotoutputparameters(self):
        """plot the simulated output parameters"""

        sr = self.simulation_frequency
        chbool, sgbool, ich, isg = self.searchchinkandsubglott()
        MOT = self.waveguide[0]

        P = MOT.pressure_time_matrix
        Ug = MOT.glottal_flow_vector
        nTubes, nFrame = MOT.area_function.area.shape
        tvec = np.arange(nFrame) / sr

        Gl = self.oscillators[0]
        lg = Gl.output_length

        sig_mass_1 = Gl.height_vector_output[1, :]
        sig_mass_2 = Gl.height_vector_output[2, :]
        openarea = np.array([min(sig_mass_1[x], sig_mass_2[x]) for x in range(len(sig_mass_1))])
        openarea[openarea <= 0] = 0
        sig_mass_1[sig_mass_1 <= 0] = 0
        sig_mass_2[sig_mass_2 <= 0] = 0
        area1 = (sig_mass_1 * lg) * 1e4
        area2 = (sig_mass_2 * lg) * 1e4
        openarea = (openarea * lg) * 1e4

        if chbool:
            Chink = self.waveguide[ich[0]]
            chinkArea = Chink.area_function.area
            area1 = area1 + chinkArea
            area2 = area2 + chinkArea
            openarea = openarea + chinkArea

        instPoral = P[int(1 * nTubes / 4), :]
        lwin = int(0.1 * sr)
        # Poral = np.abs(sm.nonparametric.lowess(instPoral,
                                        # np.arange(len(instPoral)),
                                        #        frac=lwin/len(instPoral),
                                        #        return_sorted=False))
        # Plot output parameters
        h_handle = openfig()
        ax = subplot_param(211, tvec, Ug,
                           self.phonetic_label,
                           self.phonetic_instant,
                           [0, max(Ug) * 1.2],
                           title='Glottal flow',
                           ylabel='Glottal flow (m\\textsuperscript{3}/s)',
                           xlabel=None,
                           limx=None,
                           ax_share=None)

        if chbool:
            Uch = Chink.flow_time_matrix.squeeze()
            Ut = Ug + Uch
            maxy = max(Ut) * 1.2
            addplot(ax, tvec, Uch, color=[0, 0.498, 0], lst='--')
            addplot(ax, tvec, Ut, 'r')

        ax2 = subplot_param(212, tvec, area1,
                           self.phonetic_label,
                           self.phonetic_instant,
                           [0, max(openarea) * 1.2],
                           title='Glottal opening area',
                           ylabel='Glottal opening area (cm\\textsuperscript{2})',
                           xlabel='Time (s)',
                           limx = [0, tvec[-1]],
                           ax_share=ax)
        addplot(ax2, tvec, area1, color='b')
        addplot(ax2, tvec, area2, 'r')

        # ax3 = subplot_param(313, tvec, Poral,
        #             self.phonetic_label,
        #            self.phonetic_instant,
        #            [0, max(Poral) * 1.2],
        #            title='Intraoral Pressure',
        #            ylabel='$P_{\\mathrm{Oral}}$ (Pa)',
        #            xlabel='Time (s)',
        #            limx = [0, tvec[-1]],
        #            ax_share=ax)

        # h_handle.show()

        return h_handle
