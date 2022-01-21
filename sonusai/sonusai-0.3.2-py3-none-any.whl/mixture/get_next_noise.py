import numpy as np


def get_next_noise(offset_in: int, length: int, audio_in) -> (np.ndarray, int):
    audio_out = np.zeros(length, dtype=np.int16)
    offset_out = offset_in
    for out_index in range(length):
        audio_out[out_index] = audio_in[offset_out]
        offset_out += 1
        if offset_out == len(audio_in):
            offset_out = 0

    return audio_out, offset_out
