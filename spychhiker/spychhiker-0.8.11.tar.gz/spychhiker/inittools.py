#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 07:54:59 2020

@author: benjamin
"""

from os import path
from .speechaudio import SpeechAudio

import numpy as np

def file2speech(fileName, chn=1, sro=None, start=0, end=-1):
    
    if path.isfile(fileName):
        _, ext = path.splitext(fileName)
        if ext in [".mp3", ".sph", ".flac"]:
            import librosa
            import warnings
            warnings.filterwarnings('ignore')
            y, sr = librosa.load(fileName)
        else:
            import soundfile 
            y, sr = soundfile.read(fileName)
        if len(y.shape) == 2:
            idx = np.argmax(y.shape)
            if idx == 0:
                y = y[:,chn-1]
            else:
                y = y[chn-1,:]
                
        idx1 = 0
        idx2 = len(y)
        if start > 0:
            idx1 = int(start * sr)
        if end > 0:
            idx2 = int(end * sr)            
        if idx1 > 0 or idx2 < len(y):
            y = y[idx1:idx2]
        try:
            SpeechObject = SpeechAudio('signal', y.astype(float), 
                                       'sampling_frequency', sr)
        except:
            SpeechObject = SpeechAudio('signal', np.float32(y), 
                                       'sampling_frequency', sr)
        del y
            
        if sro is not None:
            if sr != sro:
                SpeechObject.speechresample(sro)
    else:
        raise ValueError("File " + fileName + " does not exist")    
    return SpeechObject