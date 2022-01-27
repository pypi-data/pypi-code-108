#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 13:56:52 2020

@author: benjamin
"""

import numpy as np
from .utils import (nextpow2, symmetricifft, cepstrum, buffer,
                    flatten_ceps, flatten_ceps_matrix, optimize_cepstrum, 
                    get_order_from_sig)
import scipy.signal as ssg

def change_cepstrum(x2, Spx2, x_out, nwin, nhop, nfft, txx, isFlat, isNorm,
                    Sxx, Sxx_target):
    
    xwin_fft, xx_win = overlap_fft(x2, nwin, nhop, nfft)
    if isFlat:
        CepOrder = get_order_vec(Spx2, txx)
        xwin_fft = flatten_ceps_matrix(xwin_fft, xx_win, 
                                           CepOrder, Spx2.sampling_frequency)
        Sxx = 1
    xwin_fft = xwin_fft * np.abs(Sxx_target) / np.abs(Sxx)
    xnew = symmetricifft(xwin_fft, nfft)
    x_out = overlap_add(xnew, xx_win, x_out, nhop, isNorm)
    x_out[np.isnan(x_out)] = 0
    return x_out

def ola_param(nwin, novlp=None, sr=None):
    
    if novlp is None:
            novlp = int(nwin * 3 / 4)
    novlp = int(novlp)
    if sr is None:    
        nfft = int(nwin)
    else:
        nfft = 2**nextpow2(sr)
        
    nhop = nwin - novlp
    return novlp, nfft, nhop

def init_ola(x, nwin, nhop):
    
    zeros2add = np.zeros((nhop, 1))
    x2 = np.vstack((zeros2add, x.reshape(-1, 1), zeros2add)).squeeze()
    x_out = np.zeros_like(x2)
       
    return x2, x_out

def get_order_vec(sp, tx):
    
    pitch = sp.getpitch()
    pitch.timeinterpolate(tx)
    f0 = pitch.values
    f0[np.isnan(f0)] = 125
    f0[f0<=0] = 125
    return 2 * np.round(sp.sampling_frequency / f0)

def check_index(x, k, nwin, nhop):
    
    w = ssg.hann(nwin)
    deb = int(k * nhop)
    fin = deb + nwin - 1
    isC = True
    if fin > len(x) - 1:
        fin = len(x) - 1
        isC = False
    idx = np.arange(deb, fin+1).astype(int)
    xwin = x[idx] * w[:len(idx)]
    
    return xwin, idx, isC

def spec_frame(x, k, nwin, nhop, nfft):
    
    L = int(nfft / 2 + 1)
    xwin, idx, isC = check_index(x, k, nwin, nhop)
    fft_xwin = np.fft.fft(xwin, nfft)[:L]
    
    return xwin, fft_xwin, isC, idx

def change_frame(fft_xwin, h_new, h_orig, nfft, idx, x_out, xwin, 
                 isChange=True, isNorm=True, sr=8000):
    
    init_en = sum(abs(xwin)**2)
    if init_en != 0 or not np.isnan(init_en):        
        if isChange:
            order = get_order_from_sig(xwin, sr)
            fft_xwin, Cx_flat = flatten_ceps(xwin, fft_xwin, sr, order, tol=1e-4)
            # fft_new = optimize_cepstrum(xwin, fft_xwin, h_new, Cx_flat, sr,
            #   order, max_iter=10)
            fft_new = fft_xwin * abs(h_new) #  / abs(h_orig)
            x_new = symmetricifft(fft_new, nfft)
        else: 
            x_new = xwin
        
        x2add = x_new[:len(idx)]    
        new_en = sum(abs(x2add)**2)
        if new_en == 0 or np.isnan(new_en):            
            pass
        else:
            if isNorm:
                x_out[idx] = x_out[idx] + x2add * init_en / new_en
            else:
                x_out[idx] = x_out[idx] + x2add  
    
    return x_out

def check_frame(k, isC, maxFrame):
    
    k += 1
    if k >= maxFrame:
        isC = False
        
    return k, isC

def overlap_add(x_transformed, x_initial, x_out, nhop, isNorm=True):
    
    new_en = np.sum(np.abs(x_transformed**2), 0)    
    nb_win, nb_frame = x_transformed.shape
    
    if isNorm:
        init_en = np.sum(np.abs(x_initial**2), 0)
        init_en[new_en == 0] = 1
        new_en[new_en == 0] = 1
        ratio_en = init_en / new_en
        ratio_en[np.isnan(ratio_en)] = 1
    else:
        ratio_en = np.ones(nb_frame)
    
    idx1 = 0
    for k, x_add in enumerate(x_transformed.T):
        
        idx2 = idx1 + nb_win
        if idx2 >= len(x_out):
            idx2 = len(x_out)
        x_out[idx1:idx2] += x_add[:idx2-idx1] * ratio_en[k]
        idx1 += nhop
        
    return x_out[nhop:-nhop] / 1.5

def overlap_fft(x, nwin, nhop, nfft):
    
    xx = buffer(x, nwin, nhop)
    L = int(nfft/2+1)
    w = ssg.hann(nwin)
    xx_win = xx * w.reshape(-1,1)
    xwin_fft = np.fft.fft(xx_win, nfft, axis=0)[:L, :]
    return xwin_fft, xx_win