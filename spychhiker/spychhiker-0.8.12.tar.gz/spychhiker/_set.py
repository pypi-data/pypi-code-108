#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 09:33:59 2018

@author: benjamin
"""
import numpy as np
   
class struct:
    def __init__(self):
        Tair = 37
        self.rho = 1.2929 * (1 - 0.0037 * Tair)
        self.c_s = 331.45 * (1 + 0.0018 * Tair)
        self.mu = 1.85e-5
        self.a = 130 * np.pi
        self.b = (30 * np.pi)**2
        self.c1 = 4
        self.wo2 = (406 * np.pi)**2
        self.c1n = 72
        self.heat_cond = 0.0034
        self.specific_heat = 160
        self.adiabatic = 1.4
        self.wallyield = True
        self.loss = True
        self.freq = np.arange(0,5050,50,dtype='float') #Vector of frequencies
        self.nform = 4
        self.length_var = True
        self.lips_var = True
        self.area_weight = 0
        self.length_weight = 0;
        self.potential_weight = 0
        self.threshold = 1
        self.maxNumIter = 1e3
        self.psi = 1
 
class timestruct:
    def __init__(self):
        Tair = 37
        ######### Coefficients for wall parameters
        loss_terms = 'birk' # maeda, birk or mokh
        if loss_terms ==  'maeda': # ## From Maeda
            wall_resi = 1600 #/* wall resistance, gm/s/cm2		*/
            wall_mass = 1.5	#/* wall mass per area, gm/cm2		*/
            wall_comp = 3.0e5	#/* wall compliance			*/
        if loss_terms ==  'birk': # #### From Birkholz
            wall_resi = 8e3	#/* wall resistance, gm/s/cm2		*/
            wall_mass = 21e0	#/* wall mass per area, gm/cm2		*/
            wall_comp = 8.45e6	#/* wall compliance			*/
        if loss_terms ==  'mokh': #### From Mokhtari
            wall_resi = 14e3	#/* wall resistance, gm/s/cm2		*/
            wall_mass = 15e0	#/* wall mass per area, gm/cm2		*/
            wall_comp = 3e6	#/* wall compliance			*/
        
        self.fs = 2e4
        self.T = 1/self.fs
        self.tm = 1
        self.tcl = 0.01
        self.namp = 1e-7
        self.dispcomp = True
        self.wallyield = True
        self.dynterm = True
        self.wr = wall_resi
        self.wm = wall_mass
        self.wc = wall_comp
        self.rho = 1.2929 * (1 - 0.0037 * Tair)
        self.c = 331.45 * (1 + 0.0018 * Tair)
        self.c_s = 331.45 * (1 + 0.0018 * Tair)
        self.mu = 1.85e-5
        self.lg = 0.01
        self.Xg = 0.3e-2
        self.kc = 1.42
        self.dist_source = 2 # Gaussian noise
        self.fh = 0.2e3 # Cut-off frequency for high-pass filter
        self.fl = 4e3 # Cut-off frequency for low-pass filter
        self.ordh = 1 # Order of high-pass filter
        self.ordl = 7 # Order of low-pass filter
        self.bf = np.array([0.9, 0.1, -0.8] )
        self.af = 1
        self.K_b = self.kc*self.rho
        self.Lord = 50e-3
        self.Rec = 1.7e3 # Reynolds threshold for frication noise generation
        self.G = 9 / 128
        self.S = 3 / 8
        self.sep = 1.2
        self.filt = 'fir1'
        self.blim = 0
        self.beta = 5e-8
        self.nmass = 2
        self.amin = 1e-11
        self.model = 'ishi'
        self.rmlt = 400
        self.a = 130 * np.pi
        self.b = (30 * np.pi)**2
        self.c1 = 4
        self.wo2 = (406 * np.pi)**2
        self.c1n = 72
        self.heat_cond = 0.0034
        self.specific_heat = 160
        self.adiabatic = 1.4
        self.wallyield = True
        self.loss = True
        self.freq = np.arange(0,5050,50,dtype='float') #Vector of frequencies
        self.nform = 4
        self.length_var = True
        self.lips_var = True
        self.area_weight = 0
        self.length_weight = 0;
        self.potential_weight = 0
        self.threshold = 1
        self.maxNumIter = 1e3
        self.psi = 1
        self.unst = True
        
        
class miscstruct:
    def __init__(self):
        self.dum = 0
