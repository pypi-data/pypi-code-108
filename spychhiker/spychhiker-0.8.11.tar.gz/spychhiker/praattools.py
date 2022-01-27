#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 10:31:46 2020

@author: benjamin
"""

import parselmouth
from parselmouth.praat import call
import numpy as np
import copy

def sound2sp(x, sp):
    sp.signal = copy.deepcopy(x.values.squeeze())
    sp.sampling_frequency = x.sampling_frequency

def sp2sound(x, sr=None):

    if sr is None:
        sound = parselmouth.Sound(x.signal)
        sound.sampling_frequency = x.sampling_frequency
    else:
        sound = parselmouth.Sound(x)
        sound.sampling_frequency = sr

    return sound

def praat_modif_pitch(sound, time_points, values):
    
    nb_snd = sound.get_number_of_samples()
    sr = sound.sampling_frequency
    f0min = max(70, int(np.ceil(sr / nb_snd * 3)))
    manipulation = call(sound, "To Manipulation", 0.01, f0min, 600)
    newPitch = call("Create PitchTier", "source", 0, sound.xmax)
    for k in range(len(time_points)):
        call(newPitch, "Add point", time_points[k], values[k])
    call([newPitch, manipulation], "Replace pitch tier")
    return call(manipulation, "Get resynthesis (overlap-add)")

def praat_get_pitch(sound, f0min=70, f0max=300):
    
    f0Obj = sound.to_pitch(pitch_floor=f0min, pitch_ceiling=f0max)
    f0 = f0Obj.selected_array['frequency']
    tf0 = f0Obj.xs()    
    return f0, tf0

def praat_get_gci(sound, f0min=70, f0max=300):
    
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    numPoints = call(pointProcess, "Get number of points")
    oldT = []

    for point in range(numPoints):
        point += 1
        t = call(pointProcess, "Get time from index", point)
        oldT.append(t)
        
    return oldT, pointProcess


def praat_get_jitter(sound, nwin=5, f0min=70, f0max=300):
    """ compute jitter """
    if np.mod(nwin, 2) == 0:
        nwin += 1
    mid_win = int(np.floor(nwin / 2))
        
    t0max = 1/f0min
    t0min = 1/f0max

    oldT, _ = praat_get_gci(sound, 70, 300)    
    
    dT = np.diff(oldT)

    idx_False = [x for x in range(len(dT)) if dT[x] < t0min or dT[x] > t0max]
    dT[idx_False] = np.nan
    dT_stack = (np.vstack(((dT[:1:-1]).reshape(-1,1),
                          dT.reshape(-1,1),
                          (dT[-1::-1]).reshape(-1,1)))).reshape(-1)
    
    k_init = len(dT) - 2
    k_fin = 2*len(dT) - 1
    jitt = []
    
    for k in range(k_init, k_fin):
        tmp_win = dT_stack[k-mid_win:k+mid_win+1]
        
        if not np.isnan(dT_stack[k]):
            jitt.append(100*np.nanmean(np.abs(np.diff(tmp_win))) / np.nanmean(tmp_win))
        else:
            jitt.append(np.nan)
        
    return oldT, jitt    

def praat_remove_points(pointProcess):
    
    numPoints = call(pointProcess, "Get number of points")
    while call(pointProcess, "Get number of points") > 0:
        for point in range(numPoints):
            point += 1
            call(pointProcess, "Remove point", point)
    return pointProcess

def praat_change_gci(sound, newT, pointProcess):
    
    manipulation = call(sound, "To Manipulation", 0.01, 75, 600)
    newPP = pointProcess
    for k in range(len(newT)):
        call(newPP, "Add point", newT[k])
    call([newPP, manipulation], "Replace pulses")
    return call(manipulation, "Get resynthesis (overlap-add)")

def praat_change_shimmer(sound, factor, f0min=70, f0max=300):
    
    itsty = sound.to_intensity()
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    numPoints = call(pointProcess, "Get number of points")

    itstyTier = call([itsty, pointProcess], "To IntensityTier")

    r = np.random.rand(numPoints) - 0.5
    for k in range(numPoints):
        k += 1
        currI = call(itstyTier, "Get value at index", k)
        currTime = call(itstyTier, "Get time from index", k)
        newI = currI * (1 + r[k-1] * factor)
        call(itstyTier, "Remove point near", currTime)
        call(itstyTier, "Add point", currTime, newI)

    return call([sound, itstyTier], "Multiply")
    
def praat_change_duration(sound, pts, factor):
    
    manipulation = call(sound, "To Manipulation", 0.01, 75, 600)
    newDuration = call("Create DurationTier", "shorten", 0, sound.xmax)
    call(newDuration, "Add point", 0, factor[0])

    for k in range(len(pts)):
        call(newDuration, "Add point", max(0, pts[k]-1e-3), factor[k])
        call(newDuration, "Add point", pts[k]+1e-3, factor[k+1])        

    call(newDuration, "Add point", sound.xmax, factor[-1])
    call([newDuration, manipulation], "Replace duration tier")
    return call(manipulation, "Get resynthesis (overlap-add)")

def praat_get_formants(snd, nhop, nwin):
    
    sr = snd.sampling_frequency
    pitch = snd.to_pitch(nhop/sr, pitch_floor=75, pitch_ceiling=300)
    pointProcess = call(snd, "To PointProcess (periodic, cc)", 75, 300)

    formants = snd.to_formant_burg(nhop/sr, 5, 5000, nwin/sr, 50)
    numPoints = call(pointProcess, "Get number of points")

    if numPoints == 0:
        numPoints = formants.n_frames
        isZero = True
    else:
        isZero = False
    form_out = np.zeros((4, numPoints))
    bw_out = np.zeros_like(form_out)
    txx = np.zeros(numPoints)

    for point in range(numPoints):
        point += 1
        if isZero:
            t = formants.frame_number_to_time(point)
        else:
            t = call(pointProcess, "Get time from index", point)
        for k in range(4):
            form_out[k, point-1] = formants.get_value_at_time(k+1, t)
            bw_out[k, point-1] = formants.get_bandwidth_at_time(k+1, t)
        txx[point-1] = t
        
    return form_out, bw_out, txx