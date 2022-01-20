import os

import numpy as np

# copy scipy.io.wavfile to avoid including the entire scipy
from .wavfile import read as wavfile_read
from .wavfile import write as wavfile_write


def read_wav(fname):
    samplerate, samples = wavfile_read(fname)
    if len(samples.shape) > 1:
        samples = samples[:, 0]  # mono
    return samplerate, samples


def rms(samples):
    samples = samples.astype("int64")
    return round(np.sqrt(np.mean(samples ** 2)), 3)


def rms_file(fname, reject_to_short=True):
    samplerate, samples = read_wav(fname)

    # at least 0.25 second
    if reject_to_short and len(samples) < samplerate / 4:
        return None
    return rms(samples)


def wav_size_to_dur(fname):
    st = os.stat(fname)
    return round(st.st_size / 32000, 3)  # 16000 hz * 2bytes (16bit)


def trim_noise(fname, amplify_strength="strong", overwrite=True):
    try:
        begin_trim_sec = 0.0
        end_trim_sec = 0.0
        sr, s = read_wav(fname)

        # constant
        step_sr = 1000
        window = step_sr * 6
        global_peak = np.max(s)

        if amplify_strength.lower() == "strong":
            amplify_rate = 1.4
        else:
            amplify_rate = 1.2

        peak_info = []
        for i in range(0, len(s), step_sr):
            chunk = s[i : i + window]
            peak = np.max(chunk)
            peak_info.append([i, len(chunk), peak])

        avg_start = peak_info[0][2]
        avg_end = peak_info[-4][2]

        avg_min = min(avg_start, avg_end)
        min_factor = 0.1 if avg_min / global_peak < 0.01 else 0.2
        global_min_thresh = min_factor * global_peak

        trim_front = avg_start < global_min_thresh
        trim_rear = avg_end < global_min_thresh

        end = len(peak_info) - 1
        begin = 0

        if trim_front:
            front_thresh = max(avg_start * amplify_rate, global_min_thresh)
            for i in range(begin, end):
                value = peak_info[i][2]
                if value > front_thresh:
                    break
                begin = i

        if trim_rear:
            rear_thresh = max(avg_end * amplify_rate, global_min_thresh)
            for i in range(end, begin, -1):
                value = peak_info[i][2]
                if value > rear_thresh:
                    break
                end = i

        begin_frame = 0
        if trim_front:
            slop = 0
            if begin > 0:
                if peak_info[begin - 1][2] == 0:
                    slop = 999  # inf
                else:
                    slop = abs(peak_info[begin][2] / peak_info[begin - 1][2] - 1)
            # bias = 0.8 if slop < 0.5 else 0.5
            bias = max(0, min(0.6, 1 - slop))
            begin_frame = int(peak_info[begin][0] + window * bias)

        end_frame = len(s)
        if trim_rear:
            slop = 0
            if end < len(peak_info) - 1:
                if peak_info[end + 1][2] == 0:
                    slop = 999  # inf
                else:
                    slop = abs(peak_info[end][2] / peak_info[end + 1][2] - 1)
            # bias = 0.8 if slop > 0.5 else 0.5
            bias = min(0.6, slop)
            end_frame = int(peak_info[end][0] + peak_info[end][1] - window * bias)

        # rewrite the same file
        begin_sec = begin_frame / sr
        end_sec = end_frame / sr

        if end_sec - begin_sec > 0.5 and (begin_frame > 0 or end_frame < len(s)):
            if overwrite:
                wavfile_write(fname, sr, s[begin_frame:end_frame])

            # this is different than the speech scoring
            # here return how much is trimmed out head, tail
            # instead of start and end time to keep
            begin_trim_sec = round(begin_sec, 3)
            end_trim_sec = round(len(s) / sr - end_sec, 3)
    except Exception:
        pass
    finally:
        return begin_trim_sec, end_trim_sec
