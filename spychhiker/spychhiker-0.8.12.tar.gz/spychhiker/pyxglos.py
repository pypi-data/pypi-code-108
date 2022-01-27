#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 09:28:58 2018

@author: benjamin
"""
import numpy as np
import scipy
from ._set import miscstruct
from .utils import nextpow2

def initparam(obj, param):
    
    if param is None:
        param = miscstruct()        
  
    if not hasattr(param, 'win_length_sec'):
        param.win_length_sec = 0.04
    if not hasattr(param, 'win_length'):
        param.win_length = 2**nextpow2(param.win_length_sec * obj.sampling_frequency)
    if not hasattr(param, 'hop_factor'):
        param.hop_factor = 4
    if not hasattr(param, 'threshold'):
        param.threshold = 3.5
    if not hasattr(param, 'nfft'):
        param.nfft = 2**nextpow2(param.win_length * 10)
    if not hasattr(param, 'lfmed'):
        param.lfmed = 250
    if not hasattr(param, 'num_period'):
        param.num_period = 4
    if not hasattr(param, 'fomin'):
        param.fomin = 80
    if not hasattr(param, 'fomax'):
        param.fomax = 300
    if not hasattr(param, 'num_harm'):
        param.num_harm = np.floor(obj.sampling_frequency / 2 / param.fomin)
    if not hasattr(param, 'partial_length'):
        param.partial_length = 7
    if not hasattr(param, 'search_range'):
        param.search_range = 7
    if not hasattr(param, 'num_partial'):
        param.num_partial = 6
    if not hasattr(param, 'num_zero'):
        param.num_zero = 1
    if not hasattr(param, 'pct'):
        param.pct = 90
    if not hasattr(param, 'amplitude_estimator'):
        param.amplitude_estimator = 'lse'
    if not hasattr(param, 'std_estimator'):
        param.std_estimator = 'std'
    if param.amplitude_estimator.lower() != 'lse' and param.amplitude_estimator.lower() != 'wlse':
        print('Warning: the amplitude estimator is badly defined. It has been set to LSE (default)')
        param.amplitude_estimator = 'lse'
    if not hasattr(param, 'jitt'):
        param.jitt = False
    if not hasattr(param, 'shim'):
        param.shim = False
    if (param.jitt or param.shim) and (not hasattr(param, 'ord')):
        param.ord = np.ceil(np.min([param.win_length / 3, 501]))
    if param.jitt or param.shim:
        param.fcoef = scipy.signal.firwin(int(param.ord), 
                                 float(2 * param.partial_length / (obj.sampling_frequency / 2)))
    if (param.jitt or param.shim) and (not hasattr(param, 'methfreq')):
        param.methfreq = 'zcr'
    if not hasattr(param, 'verbosity'):
        param.verbosity = False      
        
    return param

def findpartials(x, fs, win, param):
    """ returns a cleaned version of the periodogram
    keeps interval of the periodogram above peaks that are above the noise
    floor (estimated by a median filtering of the periodogram) """

    Nfft = int(param.nfft)
    f = fs*np.arange(0,Nfft)/Nfft
    P = abs(np.fft.fft(x*win,Nfft))**2
    P = P/sum(P)

    nw = param.lfmed*np.ceil(Nfft/param.nfft)
    if np.mod(nw,2)==False:
        nw += 1
    if param.pct > 0:
        pth = scipy.ndimage.filters.percentile_filter(P, int(param.pct), int(nw))        
        P[P < pth] = 0
    
    P[f < param.fomin] = 0
    pks = np.zeros(len(P))
    m = np.logical_and((P[1:-1] > P[2:len(P)]),(P[1:-1] > P[0:-2]))
    locs = np.argwhere(m)+1 # find peaks
    prng = np.ceil(param.partial_length*fs/Nfft)

    # keep the periodogram around the peaks above the noise floor
    for ki in range(0,len(locs)):
        if (locs[ki] > prng) and (locs[ki]+prng < len(pks)):
            partial_range = np.arange(locs[ki]-prng, locs[ki]+prng+1)
            pks[partial_range.astype(int)] = P[partial_range.astype(int)]
            
    return pks

def findf0(pks, fs, param):
    """ Estimation of the fundamental frequency of the windowed signal S

    Input arguments:
    
    pks: cleaned periodogram
    fs: sampling frequency (in Hz)
    param : structure containing various parameters """

    f = np.arange(0,param.nfft)/ param.nfft*fs
    idx1 = np.argwhere(f >=param.fomin)[0,0]
    idx2 = np.argwhere(f <= param.fomax)[-1,-1]
     
    ## cumulated periodogram
    cum_per = np.zeros(len(pks))

    Npartials = param.num_partial

    for ki in range(idx1,idx2+1):#idx1:idx2
        for kj in range(1,min((np.floor(len(pks)/ki), Npartials))+1):
            cum_per[ki] = cum_per[ki] + pks[ki * kj]
            
    # keep only if fundamental is present
    cum_per[pks == 0] = 0
    # first estimation of f0
    maxcumul = max(cum_per)
    if maxcumul == 0:
        return 0
    idxf0 = np.argmax(cum_per)
    # find values of cum_per close to the maximum
    idxfindf0 = np.argwhere(cum_per > 0.95 * maxcumul)

    idxf0 = max(idxfindf0[np.mod(idxfindf0,idxf0)==0])
    # solve the problem when f0/2 occurs in the cumulated periodog

    if idxf0 > np.ceil(param.search_range*fs/param.nfft):
        idx1 = int(idxf0-np.ceil(param.search_range*fs/param.nfft))
        idx2 = int(idxf0+np.ceil(param.search_range*fs/param.nfft)+1)
        maxpks = max(pks[idx1:idx2])
        idxf = np.argmax(pks[idx1:idx2])
    else:
        idx2 = int(idxf0+np.ceil(param.search_range*fs/param.nfft)+1)
        maxpks = max(pks[0:idx2])
        idxf = np.argmax(pks[0:idx2])

    if ((not maxpks) or (maxpks/sum(pks) < 1e-3)):# || (np.abs(param.search_range+1-idxf) < param.partial_lengthh))
        return 0  # If empty, no voicing, the signal contains only noise

    idxf0 = int(idxf0+idxf-np.ceil(param.search_range*fs/param.nfft)-1)

    if not idxf0:
        return 0

    return f[idxf0]#, cum_per[idxf0]

def f0reeval(f0, x, fs, param):
    """ correction of f0/2 and f4/2 using the derivative criterion """
    for ki in range(0,2):

        derrive = np.zeros(len(f0))
        derrive[1:len(derrive)] = np.diff(f0)
        derrive[f0==0]=0
        f0_ = np.zeros(len(f0))
        f0_[1:len(f0_)]= f0[0:-1]
        derrive[f0_ == 0]=0
        detection = derrive/(f0+1e-5)*100
        f0[detection <-50] = 0
        f0 = scipy.signal.medfilt(f0,3)
        f0[np.logical_or(f0 < param.fomin, f0 > param.fomax)] = 0
    fk = np.zeros((len(f0), int(param.num_harm)))
 
    kit = param.hop+np.ceil(param.win_length/2)-1
    param2 = param   
    param2.pct = -1

    for cmpt in range (0,len(f0)):
        if f0[cmpt] >= param.fomin:
            tow = np.floor(1./f0[cmpt]*fs)
            npts = np.ceil(param.win_length/tow)
            if abs((npts-1)*tow-param.win_length) < abs(npts*tow-param.win_length):
                npts -= 1
            nw = npts*tow
            iw = np.arange(max((0,kit-np.floor(nw/2))),min((kit+np.floor(nw/2)-1+np.mod(nw,2)+1,len(x))))
            xw = x[iw.astype(int)]
            w = np.hanning(len(xw)+1)
            w = w[1:len(w)]
#             param2.lfmed = ceil(f0(cmpt)*1.5);            
            pks = findpartials(xw, fs, w, param2)
            fk[cmpt,:] = relocatePartials( pks, xw, fs, f0[cmpt], param2)   
        kit += param.hop; 
    return fk

def relocatePartials( pks, x, fs, f0, param ):

    nfft = int(param.nfft)
    fkm = np.zeros(int(param.num_harm))   
    w = np.hanning(len(x)+1)
    w = w[1:len(w)]
    f = np.arange(0,nfft)/ nfft*fs

    idxf0 = int(np.argwhere(f >=f0 )[0])
    fkm[0] = f0
    idxfi = idxf0
    
    yg = np.fft.fft(x*w, nfft)
    L = int(np.ceil(nfft/2)+1)
    yg = yg[0:L]
    f = f[0:L]
    pks = pks[0:L]
    nzrow = 0
    prng = np.ceil(param.search_range*fs/nfft)
    
    for ki in range(1,int(param.num_harm)+1):
        idxfi += idxf0
    #     idxfi=ki*idxf0;#+idxfi;
        if idxfi<=len(pks):
            idx1 = int(max(idxfi-prng,0))
            idx2 = int(min(idxfi+prng+1,len(pks)))
            valeur = np.max(abs(pks[idx1:idx2]))
            idxf = np.argmax(abs(pks[idx1:idx2]))
            if valeur != 0:
                idxfi += idxf-prng-1
                idxtt = int(idxfi)
                idx1 = int(max(idxfi-prng,0))
                idx2 = int(min(idxfi+prng+1,len(yg)))
                idxf = np.argmax(abs(yg[idx1:idx2]))
                idxfi2 = int(idxfi+idxf-prng-1)
                ir = np.arange(max(idxfi2-2,0),min(idxfi2+3,len(yg)))
                if max(ir)<=len(f):
                    wos = f[ir.astype(int)]
                    los = np.log(abs(yg[ir.astype(int)]))
                    p = np.polyfit(wos, los,2)
                    fkm[ki] = -p[1]/(2*p[0])
                    if (fkm[ki] < 0) or (fkm[ki] > fs/2) or (abs(fkm[ki]-f[int(idxfi2)]) > prng):
                        fkm[ki] = f[idxtt]
                        idxfi = int(idxtt)
                else:
                    fkm[ki] = ki*f0
        else:
            break        
        if np.isnan(fkm[ki]):
            fkm[ki] = 0
        if fkm[ki]:
            nzrow = 0;
        else:
            nzrow += 1
            if param.num_zero and nzrow >= param.num_zero:
                return fkm
            
    return fkm

def instprop( x, fs=1):
    
    """ returns instantaneous lower and upper amplitude """ 
    xm = np.mean(x)
    xmm = x-xm
    
    x_anal = scipy.signal.hilbert(xmm)
    phix = np.unwrap(np.angle(x_anal))    
#    ifq = (np.diff(phix)/(2.0*np.pi)*fs)
    ifq = 1./(2*np.pi)*(np.gradient(phix,1./fs))
    upenv = abs(x_anal)
    
    x = -x;
    xm = np.mean(x); 
    xmm = x-xm;
    x_anal = scipy.signal.hilbert(xmm)
    lowenv = abs(x_anal)
    
    return ifq, upenv, lowenv

def instfreq(x, fs, fo):
    """ returns instantaneous frequency """
    
    tow = np.floor(1/fo*fs)
    x = x-np.mean(x)
    nx = len(x)
    txi = np.arange(0,nx-0.99,0.01)
    f1 = scipy.interpolate.interp1d(np.arange(0,nx),x)
#    foint = f1(tfo)
    xi = f1(txi)
    px = xi[0:-1]*xi[1:len(xi)]
#    zc = np.argwhere(px <= 0)  
    zc = np.argwhere(px <= 0)
    zc = zc.reshape(zc.size)
    zct = txi[zc[0:len(zc):2]]   
    foi = np.zeros(len(x))
    
    indx = scipy.signal.argelrextrema(xi, np.greater)
    hmax = xi[indx]
    imin = scipy.signal.argelrextrema(xi, np.less)
    hmin = xi[imin]
    lmax = len(hmax)
    lmin = len(hmin);
    lm = min((lmax,lmin))
    hmax = hmax[0:lm] 
    hmin = hmin[0:lm]
    
    fo = fs/np.diff(zct)
    perloc = 0.5*(zct[0:-1]+zct[1:len(zct)])
    
    if len(perloc) >= 2:
        if perloc[0] > 2*tow:
            fo = np.append(0,fo)# zeros(1).append(fo)
            perloc = np.append(1,perloc)#np.ones(1).append(perloc)            
        if nx-perloc[-1] > 2*tow:
            fo = np.append(fo,0)#.append(0)
            perloc = np.append(perloc,nx)#.append(nx)

#        f1 = scipy.interpolate.interp1d(perloc, fo, kind='cubic',bounds_error=False,fill_value=0)
        f1 = scipy.interpolate.PchipInterpolator(perloc,fo)
        foi = f1(txi)
        foi = foi[0:len(foi):100]
    
    return foi