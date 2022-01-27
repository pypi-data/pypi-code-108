#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 07:54:59 2020

@author: benjamin
"""

import soundfile
import numpy as np
import copy


def record_to_file(path, data, sample_width, rate):    
    """ saves audio sigbal into file """
    soundfile.write(path, data, int(rate))

def clipper(x, threshold, method, is_relative=True):
    """ returns a soft or hard clipped version of an audio signal"""
    abs_thresh = threshold
    if is_relative:
        abs_thresh = np.max(abs(x)) * threshold

    y = copy.deepcopy(x)
    if method.lower() == 'hard':
        y[x >= abs_thresh] = abs_thresh
        y[x <= -abs_thresh] = -abs_thresh
    if method.lower() == 'soft':
        abs_thresh2 = abs_thresh
        y[x >= abs_thresh2] = abs_thresh
        y[x <= -abs_thresh2] = -abs_thresh
        idx = [xTmp for xTmp in range(len(x)) if
               x[xTmp] >= abs_thresh2 and x[xTmp] <= -abs_thresh2]
        y[idx] = y[idx] - (y[idx]**3) / 3
    if method.lower() not in ['hard', 'soft']:
        raise ValueError("Unexpected method for distortion. Use either hard or soft")
    return y
