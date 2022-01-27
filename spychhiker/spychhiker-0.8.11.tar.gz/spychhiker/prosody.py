#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 21:07:26 2020

@author: benjamin
"""

import copy
import numpy as np
import statsmodels.api as sm
import scipy.interpolate as scintp
import warnings
from .plottools import pitch_plot, contour_plot
from .splinetools import (check_list, move_spline, target_spline, translate_spline)

class Pitch:
    values = None
    time_points = None
    contour = None
    parent = None
    glottal_closure_instants = None
    jitter = None
    simmer = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def copy(self):

        return copy.deepcopy(self)

    def interpolate(self):
        f0 = self.values
        tf0 = self.time_points

        f0Plain = np.array([x for x in f0 if x > 0])
        t0Plain = np.array([tf0[x] for x in range(len(f0)) if f0[x] > 0])
        
        if f0Plain != []:
            f1 = scintp.interp1d(t0Plain, f0Plain, 'linear', fill_value=0,
                                 bounds_error=False)
            f0int = f1(tf0)
    
            idx_up = [x for x in range(len(tf0)) if tf0[x] <= t0Plain[0]]
            idx_down = [x for x in range(len(tf0)) if tf0[x] >= t0Plain[-1]]
            f0int[idx_up] = f0Plain[0]
            f0int[idx_down] = f0Plain[-1]            
        else:
            f0int = f0
            
        self.values = f0int
        return f0int
    
    def timeinterpolate(self, time_out, minf0=70):
        y = self.values
        tf0 = self.time_points
        
        f1 = scintp.interp1d(tf0,y,kind='linear',bounds_error=False, fill_value=0)
        y_out = f1(time_out)
        y_out[y_out<=minf0] = 0

        self.values = y_out
        self.time_points = time_out

    def getcontour(self, len_win=0.3):

        f0 = self.values
        tf0 = self.time_points

        srF0 = 1/(tf0[2]-tf0[1])
        nwin = int(len_win * srF0)
        if np.mod(nwin, 2) > 0:
            nwin = nwin + 1
        novlp = int(nwin * 1 / 2)
        nhop = nwin-novlp
        zeros2add = np.zeros((nhop, 1))

        f0up = np.vstack((zeros2add, f0.reshape(-1, 1), zeros2add))
        f0up = f0up.squeeze()

        w = np.ones(nwin)
        f0Out = np.zeros_like(f0up)

        k = 0
        isC = True
        while isC:
            deb = int(k * nhop)
            fin = deb + nwin - 1
            if fin > len(f0up) - 1:
                fin = len(f0up) -1
                isC = False
            idx = np.arange(deb, fin+1).astype(int)
            xTmp = f0up[idx]

            pp = np.polyfit(idx, xTmp, 2)
            newPitch = np.polyval(pp, idx)
            f0Out[idx] += f0Out[idx] + (newPitch[:len(idx)] * w[:len(idx)])
            k += 1

        f0Out = f0Out / 3
        f0Out = f0Out[nhop:-nhop]

        winOrd = int(0.3 * srF0)
        f0Out = sm.nonparametric.lowess(f0Out,
                                        np.arange(len(f0Out)),
                                        frac=winOrd/len(f0Out),
                                        return_sorted=False)

        self.contour = Contour('values', f0Out,
                               'time_points', self.time_points,
                               'parent', self)

    def plot(self):

        if self.contour is None:
            self.getcontour()
            
        if self.contour.spline is not None:
            spl_tp = self.contour.spline.time_points
            spl_v = self.contour.spline.values
        else:
            spl_tp = []
            spl_v = []
            
        return pitch_plot(self.time_points, self.values, self.contour.values,
                          spl_tp, spl_v, self.parent)

    def shift(self, factor):
        self.values = self.values * factor
        if self.contour is not None:
            self.contour.values = self.contour.values * factor
        if self.contour.normalized is not None:
            self.contour.detrend()
        if self.contour.spline is not None:
            self.contour.getSpline()
            self.contour.spline.parent = self

    def changespan(self, factor):
        f0 = self.values

        if self.contour is None:
            self.getcontour()

        contIn = self.contour.values
        if self.contour.normalized is None:
            self.contour.detrend()
        self.contour.normalized.values = self.contour.normalized.values * factor
        self.contour.retrend()

        self.values = (f0 - contIn) + self.contour.values
        self.getcontour()
        if self.contour.normalized is not None:
            self.contour.detrend()
        if self.contour.spline is not None:
            self.contour.getspline()
            self.contour.spline.parent = self

    def flattening(self):
        f0 = self.values

        if self.contour is None:
            self.getcontour()
        meanPitch = self.contour.values

        self.values = f0 - meanPitch + np.mean(f0)
        self.getcontour()
        if self.contour.normalized is not None:
            self.contour.detrend()
        if self.contour.spline is not None:
            self.contour.getSpline()
            self.contour.spline.parent = self

    def changecontour(self, target):

        if self.contour is None:
            self.getcontour()
        self.values = (self.values - self.contour.values +
                       target.contour.values)
        self.contour = target.contour.copy()
        self.contour.parent = self
        if self.contour.spline is not None:
            self.contour.getSpline()
            self.contour.spline.parent = self

    def changedeclination(self, target):

        if self.contour is None:
            self.getContour()
        if self.contour.normalized is None:
            self.contour.detrend()

        x = np.arange(len(self.values))
        pDecl = [np.tan(target), 0]
        pitchTrend = np.polyval(pDecl, x)
        newCont = self.contour.normalized.values + pitchTrend + self.contour.mean
        self.values = self.values - self.contour.values + newCont
        self.contour.values = newCont
        if self.contour.spline is not None:
            self.contour.getSpline()
            self.contour.spline.parent = self

class Contour(Pitch):
    mean = None
    normalized = None
    max_peaks = None
    min_peaks = None
    locs_max = None
    locs_min = None
    declination = None
    span = None
    peak_extent = None
    local_peak_dynamic = None
    top_angle = None
    base_angle = None
    spline = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def getspline(self, len_win=0.15):

        tf0 = self.time_points
        f0 = self.values
        
        srOut = 1/len_win

        srIn = 1/(tf0[2]-tf0[1])
        D = int(srIn / srOut)
        if D > 1:
            newTime = tf0[::D]
            newPitch = f0[::D]
        else:
            newTime = tf0
            newPitch = f0
        spl = scintp.splrep(newTime, newPitch)
        splFreq = scintp.splev(tf0, spl)
        (t, c, k) = spl

        splineObj = Spline('time_points', tf0,
                           'values', splFreq,
                           'knots', t,
                           'coeff', c,
                           'order', k,
                           'parent', self)

        self.spline = splineObj

        return splineObj
    
    def check_spline(self):
        if self.spline is None:
            self.getspline()

    def changespline(self, pts, factor, target=False):

        self.check_spline()
        pts = check_list(pts)
        if target:  
            target_spline(self.spline, pts, factor) 
        else:
            translate_spline(self.spline, pts, factor)

        if hasattr(self.parent, "values"):
            self.parent.values = (self.parent.values - self.parent.contour.values +
                              self.spline.values)
        self.values = self.spline.values

    def shiftspline(self, pts, factor):

        self.check_spline()
        pts = check_list(pts)
        move_spline(self.spline, pts, factor)

        self.values = self.spline.values

    def getlocalmax(self):

        f0 = self.values
        df0 = np.diff(f0)
        proddf0 = np.sign(df0[:-1]*df0[1:])
        locs = [x+1 for x in range(len(proddf0)) if proddf0[x] < 0]
        maxlocs = [x for x in locs if df0[x] < 0]
        minlocs = [x for x in locs if df0[x] > 0]

        self.max_peaks = f0[maxlocs]
        self.min_peaks = f0[minlocs]
        self.locs_max = maxlocs
        self.locs_min = minlocs

    def getbaselines(self):

        if (self.max_peaks is None or
                self.min_peaks is None or
                self.locs_max is None or
                self.locs_min is None):
                self.getlocalmax()

        maxpks = self.max_peaks
        minpks = self.min_peaks
        maxlocs = self.locs_max
        minlocs = self.locs_min


        warnings.simplefilter('ignore', np.RankWarning)
        pTop = np.polyfit(maxlocs, maxpks, 1)
        angleTop = np.arctan(pTop[0])
        
        pBase = np.polyfit(minlocs, minpks, 1)
        angleBase = np.arctan(pBase[0])
        self.declination = (angleTop - angleBase) / 2
        self.top_angle = angleTop
        self.base_angle = angleBase

    def detrend(self):

        if self.declination is None:
            self.getbaselines()

        x = np.arange(len(self.values))
        pDecl = [np.tan(self.declination), 0]
        pitchTrend = np.polyval(pDecl, x)
        detrend = self.values - pitchTrend
        self.mean = np.mean(detrend)
        self.normalized = Contour('values', detrend - np.mean(detrend),
                                  'time_points', self.time_points)

    def retrend(self):

        if self.declination is None:
            self.getbaselines()

        x = np.arange(len(self.values))
        pDecl = [np.tan(self.declination), 0]
        pitchTrend = np.polyval(pDecl, x)
        self.values = self.normalized.values + pitchTrend + self.mean

    def getpitchspan(self):
        if self.normalized is None:
            self.detrend()
        if self.normalized.max_peaks is None or self.normalized.min_peaks is None:
            self.normalized.getlocalmax()

        maxpks = self.normalized.max_peaks
        minpks = self.normalized.min_peaks
        self.span = np.mean(maxpks) - np.mean(minpks)

        return self.span

    def getnppe(self):
        if self.normalized is None:
            self.detrend()
        if self.normalized.max_peaks is None:
            self.normalized.getlocalmax()

        maxpks = self.normalized.max_peaks
        self.peak_extent = np.max(maxpks)

        return self.peak_extent

    def getlpdyn(self):
        if self.normalized is None:
            self.detrend()
        if (self.normalized.max_peaks is None or
                self.normalized.min_peaks is None or
                self.normalized.locs_max is None or
                self.normalized.locs_min is None):

            self.normalized.getlocalmax()

        tf0 = self.time_points
        maxpks = np.array(self.max_peaks).reshape(-1, 1)
        minpks = np.array(self.min_peaks).reshape(-1, 1)
        maxlocs = np.array(self.locs_max).reshape(-1, 1)
        minlocs = np.array(self.locs_min).reshape(-1, 1)

        localMaxima = np.vstack((maxpks, minpks)).squeeze()
        locsMaxima = np.vstack((maxlocs, minlocs)).squeeze()
        idxSort = np.argsort(locsMaxima)
        localMaxima = localMaxima[idxSort]
        locsMaxima = locsMaxima[idxSort]

        df = np.abs(localMaxima[1:] - localMaxima[:-1])
        dt = tf0[locsMaxima[1:]] - tf0[locsMaxima[:-1]]

        self.local_peak_dynamic = np.mean(df / dt)

        return self.local_peak_dynamic

    def db2lin(self):
        return  (10**(self.values / 10)) * 2e-5
    def lin2db(self):
        return  10 * np.log10(self.values / 2e-5)

class Spline(Contour):
    parent = None
    coeff = None
    knots = None
    order = None

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def interpolate(self):

        spl = (self.knots, self.coeff, self.order)
        splFreq = scintp.splev(self.parent.time_points, spl)

        self.values = splFreq

class Intensity(Contour):

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)

    def interpolate(self, SpObj=None):

        if SpObj is None:
            SpObj = self.parent
        y = SpObj.signal
        sr = SpObj.sampling_frequency

        txx = np.arange(len(y)) / sr
        f1 = scintp.interp1d(self.time_points, self.values,
                             'linear', fill_value="extrapolate")
        contIntp = f1(txx)

        intOut = self.copy()
        intOut.values = contIntp
        intOut.time_points = txx
        if self.contour is not None:
           f1 = scintp.interp1d(self.time_points, self.contour.values,
                                'linear', fill_value="extrapolate")
           intOut.contour.values = f1(txx)
        if self.normalized is not None:
            intOut.getnormalized()
        if self.spline is not None:
            intOut.getspline()

        return intOut

    def getcontour(self, len_win=0.15):

        x = self.values
        tVec = self.time_points

        sr = 1/(tVec[2]-tVec[1])

        winOrd = int(len_win * sr)
        xOut = sm.nonparametric.lowess(x, np.arange(len(x)),
                                       frac=winOrd/len(x),
                                       return_sorted=False)
        self.contour = Contour('values', xOut,
                               'time_points', self.time_points,
                               'parent', self)

    def getnormalized(self):

        if self.contour is None:
            self.getcontour()

        ObjOut = self.contour.copy()
        ObjOut.values = self.values - self.contour.values
        self.normalized = ObjOut

    def plot(self):

        yS = self.parent.signal
        tVecSignal = np.arange(len(yS)) / self.parent.sampling_frequency
        yI = self.db2lin()

        return contour_plot(tVecSignal, yS, 
                            self.time_points, yI * np.max(yS) / np.max(yI),
                            parent=self.parent)

    def changespan(self, factor):

        if self.contour is None:
            self.getcontour()
        if self.normalized is None:
            self.getnormalized()

        self.values = self.normalized.values * factor + self.contour.values

    def flattening(self):
        x = self.values

        if self.normalized is None:
            self.detrend()

        self.mean = np.mean(x)
        self.values += self.mean
