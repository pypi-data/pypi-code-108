import re
import pandas as pd
import numpy as np
import librosa
from scipy.io import wavfile
import librosa.display
from pydub import AudioSegment
from IPython.display import display_html
import torch


def _array_to_numpy(arr):
    # convert to np if torch
    if isinstance(arr, torch.Tensor):
        arr = arr.detach().cpu().numpy()
    # squash extra dimensions
    arr = arr.squeeze()
    # TODO: deal with 2 channels
    if 2 in arr.shape:
        raise NotImplementedError("stereo detected")
    return arr


def _array_to_float(arr):
    arr = _array_to_numpy(arr)
    arr = arr = arr.copy().astype(np.float32) / 32768
    return arr


def _array_to_int(arr):
    arr = _array_to_numpy(arr)
    # enforce int16
    if arr.dtype == np.int16:
        pass
    elif arr.dtype in (np.float32, np.float64):
        # alert if signal too high
        if np.abs(arr).max() > 1:
            raise ValueError("signal overflow")
        arr = (arr * 32768).clip(-32768, 32767).astype(np.int16)
    else:
        # TODO: convert other formats
        raise NotImplementedError("unknown format")
    # alert if audio too loud
    if np.abs(arr).mean() / 32768 >= 0.1:
        raise ValueError("audio seems too loud")
    return arr


def play_array(arr, sr=16000):
    arr = _array_to_int(arr)
    display(AudioSegment(
        arr.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    ))
