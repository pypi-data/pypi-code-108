#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 09:15:05 2020

@author: benjamin
"""

import numpy as np
import scipy.stats as sst
import copy

class RandomVar:

    samples = None
    pdf = None
    bins = None
    moments = None
    median = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0,nargin,2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        return copy.deepcopy(self)

    def get_stats(self, bins=50):

        self.moments = []
        pdf, pdf_bins = np.histogram(self.samples, bins, density=True)
        self.pdf = pdf
        self.bins = pdf_bins
        self.moments.append(np.nanmean(self.samples))
        self.moments.append(np.var(self.samples))
        self.moments.append(sst.skew(self.samples))
        self.moments.append(sst.kurtosis(self.samples))
        self.median = np.nanmedian(self.samples)
        
class Bivar(RandomVar):
    
    covariance = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0,nargin,2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
    def copy(self):
        return copy.deepcopy(self)
    
class ProsodyParam(RandomVar):

    declination = []
    span = []
    peak_extent = []
    local_peak_dynamic = []
    raw_values = []

    # Constructor method
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
        
    def copy(self):
        return copy.deepcopy(self)