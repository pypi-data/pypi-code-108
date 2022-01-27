#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 09:32:12 2020

@author: benjamin
"""

import copy
import numpy as np
import scipy.interpolate as scintp
from .plottools import plot_area
from .utils import lininterp1

class AreaFunction:
    """class for manipulating area fucntions"""
    area = None
    length = None
    parent = None
    total_length = None
    constriction_area = None
    constriction_location = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
        if self.area is not None and self.length is not None:
            _, _, _ = self.characteristics()

    def copy(self):
        """returns a deep copy of the instance"""
        return copy.deepcopy(self)

    def interpolate(self, num_tubes):
        """interpolates area function into a vector y_out of N_out evenly spaced area function."""
        
        af = self.area
        lf = self.length
        if len(af.shape) == 1:
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)

        cumx_in = np.cumsum(lf, 0)
        x_out = np.zeros((num_tubes, af.shape[1]))
        y_out = np.zeros((num_tubes, af.shape[1]))
        for kframe in range(af.shape[1]):
            y_in = af[:, kframe]
            x_in = cumx_in[:, kframe]

            x_out1 = np.arange(1, num_tubes+1)*x_in[-1]/num_tubes
            f1 = scintp.interp1d(x_in, y_in,
                                 kind='nearest', fill_value='extrapolate')
            y_out[:, kframe] = f1(x_out1)
            x_out[:, kframe] = np.append(x_out1[0], np.diff(x_out1))

        self.area = y_out.squeeze()
        self.length = x_out.squeeze()
        return x_out, y_out

    def plot(self, sl=None, hf=None):
        """plots the area function"""
        a = np.array(self.area)
        l = np.array(self.length)
        if sl is not None:
            a = a[:, sl]
            l = l[:, sl]
            
        xval = np.insert(np.cumsum(l) * 1e2, 0, 0)
        yval = np.insert(a * 1e4, 0, a[0] * 1e4)

        return plot_area(xval, yval, hf)

    def changejawopening(self, newangle, orig):
        """modifies the area function to simulate a modification of the jaw opening"""

        af = self.area
        lf = self.length

        xf = np.cumsum(lf, 0)
        if len(af.shape) == 1:
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
            xf = xf.reshape(-1, 1)

        d_wall = np.sqrt((af[-1, :] - af[orig, :])**2 + (xf[-1, :] - xf[orig, :])**2)
        current_angle = np.sign(af[-1, :] - af[orig, :]) * np.arccos((xf[-1, :] - xf[orig, :]) / d_wall)
        anglechange = newangle - current_angle

        newxf2change = (xf[orig:, :] - xf[orig, :]) * np.cos(anglechange) - \
            (af[orig:, :] - af[orig, :]) * np.sin(anglechange)
        newaf2change = (xf[orig:, :] - xf[orig, :]) * np.sin(anglechange) + \
            (af[orig:, :] - af[orig, :]) * np.cos(anglechange)

        af[orig:, :] = newaf2change + af[orig, :]
        xf[orig:, :] = newxf2change + xf[orig, :]
        newlf = np.matlib.repmat(xf[-1, :] / af.shape[0], af.shape[0], af.shape[1])

        f1 = scintp.interp1d(xf.squeeze(), af.squeeze(),
                             kind='linear', fill_value='extrapolate')
        newaf = f1(np.cumsum(newlf, 0))

        if any(newaf <= 1e-11):
            print('Warning : contact detected!')
            newaf[newaf <= 1e-11] = 1e-11

        self.area = newaf.squeeze()
        self.length = newlf.squeeze()
        _, _, _ = self.characteristics()

        return newaf.squeeze(), newlf.squeeze()
    
    def changeprotrusion(self, new_length, orig_teeth=None):
        """modifies the area function to simulate a change in lip protrusion"""
        
        af = self.area
        lf = self.length

        if len(af.shape) == 1:
            af = af.reshape(-1, 1)
            lf = lf.reshape(-1, 1)
            
        num_lips = af.shape[0] - orig_teeth - 1
        lf[orig_teeth+1:] = lf[orig_teeth+1:] + (new_length - np.sum(lf, 0)) / num_lips
        
        self.length = lf.squeeze()
        self.area = af.squeeze()
        _, _, _ = self.characteristics()
        
        return af.squeeze(), lf.squeeze()
    
    def areamorph(self, area_target, pct_path=50):
        """modifies the area function so that it goes a certain % towards a target"""
        
        
        afMat = np.hstack((self.area.reshape(-1, 1), area_target.area.reshape(-1, 1)))
        lfMat = np.hstack((self.length.reshape(-1, 1), area_target.length.reshape(-1, 1)))

        xi = [0, 1]
        xo = np.arange(101)/ 100

        afOut = lininterp1( xi, afMat, xo, 1 )
        lfOut = lininterp1( xi, lfMat, xo, 1)
        self.area = afOut[:,int(pct_path)]
        self.length = lfOut[:,int(pct_path)]
        
    
    def characteristics(self):
        """returns the characteristics of the area function"""
        
        self.total_length = np.sum(self.length, 0)
        self.constriction_area = np.min(self.area, 0)
        self.constriction_location = np.argmin(self.area, 0)
        
        return self.total_length, self.constriction_area, self.constriction_location
    
    def extend(self, nb_frame):
        """ Extends area function to a specified number of frames """
        if len(self.area.squeeze().shape) > 1:
            raise ValueError("Area function should contain only one frame")
            
        self.area = np.tile(self.area.squeeze().reshape(-1,1), 
                            (1, nb_frame))
        self.length = np.tile(self.length.squeeze().reshape(-1,1), 
                              (1, nb_frame))