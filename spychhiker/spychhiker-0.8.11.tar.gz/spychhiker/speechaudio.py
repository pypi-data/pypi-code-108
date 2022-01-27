# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:09:32 2020

@author: benjamin
"""

import numpy as np
import scipy
import scipy.signal
from .audiotools import record_to_file
from .subclasses import Formants, FreqSig, TimeFreq, MFCC
from .prosody import Pitch, Intensity
from .utils import *
from .pyxglos import *
import warnings
import statsmodels.api as sm
from librosa.core import lpc
import parselmouth
from .filetools import *
import scipy.stats as sst
import json
import numpy.matlib as npmt
import copy
from .ola import *
from .praattools import *
from .transformtools import (transform_formant, transform_formant_from_dist,
                             sparse_regression, get_pros_modif_factor_from_dist,
                             transform_pitch)

class SpeechAudio:

    signal = None
    sampling_frequency = 1
    phonetic_labels = None
    phonetic_instants = None
    utter_id = None

    time_vector = None
    spectrum = None
    spectrogram = None
    pitch = None
    instantaneous_pitch = None
    maximal_voiced_frequency = None
    voiced_signal = None
    unvoiced_signal = None
    spectral_centroid = None
    spectral_spread = None
    skewness = None
    kurtosis = None
    spectral_envelope = None
    formants = None
    zeros = None
    hnr = None
    voicing_quotient = None
    segments = None
    intensity = None
    mfcc = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):

        return copy.deepcopy(self)

    def computespectrogram(self, nwin=256, win=None, nfft=None, novlp=None):

        if self.sampling_frequency == 1:
            warnings.warn("Warning: the sampling frequency is 1")
        if win is None:
            win = 'hanning'
        if nfft is None:
            nfft = 2**nextpow2(self.sampling_frequency)
        if novlp is None:
            novlp = int(nwin * 3 / 4)

        x = self.signal
        sr = self.sampling_frequency
        nhop = nwin - novlp
        xbuff = buffer(x, nwin, nhop)
        w = window(nwin, win)
        L = int(nfft / 2 + 1)
        fxx = np.arange(L) * sr / nfft

        nFrame = xbuff.shape[1]
        txx = np.arange(0, len(x), nhop) / sr
        txx = txx[:nFrame] + (nwin / 2) / sr

        Sxx = np.zeros((L, nFrame))
        w = np.matlib.repmat(w.reshape(-1,1), 1, nFrame)
        xwin = xbuff * w
        # xwin[xwin==0] = 1e-22
        # xEnv = np.zeros((nfft, nFrame))

        Sxx = np.fft.fft(xwin, n=nfft, axis=0)[:L,:]
        # fxx, txx, Sxx = scipy.signal.spectrogram(self.signal, self.sampling_frequency,
        #                                 win, winLength, novlp, nfft)
        Sxx[Sxx == 0] = np.finfo(type(Sxx[0, 0])).eps
        outputSpectro = TimeFreq('parent', self,
                                 'time_frequency_matrix', Sxx,
                                 'time_vector', txx,
                                 'frequency_vector', fxx,
                                 'window', win,
                                 'overlap', novlp,
                                 'nfft', nfft)

        self.spectrogram = outputSpectro

        return Sxx, fxx, txx

    def computespectrum(self, win='rect', nfft=2048, whole=False):
        N = len(self.signal)
        if win == 'rect':
            w = np.ones(N)
        if win == 'hann':
            w = np.hanning(N)
        if win == 'hamming':
            w = np.hamming(N)

        if self.sampling_frequency == 1:
            warnings.warn("Warning: the sampling frequency is 1")

        sig2fft = self.signal*w
        sp = np.fft.fft(sig2fft, nfft)
        freq = np.fft.fftfreq(nfft, 1/self.sampling_frequency)
        if not whole:
            L = int(nfft/2)
            sp = sp[:L]
            freq = freq[:L]

        outputSpectrum = FreqSig('parent', self,
                                 'values', sp,
                                 'frequency_vector', freq,
                                 'window', w,
                                 'nfft', nfft)

        self.spectrum = outputSpectrum
        return sp, freq

    def computespectralmoments(self, winLength=256,
                               win=None, nfft=None, novlp=None):

        if win is None:
            win = scipy.signal.hanning(winLength)
        if nfft is None:
            nfft = 2**nextpow2(self.sampling_frequency)
        if novlp is None:
            novlp = int(winLength * 3 / 4)

        if self.spectrogram is None:
            self.computespectrogram(winLength, win, nfft, novlp)

        f = self.spectrogram_frequency_vector
        Sxx = abs(self.spectrogram)**2

        nFreq, nFrame = Sxx.shape
        cgs = np.zeros(nFrame)
        spread = np.zeros(nFrame)

        for k in range(nFrame):
            Sxxtmp = Sxx[:, k]
            cgs[k] = np.sum(Sxxtmp * f) / np.sum(Sxxtmp)
            spread[k] = np.sqrt(np.sum((f - cgs[k])**2 * Sxxtmp) / np.sum(Sxxtmp))

        self.spectral_centroid = cgs
        self.spectral_spread = spread

        return cgs, spread

    def getpitch(self, f0min=70, f0max=300, isInterp=True):

        sound = sp2sound(self)
        f0min = max(f0min, int(np.ceil(self.sampling_frequency / len(self.signal) * 3 )))
        f0, tf0 = praat_get_pitch(sound, f0min, f0max)
        pitchOut = Pitch('values', f0, 'time_points', tf0, 'parent', self)

        if isInterp:
            f0 = pitchOut.interpolate()

        self.pitch = pitchOut
        return pitchOut

    def getjitter(self, nwin=5):
        sound = sp2sound(self)
        if self.pitch is None:
            self.getpitch()
        f0min = 0.8 * np.min(self.pitch.values)
        f0max = 1.2 * np.max(self.pitch.values)
        time, jitter =  praat_get_jitter(sound, nwin=nwin, f0min=f0min, f0max=f0max)
        self.pitch.glottal_closure_instants = time
        self.pitch.jitter = jitter

    def changecontour(self, pitchTarget):

        if self.pitch is None:
            inPitch = self.getpitch()
        inPitch = self.pitch
        sound = sp2sound(self)
        sOut = praat_modif_pitch(sound, inPitch.time_points, pitchTarget.values)
        sound2sp(sOut, self)

    def changejitter(self, factor, f0min=70, f0max=300):

        sound = sp2sound(self)
        oldT, pointProcess = praat_get_gci(sound, f0min, f0max)
        pointProcess = praat_remove_points(pointProcess)

        r = 4 * np.random.rand(len(oldT)) - 2
        To = np.abs(np.diff(oldT))
        To = np.insert(To, 0, 0)
        newT = np.sort(oldT + r * factor / 100 * To)

        sOut = praat_change_gci(sound, newT, pointProcess)
        sound2sp(sOut, self)

    def changeshimmer(self, factor, f0min=70, f0max=300):

        sound = sp2sound(self)
        sOut = praat_change_shimmer(sound, factor, f0min=70, f0max=300)
        sound2sp(sOut, self)

    def getintensity(self, len_win=0.03):

        y = self.signal.squeeze()
        sr = self.sampling_frequency
        tsig = np.arange(0, len(y)) / sr

        nwin = int(len_win * sr)
        if np.mod(nwin, 2) > 0:
            nwin = nwin + 1

        energy = []
        s = 0
        for k, smpl in enumerate(y):
            s += smpl**2
            if (k + 1) % nwin == 0:
                energy.append(s)
                s = 0
            elif k == len(y) - 1:
                energy.append(s)

        yOut_lin = np.array(energy) / np.sqrt(nwin)
        yOut_dB = 10 * np.log10(yOut_lin / 2e-5)
        tVec = tsig[::nwin] + len_win / 2
        objOut = Intensity('values', yOut_dB,
                           'time_points', tVec,
                           'parent', self)

        self.intensity = objOut
        return objOut

    def changeintensity(self, intTarget):

        if self.intensity is None:
            intIn = self.getintensity()
        else:
            intIn = self.intensity
        intIn = intIn.interpolate(self)
        intTarget = intTarget.interpolate(self)

        y = self.signal
        ydetrend = y / intIn.db2lin()
        ychange = ydetrend * intTarget.db2lin()

        self.signal = ychange

    def changetilt(self, factor, durWin=0.04, f0min=70, f0max=300):

        y = self.signal
        sr = self.sampling_frequency

        tVec = np.arange(len(y)) / sr

        nwin = int(durWin * sr)
        if np.mod(nwin, 2) > 0:
            nwin = nwin + 1

        novlp, nfft, nhop = ola_param(nwin, novlp=None, sr=sr)
        L = int(nfft / 2 + 1)
        freq_out = np.arange(L) * sr / nfft

        if self.pitch is None:
            self.getpitch(f0min=f0min, f0max=f0max)

        tf0 = self.pitch.time_points
        f0 = self.pitch.values

        f1 = scipy.interpolate.interp1d(tf0, f0, 'linear', fill_value='extrapolate')
        f0 = f1(tVec)

        w = scipy.signal.hann(nwin)
        f0 = np.vstack((np.zeros((nhop, 1)),
                        f0.reshape(-1, 1),
                        np.zeros((nhop, 1)))).squeeze()
        y = np.vstack((np.zeros((nhop, 1)),
                       y.reshape(-1, 1),
                       np.zeros((nhop, 1)))).squeeze()
        yOut = np.zeros_like(y)

        k = 0
        isC = True
        while isC:
            xTmp, idx, isC = check_index(y, k, nwin, nhop)

            f0Tmp = np.median(f0[idx])
            y_fft = np.fft.fft(xTmp, nfft)[:L]

            idxStart = np.abs(freq_out- f0Tmp).argmin()
            bk = y_fft[idxStart:]
            fk = freq_out[idxStart:]

            p_obs = np.polyfit(fk, np.log(np.abs(bk)), 1)
            p1 = np.log(np.abs(abs(bk[0]))) - p_obs[0] * fk[0]
            line_obs = p_obs[0] * freq_out + p1
            p2 = np.log(np.abs(abs(bk[0]))) - factor * p_obs[0] * fk[0]
            line_targ = factor * p_obs[0] * freq_out + p2

            amp_ratio = np.exp(line_targ - line_obs)
            amp_ratio[freq_out <= fk[0]] = 1

            y_modif_fft = y_fft * amp_ratio
            xNew = symmetricifft(y_modif_fft)[:len(idx)]

            yOut[idx] = yOut[idx] + xNew
            k += 1

        yOut = yOut / 1.5

        SpOut = self.copy()
        SpOut.signal = yOut
        SpOut.sampling_frequency = sr

        return SpOut

    def changeduration(self, pts, factor, isSeg=True):

        sound = sp2sound(self)
        if self.phonetic_instants is None:
            isSeg = False

        if isSeg:
            phon_inst_old = copy.deepcopy(self.phonetic_instants)
            phon_inst_new = copy.deepcopy(self.phonetic_instants)
            currSeg = np.zeros(len(phon_inst_old)).astype(int)
            newDur = np.zeros(len(phon_inst_old))
            oldDur = np.zeros(len(phon_inst_old))

            for k in range(len(pts)):
                currPhonInst = phon_inst_old[0][k, :]
                oldDur[0] = phon_inst_old[0][k, 1] - phon_inst_old[0][k, 0]
                newDur[0] = oldDur[0] * factor[k]
                phon_inst_new[0][k, 1] = phon_inst_new[0][k, 0] + newDur[0]
                phon_inst_new[0][k + 1:, :] += newDur[0] - oldDur[0]
                for kinst in range(1,len(phon_inst_old)):
                    newDur[kinst] += newDur[0]
                    oldDur[kinst] += oldDur[0]
                    if currPhonInst[1] >= phon_inst_old[kinst][currSeg[kinst], 1]:
                        phon_inst_new[kinst][currSeg[kinst], 1] = phon_inst_new[kinst][currSeg[kinst], 0] + newDur[kinst]
                        phon_inst_new[kinst][currSeg[kinst]+ 1 :, :] += newDur[kinst] - oldDur[kinst]
                        currSeg[kinst] += 1
                        newDur[kinst] = 0
                        oldDur[kinst] = 0

        sOut = praat_change_duration(sound, pts, factor)
        sound2sp(sOut, self)
        if isSeg:
            self.phonetic_instants = phon_inst_new

    def xglos(self, param=None):

        param = initparam(self, param)

        S = self.signal

        if self.sampling_frequency == 1:
            warnings.warn("Warning: the sampling frequency is 1")

        sr = self.sampling_frequency

        #### Build sliding window for the time signal
        Lw = int(param.win_length)
        w = scipy.signal.hanning(Lw + 1)
        w = w[1:]
        param.hop = param.win_length / param.hop_factor
        a = param.hop

        ## Initialization
        #### zero-padding of the signal at both extremities
        npad = Lw
        Spad = np.concatenate((np.zeros((npad)), S, np.zeros((npad))))
        Nframes = int(np.ceil((len(Spad) - 2 * Lw) / a))

        t = np.arange(1, Nframes + 1) * (a / sr) + Lw / (2 * sr) - npad / sr
        param.t = t

        ## F0
        if self.pitch is None:
            pks = np.zeros((int(param.nfft), Nframes))
            x = np.zeros((Lw, Nframes))
            f0 = np.empty(Nframes)
            f0[:] = np.nan
            param.lfmed = np.ceil(param.fomin*2.5)

            for u in range(Nframes):
                idx1 = int((u+1)*a-1)
                idx2 = int((u+1)*a+Lw-1)
                x[:, u] = Spad[idx1:idx2]
                xtmp = Spad[idx1:idx2]
                pks[:, u] = findpartials(xtmp, sr, np.ones(Lw), param)
                f0[u] = findf0(pks[:, u], sr, param)# Get pitch and detected harmonics
            #            # adapts the length of the median filter
                if f0[u]:
                    param.lfmed = np.ceil(f0[u]*2.5)
        else:
            f0_raw = self.pitch.values
            tfo = self.pitch.time_points
            f1 = scipy.interpolate.PchipInterpolator(tfo, f0_raw)
            f0 = f1(t)

        fk = f0reeval(f0, Spad, sr, param)
        f0 = fk[:, 0]
        mvf = np.max(fk, axis=1)

        # interpolation of f0 and MVF
        tfo = np.arange(len(Spad)) / sr - npad / sr
        f1 = scipy.interpolate.PchipInterpolator(t, f0)
        foint = f1(tfo)
        foint[np.isnan(foint)] = 0
        aiint = np.ones_like(foint)
        f2 = scipy.interpolate.PchipInterpolator(t, mvf)
        mvfint = f2(tfo)
        mvfint[np.isnan(mvfint)] = 0

        # jitter
        if param.jitt or param.shim:
            sfilt = np.zeros((len(Spad), Nframes))
            fkcmat = np.zeros(Nframes)
            fojmat = np.empty((len(Spad), Nframes))
            fojmat[:] = np.nan
            aimat = np.empty((len(Spad), Nframes))
            aimat[:] = np.nan
            kfk = 0
            for u in range(Nframes):
                idx = np.arange((u+1)*a-1, (u+1)*a+Lw)
                if fk[u, 0] > 0:
                    fkc = np.round(fk[u, 0])
                    if any(fkcmat == fkc) == False:
                        bb = param.fcoef * np.cos(2 * np.pi * fkc /
                                                  sr * np.arange(len(param.fcoef)))
                        xwf = scipy.signal.filtfilt(bb, 1, Spad)
                        sfilt[:, kfk] = xwf
                        fkcmat[kfk] = fkc
                        xwf = xwf[idx.astype(int)]
                        kfk += 1
                    else:
                        xwf = sfilt[idx.astype(int), fkcmat == fkc]

                    #fojitt = instfreq(xwf,sr, fk[u,0])
                    fojitt, aijitt, dum = instprop(xwf, sr)
                    aijitt[np.logical_or(fojitt < param.fomin, fojitt > param.fomax)] = 0
                    fojitt[np.logical_or(fojitt < param.fomin, fojitt > param.fomax)] = 0
                    fojmat[idx.astype(int), u] = fojitt
                    aimat[idx.astype(int), u] = fojitt
            foj = np.nanmedian(fojmat, axis=1)
            aij = np.nanmedian(fojmat, axis=1)
            aij[aij == np.nan] = 0
            aij[np.logical_or(foj < param.fomin, foj > param.fomax)] = 0
            aij = sm.nonparametric.lowess(aij,
                                          np.arange(len(aij)),
                                          frac=101/len(aij),
                                          return_sorted=False)
            foj[foj == np.nan] = 0
            foj[np.logical_or(foj < param.fomin, foj > param.fomax)] = 0
            foj = sm.nonparametric.lowess(foj,
                                          np.arange(len(foj)),
                                          frac=101/len(foj),
                                          return_sorted=False)
            foint = foj
            aiint = aij

        Sh = np.zeros(len(Spad))
        Sh2 = np.zeros(len(Spad))

        harm = fk
        harm[harm == 0] = np.nan

        for u in range(Nframes):
            idx = np.arange((u + 1) * a - 1, (u + 1) * a + Lw)
            wh = scipy.signal.hanning(len(idx) + 1)
            wh = wh[1:]
            s = Spad[idx.astype(int)] * wh
            if fk[u, 0] > 0:
                nk = fk[u, :] / fk[u, 0]
                nk = nk[nk > 0]

                if param.shim:
                    aijitt = aij[idx.astype(int)]
                else:
                    aijitt = 1
                hann_window = npmt.repmat((wh * aijitt).reshape((wh.size, 1)), 1, len(nk))
                if param.jitt:
                    fojitt = foj[idx.astype(int)]
                    alp_phase = ((np.cumsum(fojitt).reshape(-1, 1)).dot(nk.reshape(1, -1)))
                    alp = np.exp(1j * 2 * np.pi / sr * alp_phase)
                else:
                    fk_tmp = (nk * fk[u, 0])
                    sig_tmp = np.arange(len(s)).reshape(-1, 1)
                    alp_phase = 1j * 2 * np.pi / sr
                    alp = np.exp(alp_phase * (sig_tmp).dot(fk_tmp.reshape(1, -1)))

                E = alp[:len(s), :] * hann_window
                bk, dum1, dum2, dum3 = np.linalg.lstsq(E, s.reshape(-1, 1))
                Sp = 2 * np.real(E.dot(bk.reshape(-1, 1))).reshape(-1)
            else:
                Sp = np.zeros(len(s))

            Sh[idx.astype(int)] = Sh[idx.astype(int)] + Sp * wh
            Sh2[idx.astype(int)] = Sh2[idx.astype(int)] + s * wh

        frame_bound = 1.5 * param.hop_factor / 4

        deb = npad
        fin = deb + len(S)
        Sh = Sh[deb:fin] / frame_bound
        Sh2 = Sh2[deb:fin] / frame_bound

        foint = foint[deb:fin]
        mvfint = mvfint[deb:fin]

        self.voiced = SpeechAudio('signal', Sh,
                                  'sampling_frequency', sr)
        self.unvoiced = SpeechAudio('signal', Sh2 - Sh,
                                    'sampling_frequency', sr)

        grossPitch = Pitch('values', harm[:, 0], 'time_points', t)
        instPitch = Pitch('values', foint,
                          'time_points', np.arange(len(self.signal)) / self.sampling_frequency)

        self.instantaneous_pitch = instPitch
        self.maximal_voiced_frequency = mvfint
        self.harmonics = harm
        self.instantaneous_periodic_amplitude = aiint[deb:fin]
        self.pitch = grossPitch

        return Sh, Sh2 - Sh, foint, mvfint, harm

    def backgroundnoise(self, Pxx, targetSNR):

        sig = self.signal
        nSig = len(sig)
        sr = self.sampling_frequency

        nwin = 4096
        novlp, nfft, nhop = ola_param(nwin, novlp=None, sr=sr)
        wNoise = np.random.normal(loc=0, scale=1, size=nSig)
        wNoise, backNoise = init_ola(wNoise, nwin, nhop)

        k = 0
        isC = True
        while isC:
            xwin, fft_xwin, isC, idx = spec_frame(wNoise, k, nwin, nhop, nfft)
            backNoise = change_frame(fft_xwin, Pxx, 1, nfft, idx, backNoise,
                                     xwin, isChange=True)

            k += 1

        backNoise = backNoise[nhop:-nhop] / 1.5
        X = np.sqrt(np.var(sig) / np.var(backNoise) / targetSNR)
        backNoise = backNoise * X
        xOut = sig + backNoise
        self.signal = xOut

        return xOut, backNoise

    def computespectralenvelope(self, nwin=512, novlp=None,
                                nfft=None, order=None):

        sr = self.sampling_frequency
        x = self.signal
        if sr == 1:
            warnings.warn("Warning: the sampling frequency is 1")
        if novlp is None:
            novlp = int(nwin * 3 / 4)
        if nfft is None:
            nfft = nwin
        if order is None:
            order = np.ceil(sr / 1000 + 2)

        nhop = nwin - novlp
        xbuff = buffer(x, nwin, nhop)
        w = np.hamming(nwin)
        preemph = [1, 0.63]
        L = int(nfft / 2 + 1)
        fxx = np.arange(L) * sr / nfft

        nFrame = xbuff.shape[1]
        txx = np.arange(0, len(x), nhop) / sr
        txx = txx[:nFrame]

        Sxx = np.zeros((L, nFrame))

        for k in range(nFrame):
            xwin = xbuff[:, k] * w
            xwin = scipy.signal.filter(1, preemph, xwin)
            lpc_xx = lpc(xwin, order)
            w_lpc, h_lpc = scipy.signal.freqz(1, lpc_xx, L)
            Sxx[:, k] = h_lpc

        outputEnvelope = TimeFreq('parent', self,
                                  'time_frequency_matrix', Sxx,
                                  'time_vector', txx,
                                  'frequency_vector', fxx,
                                  'window', w,
                                  'overlap', novlp,
                                  'nfft', nfft)

        self.spectral_envelope = outputEnvelope

        return Sxx, fxx, txx

    def computecepstrumenvelope(self, nwin=1024, novlp=None,
                                order=None, toldB=None):

        if novlp is None:
            novlp = int(nwin * 3 / 4)

        x = self.signal
        sr = self.sampling_frequency
        novlp, nfft, nhop = ola_param(nwin, novlp=novlp)
        xbuff = buffer(x, nwin, nhop)
        w = np.hamming(nwin)
        L = int(nfft / 2 + 1)
        fxx = np.arange(L) * sr / nfft

        nFrame = xbuff.shape[1]
        txx = np.arange(0, len(x), nhop) / sr
        txx = txx[:nFrame] + (nwin / 2) / sr

        Sxx = np.zeros((L, nFrame))
        if self.pitch is None and order is None:
            self.getpitch(70, 400, False)
            self.pitch.timeinterpolate(txx)
        else:
            self.pitch.timeinterpolate(txx)

        w = np.matlib.repmat(w.reshape(-1,1), 1, nFrame)
        xwin = xbuff * w
        xwin[xwin==0] = 1e-22
        Sxx = np.zeros((L, nFrame))

        for k in range(nFrame):
            order = get_order_ceps(self.pitch.values[k], sr)
            Sxx[:,k] = cepstrum(xwin[:,k], sr, order, toldB)

        outputEnvelope = TimeFreq('parent', self,
                                  'time_frequency_matrix', Sxx,
                                  'time_vector', txx,
                                  'frequency_vector', fxx,
                                  'window', w,
                                  'overlap', novlp,
                                  'nfft', nwin)

        self.spectral_envelope = outputEnvelope

        return Sxx, fxx, txx

    def mfcc(self, nwin=512, novlp=None, nfft=1024, nb_filter=24, nb_coeff=12,
              preemph=[1, -0.95], win='hamming', replace=False):
        """ computes the MFCC coefficients """

        if novlp is None:
            novlp = int(nwin * 3 / 4)
        if nfft is None:
            nfft = nwin

        Sp = self.copy()

        if preemph is not None:
            Sp.signal = scipy.signal.lfilter([1], preemph, Sp.signal)
        Sxx, fxx, txx = Sp.computespectrogram(win=win, nwin=nwin, novlp=novlp,
                                              nfft=nfft)
        filters, mels, mel_freqs = mel_filter_bank(sr=self.sampling_frequency,
                                                   fmin=0, fmax=None,
                                                   nb_filter=nb_filter,
                                                   nfft=nfft)

        Pxx = np.abs(Sxx)**2
        energy = np.sum(Pxx, axis=0).reshape(1, -1)
        Pxx_filtered = filters @ Pxx
        Pxx_log = 10 * np.log10(Pxx_filtered)

        # dct_basis = dct(nb_coeff + 1, filter_len=nb_filter)[1:,:]
        dct_basis = dct(nb_coeff + 1, filter_len=nb_filter)
        static_coeff = dct_basis @ Pxx_log
        c0 = np.array([x for x in static_coeff[0,:]])
        if replace:
            static_coeff[0,:] = energy
        dt = delta(static_coeff)
        ddt = delta(dt)
        mfcc_coeff = np.vstack((static_coeff, dt, ddt))

        mfcc = MFCC('coeff', mfcc_coeff, 'time_vector', txx,
                    'mel_vector', mels, 'frequency_vector', mel_freqs,
                    'power_log', Pxx_log, 'nb_coeff', nb_coeff, 'c0', c0,
                    'energy', energy, 'parent', self)
        mfcc.mfcc2melspectro()

        self.mfcc = mfcc

    def addformants(self, tf_add, nwin=512, novlp=None, nfft=None, nargout=1):

        novlp, _, nhop = ola_param(nwin, novlp)
        x2, x_out = init_ola(self.signal, nwin, nhop)

        k = 0
        isC = True
        while isC:
            xwin, fft_xwin, isC, idx = spec_frame(x2, k, nwin, nhop, nfft)
            x_out = change_frame(fft_xwin, tf_add, 1, nfft, idx, x_out, xwin)
            k += 1

        x_out = x_out[nhop:-nhop] / 1.5

        if nargout < 1:
            self.signal = x_out
        else:
            obj_out = self.copy()
            obj_out.signal = x_out

            return obj_out

    def alignread(self, fileName, utt_id=None):

        if fileName.lower().find('.textgrid') > 0:
            labels, start, stop = func_readTextgrid(fileName)
            labels = removequotes(labels)
            instants = []

            for k in range(len(labels)):
                startTmp = np.array(start[k]).reshape(-1, 1)
                stopTmp = np.array(stop[k]).reshape(-1, 1)
                instTmp = np.concatenate((startTmp, stopTmp), 1)
                instants.append(instTmp)

        elif fileName.lower().find('.xml') > 0:
            labels, start, stop = read_xml_segmentation_files(fileName)
            # labels = removequotes(labels)
            instants = []
            for k in range(len(labels)):
                # startTmp = start[k]).reshape(-1, 1)
                # stopTmp = np.array(stop[k]).reshape(-1, 1)
                instTmp = np.array([start[k], stop[k]]).reshape(1,2)
                if instants == []:
                    instants = instTmp
                else:
                    instants = np.vstack((instants, instTmp))
        elif fileName.lower().find('.json') > 0:
            labels, instants = read_json_segmentation_files(fileName)
        elif fileName.lower().find('.whc') > 0:
            labels, instants = read_whc_segmentation_files(fileName)
        elif fileName.lower().find('.seg') > 0:
            if utt_id is None:
                labels, instants = read_seg_segmentation_files(fileName)
            else:
                labels, instants = read_seg_segmentation_files_2(fileName, utt_id)
        elif fileName.lower().find('.ctm') > 0:
            labels, instants = parse_align_file(fileName)           
        else:
            raise FormatError('Unknown file format')

        self.phonetic_labels = labels
        self.phonetic_instants = instants

        return labels, instants

    def sparse_transform(self, A_source, A_target, isFlat=True, isNorm=True, 
                         is_feat_norm=True, is_residual=True, feat_type="lin",
                         n_jobs=1, alpha=1e-3):

        nb_feat, nb_atoms = A_source.shape
        nwin = (nb_feat - 1) * 2
        novlp = int(nwin * 3 / 4)
        novlp, nfft, nhop = ola_param(nwin, novlp)
        x2, x_out = init_ola(self.signal, nwin, nhop)
        Spx2 = SpeechAudio("signal", x2,
                           "sampling_frequency", self.sampling_frequency)
        Sxx, fxx, txx = Spx2.computecepstrumenvelope(nwin, novlp)
        if feat_type == "log":
            features = np.log(Sxx)
        else:
            features = Sxx * 1
        Sxx_target = sparse_regression(features, A_source, A_target, 
                                       is_feat_norm, is_residual, 
                                       n_jobs=n_jobs, alpha=alpha,
                                       feat_type=feat_type)
        if feat_type == "log":
            Sxx_target = np.exp(Sxx_target)
        self.signal = change_cepstrum(x2, Spx2, x_out, nwin, nhop, nfft, txx, isFlat, isNorm,
                    Sxx, Sxx_target)

    def cepstraltransform(self, transOper, nwin=1024,
                          novlp=None, sr=8000, freq_out=None,
                          method='linear', nargout=1, feat_type='ceps'):

        novlp, nfft, nhop = ola_param(nwin, novlp)
        x2, x_out = init_ola(self.signal, nwin, nhop)

        sr_in = self.sampling_frequency
        if sr_in != sr:
            self.speechresample(sr)

        x2, x_out = init_ola(self.signal, nwin, nhop)
        Spx2 = SpeechAudio('signal', x2, 'sampling_frequency', sr)
        if feat_type == 'ceps':
            Sxx_in, fxx, txx = Spx2.computecepstrumenvelope(nwin, novlp)
        elif feat_type == 'mfcc':
            L = int(nfft / 2 + 1)
            freq_oo = np.arange(L) * self.sampling_frequency / nfft
            nb_coeff = transOper.nb_coeff
            nb_filter = len(transOper.mel_vector) - 2
            S_tmp = transOper.mfcc2melspectro(freq_oo)
            Sxx_trans = S_tmp.time_frequency_matrix

            Spx2.mfcc(nwin=nwin, novlp=novlp,
                      nb_filter=nb_filter, nb_coeff=nb_coeff)
            S_tmp_2 = Spx2.mfcc.mfcc2melspectro(freq_oo)
            Sxx_in = S_tmp_2.time_frequency_matrix

            fxx = S_tmp_2.frequency_vector
            txx = S_tmp_2.time_vector

        if method.lower() == 'dnn':
            """ DNN-based modification is in progress """
            pass
            # if freq_out is not None:
            #     if len(freq_out) != len(fxx) and not (freq_out==fxx).all():
            #         self.spectral_envelope.interpolate(freq_out, axis='freq')
            #         isChange = True
            #     Sxx_in = np.log(self.spectral_envelope.time_frequency_matrix)
            #     Sxx_trans = np.exp(predict(transOper, Sxx_in.T,
            #                                   train_domain='frequency')).T
            # else:
            #     Sxx_in, Sxx_trans = predict(transOper, Sxx_in,
            #                                   train_domain='time')
        else:
            isChange = False
            # if freq_out is not None:
            #     if not (freq_out==fxx):
            #         self.spectral_envelope.interpolate(freq_out, axis='freq')
            #         isChange = True
            #     Sxx_in = self.spectral_envelope.time_frequency_matrix
            if method.lower() == 'linear':
                Sxx_in, Sxx_trans = ceps_transform(Sxx_in, transOper, nwin, novlp,
                                               fxx, freq_out, method)

            if method.lower() == 'target' and feat_type != 'mfcc':
                Sxx_trans = transOper
            if isChange:
                a = TimeFreq('time_frequency_matrix', Sxx_trans,
                            'frequency_vector', freq_out)
                a.interpolate(fxx, axis='freq')
                Sxx_trans = a.time_frequency_matrix
                a = TimeFreq('time_frequency_matrix', Sxx_in,
                            'frequency_vector', freq_out)
                a.interpolate(fxx, axis='freq')
                Sxx_in = a.time_frequency_matrix
            if Sxx_trans.shape[1] < Sxx_in.shape[1]:
                a = TimeFreq('time_frequency_matrix', Sxx_trans,
                            'frequency_vector', freq_out,
                            'time_vector', txx[1:-1] - nhop / sr)
                a.interpolate(txx - nhop / sr, axis='time')
                Sxx_trans = a.time_frequency_matrix
        k = 0
        isC = True

        while isC:
            xwin, fft_xwin, isC, idx = spec_frame(x2, k, nwin, nhop, nfft)

            x_out = change_frame(fft_xwin, Sxx_trans[:,k], Sxx_in[:,k], nfft, idx, x_out,
                                     xwin, isChange=True, isNorm=False)
            k, isC = check_frame(k, isC, maxFrame=Sxx_in.shape[1])
        x_out = x_out[nhop:-nhop] / 1.5

        if nargout == 1:
            obj_out = self.copy()
            obj_out.signal = x_out
            if sr_in != sr:
                obj_out.speechresample(sr_in)
            return obj_out
        else:
            self.signal = x_out
            self.sampling_frequency = sr
            if sr_in != sr:
                self.speechresample(sr_in)

    def createdisto(self, dist_threshold=0.8):

        x = np.zeros_like(self.signal)
        x[:] = self.signal
        xMax = max(abs(x))*dist_threshold
        x[x > xMax] = xMax
        x[x < -xMax] = -xMax
        self.signal = x


    def exportsegment2json(self, jsonFileName):

        if self.phonetic_labels is None:
            raise SegError('No segmentation: cannot export empty data')

        nTiers = len(self.phonetic_labels)
        idjson = {}
        idjson['tiers'] = []
        for k in range(nTiers):
            lbl = self.phonetic_labels[k]
            inst = self.phonetic_instants[k]
            nEvents = len(lbl)
            segStart = []
            segStop = []
            events = []
            for kE in range(nEvents):
                segStart = "%.3f" %(inst[kE, 0])
                segStop = "%.3f" %(inst[kE, 1])
                events.append({'segment_name': lbl[kE],
                               'segment_start': segStart,
                               'segment_stop': segStop})
            idjson['tiers'].append({'events': events})

        fileJSON = jsonFileName.replace('.json', '') + '.json'
        with open(fileJSON, 'w') as f:
            json.dump(idjson, f)

    def formantestimate(self, nwin=512, novlp=None, ord_filt=25):

        sr = self.sampling_frequency
        novlp, _, nhop = ola_param(nwin, novlp)
        snd = sp2sound(self)
        time_vec = np.arange(0, len(self.signal) + nhop, nhop) / sr
        form_out, bw_out, txx = praat_get_formants(snd, nhop, nwin)
        for k in range(4):
            fTmp = np.squeeze(form_out[k, :])
            fTmp = fill_nan_and_zero(fTmp)
            bwTmp = np.squeeze(bw_out[k, :])
            bwTmp = fill_nan_and_zero(bwTmp)

            if ord_filt is not None:
                if ord_filt > 0:
                    num_frames = len(fTmp)
                    if num_frames >= ord_filt:
                        fTmp = sm.nonparametric.lowess(fTmp,
                                                       np.arange(len(fTmp)),
                                                       frac=ord_filt/len(fTmp),
                                                       return_sorted=False)

                        bwTmp = sm.nonparametric.lowess(bwTmp,
                                                        np.arange(len(fTmp)),
                                                        frac=ord_filt/len(fTmp),
                                                        return_sorted=False)
                    else:
                        pass
            form_out[k, :] = fTmp
            bw_out[k, :] = bwTmp

        damp = bw_out * np.pi
        formantObject = Formants('frequency', form_out,
                                 'bandwidth', bw_out,
                                 'damping', damp,
                                 'amplitude', np.ones_like(form_out),
                                 'time_vector', txx,
                                 'parent', self,
                                 'isForm', True)

        formantObject.interpolate(time_vec)
        formantObject.getcontour()
        self.formants = formantObject

        return formantObject

    def formantshifting(self, formTarget, nwin=512,
                        novlp=None, nfft=None, tf_add=1):

        novlp, nfft, nhop = ola_param(nwin, novlp)
        x2, x_out = init_ola(self.signal, nwin, nhop)
        sr = self.sampling_frequency

        Sxx, fxx, txx = self.computecepstrumenvelope(nwin, novlp)
        if tf_add is not None:
            tf_add.interpolate(fxx)
            tf_resp = tf_add.values
        else:
            tf_resp = 1

        nF = len(formTarget)
        [x.interpolate(txx) for x in formTarget]
        isNewZero = False
        if nF == 1:
            formTarget = formTarget[0]
            zeroTarget = None
        if nF == 2:
            zeroTarget = formTarget[1]
            formTarget = formTarget[0]
            isNewZero = True

        newDamp = formTarget.damping
        newFreq = formTarget.frequency
        newZ = np.exp(2 * np.pi * 1j * newFreq / sr) * np.exp(-newDamp / sr)
        newZ = np.concatenate((newZ, np.conj(newZ)), 0)
        if isNewZero:
            newZeroFreq = zeroTarget.frequency
            newZeroDamp = zeroTarget.damping
            newZero = np.exp(2 * np.pi * 1j * newZeroFreq / sr) * np.exp(-newZeroDamp / sr)
            newZero = np.concatenate((newZero, np.conj(newZero)), 0)
        else:
            newZero = np.zeros_like(newZ)

        k = 0
        isC = True

        while isC:
            xwin, fft_xwin, isC, idx = spec_frame(x2, k, nwin, nhop, nfft)
            if (newFreq[:,k] != 0).all():
                _, h_new = z2freqz(newZ[:, k], newZero[:, k], nfft=nfft)
            else:
                h_new = 1
            h_orig = Sxx[:,k]
            x_out = change_frame(fft_xwin, h_new, h_orig,
                                         nfft, idx, x_out, xwin=xwin,
                                         isChange=(newFreq[:,k] != 0).all())

            k, isC = check_frame(k, isC, maxFrame=newFreq.shape[1])

        x_out = x_out[nhop:-nhop] / 1.5
        x_out[np.isnan(x_out)] = 0

        self.signal = x_out
        self.formants = formTarget
        
    def change_prosody(self, dil_fact=1, trans_fact=1, dur_fact=1, dist=None):

        if self.pitch is None:
            self.getpitch()
        if dist is not None:
            trans_fact, dil_fact, dur_fact = get_pros_modif_factor_from_dist(dist)
            
        if dil_fact != 1 and trans_fact != 1:
            pitch_output = transform_pitch(self.pitch, trans_fact, dil_fact)
            self.changecontour(pitch_output)

        if dur_fact != 1:
            pts = [0, len(self.signal)/ self.sampling_frequency]
            factor = np.ones(3) * dur_fact
            self.changeduration(pts, factor)

    def frequency_warping(self, dil_fact, trans_fact, dist=None, ord_filt=None,
                      nwin=512, novlp=None, isNorm=True, isFlat=True):

        novlp, nfft, nhop = ola_param(nwin, novlp)
        x2, x_out = init_ola(self.signal, nwin, nhop)
        Spx2 = SpeechAudio('signal', x2,
                           'sampling_frequency', self.sampling_frequency)
        Sxx, fxx, txx = Spx2.computecepstrumenvelope(nwin, novlp)
        form_in = Spx2.formantestimate(nwin, novlp, ord_filt=ord_filt)
        form_in.interpolate(txx)

        if dist is None:
            form_output = transform_formant(form_in, dil_fact, trans_fact)
        else:
            form_output = transform_formant_from_dist(form_in, dist)
        form_output.interpolate(txx)

        nb_frame = Sxx.shape[1]
        xx, yy = np.meshgrid(np.arange(0, nb_frame), fxx)
        h_new = dfw_matrix(np.abs(Sxx), fxx,
                           np.sort(form_output.frequency, axis=0),
                           form_in.frequency)

        self.signal = change_cepstrum(x2, Spx2, x_out, nwin, nhop, nfft, txx,
                                      isFlat, isNorm, Sxx, h_new)
        self.formantestimate(nwin, novlp, ord_filt=None)
        self.formants.interpolate(txx)

    def time_warping(self, inst_target, tiers=0):
        """ dynamic time warping of phonemes to match the specified target """
        if inst_target.shape[0] != self.phonetic_instants[tiers].shape[0]:
            raise ValueError('The number of phonemes does not match')

        len_input = len(self.signal) / self.sampling_frequency
        inst_input = self.phonetic_instants[0]
        if inst_input[-1,1] < len_input:
            inst_input[-1,1] = len_input

        dur_input =  inst_input[:,1]- inst_input[:,0]
        dur_target = inst_target[:, 1] - inst_target[:, 0]

        factor = dur_target / dur_input
        factor[np.isnan(factor)] = 0
        factor[np.isinf(factor)] = 0

        pts = inst_input[:-1,1]
        self.changeduration(pts, factor, isSeg=True)

    def remove_silence(self, side="both"):
        y = self.signal
        sr = self.sampling_frequency
        lbl = self.phonetic_labels[0]
        inst = self.phonetic_instants[0]

        if lbl[0] == "." and side in ["both", "l"]:
            delay = inst[1,0]
            idx_st = int(delay * sr)
            y = y[idx_st:]
            lbl = lbl[1:]
            inst = inst[1:, :] - delay
            if len(self.phonetic_labels) > 1:
                if self.phonetic_labels[1][0] ==  "[silence]":
                    self.phonetic_labels[1] = self.phonetic_labels[1][1:]
                    self.phonetic_instants[1] = self.phonetic_instants[1][1:, :] - delay
        if lbl[-1] == "." and side in ["both", "r"]:
            idx_st = int(inst[-1,0] * sr)
            y = y[:idx_st]
            lbl = lbl[:-1]
            inst = inst[:-1,:]
            if len(self.phonetic_labels) > 1:
                if self.phonetic_labels[1][-1] ==  "[silence]":
                    self.phonetic_labels[1] = self.phonetic_labels[1][:-1]
                    self.phonetic_instants[1] = self.phonetic_instants[1][:-1, :]

        self.phonetic_labels[0] = lbl
        self.phonetic_instants[0] = inst
        self.signal = y

    def savespeech(self, fileName, norm=None):
        """ saves speech into an audio file """

        if norm is None:
            norm = 'notnormalized'
        if norm is type(str):
            norm = norm.lower()

        sig2save = self.signal
        if norm == 'normalized':
            maxSig = max(abs(sig2save)) * 1.1
        if norm == 'notnormalized':
            maxSig = 1
        if type(norm) is not str:
            maxSig = norm

        sig2save = sig2save / maxSig * 32768
        record_to_file(fileName, sig2save.astype('i2'),
                       2, self.sampling_frequency)

    def segmentspeech(self, tiers=0, isSeg=True):

        if self.phonetic_labels is None:
            raise ValueError('Speech audio object is not segmented, please perform segmentation')

        nTiers = len(self.phonetic_labels)
        ph_label = self.phonetic_labels[tiers]
        ph_ist = self.phonetic_instants[tiers]
        x = self.signal
        sr = self.sampling_frequency
        if self.pitch is not None:
            f0 = self.pitch.values
            tf0 = self.pitch.time_points
        else:
            f0 = None
            tf0 = None
        formants = self.formants
        segments = []

        for k in range(len(ph_label)):
            phon_tmp = SpeechSegment('phoneme_label', ph_label[k])
            phon_tmp.getphoninfo()
            phon_tmp.sampling_frequency = sr
            inst_tmp = ph_ist[k, :]
            phonSegLbl = []
            phonSegInst = []
            for kT in range(tiers + 1):
                lblTiers = self.phonetic_labels[kT]
                instTiers = self.phonetic_instants[kT]
                idxStart = [x for x in range(instTiers.shape[0])
                            if instTiers[x,0] >= inst_tmp[0] and instTiers[x,1] <= inst_tmp[1]]
                lblTmp = [lblTiers[x] for x in idxStart]
                momTmp = instTiers[idxStart,:]
                momTmp = momTmp - momTmp[0,0]
                phonSegLbl.append(lblTmp)
                phonSegInst.append(momTmp)

            idx_sig = [x for x in range(int(inst_tmp[0] * sr),
                                        int(inst_tmp[1] * sr)+1) if x < len(self.signal)]
            phon_tmp.signal = x[np.unique(idx_sig)]

            if f0 is not None and isSeg:
                f02 = [f0[x] for x in range(len(f0)) if (tf0[x] >= inst_tmp[0]
                                                         and tf0[x] <= inst_tmp[1])]
                tf02 = [x for x in tf0 if (x >= inst_tmp[0] and x <= inst_tmp[1])]
                phon_tmp.gross_fundamental_frequency = f02
                phon_tmp.gross_f0_time_vector = tf02

            if formants is not None and isSeg:
                tform = formants.time_vector
                idx_form = [x for x in range(len(tform)) if (tform[x] >= inst_tmp[0]
                                                             and tform[x] <= inst_tmp[1])]
                phon_tmp.formants = Formants('frequency',
                                             formants.frequency[:, idx_form],
                                             'bandwidth', formants.bandwidth[:, idx_form],
                                             'damping', formants.bandwidth[:, idx_form],
                                             'amplitude', formants.amplitude[:, idx_form],
                                             'time_vector', formants.time_vector[idx_form])
            phon_tmp.phonetic_labels = phonSegLbl
            phon_tmp.phonetic_instants = phonSegInst
            segments.append(phon_tmp)

        for k in range(len(segments)):
            if k == 0:
                segments[k].following_phoneme = segments[k+1]
            elif k == len(segments)-1:
                segments[k].previous_phoneme = segments[k-1]
            else:
                segments[k].following_phoneme = segments[k+1]
                segments[k].previous_phoneme = segments[k-1]

        return segments

    def simulmicdisto(self, phonemes, coeff, tiers=1, dist_thresh=1.2):

        if self.phonetic_labels is None:
            raise ValueError('No phonetic segmentation. Please perform speech-text alignment')
        labels = self.phonetic_labels[tiers-1]
        instants = self.phonetic_instants[tiers-1]

        x_modif = self.signal.copy()
        max_sig = np.max(np.abs(x_modif)) * dist_thresh
        sr = self.sampling_frequency

        for k in range(len(phonemes)):
            x_modif = speechmodif(x_modif, sr, phonemes[k],
                                  coeff[k], labels, instants)

        self.signal = x_modif

        return self

    def speechresample(self, sro):

        sr = self.sampling_frequency;
        if sr != sro:
            sig = self.signal;
            num = int(sro * len(sig) / sr)
            sig_output = scipy.signal.resample(sig, num)
            self.signal = sig_output;
            self.sampling_frequency = sro;
        else:
            print('Warning : The output sampling frequency '
                  'is the same as the input. Nothing''s done!')

    def computeVQ(self, nwin=1024, novlp=None, nfft=None, meth="rms"):

        if self.voiced is None or self.unvoiced is None:
            raise ValueError("No separation has been done. Please run X-GLOS")

        sr = self.sampling_frequency;
        tvec = np.arange(0, len(self.signal)) / sr

        if novlp is None:
            novlp = int(nwin * 3 / 4)
        if nfft is None:
            nfft = 2**nextpow2(sr)

        V = self.voiced
        U = self.unvoiced

        if meth.lower() == "spectro":
            Sxx_V, fxx, txx = V.computespectrogram(nwin, novlp=novlp, nfft=nfft)
            Sxx_U, _, _ = U.computespectrogram(nwin, novlp=novlp, nfft=nfft)

            Den = np.sum(abs(Sxx_U)**2, 0) + np.sum(abs(Sxx_V)**2, 0)
            grossVQ = np.sum(abs(Sxx_V)**2, 0) / Den
            grossHNR = 20*np.log10(abs((np.sum(abs(Sxx_V)**2, 0))/
                                       (np.sum(abs(Sxx_U)**2, 0))))
        elif meth.lower() == "rms":
                nhop = nwin - novlp
                Vbuff = buffer(V.signal, nwin, nhop)
                Ubuff = buffer(U.signal, nwin, nhop)
                nFrame = Vbuff.shape[1]
                txx = np.arange(0,len(self.signal) - 1, nhop) / sr
                txx = txx[:nFrame] + nwin / sr / 2

                grossVQ = np.zeros(nFrame)
                grossHNR = np.zeros(nFrame)
                w = scipy.signal.hann(nwin)

                for k in range(nFrame):
                    xpt = Vbuff[:,k] * w
                    xpt = xpt - np.mean(xpt)
                    xnt = Ubuff[:,k] * w
                    xnt = xnt - np.mean(xnt)
                    grossVQ[k] = ((np.linalg.norm(xpt,2)**2)/
                                  (np.linalg.norm(xpt,2)**2+np.linalg.norm(xnt,2)**2))**2
                    grossHNR[k] = ((np.linalg.norm(xpt,2)**2)/(np.linalg.norm(xnt,2)**2))**2
        else:
             raise ValueError("The method to compute VQ does not exist. Please choose either spectro or rms")

        VQ = lininterp1(txx, grossVQ, tvec) * 100
        VQ[VQ < 0] = 0
        VQ[VQ > 100] = 100
        HNR = lininterp1(txx, grossHNR, tvec)

        self.voicing_quotient = VQ
        self.hnr = HNR

        if self.time_vector is None:
            self.time_vector = tvec

        return VQ, HNR
class SpeechSegment(SpeechAudio):

    phoneme_label = None
    phonetic_class = None
    voiced = None
    previous_phoneme = None
    following_phoneme = None
    context = None
    mean_formants = None
    mean_fundamental_frequency = None

    mean_hnr = None
    mean_vq = None
    dispersion_formants = None
    dispersion_fundamental_frequency = None
    dispersion_hnr = None
    dispersion_vq = None
    jitter = None
    shimmer = None
    devoing_index = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def getdevoicing(self):

        phm1 = self.previous_phoneme
        if phm1 is None:
            phm1 = SpeechSegment('voicing_quotient', 0)

        if phm1.phoneme_label == '#':
            phm1.voicing_quotient = 0

        php1 = self.following_phoneme
        if php1 is None:
            php1 = SpeechSegment('voicing_quotient', 0)

        if php1.phoneme_label == '#':
            php1.voicing_quotient = 0

        if ((self.voicing_quotient is None) or
                (phm1.voicing_quotient is None) or
                (php1.voicing_quotient is None)):
            raise PhoneError('Phonemes has no voicing_quotient, '
                             'please compute the voicing quotient')

        maxm1 = max(phm1.voicing_quotient)
        maxp1 = max(php1.voicing_quotient)
        minvq = min(self.voicing_quotient)
        maxadj = max(maxm1, maxp1)
        devoicingIndex = maxadj - minvq
        self.devoicing_index = devoicingIndex

        return devoicingIndex

    def getphoninfo(self):

        ph = self.phoneme_label
        oral_vowel_dict = ['a', 'e', 'i', 'o', 'u', 'y', 'A', 'E', 'O', 'I',
                           'U', 'Y', '}', '2', '@', '6', '7', '8', '9', 'V',
                           '&', '3', 'Q', '{', 'a/', 'e/', 'i/', 'o/', 'u/',
                           'y/', 'A/', 'E/', 'O/', 'I/', 'U/', 'Y/', '}/',
                           '2/', '@/', '6/', '7/', '8/', '9/', 'V/', '&/', '3/',
                           'Q/', '{/', '^']
        nasal_vowel_dict = ['a~', 'e~', 'i~', 'o~', 'u~', 'y~', 'A~', 'E~',
                            'O~', 'I~', 'U~', 'Y~', '}~', '2~', '@~', '8~',
                            '7~', 'V~', '&~', '6~', '3~', '3\~', 'Q~', '{~', '@\~']
        voiced_fricative = ['z', 'Z', 'v']
        voiceless_fricative = ['s', 'S', 'f', 'C', 'X', 'x']
        voiced_plosive = ['b', 'd', 'g', '_b', 'b_', '_d', 'd_', 'g_', '_g']
        voiceless_plosive = ['p', '_p', 'p_', 't', 't_', '_t', 'k', 'k_', '_k']
        liquids = ['l', 'r', 'L', 'R']
        nasal_consonants = ['m', 'n']

        if ph in oral_vowel_dict:
            self.phonetic_class = 'oral vowel'
            self.voiced = True
        if ph in nasal_vowel_dict:
            self.phonetic_class = 'nasal vowel'
            self.voiced = True
        if ph in voiced_fricative:
            self.phonetic_class = 'fricative'
            self.voiced = True
        if ph in voiceless_fricative:
            self.phonetic_class = 'fricative'
            self.voiced = False
        if ph in voiced_plosive:
            self.phonetic_class = 'plosive'
            self.voiced = True
        if ph in voiceless_plosive:
            self.phonetic_class = 'plosive'
            self.voiced = False
        if ph in liquids:
            self.phonetic_class = 'liquid'
            self.voiced = True
        if ph in nasal_consonants:
            self.phonetic_class = 'nasal_consonant'
            self.voiced = True

    def getstats(self, meth='central'):

        if meth.lower() not in ['central', 'mean', 'median']:
            raise MethError('Method is not recongnized. Please choose either mean or median')

        if meth.lower() == 'mean':
            self.mean_formants = np.mean(self.formants, axis=1)
            self.dispersion_formants = np.std(self.formants, axis=1)
            self.mean_fundamental_frequency = np.mean(self.gross_fundamental_frequency)
            self.dispersion_fundamental_frequency = np.std(self.gross_fundamental_frequency)
            self.mean_hnr = np.mean(self.hnr)
            self.dispersion_hnr = np.std(self.hnr)
            self.mean_vq = np.mean(self.voicing_quotient)
            self.dispersion_vq = np.std(self.voicing_quotient)
        if meth.lower() == 'median':
            self.mean_formants = np.median(self.formants, axis=1)
            self.dispersion_formants = sst.median_abs_deviation(self.formants, axis=1)
            self.mean_fundamental_frequency = np.median(self.gross_fundamental_frequency)
            self.dispersion_fundamental_frequency = \
                sst.median_abs_deviation(self.gross_fundamental_frequency)
            self.mean_hnr = np.median(self.hnr)
            self.dispersion_hnr = sst.median_abs_deviation(self.hnr)
            self.mean_vq = np.median(self.voicing_quotient)
            self.dispersion_vq = np.median_abs_deviation(self.voicing_quotient)
        if meth.lower() == 'central':
            numFor = self.formants.shape[1]
            isOdd = np.mod(numFor, 2)
            if isOdd:
                self.mean_formants = self.formants[:, numFor / 2 - 0.5]
            else:
                self.mean_formants = \
                    np.mean(self.formants[:, numFor / 2 - 1:numFor / 2 + 1], axis=1)
            numFor = len(self.gross_fundamental_frequency)
            isOdd = np.mod(numFor, 2)
            if isOdd:
                self.mean_fundamental_frequency = self.gross_fundamental_frequency[numFor / 2 - 0.5]
            else:
                self.mean_fundamental_frequency = \
                    np.mean(self.gross_fundamental_frequency[numFor / 2 - 1:numFor / 2 + 1])
            if self.hnr != []:
                numFor = len(self.voicing_quotient)
                isOdd = np.mod(numFor, 2)
                if isOdd:
                    self.mean_hnr = self.hnr[numFor / 2 - 0.5]
                    self.mean_vq = self.voicing_quotient[numFor / 2 - 0.5]
                else:
                    self.mean_hnr = np.mean(self.hnr[numFor / 2 - 1:numFor / 2 + 1])
                    self.mean_vq = np.mean(self.voicing_quotient[numFor / 2 - 1:numFor / 2 + 1])

def sound2sp(x, sp=None):

    if sp is not None:
        # spOut = sp.copy()
        sp.signal = copy.deepcopy(x.values.squeeze())
        sp.sampling_frequency = x.sampling_frequency
        spOut = sp.copy()
        # sp = spOut.copy()
    else:
        spOut = SpeechAudio('signal', x.values.squeeze(),
                         'sampling_frequency', x.sampling_frequency)
    return spOut

def sp2sound(x):

    sound = parselmouth.Sound(x.signal)
    sound.sampling_frequency = x.sampling_frequency

    return sound
