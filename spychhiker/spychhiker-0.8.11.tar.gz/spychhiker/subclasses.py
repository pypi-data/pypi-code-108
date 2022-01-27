# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 15:32:24 2020

@author: benjamin
"""

import numpy as np
import scipy.interpolate as scintp
from .utils import *
import spychhiker.utils as utils
import spychhiker.plottools as plottools
import copy
from .stats import RandomVar, ProsodyParam
from .prosody import Contour

class TimeFreq:

    parent = None
    time_frequency_matrix = None
    time_vector = None
    frequency_vector = None
    window = None
    overlap = None
    nfft = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        return copy.deepcopy(self)

    def interpolate(self, vec_out, axis='time', method='linear'):

        y = self.time_frequency_matrix
        if axis == 'freq':
            vec_in = self.frequency_vector
            axis_num = 0
        elif axis == 'time':
            vec_in = self.time_vector
            axis_num = 1

        f1 = scintp.interp1d(vec_in, y, kind=method, axis=axis_num,
                             fill_value='extrapolate')
        y_out = f1(vec_out)

        self.time_frequency_matrix = y_out
        if axis == 'freq':
            self.frequency_vector = vec_out
        elif axis == 'time':
            self.time_vector = vec_out

    def tfplot(self, dyn=100, norm=False,
               pitch_plot=False, formant_plot=False):

        tvec = np.arange(len(self.parent.signal)) / self.parent.sampling_frequency
        lbl = self.parent.phonetic_labels
        inst = self.parent.phonetic_instants

        Pxx = abs(self.time_frequency_matrix)**2
        if norm:
            Pxx = Pxx / np.max(Pxx)

        fsp = self.frequency_vector
        tsp = self.time_vector
        Pxx = 10*np.log10(Pxx)
        signal = self.parent.signal

        pitch_time_points = []
        pitch_values = []
        formants_time = []
        formants_freq = []

        if pitch_plot:
            if self.parent.pitch is None:
                print('Warning: no pitch found!')
            else:
                pitch_time_points = self.parent.pitch.time_points
                pitch_values = self.parent.pitch.values

        if formant_plot:
            if self.parent.formants is None:
                print('Warning: no formants found!')
            else:
                formants_time = self.parent.formants.time_vector
                formants_freq = self.parent.formants.frequency.T

        return plottools.plot_spec(Pxx, tsp, fsp, dyn, tvec, signal,
              lbl, inst, pitch_plot, pitch_time_points, pitch_values,
              formant_plot, formants_time, formants_freq)

class FreqSig:

    parent = None
    values = None
    frequency_vector = None
    window = None
    nfft = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        return copy.deepcopy(self)

    def freqplot(self, dyn=100, norm=False):

        Pxx = np.abs(self.values)**2
        if norm:
            Pxx = Pxx / np.max(Pxx)
        return plottools.freq_plot(self.frequency_vector, Pxx, dyn)

    def interpolate(self, freq_out, isdB=False, method='linear'):
        y = self.values
        freq_in = self.frequency_vector
        if isdB:
            y = 10*np.log10(np.abs(y))
        else:
            y = np.abs(y)

        f1 = scintp.interp1d(freq_in,y,kind=method,fill_value='extrapolate')
        y_out = f1(freq_out)

        if isdB:
            y_out = 10**(y_out / 20)

        self.values = y_out
        self.frequency_vector = freq_out


class Formants:
    frequency = None
    bandwidth = None
    damping = None
    amplitude = None
    isForm = None
    trajectory = None

    time_vector = None
    parent = None
    stats = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):
        return copy.deepcopy(self)

    def addzeros(self, A):

        freq = self.frequency
        damp = self.damping
        ampl = self.amplitude
        bw = self.bandwidth
        nF, nFrame = freq.shape
        nZ, nF2ch = A.shape
        freqMat = np.vstack((freq[:nF2ch-1,:], np.ones((1,nFrame))))
        freqzero = A @ freqMat

        zeroObj = Formants('parent', self.parent,
        'frequency', freqzero,
        'damping', damp[:nZ,:],
        'bandwidth', bw[:nZ,:],
        'amplitude', ampl[:nZ,:],
        'isForm', False,
        'time_vector', self.time_vector)

        return zeroObj
    
    def getcontour(self):
        
        nb_form = self.frequency.shape[0]
        self.trajectory = []
        for k in range(nb_form):
            trj_tmp = Contour("time_points", self.time_vector, 
                              "values", self.frequency[k,:], 
                              "parent", self)
            self.trajectory.append(trj_tmp)
            
    def update_trajectory(self):
        
        if self.trajectory is not None:
            self.interpolate(self.trajectory[0].time_points)
            self.frequency = []
            for trj in self.trajectory:
                self.frequency.append(trj.values)
                self.time_vector = trj.time_points
            self.frequency = np.array(self.frequency)
    
    def transform(self, sr, *args):

        freq = self.frequency
        damp = self.damping
        tVec = self.time_vector
        nForm, nFrame = freq.shape
        z = np.exp(2 * 1j * np.pi * freq / sr) * np.exp(-damp / sr)
        z_module = np.abs(z)
        z_angle = np.exp(1j * np.angle(z))
        dampcoeff = np.array([1])
        freqcoeff = np.array([1])

        for k in range(0,len(args),2):
            field, argvalue =  args[k:k+2]
            if field.lower() == 'frequency':
                freqcoeff = argvalue
                if isinstance(freqcoeff, (list, tuple, np.ndarray)) is False:
                    freqcoeff = np.array([freqcoeff])
            elif field.lower() == 'damping':
                dampcoeff = argvalue
                if isinstance(dampcoeff, (list, tuple, np.ndarray)) is False:
                    dampcoeff = np.array([dampcoeff])
            else:
                raise ValueError('Atttribute to modify not recognized. Please choose either frequency or damping')

        if len(freqcoeff.shape) == 1:
            if len(dampcoeff.shape) == 1:
                z_new = (z_module**dampcoeff) * (z_angle**argvalue)
            else:
                nForm2ch = dampcoeff.shape[0]
                if nForm2ch > nForm:
                    nForm2ch = nForm
                    idx = list(range(nForm))
                    idx.append(dampcoeff.shape[1])
                    dampcoeff = dampcoeff[:nForm, idx]
                z_new = z
                for kF in range(nFrame):
                    f_pos = damp[:nForm2ch, kF]
                    damp_vec = np.concatenate((f_pos.reshape(-1),1))
                    new_damp = dampcoeff * damp_vec
                    ratio_damp = new_damp / f_pos
                    z_module_tmp = z_module[:nForm2ch, kF]
                    z_angle_tmp = z_angle[:nForm2ch, kF]
                    z_new[:nForm2ch, kF] = (z_module_tmp**ratio_damp) * (z_angle_tmp**freqcoeff)
        else:
            nForm2ch = freqcoeff.shape[0]
            if nForm2ch > nForm:
                nForm2ch = nForm
                idx = list(range(nForm))
                idx.append(freqcoeff.shape[1])
                freqcoeff = freqcoeff[:nForm, idx]

            if len(dampcoeff.shape) == 1:
                ratio_damp = dampcoeff
                isVec = False
            else:
                nDamp2ch = dampcoeff.shape[0]
                if nDamp2ch > nForm:
                    nDamp2ch = nForm
                    idx = list(range(nForm))
                    idx.append(dampcoeff.shape[1])
                    dampcoeff = dampcoeff[:nForm, idx]
                isVec = True

            z_new = z
            for kF in range(nFrame):
                f_pos = freq[:nForm2ch, kF]
                freq_vec = np.append(f_pos, 1)
                new_freq = np.squeeze(freqcoeff @ freq_vec.reshape(-1,1))

                ratio_freq = new_freq / f_pos
                z_module_tmp = z_module[:nForm2ch, kF]
                z_angle_tmp = z_angle[:nForm2ch, kF]
                if isVec:
                    damp_pos = damp[:nForm2ch, kF]
                    damp_vec = np.concatenate((f_pos.reshape(-1),1))
                    new_damp = dampcoeff * damp_vec
                    ratio_damp = new_damp / damp_pos
                z_new[:nForm2ch, kF] = (z_module_tmp**ratio_damp) * (z_angle_tmp**ratio_freq)

        freq_new = np.angle(z_new) / 2 / np.pi * sr
        damp_new = -np.log(abs(z_new)) * sr
        bw_new = damp_new / np.pi

        obj_out = Formants('frequency', freq_new,
                'damping', damp_new,
                'bandwidth', bw_new,
                'amplitude', self.amplitude,
                'time_vector', tVec,
                'parent', self.parent,
                'isForm', self.isForm)
        return obj_out

    def interpolate(self, txx):
        """ Interpolation of formant trajectory along the time axis """
        for attr in ["frequency", "damping", "bandwidth", "amplitude"]:
            f1 = scintp.interp1d(self.time_vector, getattr(self, attr), 
                                 kind='linear', axis=1, 
                                 bounds_error=False, fill_value=0)
            setattr(self, attr, f1(txx))       
        self.time_vector = txx
        self.extrap()
        
    def extrap(self):
        
        nb_formant = self.frequency.shape[0]
        for k in range(nb_formant):
            self.frequency[k,:] = fill_nan_and_zero(self.frequency[k,:])
            self.damping[k,:] = fill_nan_and_zero(self.damping[k,:])
            self.bandwidth[k,:] = fill_nan_and_zero(self.bandwidth[k,:])
            self.amplitude[k,:] = fill_nan_and_zero(self.amplitude[k,:])
        
    def create_spectral_envelope(self, nfft=None):
        
        if nfft is None:
            if hasattr(self.parent, 'sampling_frequency'):
                nfft = 2**nextpow2(self.parent.sampling_frequency)
            else:
                raise ValueError('Parent of formant object is None')
                
        frequency = self.frequency
        damping = self.damping
        sr = self.parent.sampling_frequency
        L = int(nfft / 2 + 1)
        nb_frame = len(self.time_vector)
        
        z_pos = np.exp(2 * np.pi * 1j * frequency / sr) * np.exp(-damping / sr)
        z_whole = np.concatenate((z_pos, np.conj(z_pos)), 0)
        
        spec_envelope = np.zeros((L, nb_frame), dtype='complex')
        
        for k in range(nb_frame):
            fxx, h_curr = z2freqz(1, z_whole[:,k], sr=sr, nfft=nfft)    
            spec_envelope[:,k] = h_curr
            
        self.parent.spectral_envelope = TimeFreq('time_frequency_matrix', spec_envelope,
                                                 'time_vector', self.time_vector,
                                                 'frequency_vector', fxx, 
                                                 'parent', self.parent)

    def get_stats(self, attr='frequency'):
        self.stats = []
        x = getattr(self, attr)
        for k in range(4):
            obj = RandomVar('samples', x[k,:])
            obj.get_stats(50)
            self.stats.append(obj)

    def plotformantspace(self, n1=1, n2=2, h=None):
        print('Plotting formant space')
        if n1 is not None and n2 is not None:
            h, ax1 = plottools.vowel_space(self.frequency, n1=1, n2=2)
        else:
            if self.stats is None:
                self.get_stats()
            return plottools.formantspace(self, subax=[5, 9, 10, 13, 14, 15],
                             h=None, clr='b')

    def compareformantspace(self, objForm):

        h = self.plotformantspace(n1=None, n2=None)
        if objForm.stats is None:
            objForm.get_stats()
        h = plottools.formantspace(objForm, subax=[2, 3, 4, 7, 8, 12],
                              h=h, clr='r', order=2)

    def plotstats(self):
        return plottools.formant_stats(self)

    def comparestats(self, objForm):
        return plottools.formant_stats(self, objForm)

    def comparehull(self, objForm):
        return plottools.hull_compare(self, objForm)
    
class MFCC:
    
    coeff = None
    nb_coeff = None
    time_vector = None
    mel_vector = None
    frequency_vector = None
    power_log = None
    parent = None
    c0 = None
    energy = None
    
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0,nargin,2):
            key, value = args[k:k+2]
            setattr(self, key, value)
        
    def copy(self):
        return copy.deepcopy(self)

    def mfcc2melspectro(self, freq_out=None):
        
        nb_coeff = self.nb_coeff + 1
        coeff = self.coeff[:nb_coeff,:]
        nb_filt = len(self.mel_vector)
        if self.c0 is not None:
            coeff[0,:] = [x for x in self.c0] 
        # basis  = dct(nb_coeff + 1, filter_len=nb_filt-2)[1:,:]
        basis  = dct(nb_coeff, filter_len=nb_filt-2)
        pxx_new = np.linalg.pinv(basis) @ coeff
        
        S_log = TimeFreq('time_vector', self.time_vector, 
                         'frequency_vector', self.mel_vector[1:-1], 
                          'time_frequency_matrix', np.abs(10**(pxx_new/10)),
                          'parent', self.parent)

        self.power_log = pxx_new
        mels_lin = np.linspace(0, self.mel_vector[-1], len(self.mel_vector))
        S_log.interpolate(mels_lin, axis='freq')
        freq_mel = mel2freq(mels_lin)
        S_log.frequency_vector = freq_mel
        freq_lin = np.linspace(0, freq_mel[-1], len(freq_mel) )
        S_log.interpolate(freq_lin, axis='freq')
        if freq_out is not None:
            S_log.interpolate(freq_out, axis='freq')
        S_log.time_frequency_matrix = np.abs(S_log.time_frequency_matrix)
        if self.parent is not None:
            self.parent.spectral_envelope = S_log
    
        return S_log
    
class Speaker:

    mother_tongue = None
    speaker_id = None
    L2 = None
    L2_level = None
    gender = None
    age = None
    utterance = []
    phonemes = []
    formants_stats = None
    pitch_stats = None
    intensity_stats = None
    formants = None
    accent = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0,nargin,2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def get_all_formants(self, attr='utterance', meth=None):
        """ returns formants values of all utterances in one Formant object """

        y = []
        y_bw = []
        list_attr = getattr(self, attr)
        for numk, k in enumerate(list_attr):
            nwin = 512
            novlp = int(nwin * 3 / 4)
            Fr = k.formants
            n_frame = Fr.frequency.shape[1]
            if n_frame > 0:
                if Fr is None:
                    Fr = k.formantestimate(nwin, novlp, ord_filt = 5)
                if meth == 'mean':
                    Fr.frequency = np.nanmean(Fr.frequency, axis=1).reshape(-1,1)
                    Fr.bandwidth = np.nanmean(Fr.bandwidth, axis=1).reshape(-1,1)
                if meth == 'median':
                    Fr.frequency = np.nanmedian(Fr.frequency, axis=1).reshape(-1,1)
                    Fr.bandwidth = np.nanmedian(Fr.bandwidth, axis=1).reshape(-1,1)
                if meth == 'central':
                    Fr.frequency = Fr.frequency[:,int(n_frame/2)].reshape(-1,1)
                    Fr.bandwidth = Fr.bandwidth[:,int(n_frame/2)].reshape(-1,1)
                if numk == 0:
                    y = Fr.frequency
                    y_bw = Fr.bandwidth
                else:
                    y = np.hstack((y, Fr.frequency))
                    y_bw = np.hstack((y_bw, Fr.bandwidth))
            else:
                pass
            
        y, idx = utils.reject_outliers(y)
        y_bw = y_bw[:,idx]            
        self.formants = Formants('frequency', y,
                                 'bandwidth', y_bw,
                                 'parent', self)

    def get_stats(self, attr):

        setattr(self, attr, [])

        for numk, k in enumerate(self.utterance):

            if attr != 'formant_stats':
                if attr == 'pitch_stats':
                    pros_feat = k.getpitch()
                if attr == 'intensity_stats':
                    pros_feat = k.getintensity()
                prmTmp = ProsodyParam('mean', np.nanmean(pros_feat.values))
                prmTmp.median = np.nanmedian(pros_feat.values)
                pros_feat.getcontour()
                cont = pros_feat.contour
                cont.values = pros_feat.values
                cont.getbaselines()
                prmTmp.declination = cont.declination
                prmTmp.span = cont.getpitchspan()
                prmTmp.peak_extent = cont.getnppe()
                prmTmp.local_peak_dynamic = cont.getlpdyn()
            else:
                formants = k.formantestimate(512, 384, ord_filt=5)
                freq = formants.frequency
                t_form = formants.time_vector
                prmTmp = ProsodyParam('mean', np.nanmean(freq, 1),
                                                   'raw_values', freq,
                                                   'span', [],
                                                   'declination', [],
                                                   'peak_extent', [],
                                                   'local_peak_extent', [])
                prmTmp.median = np.nanmedian(freq, 1)
                for k in range(4):
                    cont = Contour('values', freq[k,:].squeeze(),
                                  'time_points', t_form.squeeze())
                    cont.getbaselines()
                    prmTmp.declination.append(cont.declination)
                    prmTmp.span.append(cont.getpitchspan())
                    prmTmp.peak_extent.append(cont.getnppe())
                    prmTmp.local_peak_dynamic.append(cont.getlpdyn())

            getattr(self, attr).append(prmTmp)
