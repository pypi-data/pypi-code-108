# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 09:55:08 2020

@author: benjamin
"""

import json
import numpy as np
import numpy.matlib as npmt
from numpy.linalg import multi_dot
import scipy.signal as ssg
from .utils import ChainMatrix, mat2column, esprit, symmetricifft
# from .signaltools import esprit, symmetricifft
from ._set import struct, timestruct
from .vtnetwork import VtNetwork
from .areafunction import AreaFunction
from .acoustics import AcousticsTime, AcousticsFreq
#from .plottools import plot_tf


class VtWaveguide(VtNetwork):
    """ Class for analyzing and make operations on vocal tract cavities """
    #### Properties
    area_function = None # area function
    formants = None # formants
    child_wvg = None # name of the child waveguide object
    parent_wvg = None # name of the parent waveguide object
    twin_wvg = None # name of the twin waveguide object
    anabranch_wvg = None # name of the anabranch waveguide object
    child_point = None # point of connection where the child waveguide is connected
    parent_point = None # point of connection of the parent waveguide
    radiation = None # Boolean. True if the waveguide radiates (e.g. oral tract).
    transfer_function = None # transfer function of the waveguide
    transfer_function_constriction = None
    chain_matrix = None
    chain_matrix_derivative = None
    input_impedance = None
    freq = None # frequency vector of the transfer function
    actualVT = None
    velopharyngeal_port = 0
    velum_area = 0
    norder = 1
    time_acoustics = AcousticsTime()
    freq_acoustics = AcousticsFreq()

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            if key == 'area_function':
                self.area_function.parent = self

    def computetransferfunction(self, param=None, meth='tmm', loc=-1):
        """ Compute the transfer function and the impulse response of the vocal tract
        defined by area function Avt and lvt. The resonance frequencies are
        estimated via ESPRIT. They are the pole frequencies of the impulse
        response of the vocal tract. The constant values are stocked in
        param.
        The transfer function is computed using the chain paradigm by Sondhi and
        Schroeter (A hybrid time-frequency domain articulatory speech
        synthesizer, IEEE TASSP, 1987)"""

        if param is None:
            param = timestruct()
        if not hasattr(param, 'rho'):
            param.rho = 1.204/1000
        if not hasattr(param, 'c'):
            param.c = 343.4
        if not hasattr(param, 'mu'):
            param.mu = 1.9831e-5
        if not hasattr(param, 'a'):
            param.a = 130 * np.pi
        if not hasattr(param, 'b'):
            param.b = (30 * np.pi)**2
        if not hasattr(param, 'c1'):
            param.c1 = 4
        if not hasattr(param, 'wo2'):
            param.wo2 = (406 * np.pi)**2
        if not hasattr(param, 'c1n'):
            param.c1n = 72
        if not hasattr(param, 'heat_cond'):
            param.heat_cond = 0.0034
        if not hasattr(param, 'specific_heat'):
            param.specific_heat = 160
        if not hasattr(param, 'adiabatic'):
            param.adiabatic = 1.4
        if not hasattr(param, 'wallyield'):
            param.wallyield = True
        if not hasattr(param, 'loss'):
            param.loss = True

        param.freq[param.freq <= 1e-11] = 1e-11
        freq = param.freq.reshape(-1)
        af = self.area_function.area # to make it from the lips to the glottis
        lf = self.area_function.length # to make it from the lips to the glottis
        if af is None or lf is None:
            print('Warning: the waveguide instance has no area function!')
            return None
        w = 2 * np.pi * freq # angular frequency
        lw = len(w)

        if meth.lower() == 'cmp':
            param.alp = np.sqrt(1j*w * param.c1)
            param.bet = 1j*w * param.wo2 / ((1j*w + param.a) * 1j*w + param.b) + param.alp
            param.gam = np.sqrt((param.alp + 1j*w) / (param.bet + 1j*w))
            param.sig = param.gam * (param.bet + 1j*w)

        af_size = af.shape
        if len(af_size) == 1:
            nframe = 1
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
        else:
            nframe = af_size[1]
        transFun = np.zeros((lw, nframe)) + 1j*np.zeros((lw, nframe))
        Hf_cstr = np.zeros((lw, nframe)) + 1j*np.zeros((lw, nframe))

        if isinstance(loc, int) and nframe > 1:
            loc = loc * np.ones(nframe)
        if isinstance(loc, int):
            loc = [loc]

        for kf in range(nframe):
            Avt = af[:, kf]
            lvt = lf[:, kf]
            Grad = param.rho * w**2 / 2. / np.pi / param.c_s
            Jrad = 8 * param.rho * w / 3. / np.pi**(1.5) * Avt[-1]**(-0.5)
            Zrad = Grad + 1j*Jrad

            A, _, C, _, _ = ChainMatrix(Avt, lvt, freq, param, meth)

            Hf = 1 / (-C * Zrad + A)
            transFun[:, kf] = Hf
            Hf_cstr[:, kf] = Hf

            if loc[kf] > 0:
                param.lg = 0.03
                param.Ag0 = 0.4e-4
                Zg = 12 * param.mu * param.lg**3 / param.Ag0**3 + \
                0.875 * param.rho / 2 / param.Ag0**2 + \
                1j*freq * 2 * np.pi * param.rho * param.lg / param.Ag0
                k_tmp = loc[kf]
                aup = Avt[k_tmp::-1]
                adown = Avt[k_tmp+1:]
                lup = lvt[k_tmp::-1]
                ldown = lvt[k_tmp+1:]
                Aup, Bup, Cup, Dup, _ = ChainMatrix(aup, lup, freq, param, meth)
                Adown, Bdown, Cdown, Ddown, _ = ChainMatrix(adown, ldown, freq, param, meth)
                Tf_front = 1 / (Cdown * Zrad + Ddown)
                Z_front = (Adown * Zrad + Bdown) / (Cdown * Zrad + Ddown)
                Z_back = (Aup * Zg + Bup) / (Cup * Zg + Dup)
                Hf_cstr[:, kf] = Tf_front * Z_back / (Z_front + Z_back)

        self.transfer_function = np.squeeze(transFun)
        self.transfer_function_constriction = np.squeeze(Hf_cstr)
        self.freq = freq
        return transFun, freq

    def computeformants(self, param=None):
        """ Computes the resonance frequencies of the VT_Waveguide object.
         Use the ESPRIT method on the impulse response to estimate the poles of
         the transfer function"""

        if param is None:
            param = struct()
        if self.transfer_function is None:
            self.computetransferfunction(self, param)
        tf_size = self.transfer_function.shape
        if len(tf_size) == 1:
            nfreq = tf_size[0]
            nframe = 1
            self.transfer_function = self.transfer_function.reshape(-1, 1)
        else:
            nfreq, nframe = tf_size

        K = 2 * (param.nform + 2)
        fmt = np.empty((param.nform, nframe))
        fmt[:] = np.nan
        for kf in range(nframe):
            Hf = self.transfer_function[:, kf]
            if np.isinf(Hf[0]) or np.isnan(Hf[0]):
                Hf[0] = Hf[1]
            df = self.freq[2] - self.freq[1]
            x = symmetricifft(Hf)
            x = len(x) * x
            himp = x[:int(np.ceil(0.5 * len(x)))]
            himp -= np.mean(himp)
            fk = esprit(himp, df * 2 * (nfreq - 1), K)
            fmt[:, kf] = fk[:param.nform]
        self.formants = fmt
        return fmt

    def computenoise(self, Const, namp, Udc, aglot):
        """ compute the noise component inside the waveguide"""

        k = Const.k_iter
        af = self.area_function.area
        nTube, nFrame = af.shape
        A2o = np.append(aglot, af[:, k].squeeze())

        Nsk = np.zeros(nTube + 1)
        if self.actualVT is None:
            self.actualVT = np.arange(nTube).astype(int)
        actVT = np.array(self.actualVT)
        actVT2 = np.append(actVT, actVT[-1] + 1)
        idxAct = actVT2.reshape(-1, 1)

        ac = min(af[actVT.astype(int), k])
        ic = np.argmin(af[actVT.astype(int), k]).squeeze()
        fny = Const.fs/2
        if namp != 0:
            W = self.time_acoustics.noise_matrix
            dk = 20
            if k - dk >= 0:
                idxStart = k-dk
            else:
                idxStart = 0
            if k+dk < nFrame:
                idxEnd = k + dk
            else:
                idxEnd = nFrame - 1
            
            bb = np.arange(idxStart, idxEnd+1)

            if ic >= 38:
                hl = Const.hld
            else:
                fpeak = min(0.3*np.sqrt(np.pi)*Udc/(ac*np.sqrt(ac)), fny*0.999)
                ordl = 9+2*(38-ic-1)
                hl = ssg.firwin(int(ordl), float(fpeak/fny))

            Wb = W[idxAct, bb]

            if ic >= 38:
                Wb = ssg.lfilter(Const.hld2, 1, Wb)
            else:
                Wb = ssg.lfilter(hl, 1, Wb)
            Wb = Wb / np.std(Wb)
            phik = namp * (self.reynolds_inst**2 - Const.Rec**2)
            WbTmp = phik * (Wb[idxAct, round(len(bb) / 2)].squeeze())

            Nsk[actVT2] = WbTmp / (A2o[idxAct].squeeze()**2.5) * Udc**3
            if isinstance(self, MainOralTract) and Const.dynterm:
                self.time_acoustics.elements.Udj[ic+1] = Const.beta * phik
            Nsk[0] = 0
            if len(Nsk) > len(actVT2):
                Nsk[len(actVT2):] *= 0
        else:
            Nsk = np.zeros(nTube+1)
        self.time_acoustics.elements.Ns = Nsk

    def exportaf2json(self, fileName):
        """export the area function in a .JSON file"""

        af = self.area_function.area
        lf = self.area_function.length

        if hasattr(self, 'velopharyngeal_port'):
            vpo = self.velopharyngeal_port
        else:
            vpo = 0
        if hasattr(self, 'velum_area'):
            vArea = self.velum_area
        else:
            vArea = np.zeros_like(af)

        if len(af.shape) == 1:
            nFrame = 0
            nTubes = len(af)
        else:
            nTubes, nFrame = af.shape

        idx = fileName.find('.json')
        if idx >= 0:
            fileName = fileName[:idx]

        if isinstance(vpo, (float, int)) and nFrame > 0:
            vpo = vpo * np.ones(nFrame)

        if isinstance(vArea, (float, int)) and nFrame > 0:
            vArea = vArea * np.ones((nTubes, nFrame))

        if isinstance(vArea, (float, int)) and nFrame > 0:
            vArea = npmt.repmat(vArea.reshape(-1, 1), 1, nFrame)

        if nFrame == 0:
            fTmp = fileName + '.json'
            nFrame = 1
            vpo = [vpo]
            vArea = vArea * np.ones((nTubes, 1))
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
        for kF in range(nFrame):
            if nFrame > 1:
                fTmp = fileName + '_' + '%.5d' %(kF+1) + '.json'
            else:
                fTmp = fileName + '.json'

            idjson = {}
            idjson['VelumOpeningInCm'] = np.sqrt(vpo[kF]) * 1e2
            idjson['frameId'] = fTmp
            idjson['tubes'] = []
            for kT in range(nTubes):
                idjson['tubes'].append({
                    'area' : af[kT, kF] * 1e4,
                    'velumArea' : vArea[kT, kF] * 1e4,
                    'x' : lf[kT, kF] * 1e2
                })
        with open(fTmp, 'w') as f:
            json.dump(idjson, f)

    def initacoustics(self):
        """ Initialisation of the derivative and integration terms
        Nx is the number of tubelets of the considered pipe"""

        self.time_acoustics = AcousticsTime()
        stmp = self.area_function.area.shape
        nTube = stmp[0]
        if len(stmp) == 1:
            nFrame = 1
        else:
            nFrame = stmp[1]

        P = np.zeros((nTube+1, nFrame))
        U = np.zeros((nTube+1, nFrame))
        np.random.seed(100)
        W = np.random.randn(nTube+1, nFrame)

        if isinstance(self, GlottalChink):
            P = np.zeros((1, nFrame))
            U = np.zeros((1, nFrame))
            self.glottal_flow_vector = np.zeros(nFrame)
            self.glottal_flow_inst = 0

        if isinstance(self, MainOralTract):
            self.glottal_flow_vector = np.zeros(nFrame)
            self.glottal_flow_inst = 0
            self.reynolds_inst = 0
            self.reynolds_vector = np.zeros(nFrame)

        if isinstance(self, SubGlottalTract):
            self.connection_pressure_inst = 0
            self.connection_pressure_vector = np.zeros(nFrame)

        self.time_acoustics.pressure_time_matrix = P
        self.time_acoustics.flow_time_matrix = U
        self.time_acoustics.pressure_time = P[:, 0]
        self.time_acoustics.flow_time = U[:, 0]
        self.time_acoustics.parent = self

        if self.actualVT is None:
            self.actualVT = np.arange(nTube).astype(int)
        actVT = np.array(self.actualVT).astype(int)
        if nTube > max(actVT):
            W[max(actVT):, :] *= 0
        self.time_acoustics.noise_matrix = W

    def formant2af(self, formant_target, param=None):
        """Dynamic acoustic-to-articulatory inversion of oral vowels using the sensitivity
        matrix technique"""

        if param is None:
            param = struct()
        if not hasattr(param, 'length_var'):
            param.length_var = True
        if not hasattr(param, 'lips_var'):
            param.lips_var = True
        if not hasattr(param, 'area_weight'):
            param.area_weight = 0
        if not hasattr(param, 'length_weight'):
            param.length_weight = 0
        if not hasattr(param, 'threshold'):
            param.threshold = 1
        if not hasattr(param, 'laxNumIter'):
            param.maxNumIter = 1000
        if not hasattr(param, 'psi'):
            param.psi = 0.5
        if not hasattr(param, 'tf_method'):
            param.tf_method = 'cmp'
        if not hasattr(param, 'verbose'):
            param.verbose = True

        dl = param.length_var
        norm_lips = True - param.lips_var
        carea = param.area_weight
        cleng = param.length_weight
        cpot = param.potential_weight
        thresh = param.threshold
        Nbreak = param.maxNumIter
        # Acceleration term. psii > 1 => enhance speed,
        # but risk of unstability,
        # psii < 1 to make sure we are in the linearity domain...
        psii = param.psi
        err_form = np.zeros(int(Nbreak))

        # size of the acoustic vector
        shapeForm = formant_target.shape
        nFormant = shapeForm[0]
        if len(shapeForm) == 1:
            nFrame = 1
        else:
            nFrame = shapeForm[1]

        # get initial solutions
        a0 = self.area_function.area
        l0 = self.area_function.length
        shapeAf = a0.shape
        nTube = shapeAf[0]
        if len(shapeAf) == 1:
            nFrame = 1
            a0 = a0.reshape((nTube, nFrame), order='F')
            l0 = l0.reshape((nTube, nFrame), order='F')
        else:
            nFrame = shapeAf[1]

        # Vector must be column vectors
        a0vec = mat2column(a0)
        l0vec = mat2column(l0)
        ftargvec = mat2column(formant_target)

        # Initalization
        count_loop = 1
        ak = a0vec[:]
        lk = l0vec[:]
        lkp1 = lk[:]
        akp1mat = a0[:]
        lkp1mat = l0[:]

        if nFrame == 1:
            carea = 0
            cleng = 0
            # if only one frame, no kinetic energy constraints (static configuration)

        self.freq_acoustics.parent = self
        self.computetransferfunction(param, meth=param.tf_method)
        fk = self.computeformants(param)
        Sn_x = self.freq_acoustics.areasensitivityfunction(fk, param)
        if dl:
            Sn_x_l = self.freq_acoustics.lengthsensitivityfunction(fk, param)

            if nFrame > 1:
                Sn_x_l = Sn_x_l.reshape((nTube * nFrame, nFrame * nFormant),
                                        'F')
            else:
                Sn_x_l = np.squeeze(Sn_x_l)

        if nFrame > 1:
            Sn_x = Sn_x.reshape((nTube * nFrame, nFrame * nFormant),
                                'F')
        else:
            Sn_x = np.squeeze(Sn_x)

        fnest = mat2column(fk)

        currErr = np.mean(abs(fnest-ftargvec)/fnest)*100
        if param.verbose:
            print('Cost function is ' + '%.4f' %currErr)
        err_form = [currErr]


        while (err_form[-1] >= thresh and count_loop <= Nbreak):

            zn = (ftargvec-fnest)/fnest # Delta_f vector
            alph = np.real(multi_dot([zn.T, Sn_x.T, Sn_x, zn])/ \
                           multi_dot([multi_dot([Sn_x.T, Sn_x, zn]).T,
                                      Sn_x.T, Sn_x, zn])) * psii

            if dl:
                alphl = np.real(multi_dot([zn.T, Sn_x_l.T, Sn_x_l, zn])/ \
                           multi_dot([multi_dot([Sn_x_l.T, Sn_x_l, zn]).T,
                                      Sn_x_l.T, Sn_x_l, zn])) * psii

            dak = alph[0][0] * (Sn_x @ zn) # perturbation of area function, if unconstrained
            dakD = 0
            daikD = 0 # initalization of constraint terms

            if carea != 0: # if kinetic energy constraint on area function is enabled
                dpdamat = np.zeros_like(akp1mat)
                dpmat = np.diff(akp1mat, 1, 1)
                dpdamat[:, 0] = -2 * dpmat[:, 0]
                dpdamat[:, 1:-1] = 2 * dpmat[:, :-1] - 2 * dpmat[:, 1:]
                dpdamat[:, -1] = 2 * dpmat[:, -1]
                dpdamat2 = dpdamat*npmt.repmat(np.sum(abs(dpdamat)**2, 0), nTube, 1)
                dakD = mat2column(dpdamat2)

            if cpot != 0: # if potential energy constraint is enabled
                aRep = npmt.repmat(np.sum(abs((a0-akp1mat)/a0)**2, 0),
                                   nTube, 1)
                daikD_mat = 2 * (a0 - akp1mat) / a0 * aRep
                daikD = mat2column(daikD_mat)

            akp1 = abs(ak+np.diag(ak)*((1-carea)*dak+carea*dakD+cpot*daikD))
        #     Ind = find(akp1<=0.1e-4)
        #     akp1(Ind) = exp(log(ak(Ind)) + log(dak(Ind)+1))
            akp1mat = akp1.reshape((nTube, nFrame), order='F')
            if norm_lips:
                akp1mat[-1, :] = a0[-1, :]
                # if lip aperture is imposed

            akp1 = mat2column(akp1mat)
            ak = akp1[:]

            if dl: # Compute the new length function
                dlkD = 0
                dlikD = 0
                if cleng != 0:
                    dldamat = np.zeros(lkp1mat.shape)
                    dlmat = np.diff(np.cumsum(lkp1mat, 0), 1, 1)
                    dldamat[:, 0] = -2 * dlmat[:, 0]
                    dldamat[:, 1:-1] = 2 * dlmat[:, :-1] - 2 * dlmat[:, 1:]
                    dldamat[:, -1] = 2 * dlmat[:, -1]
                    dldamat2 = dldamat*npmt.repmat(np.sum(abs(dldamat)**2, 0), nTube, 1)
                    dlkD = mat2column(dldamat2) # np.reshape(dldamat2, (np.size(dldamat2, 1)))

                if cpot != 0:
                    lRep = npmt.repmat(np.sum(abs((l0-lkp1mat))**2, 0),
                                       nTube, 1)
                    dlikD_mat = 2 * (l0 - lkp1mat) * lRep
                    dlikD = mat2column(dlikD_mat)

                xi_vec = ((1 - cleng) * (Sn_x_l @ zn) + cleng * dlkD + cpot * dlikD) * alphl[0][0]
                argdiag = np.squeeze(1 / (1 + xi_vec))
                Xi_mat = np.diag(argdiag)
                lkp1 = abs(Xi_mat @ lk.reshape(-1, 1))
                lkp1[lkp1 * 40 > 0.2] = 0.2 / 40
                lk = lkp1[:]

            lkp1mat = lkp1.reshape((nTube, nFrame), order='F')

            # Inialization
            self.area_function = AreaFunction('area', akp1mat,
                                              'length', lkp1mat,
                                              'parent', self)
            self.computetransferfunction(param, param.tf_method)
            fk = self.computeformants(param)
            Sn_x = self.freq_acoustics.areasensitivityfunction(fk, param)
            if dl:
                Sn_x_l = self.freq_acoustics.lengthsensitivityfunction(fk, param)
                if nFrame > 1:
                    Sn_x_l = Sn_x_l.reshape((nTube * nFrame, nFrame * nFormant),
                                            'F')
                else:
                    Sn_x_l = np.squeeze(Sn_x_l)

            if nFrame > 1:
                Sn_x = Sn_x.reshape((nTube * nFrame, nFrame * nFormant),
                                    'F')
            else:
                Sn_x = np.squeeze(Sn_x)

            fnest = mat2column(fk)
            count_loop += 1

            currErr = np.mean(abs(fnest - ftargvec) / fnest) * 100
            err_form.append(currErr)
            if param.verbose:
                print('Cost function is ' + '%.4f' %currErr)

        akmat = akp1mat
        lkmat = lkp1mat
        self.area_function = AreaFunction('area', akmat.squeeze(),
                                          'length', lkmat.squeeze(),
                                          'parent', self)
        fnest = fnest.reshape((nFormant, nFrame),
                              order='F')
        Hnest = self.computetransferfunction(param)

        return akmat, lkmat, fnest, Hnest, err_form
    
    
    def check_instance(self, class_type):
        """ check instance """
        return eval('isinstance(self, ' + class_type + ')')

class GlottalChink(VtWaveguide):
    """Class for modeling a glottal chink"""
    glottal_flow_vector = None
    glottal_flow_inst = None
    chink_length = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            if key == 'area_function':
                self.area_function.parent = self

        self.parent_point = [1]
        self.radiation = False


class SubGlottalTract(VtWaveguide):
    """Class for modeling the subglottal tract"""
    connection_pressure_inst = None
    connection_pressure_vector = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            if key == 'area_function':
                self.area_function.parent = self

        self.parent_point = 1
        self.radiation = False

class MainOralTract(VtWaveguide):
    """Class for modeling the main oral tract"""

    #### Instantaneous acoustics
    subglottal_pressure = None
    supraglottal_pressure = None
    glottal_bernoulli = None
    glottal_resistance = None
    glottal_inductance = None
    glottal_flow_inst = None
    chink_flow_inst = 0
    reynolds_inst = None
    Qug = 0

    #### Output acoustic matrix
    subglottal_pressure_vector = None
    supraglottal_pressure_vector = None
    reynolds_vector = None
    glottal_flow_vector = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            if key == 'area_function':
                self.area_function.parent = self

        self.parent_point = 1
        self.parent_wvg = None
        self.radiation = True

    def computereynolds(self, Udc=0, Const=None):
        """Compute the Reynolds number inside the constriction of the waveguide
        defined by a, l."""

        if Const is None:
            Const = timestruct()
        co_mu = Const.mu
        rho = Const.rho
        af = self.area_function.area
        shapeAf = af.shape
        nTube = shapeAf[0]
        if len(shapeAf) == 1:
            nFrame = 1
            af = af.reshape(-1, 1)
        else:
            nFrame = shapeAf[1]
        if hasattr(Const, 'k_iter'):
            a = af[:, Const.k_iter]
        else:
            Const.k_iter = np.array(0, nFrame)
            a = self.area_function

        # find the constriction geometry
        if self.actualVT is None:
            self.actualVT = np.arange(nTube).astype(int)
        actVT = self.actualVT

        Ack = min(a[actVT])
        Reyn = 2*rho/co_mu*Udc/np.sqrt(np.pi*Ack)
        self.reynolds_inst = Reyn
        return Reyn

    def updatesup(self, Const):
        """ Update the glottal upstream pressure"""

        Rj = self.time_acoustics.elements.Rj[0]
        Lj = self.time_acoustics.elements.Lj[0]
        Rcm = self.time_acoustics.elements.Rcm[0]

        Ug = self.glottal_flow_inst
        Uch = self.chink_flow_inst
        currP = self.time_acoustics.pressure_time[0]
        addP = (Rj + 2 / Const.T * Lj + Rcm)
        psup = currP + addP * (Ug + Uch) - self.Qug
        self.Qug = 4 / Const.T * Lj * (Ug + Uch) - self.Qug
        self.supraglottal_pressure = psup
        return psup
