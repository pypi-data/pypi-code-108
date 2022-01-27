#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 15:48:04 2019

@author: benjamin
"""

import numpy as np
import scipy
from .praattools import (sp2sound, praat_get_pitch)

def symmetricifft(x, nfft=None):
    """ returns the IFFT by symmetric inverse Fourier transform """
    if len(x.shape) == 1:
        x = x.reshape(-1,1)
    xconj = np.conj(x[-2:0:-1,:])
    xconc = np.concatenate((x, xconj), 0)
    if nfft is None:
        nfft = len(xconc)
    y = np.real(np.fft.ifft(xconc, nfft, axis=0))

    return np.squeeze(y)

def window(nwin, win_type):
    
    if win_type == 'hann':
        return scipy.signal.hann(nwin)
    elif win_type == 'hanning':
        return scipy.signal.hanning(nwin)
    elif win_type == 'hamming':
        return scipy.signal.hamming(nwin)
    else:
        raise ValueError('Wrong type of window')

def freq2mel(freq):
    """ converts frequency in mel scale """
    return 2595 * np.log10(1 + freq / 700)

def mel2freq(mel):
    """ converts mels to frequency scale """
    return 700 * (10**(mel / 2595) - 1)

def mel_filter_bank(sr, fmin=0, fmax=None, nb_filter=24, nfft=1024):
    """ compute mel filter banks for MFCC computation """
    if fmax is None:
        fmax = int(sr / 2)
        
    fmin_mel = freq2mel(fmin)
    fmax_mel = freq2mel(fmax)

    mels = np.linspace(fmin_mel, fmax_mel, num=nb_filter+2)
    mel_freqs = mel2freq(mels)
    
    center_freq = np.floor((nfft + 1) / sr * mel_freqs).astype(int)

    filters = np.zeros((len(center_freq)-2, int(nfft/2+1)))
    
    for n in range(len(center_freq)-2):
        filters[n, center_freq[n] : center_freq[n + 1]] = np.linspace(0, 1, center_freq[n + 1] - center_freq[n])
        filters[n, center_freq[n + 1] : center_freq[n + 2]] = np.linspace(1, 0, center_freq[n + 2] - center_freq[n + 1])
    
    enorm = 2.0 / (mel_freqs[2:nb_filter+2] - mel_freqs[:nb_filter])
    filters *= enorm[:, np.newaxis]
    
    return filters, mels, mel_freqs

def dct(dct_filter_num, filter_len):
    """ computes DCT basis """
    basis = np.empty((dct_filter_num,filter_len))
    basis[0, :] = 1.0 / np.sqrt(filter_len)
    
    samples = np.arange(1, 2 * filter_len, 2) * np.pi / (2.0 * filter_len)

    for i in range(1, dct_filter_num):
        basis[i, :] = np.cos(i * samples) * np.sqrt(2.0 / filter_len)
        
    return basis

def delta(x):
    nb_feat, nb_frame = x.shape
    y = np.zeros_like(x)
    for k in range(nb_frame):
        if k == 0:
            y[:,k] = 0.5 * x[:,k+1]
        elif k == nb_frame - 1:
            y[:,k] = - 0.5 * x[:,k-1]
        else:
            y[:,k] = 0.5 * (x[:, k+1] - x[:, k-1])
            
    return y

def dfw(x, f_input, form_input, form_output):
    """ frequency warping of cepstral envelope such that peaks match target formants """
    in_form = form_input
    in_form = np.insert(in_form, 0, 0)
    in_form = np.append(in_form, f_input[-1])

    out_form = np.insert(form_output, 0, 0)
    out_form = np.append(out_form, f_input[-1])

    for k in range(5):
        fTmp = lin_freq(f_input, in_form[k:k+2], out_form[k:k+2])
        if k == 0:
            f_output = fTmp
        else:
            f_output = np.vstack((f_output.reshape(-1,1), fTmp.reshape(-1,1)))

    f_output = f_output[:len(f_input)]

    f1 = scipy.interpolate.interp1d(f_input, x, kind='quadratic', 
                                    fill_value='extrapolate')
    return f1(f_output.squeeze())

def dfw_matrix(x, f_input, form_input, form_output):
    """ frequency warping of cepstral envelope such that peaks match target formants """
    
    nb_frame = form_input.shape[1]
    nb_freq = len(f_input)
    in_form = form_input
    in_form = np.insert(in_form, 0, 0, axis=0)
    in_form = np.append(in_form, f_input[-1]*np.ones(nb_frame).reshape(1,-1),
                        axis=0)

    out_form = np.insert(form_output, 0, 0, axis=0)
    out_form = np.append(out_form, f_input[-1]*np.ones(nb_frame).reshape(1,-1),
                        axis=0)
    f_output_fin = np.zeros((nb_freq, nb_frame))
    for k1 in range(nb_frame):
        if np.linalg.norm(in_form[1:-1, :] - out_form[1:-1, :]) > 1:
            for k in range(5):
                fTmp = lin_freq(f_input, in_form[k:k+2, k1], out_form[k:k+2, k1])
                if k == 0:
                    f_output = fTmp
                else:
                    f_output = np.vstack((f_output.reshape(-1,1), 
                                          fTmp.reshape(-1,1)))
        else:
            f_output = f_input
        f_output = np.unique(f_output.squeeze())
        f_output_fin[:,k1] = (f_output / max(f_output) * (len(f_output) - 1))
    f_output = f_output_fin
    nb_form = f_output.shape[0]    
    xx, yy = np.meshgrid(np.arange(0, nb_frame), f_input / max(f_input) * len(f_input))
    xxf = xx.flatten()
    output = scipy.ndimage.interpolation.map_coordinates(x, 
                                                         [f_output.flatten(), xxf],
                                                         order=1,
                                                         mode="constant",
                                                         prefilter=False)
    return output.reshape((nb_form, nb_frame))

def lin_freq(f, F1, Fp1):
    """ returns linear relationship for piece-wise linear warping """
    f_1 = [x for x in f if x >= F1[0] and x<= F1[1]]
    return (Fp1[1] - Fp1[0]) / (F1[1] - F1[0]) * np.array(f_1 - F1[0]) + Fp1[0]

def ceps2peaks(x, freq, fxx):
    
    x = abs(x)
    indx = scipy.signal.argrelextrema(x, np.greater)
    freq_tmp = fxx[indx]
    try:
        out = np.sort([freq_tmp[np.argmin(abs(freq_tmp - x))] for x in freq])
    except:
        out = freq
        
    return out

def get_order_from_sig(x, sr):
    snd = sp2sound(x, sr)
    f0, tf0 = praat_get_pitch(snd, f0min=70, f0max=300)
    f0 = np.nanmedian(f0)
    return get_order_ceps(f0, sr)

def cepstrum(x, sr, order, toldB=None):
    
    if toldB is not None:
        return true_envelope(x, sr, toldB, order)
    else:
        fft_win = abs(np.fft.fft(x))
        fft_win[fft_win==0] = 1e-51
        logx = np.log(fft_win)
        nwin = len(x)
        L = int(nwin / 2 + 1)
        return np.exp(cepstral_filtering(logx, nwin, order)[:L])

def check_converge(x, xm1):
    return x < xm1
    
def flatten_ceps(xwin, fft_xwin, sr, order, tol=1e-7):
    
    Cxwin = cepstrum(xwin, sr, order)
    var_ceps = np.var(Cxwin)
    nfft = len(xwin)
    isConverge = True
    nb_iter = 0
    while (var_ceps > tol and nb_iter < 30 and isConverge):
    
        fft_new = fft_xwin / np.abs(Cxwin)
        x_flat = symmetricifft(fft_new, nfft=nfft)
        Cxnew = cepstrum(x_flat, sr, order)        
        isConverge = check_converge(np.var(Cxnew), var_ceps)
        if not isConverge:
            return fft_xwin, Cxwin
        var_ceps = np.var(Cxwin)
        fft_xwin = fft_new
        Cxwin = Cxnew
    return fft_xwin, Cxwin

def flatten_ceps_matrix(x_win_fft, x_win, CepOrder, sr):
    
    nb_win, nb_frame = x_win_fft.shape
    x_win_flat = np.zeros_like(x_win_fft)
    for k in range(nb_frame):    
        if np.floor(CepOrder[k] / 2) == CepOrder[k] / 2:
            CepOrder[k] -= 1
        x_win_flat[:, k], Cx_flat = flatten_ceps(x_win[:,k], x_win_fft[:,k],
                                                    sr, CepOrder[k], tol=1e-4)
    return x_win_flat
    
def optimize_cepstrum(xwin, fft_xwin, Cx_target, Cx_flat, sr, order, max_iter=30):
    nb_iter = 0
    err = np.linalg.norm(Cx_flat - Cx_target)**2
    nfft = len(xwin)
    isConverge = True
    while nb_iter < max_iter and isConverge:
        
        fft_new = fft_xwin / np.abs(Cx_flat) * Cx_target
        new_x = symmetricifft(fft_new, nfft=nfft)
        Cx_flat = cepstrum(new_x, sr, order)        
        isConverge = check_converge(np.linalg.norm(Cx_flat - Cx_target)**2, 
                                    err)
        if not isConverge:
            return fft_xwin
        err = np.linalg.norm(Cx_flat - Cx_target)**2
        nb_iter += 1
        fft_xwin = fft_new
        
    return fft_new

def time_ceps_transform(Sxx, transOper, nfft):
    
    L = int(nfft / 2 + 1)
    nord = transOper.shape[0]
    ceps_coeff = symmetricifft(20 * np.log10(np.abs(Sxx)), nfft)[:nord, :]
    ceps_coeff = scipy.stats.zscore(ceps_coeff)
    cepsT = transOper @ ceps_coeff
    cepsT2 = scipy.stats.zscore(cepsT)
    Sxx_trans = 10**(np.real(np.fft.fft(cepsT2, nfft, axis=0))[:L, :] / 20)
    Sxx_in = 10**(np.real(np.fft.fft(ceps_coeff, nfft, axis=0))[:L, :] / 20)
    
    return Sxx_in, Sxx_trans

def freq_ceps_transform(Sxx, transOper, freq_out, fxx):
    
    Sxx_in = scipy.stats.zscore(Sxx)
    Sxx_trans = transOper @ Sxx_in
    Sxx_trans = scipy.stats.zscore(Sxx_trans)    
        
    return Sxx_in, Sxx_trans

def ceps_transform(Sxx, transOper, nwin, novlp, fxx=None, freq_out=None, method='linear'):
    """ cepstral transformation """
    
    nfft = nwin
    if freq_out is None:
        Sxx_in, Sxx_trans = time_ceps_transform(Sxx, transOper, nfft)
    else:
        Sxx_in, Sxx_trans = freq_ceps_transform(Sxx, transOper, freq_out, fxx)

    return Sxx_in, Sxx_trans

def get_order_ceps(f0, sr):
    """ returns the optimal cepstral order based on pitch estimation """

    if np.nanmedian(f0) < 0:
        f0 = 125
    else:
        f0 = np.nanmedian(f0)

    if f0 <= 0:
        f0 = 125
    CepOrder = 2 * np.round(sr / f0)

    if np.floor(CepOrder / 2) == CepOrder / 2:
        CepOrder -= 1

    return int(CepOrder)

def cepstral_filtering(logx, nwin, order=None):
    """ cepstral liftering """
    xRealCep = np.real(np.fft.ifft(logx))
    wzp = np.zeros_like(xRealCep)

    CepOrder = int(order)
    midOrdp1 = int((CepOrder+1)/2-1)
    midOrdm1 = int((CepOrder-1)/2)

    winCeps = scipy.signal.hann(CepOrder)
    wzp = np.concatenate((winCeps[midOrdp1:CepOrder],
                          np.zeros(nwin - CepOrder),
                          winCeps[:midOrdm1]))

    liftCeps = wzp * xRealCep
    xEnv = np.real(np.fft.fft(liftCeps, nwin, axis=0))

    return xEnv

def true_envelope(x, sr, toldB=2, order=None):
    """ returns the true envelope of x """
    nwin = len(x)
    Ao = np.log(abs(np.fft.fft(x)))
    Vo = -np.inf * np.ones_like(Ao)
    while any(20*np.log10(np.exp(Ao)/np.exp(Vo)) > toldB):
        Ao = np.maximum(Ao, Vo)
        Vo = cepstral_filtering(Ao, nwin, order)

    return Vo

def esprit(x, sr = 1, K = 12):
    """ estimate the frequency of the damped sinusoids that model x """
    
    idx = np.argmax(x)
    x = x[idx:]
    x = x - np.mean(x)
    
    M = int(min(100, np.floor(len(x) / 2)))
    Nl = len(x) - M + 1
    Nt = int(Nl / M)
    
    R = np.zeros((M,M))
    for k in range(Nt):
        deb = int(k * M)
        fin = int(deb + 2 * M - 1)
        xtmp = x[deb:fin]
    
        H = scipy.linalg.hankel(xtmp[0:M], xtmp[M - 1:])
        R += H.dot(H.T)
        
    u, s, d = np.linalg.svd(R)
    nx, ny = u.shape
    
    Up = u[1:,:K]
    Um = u[:-1,:K]
    Phi = np.linalg.pinv(Um).dot(Up)
    z,w = np.linalg.eig(Phi)
    freq = np.angle(z) / 2 / np.pi * sr
    
    return np.sort(freq[freq > 50])

def z2freqz(p, z, sr=2*np.pi, nfft=None):
    
    if nfft is None:
        nfft = 2**nextpow2(sr)
    L = int(nfft / 2 + 1)
    b = np.poly(z)
    a = np.poly(p)
    return scipy.signal.freqz(b, a, L, fs=sr)
    
def fill_nan(x):

    idxAll = np.arange(x.shape[0])
    idxVal = np.where(np.isfinite(x))
    try:
        f = scipy.interpolate.interp1d(idxAll[idxVal], x[idxVal], 
                                   kind='cubic', fill_value='extrapolate')
    except:
        f = scipy.interpolate.interp1d(idxAll[idxVal], x[idxVal], 
                                   kind='linear', fill_value='extrapolate')
    return np.where(np.isfinite(x), x, f(idxAll))

def fill_nan_and_zero(x):
    
    y = fill_nan(x)
    first_non_zero = np.argwhere(y>0)[0][0]
    last_non_zero = len(y) - np.argwhere(y[::-1]>0)[0][0] - 1
    y[:first_non_zero] = y[first_non_zero]
    y[last_non_zero:] = y[last_non_zero]
    
    return y

def nextpow2(x):
    return int(np.ceil(np.log2(np.abs(x))))
    
def mat2column(x):
    return np.reshape(x, -1, order="F")

def column2mat(x, nb_row, nb_col):
    return np.reshape(x, (nb_row, nb_col), order="F")
    
def buffer(x, nwin, nhop):    
    
    if len(x) > nwin:
        nX = len(x)    
        idx1 = int(nhop)
        nFrame = int(np.ceil(nX / nhop)) 
        xOut = np.zeros((nwin, nFrame))
        xOut[:,0] = x[:nwin]
        
        for k in range(1, nFrame):
            idx2 = int(idx1 + nwin)       
            xTmp = x[int(idx1):int(idx2)]
            if idx2 >= nX:
                npad = int(idx2 - nX)
                xTmp = np.concatenate((xTmp, np.zeros(npad)))
            xOut[:,k] = xTmp
            idx1 += nhop
    
        return xOut
    else:
        return x.reshape(-1, 1)

def reject_outliers(x, thresh=3):
    """ reject outliers in x. Outliers are considered as data that are 
    at a distance more than thresh*SMAD where SMAD is the 
    scaled median absolute deviation of x"""
    
    K = 1.4826
    numF, nFrame = x.shape    
    median = np.matlib.repmat(np.median(x, axis=1).reshape(-1,1), 1, nFrame)
    diff = np.median(np.abs(x - median), axis=1)
    med_abs_deviation = np.matlib.repmat((K * diff).reshape(-1,1), 1, nFrame)
    idx = abs(x - median) < thresh * med_abs_deviation
    x_out = None
    idx_true = []

    for k in range(nFrame):
        yTmp = idx[:,k]
        if yTmp.all():
            if x_out is None:
                x_out = np.array(x[:,k]).reshape(-1,1)
            else:
                x_out = np.hstack((x_out, 
                                   np.array(x[:,k]).reshape(-1,1)))
            idx_true.append(k)

    return x_out, idx_true

def ProdMat3D(A,B):
    
    # Compute the product of 3D matrices along a single dimension
    l1, l2, l3 = A.shape
    C = np.zeros_like(A) + 1j * np.zeros_like(A)
    if l1 == 2 and l2 == 2:    
        C11 = np.zeros((1,1,l3)) + 1j * np.zeros((1,1,l3))
        C12 = np.zeros((1,1,l3)) + 1j * np.zeros((1,1,l3))
        C21 = np.zeros((1,1,l3)) + 1j * np.zeros((1,1,l3))
        C22 = np.zeros((1,1,l3)) + 1j * np.zeros((1,1,l3))
        a11 = A[0,0,:]
        a12 = A[0,1,:]
        a21 = A[1,0,:]
        a22 = A[1,1,:]
        b11 = B[0,0,:]
        b12 = B[0,1,:]
        b21 = B[1,0,:]
        b22 = B[1,1,:]
        C11[0,0,:] = a11 * b11 + a12 * b21
        C21[0,0,:] = a21 * b11 + a22 * b21
        C12[0,0,:] = a11 * b12 + a12 * b22
        C22[0,0,:] = a21 * b12 + a22 * b22
        C = np.concatenate((np.concatenate((C11,C12),1),np.concatenate((C21,C22),1)),0);
    else:
        for k in range(l3):    
            C[:,:,k] = np.dot(A[:,:,k],B[:,:,k])        
    return C
    
def ChainMatrix(af, lf, freq, param, meth='tmm',  Tf=None):
    lw = len(freq)
    if Tf is None:
        Tf = np.tile(np.eye(2).reshape((2,2,1)),(1, 1, lw))

    A = np.zeros((1,1,lw)) + 1j * np.zeros((1,1,lw))
    B = np.zeros((1,1,lw)) + 1j * np.zeros((1,1,lw)) 
    C = np.zeros((1,1,lw)) + 1j * np.zeros((1,1,lw))
    Zo = af / (param.rho * param.c)

    if meth.lower() != 'cmp':
        om = param.freq * 2 * np.pi    
        S = 2 * np.sqrt(af * np.pi)        
        L = param.rho / af
        Celem = Zo / param.c        
    
    for k in range(len(af)-1,-1,-1):        
        if meth.lower() == 'cmp':
            if param.loss:
                argh = param.sig * lf[k] / param.c
            else:
                argh = 1j * om / param.c * lf[k]
                param.gam = 1
            A[0,0,:] = np.cosh(argh)
            B[0,0,:] = -1 / Zo[k] * param.gam * np.sinh(argh)
            C[0,0,:] = -Zo[k] / param.gam * np.sinh(argh)
        else:
            R = S[k]*np.sqrt(param.rho * param.mu * om) / (2 * np.sqrt(2) * af[k]**2)
            G = (param.adiabatic - 1) * S[k] / (param.rho * param.c**2) * np.sqrt(param.heat_cond * om / (2 * param.specific_heat * param.rho))
            if param.loss:
                invZw = 1 / (param.wr / S[k]**2 + 1j*om*param.wm / S[k]**2 + 1 / (1j * om * S[k]**2 / param.wc)) * param.wallyield
                gam = np.sqrt((R + 1j * om * L[k]) * (G + 1j * om * Celem[k] + invZw))
            else:
                gam = 1j * om / param.c

            A[0,0,:] = np.cosh(gam * lf[k])
            B[0,0,:] = -np.sinh(gam * lf[k]) / Zo[k]
            C[0,0,:] = -Zo[k] * np.sinh(gam * lf[k])            
        Tn = np.concatenate((np.concatenate((A,B),1),np.concatenate((C,A),1)),0)
        Tf = ProdMat3D( Tf, Tn )
    
    A = Tf[0,0,:].reshape(-1)
    B = Tf[0,1,:].reshape(-1)
    C = Tf[1,0,:].reshape(-1)
    D = Tf[1,1,:].reshape(-1)
    
    return A, B, C, D, Tf

def Cosine_interp( xi, yi, xo ):
 # Cosine interpolation at points xo

    xa = xi[0]
    xb = xi[-1] 
    nTubes, nPt = yi.shape
    if min(nTubes, nPt) == 1:
        yi = yi.squeeze()
        ya = yi[0]
        yb = yi[-1]
    else:
        ya = yi[:,0] 
        yb = yi[:,-1]
    dy = yb-ya
    Xo = (xo-xa)/(xb-xa)*np.pi+np.pi
    
    if dy.size > 1:
        [Xm, Ym] = np.meshgrid(Xo, dy)
        [ XMdum, Ya ] = np.meshgrid(Xo, ya)
    else:
        Ya = ya
        Xm = Xo
        Ym = dy
    return Ya+1/2*(1+np.cos(Xm))*Ym
    
def findelements(a, b):
    # find indices of elements in a that contains elements in b
    nB = len(b)
    idx = []
    
    for k in range(nB):
        bTmp = b[k]
        idxTmp = [i for i,x in enumerate(a) if x==bTmp]
        if idxTmp != []: 
            if idx == []:
                idx = idxTmp
            else:
                idx = np.concatenate((idx, idxTmp)).astype(int)
                
    return idx

def lininterp1(xi, yi, xo, axis=1):
    
    if type(xi) is list:
        f1 = scipy.interpolate.interp1d(xi, yi, 'linear', 
                                        fill_value='extrapolate')
    else:
        while axis >= len(yi.shape): 
            axis -= 1        
        f1 = scipy.interpolate.interp1d(xi, yi, 'linear',
                                        fill_value='extrapolate', axis=axis)
   
    return f1(xo)

def modiffric(x, nwin=512, novlp=None, filt_coeff=[1,-0.9]):
    
    if novlp is None:
        novlp = np.ceil(nwin * 3 / 4)
    nhop = nwin - novlp
    xbuff = buffer(x, nwin, nhop)
    
    nFrame = xbuff.shape[1]
    y = np.zeros_like(x)
    w = scipy.signal.hann(nwin)
    
    for k in range(nFrame):
        deb = int((k - 1) * nhop)
        fin = int(deb + nwin - 1)
        if fin > len(y):
            y = np.concatenate((y.reshape(-1), np.zeros(nwin)))

        idx = [x for x in range(deb,fin+1)]
        xwin = xbuff[:,k] * w
        x_new = scipy.signal.lfilter([1],filt_coeff, xwin)
        x_new = x_new * (np.std(xwin) / np.std(x_new))
        y[idx] += x_new

    return y[:len(x)]/1.5

def speechmodif(x, sr, phoneme, modif_coeff, labels, instants):
    
    envelope = np.ones(x.shape)
    if phoneme in ['p', 'k', 't']:
        isBurst = True
        isFric = False
    if phoneme in ['f', 'v']:
        isBurst = False
        isFric = True
    if phoneme not in ['f', 'v', 'p', 'k', 't']:
        isBurst = False
        isFric = False
        
    phonemePlus = [phoneme, phoneme + '_']
    idx = findelements(labels, phonemePlus)

    if idx == []:
        # print('Warning : phoneme ' + phoneme + ' not found')
        return x
    
    for k in range(len(idx)):    
        
        idxtmp = idx[k]
        idx_init = int(instants[idxtmp,0] * sr)
        idx_final = int(instants[idxtmp,1] * sr)
        if k !=len(idx)-1:
            if idx[k+1] == idxtmp + 1:                
                k = k+1
                idx_final = int(instants[idxtmp+1,1] * sr)
        idx_p = [x for x in range(idx_init, idx_final+1)]

        tr_dur = 0.01
        tr_size = np.floor(tr_dur * sr)
        if np.mod(tr_size, 2):
            tr_size = tr_size - 1

        win = scipy.signal.hann(int(tr_size))
        winup = win[:int(tr_size / 2)]
        windown = win[int(tr_size / 2 - 1):]
        if isBurst:
#              try
#                 yTmp = modifburst(x[idx_p], sr, modif_coeff)
#                 x[idx_p] = yTmp
#                   print('Burst enhancement working')
#             except
#                 print('Burst enhancement did not work')
                envelope[idx_p] = modif_coeff * np.ones(len(idx_p))
                rise_start = int(idx_p[0] - tr_size / 4 - 1)
                if rise_start < 0:
                    rise_start = 0
                rise_end = rise_start + len(winup)
                # rise_end = int(idx_p[0] - tr_size / 4 + len(winup)-1)
                envelope[rise_start:rise_end] = 1 + (modif_coeff-1) * winup

                fall_start = int(idx_p[-1] - tr_size / 4 - 1)
                fall_end = int(idx_p[-1] - tr_size / 4 + len(windown) - 1)
                envelope[fall_start:fall_end] = 1 + (modif_coeff - 1) * windown
#             end
        else:
            envelope[idx_p] = modif_coeff * np.ones(len(idx_p))   
            rise_start = int(idx_p[0] - tr_size / 4 - 1)
            # rise_end = int(idx_p[0] - tr_size / 4 + len(winup)-1)
            if rise_start < 0:
                rise_start = 0
            rise_end = rise_start + len(winup)
            envelope[rise_start:rise_end] = 1 + (modif_coeff-1) * winup
            fall_start = int(idx_p[-1] - tr_size / 4 - 1)
            fall_end = int(idx_p[-1] - tr_size / 4 + len(windown) - 1)
            envelope[fall_start:fall_end] = 1 + (modif_coeff - 1) * windown
            if isFric:
                nwin = 512
                xTmp = x[rise_start:fall_end] 
                xTmp2 = np.zeros(x.shape)
                xTmp2[:] = x
                xTmp2[rise_start:fall_end] = 0
                xTmp = np.concatenate((np.zeros(int(nwin / 2)).reshape(-1), 
                            xTmp.reshape(-1),
                            np.zeros(int(nwin / 2)).reshape(-1)))    
                yTmp = modiffric(xTmp, nwin, nwin * 3 / 4, [ 1, -0.9 ])
                idxStart = int(rise_start - nwin / 2)
                if idxStart < 0:
                    idxStart = 0
                idxStop = int(fall_end + nwin / 2)
                x2add = xTmp2[idxStart:idxStop]
                x[idxStart:idxStop] = x2add + yTmp[:len(x2add)]
 
    return x * envelope
#########################################################################
############## The following functions are from N. Ruty #################
### "N. Ruty. Modèles d'interactions fluide/parois dans le conduit vocal. 
### Applications aux voix et aux pathologies. PhD thesis, 2007 ##########
#########################################################################

def forcecompute(Ug,lg,d_Ug_dt,Ps,Psupra,xvec,h1,h2,A,B,h0,xs,hs,const):
    # calcul des 4 forces at the points i=0,1,2,3
    # l: reaction forces resulting from the pressure distribution in the flow channel LEFT from the point i
    # r: reaction forces resulting from the pressure distribution in the flow channel RIGHT from the point i
    # formules Annexe C Vilain, 
    
    
    # modification par NR le 02/04/07
    ############# New modifications by B. Elie, 2016
    #
    # d�veloppement limit� de Fr_h1 et Fl_h2, lorsque le rapport A[1]*x2/B[1] tend vers 0 (<pres ,
    # pres fix� dans init_gen) , ligne 78-89, 116-128, 193-206
    #
    # Fonction pour le calcul de la contribution des forces de pression sur les
    # masses 1 et 2
    # 
    # Param�tres d'entr�e:
    # Ug: D�bit glottique
    # Lg: largeur de la glotte,
    # d_Ug_dt: derivee du d�bit glottique
    # P: pression sous-glottique
    # Psupra: pression supra glottique
    # xvec: vecteur contenant les abscisses des masses
    # h1,h2: ouvertures au niveau des masses 1 et 2
    # A,B: coeficients des �quations des plaques
    # h0: ouverture en entr�e/sortie de constriction
    # Visco,Instat: indicateurs de prise en compte ou non de la viscosit� et de l'inertie
    # xs: abscisse du point de s�paration de l'�coulement
    # hs: ouverture au niveau du point de s�paration
    # 
    # Param�tres de sortie:
    # 
    # Fl_h2: force de pression sur la masse 2 � gauche
    # Fr_h2: force de pression sur la masse 2 � droite
    # Fl_h1: force de pression sur la masse 1 � gauche
    # Fr_h1: force de pression sur la masse 1 � droite
    
    rho = const.rho
    co_mu = const.mu
    sep = const.sep
    # initialisation des forces
    Fl_h2 = 0
    Fr_h1 = 0
    
    # assignation des abscisses � partir du vecteur xvec
    (x0, x1, x2, x3) = xvec
    pres = 1e-5
    # quelques variables temporaires
    tmp1  = 0.5*rho*(Ug**2)/(lg**2) #variable temporaire associ�e au terme de Bernoulli
    tmp2  = -12*co_mu*Ug/lg #variable temporaire associ�e au terme de Poiseuille
    tmp3  = -rho*d_Ug_dt/lg #variable temporaire li�e au terme d'inertie
    
    Fl_h1 = 0.5*(x1-x0)*lg*Ps #force sur la masse 1 � gauche, temporaire, valable en cas de fermeture
    
    if (h1>0) and (h2>0): 
        ########################################################
        ################## Fl_h1 #####################
        i1 = 1
        bern = tmp1*(1/(h0**2)-2*(Xv1(x0,x1,A,B,i1)-x0*Wv1(x0,x1,A,B,i1))/(x1-x0)**2) #     Bernoulli 
        pois = tmp2/(2*A[0])*(1/(h0**2)-2*(Xv1(x0,x1,A,B,i1)-x0*Wv1(x0,x1,A,B,i1))/(x1-x0)**2)#     Poiseuille
        inst = tmp3/A[0]*(2*(Zv1(x0,x1,A,B,i1)-x0*Yv1(x0,x1,A,B,i1))/(x1-x0)**2-np.log(h0)) #     Inertia   
        Fl_h1 = 0.5*(x1-x0)*lg*(Ps+bern+pois+inst)
        
        ########################################################
        ################## Fr_h1 #####################
        ### two cases :::: h2 < h1*sep and h2 > h1*sep ###
        if (h2 < h1*sep):
            if (abs(A[1]*x2/B[1])<pres): # Parrallel duct
                i2 = 2
    #             bern  = tmp1*(1/(h0**2)-1/(h1**2))
                bern = tmp1*(1/(h0**2)+2*(Xv1(x1,x2,A,B,i2)-x2*Wv1(x1,x2,A,B,i2))/(x2-x1)**2) #  Bernoulli
    #             pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+(x2-x1)/(h1**3))
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))-1/B[1]**3*(x1-1.5*A[1]/B[1]*x1**2+2*A[1]**2/B[1]**2*x1**3)\
                    -2/(x2-x1)**2/B[1]**3*((x2**3/3-0.375*A[1]/B[1]*x2**4+0.4*A[1]**2/B[1]**2*x2**5-\
                                           x2*(x2**2/2-0.5*A[1]/B[1]*x2**3+0.5*A[1]**2/B[1]**2*x2**4))\
                                           -(x1**3/3-0.375*A[1]/B[1]*x1**4+0.4*A[1]**2/B[1]**2*x1**5-\
                                           x2*(x1**2/2-0.5*A[1]/B[1]*x1**3+0.5*A[1]**2/B[1]**2*x1**4)))) # Poiseuille
    #             inst = tmp3*(np.log(h1ia/h0)/A[0]+(x2-x1)/h1)
                inst = tmp3*(np.log(h1/h0)/A[0]-1/B[1]*(x1-0.5*A[1]/B[1]*x1**2+1/3*A[1]**2/B[1]**2*x1**3)-\
                    2/(x2-x1)**2/B[1]*((1/3*x2**3-1/8*A[1]/B[1]*x2**4+1/15*A[1]**2/B[1]**2*x2**5-\
                                      x2*(0.5*x2**2-1/6*A[1]/B[1]*x2**3+1/12*A[1]**2/B[1]**2*x2**4))\
                                      -(1/3*x1**3-1/8*A[1]/B[1]*x1**4+1/15*A[1]**2/B[1]**2*x1**5-\
                                      x2*(0.5*x1**2-1/6*A[1]/B[1]*x1**3+1/12*A[1]**2/B[1]**2*x1**4)))) # Inertia
                  #proposition modif par NR 11/04/2007
    #             inst = tmp3*(np.log(h1/h0)/A[0]+(x2-x1)/3/h1)            
            else: #glotte formant un canal convergent ou divergent avec h2<hs
                i2 = 2 #num�ro de la plaque sur laquelle on calcule les forces
                bern = tmp1*(1/(h0**2)+2*(Xv1(x1,x2,A,B,i2)-x2*Wv1(x1,x2,A,B,i2))/(x2-x1)**2)# Bernoulli
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+1/(2*A[1])*(1/(h1**2)+2*(Xv1(x1,x2,A,B,i2)-x2*Wv1(x1,x2,A,B,i2))/(x2-x1)**2))# Poiseuille
                inst = tmp3*(np.log(h1/h0)/A[0] + 1/A[1]*(2*(x2*Yv1(x1,x2,A,B,i2)-Zv1(x1,x2,A,B,i2))/(x2-x1)**2-np.log(h1)))# Inertia
            
            Fr_h1 = 0.5*(x2-x1)*lg*(Ps+bern+pois+inst)
        else:   #cas o� la glotte forme un canal divergent avec h2>hs
            if (abs(A[1]*x2/B[1])<pres):
                i2 = 2 #num�ro de la plaque sur laquelle on calcule les forces
                tmpG = (xs-x1)/(x2-x1)*(x2-(xs+x1)/2) #variable temporaire
                bern = tmp1*(1/(h0**2)-(x2*Wv1(x1,xs,A,B,i2)-Xv1(x1,xs,A,B,i2))/(tmpG*(x2-x1)))
    #             terme de poiseuille
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))-1/B[1]**3*(x1-1.5*A[1]/B[1]*x1**2+2*A[1]**2/B[1]**2*x1**3)\
                    -2/(x2-x1)/tmpG/B[1]**3*((xs**3/3-0.375*A[1]/B[1]*xs**4+0.4*A[1]**2/B[1]**2*xs**5-\
                                           x2*(xs**2/2-0.5*A[1]/B[1]*xs**3+0.5*A[1]**2/B[1]**2*xs**4))\
                                           -(x1**3/3-0.375*A[1]/B[1]*x1**4+0.4*A[1]**2/B[1]**2*x1**5-\
                                           x2*(x1**2/2-0.5*A[1]/B[1]*x1**3+0.5*A[1]**2/B[1]**2*x1**4)))) 
    
    #             terme d'inertie
                inst = tmp3*(np.log(h1/h0)/A[0]-1/B[1]*(x1-0.5*A[1]/B[1]*x1**2+1/3*A[1]**2/B[1]**2*x1**3)\
                    -2/(x2-x1)/tmpG/B[1]*((1/3*xs**3-1/8*A[1]/B[1]*xs**4+1/15*A[1]**2/B[1]**2*xs**5-\
                                      x2*(0.5*xs**2-1/6*A[1]/B[1]*xs**3+1/12*A[1]**2/B[1]**2*xs**4))\
                                      -(1/3*x1**3-1/8*A[1]/B[1]*x1**4+1/15*A[1]**2/B[1]**2*x1**5-\
                                      x2*(0.5*x1**2-1/6*A[1]/B[1]*x1**3+1/12*A[1]**2/B[1]**2*x1**4))))
                
            else:
                i2 = 2 #num�ro de la plaque sur laquelle on calcule les forces
                tmpG = (xs-x1)/(x2-x1)*(x2-(xs+x1)/2) #variable temporaire       
        #         terme de bernoulli
                bern = tmp1*(1/(h0**2)-(x2*Wv1(x1,xs,A,B,i2)-Xv1(x1,xs,A,B,i2))/(tmpG*(x2-x1)))
        #         terme de poiseuille
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+1/(2*A[1])*(1/(h1**2))-(x2*Wv1(x1,xs,A,B,i2)-Xv1(x1,xs,A,B,i2))/(tmpG*(x2-x1)))
        #         terme d'inertie
                inst = tmp3*(np.log(h1/h0)/A[0]+1/A[1]*((x2*Yv1(x1,xs,A,B,i2)-Zv1(x1,xs,A,B,i2))/(tmpG*(x2-x1))-np.log(h1))) 
            
            Fr_h1 = lg*tmpG*(Ps+bern+pois+inst)+lg*Psupra*(x2-xs)/(x2-x1)*(x2-(x2+xs)/2)
        ########################################################
        ################## Calcul de Fl_h2 #####################
        ### two cases :::: h2 < h1*sep et le cas h2 > h1*sep ###
        
        if (h2 < h1*sep):
            if (abs(A[1]*x2/B[1])<pres): #glotte formant un conduit parall�le
                i2 = 2
    #         terme de bernoulli
    #             bern  = tmp1*(1/(h0**2)-1/(h1**2))
                bern = tmp1*(1/(h0**2)-2*(Xv1(x1,x2,A,B,i2)-x1*Wv1(x1,x2,A,B,i2))/(x2-x1)**2)
    #         terme de poiseuille
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))-1/B[1]**3*(x1-1.5*A[1]/B[1]*x1**2+2*A[1]**2/B[1]**2*x1**3)\
                    +2/(x2-x1)**2/B[1]**3*((x2**3/3-0.375*A[1]/B[1]*x2**4+0.4*A[1]**2/B[1]**2*x2**5-\
                                           x1*(x2**2/2-0.5*A[1]/B[1]*x2**3+0.5*A[1]**2/B[1]**2*x2**4))\
                                           -(x1**3/3-0.375*A[1]/B[1]*x1**4+0.4*A[1]**2/B[1]**2*x1**5-\
                                           x1*(x1**2/2-0.5*A[1]/B[1]*x1**3+0.5*A[1]**2/B[1]**2*x1**4)))) 
    
    #         terme d'inertie
                inst = tmp3*(np.log(h1/h0)/A[0]-1/B[1]*(x1-0.5*A[1]/B[1]*x1**2+1/3*A[1]**2/B[1]**2*x1**3)+\
                    2/(x2-x1)**2/B[1]*((1/3*x2**3-1/8*A[1]/B[1]*x2**4+1/15*A[1]**2/B[1]**2*x2**5-\
                                      x1*(0.5*x2**2-1/6*A[1]/B[1]*x2**3+1/12*A[1]**2/B[1]**2*x2**4))\
                                      -(1/3*x1**3-1/8*A[1]/B[1]*x1**4+1/15*A[1]**2/B[1]**2*x1**5-\
                                      x1*(0.5*x1**2-1/6*A[1]/B[1]*x1**3+1/12*A[1]**2/B[1]**2*x1**4))))
                
            else: #glotte formant un canal convergent ou divergent avec h2<hs
                i2 = 2 #num�ro de la plaque sur laquelle on fait le calcul\
    #         terme de bernoulli
                bern = tmp1*(1/(h0**2)-2*(Xv1(x1,x2,A,B,i2)-x1*Wv1(x1,x2,A,B,i2))/(x2-x1)**2)
    #         terme de poiseuille	        
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+1/(2*A[1])*(1/(h1**2)-2*(Xv1(x1,x2,A,B,i2)-x1*Wv1(x1,x2,A,B,i2))/(x2-x1)**2))
    #         terme d'inertie	        
                inst = tmp3*(np.log(h1/h0)/A[0] +1/A[1]*(2*(Zv1(x1,x2,A,B,i2)-x1*Yv1(x1,x2,A,B,i2))/(x2-x1)**2-np.log(h1)))
            
            Fl_h2 = 0.5*(x2-x1)*lg*(Ps+bern+pois+inst)
            
        else: #cas o� la glotte forme un canal divergent avec h2>hs
            if (abs(A[1]*x2/B[1])<pres): #glotte formant un conduit parall�le
                i2 = 2
                tmpH = (xs-x1)/(x2-x1)*((xs+x1)/2-x1) #variable temporaire
            #         terme de bernoulli
                bern = tmp1*(1/(h0**2)-(Xv1(x1,xs,A,B,i2)-x1*Wv1(x1,xs,A,B,i2))/(tmpH*(x2-x1)))
    #         terme de poiseuille
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))-1/B[1]**3*(x1-1.5*A[1]/B[1]*x1**2+2*A[1]**2/B[1]**2*x1**3)\
                    +2/(x2-x1)/tmpG/B[1]**3*((xs**3/3-0.375*A[1]/B[1]*xs**4+0.4*A[1]**2/B[1]**2*xs**5-\
                                           x1*(xs**2/2-0.5*A[1]/B[1]*xs**3+0.5*A[1]**2/B[1]**2*xs**4))\
                                           -(x1**3/3-0.375*A[1]/B[1]*x1**4+0.4*A[1]**2/B[1]**2*x1**5-\
                                           x1*(x1**2/2-0.5*A[1]/B[1]*x1**3+0.5*A[1]**2/B[1]**2*x1**4)))) 
    
    #         terme d'inertie
                inst = tmp3*(np.log(h1/h0)/A[0]-1/B[1]*(x1-0.5*A[1]/B[1]*x1**2+1/3*A[1]**2/B[1]**2*x1**3)\
                    +2/(x2-x1)/tmpH/B[1]*((1/3*xs**3-1/8*A[1]/B[1]*xs**4+1/15*A[1]**2/B[1]**2*xs**5-\
                                      x1*(0.5*xs**2-1/6*A[1]/B[1]*xs**3+1/12*A[1]**2/B[1]**2*xs**4))\
                                      -(1/3*x1**3-1/8*A[1]/B[1]*x1**4+1/15*A[1]**2/B[1]**2*x1**5-\
                                      x1*(0.5*x1**2-1/6*A[1]/B[1]*x1**3+1/12*A[1]**2/B[1]**2*x1**4))))
                
            else:
                i2 = 2 #num�ro de la plaque sur laquelle on fait le calcul\
                tmpH = (xs-x1)/(x2-x1)*((xs+x1)/2-x1) #variable temporaire
        #         terme de bernoulli
                bern = tmp1*(1/(h0**2)-(Xv1(x1,xs,A,B,i2)-x1*Wv1(x1,xs,A,B,i2))/(tmpH*(x2-x1)))
        #         terme de poiseuille
                pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+1/(2*A[1])*(1/(h1**2))-(Xv1(x1,xs,A,B,i2)-x1*Wv1(x1,xs,A,B,i2))/(tmpH*(x2-x1)))
                #proposition NR, 11/04/2007
        #         pois = tmp2*(1/(2*A[0])*(1/(h0**2)-1/(h1**2))+1/(2*A[1])*(1/(h1**2)-(Xv1(x1,xs,A,B,i2)-x1*Wv1(x1,xs,A,B,i2))/(tmpH*(x2-x1))))
        #         terme d'inertie	
                inst = tmp3*(np.log(h1/h0)/A[0] +1/A[1]*((Zv1(x1,xs,A,B,i2)-x1*Yv1(x1,xs,A,B,i2))/(tmpH*(x2-x1))-np.log(h1)))
          
            Fl_h2 = lg*tmpH*(Ps+bern+pois+inst)+ lg*Psupra*(x2-xs)/(x2-x1)*((x2+xs)/2-x1)
            
    elif (h1>0) and (h2<=0):   #ajout pas NR (04/04/2007), pour calculer les forces de pression
        Fr_h1 = 0.5*(x2-x1)*lg*Ps #en cas de fermeture au niveau d'une masse ou l'autre
        Fl_h2 = 0.5*(x2-x1)*lg*Ps #ici, fermeture au niveau de la masse 2
    elif (h1<=0) and (h2>0):
        Fr_h1 = 0.5*(x2-x1)*lg*Psupra #ici fermeture au niveau de la masse 1
        Fl_h2 = 0.5*(x2-x1)*lg*Psupra
     #modif par NR et CBV, sortie de cette ligne de la condition if de d�part
        ########################################################
        ################## Calcul de Fr_h2 #####################
    
    Fr_h2 = 0.5*lg*Psupra*(x3-x2) 
    Fvf = np.array([ [Fl_h1, Fl_h2 ], [Fr_h1, Fr_h2 ]])         
    return Fvf

def Wv1(xi,xip1,A,B,i):

    #****************************************************#
    # Calcul de la primitive de 1/h2  , entre xi et x(i+1), pour 
    # la plaque numero i
    # 
    # Parametres d'entree
    # 
    # xi,xip1: abscisse entre lesquelles on calcule l'integrale
    # A,B: coefficient de l'equation du la plaque,
    # i: numero de la plaque
    # 
    # Parametre de sortie
    # 
    # X: valeur de l'integrale
    #****************************************************#                                
    # Formules de CV   
    #****************************************************#
    
    pres = 1e-5
    
    hi = A[i-1]*xi + B[i-1]  # = hi 
    hip1 = A[i-1]*xip1 + B[i-1]    # = hi+1 
    # 
    # if (hi == hip1)
    #     W = (xip1-xi)/(hi**2) #cas oe la plaque est horizontale
    if (abs(A[i-1]*xip1/B[i-1])<pres): #cas de presque horizontalite, avec dvpt limite
          W2 = 1/B[i-1]**2*(xip1-A[i-1]*xip1**2/B[i-1]+A[i-1]**2*xip1**3/B[i-1]**2)
          W1 = 1/B[i-1]**2*(xi-A[i-1]*xi**2/B[i-1]+A[i-1]**2*xi**3/B[i-1]**2) 
          W = W2-W1
    else:
        W = 1/A[i-1]*(1/hi-1/hip1)
        
    return W

def Xv1(xi,xip1,A,B,i):

    #****************************************************#
    # Calcul de la primitive de x/h2 , entre xi et x(i+1), pour 
    # la plaque numero i
    # 
    # Parametres d'entree
    # 
    # xi,xip1: abscisse entre lesquelles on calcule l'integrale
    # A,B: coefficient de l'equation du la plaque,
    # i: numero de la plaque
    # 
    # Parametre de sortie
    # 
    # X: valeur de l'integrale
    #****************************************************#
    
    pres = 1e-5
    hi = A[i-1]*xi+B[i-1]  # = hi 
    hip1 = A[i-1]*xip1+B[i-1]    # = hi+1 
    
    # if (hi == hip1)
    #     X = (xip1-xi)*xi/(hi**2)  #cas oe la plaque est horizontale
    
    if (abs(A[i-1]*xip1/B[i-1])<pres): #cas de presque horizontalite, avec dvpt limite
          X2 = 1/B[i-1]**2*(xip1**2/2-2*A[i-1]*xip1**3/3/B[i-1]+3*A[i-1]**2*xip1**4/4/B[i-1]**2)
          X1 = 1/B[i-1]**2*(xi**2/2-2*A[i-1]*xi**3/3/B[i-1]+3*A[i-1]**2*xi**4/4/B[i-1]**2) 
          X = X2-X1
    else:
        X = 1/(A[i-1]**2)*np.log(hip1/hi)+1/A[i-1]*(xi-hi/A[i-1])*(1/hi-1/hip1)
        
    return X

def Yv1(xi,xip1,A,B,i):

    #****************************************************#
    # Calcul de la primitive de ln(h)  , entre xi et x(i+1), pour 
    # la plaque numero i
    # 
    # Parametres d'entree
    # 
    # xi,xip1: abscisse entre lesquelles on calcule l'integrale
    # A,B: coefficient de l'equation du la plaque,
    # i: numero de la plaque
    # 
    # Parametre de sortie
    # 
    # X: valeur de l'integrale                              
    #****************************************************#
    
    pres = 1e-5
    hi = A[i-1]*xi+B[i-1]  # = hi 
    hip1 = A[i-1]*xip1+B[i-1]    # = hi+1 
    # if (hi == hip1)
    #     Y = (xip1-xi)*np.log(hi)  #cas oe la plaque est horizontale
    if (abs(A[i-1]*xip1/B[i-1])<pres): #cas de presque horizontalite, avec dvpt limite
        Y2=(xip1*np.log(B[i-1])+A[i-1]/B[i-1]/2*xip1**2-A[i-1]**2/B[i-1]**2/6*xip1**3)
        Y1=(xi*np.log(B[i-1])+A[i-1]/B[i-1]/2*xi**2-A[i-1]**2/B[i-1]**2/6*xi**3)
        Y=Y1-Y2
    else:
        Y = 1/A[i-1]*(hip1*np.log(hip1)-hip1-hi*np.log(hi)+hi)
    
    return Y

def Zv1(xi,xip1,A,B,i):
    
    #****************************************************#
    # Calcul de la primitive de x*ln(h)    , entre xi et x(i+1), pour 
    # la plaque numero i
    # 
    # Parametres d'entree
    # 
    # xi,xip1: abscisse entre lesquelles on calcule l'integrale
    # A,B: coefficient de l'equation du la plaque,
    # i: numero de la plaque
    # 
    # Parametre de sortie
    # 
    # X: valeur de l'integrale                            
    #****************************************************#
    
    pres = 1e-5
    hi = A[i-1]*xi+B[i-1]  # = hi 
    hip1 = A[i-1]*xip1+B[i-1]    # = hi+1 
    # if (hi == hip1)
    #     Z = xi*(xip1-xi)*np.log(hi)  #cas oe la plaque est horizontale
    if (abs(A[i-1]*xip1/B[i-1])<pres): #cas de presque horizontalite, avec dvpt limite
        Z2=(xip1**2/2*np.log(B[i-1])+A[i-1]*xip1**3/B[i-1]/3-A[i-1]**2*xip1**4/8/B[i-1]**2)
        Z1=(xi**2/2*np.log(B[i-1])+A[i-1]*xi**3/B[i-1]/3-A[i-1]**2*xi**4/8/B[i-1]**2)
        Z=Z2-Z1
    else:
        tempo = 1/(A[i-1]**2)
        tempo = tempo*(((hip1**2)*np.log(hip1)-(hi**2)*np.log(hi))/2-((hip1**2)-(hi**2))/4)
        Z     = tempo+1/A[i-1]*(xi-hi/A[i-1])*(hip1*np.log(hip1)-hip1-hi*np.log(hi)+hi)
        
    return Z

def solve_pol_2(a,b,c):
    
    delta = b*b-4*a*c
    
    if delta>=0:  
        x1 = (-b+np.sqrt(delta))/(2*a)
        x2 = (-b-np.sqrt(delta))/(2*a)   
    else:
        print('no real solution for this equation')   
    return max(x1,x2)

def powtr( x, a, b, dr=1 ):
    # converts area function to midsagittal distance, or the contrary according
    # ot the power transformation
    
    
    if dr == 1: # midsagittal to area function
        x = 100*x # x should be in cm
        y = a*(x**b)
        y = y*1e-4 # goes back to m^2
    else: # area to midsagittal distance
        x = 1e4*x # x should be in cm^2
        y = np.exp((np.log(x)-np.log(a))/b)
        y = y*1e-2 # goes back to m

    return y