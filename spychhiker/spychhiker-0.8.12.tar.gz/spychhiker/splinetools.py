#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:52:12 2021

@author: benjamin
"""

import numpy as np

def check_list(x):
    if isinstance(x, float) or isinstance(x, int):
            x = [x]
    return x

def get_index(spline, time_points):
    return np.array([(np.abs(spline.knots - x)).argmin() - 2 for x in time_points])

def move_spline(spline, time_points, factor):
    
    idx = get_index(spline, time_points)
    spline.knots[idx] += factor

    idxSort = np.argsort(spline.knots)
    spline.knots = spline.knots[idxSort]
    spline.coeff = spline.coeff[idxSort]
    spline.interpolate()

def target_spline(spline, time_points, targets):
    
    idx = get_index(spline, time_points)
    idx_time = np.array([(np.abs(spline.time_points - x)).argmin() 
                         for x in time_points])
    curr_val = spline.values[idx_time]
    nb_iter = 0
    nb_pts = len(time_points)
    cost_fun = np.sum(np.abs(np.array(targets) - np.array(curr_val)))
    while cost_fun > nb_pts and nb_iter < 100:
        curr_factor = np.array(targets) / np.array(curr_val)        
        spline.coeff[idx] *= curr_factor
        spline.interpolate()
        curr_val = spline.values[idx_time]
        cost_fun = np.sum(np.abs(np.array(targets) - np.array(curr_val)))
        nb_iter += 1
        
    if nb_iter >= 100:
        print("Warning: number of iterations exceeds 100")
        
def translate_spline(spline, time_points, factor):
    
    idx = get_index(spline, time_points)
    spline.coeff[idx] *= factor
    spline.interpolate()