import numpy as np
import math


def peak_detector(ppg, Fs):
    """
    Peak detector written by Gasper Slapnicar. Optimized for detecting peaks in PPG signal.
    :param ppg: Signal where peaks are to be detected. 1-D array like
    :param Fs: Sampling frequency
    :return: Peaks and valleys in PPG. Two arrays of indices in ppg input
    """
    peak_duration = int(math.floor((1.0 / 9) * Fs))
    aver_pulse_rate = int(math.floor((2.0 / 3) * Fs))
    aver_level_window = int(math.floor(2 * Fs))

    mean_coef_for_threshold = 0.02
    signal_length = len(ppg)

    ppg_squared = np.square(ppg)
    ppg_squared[ppg < 0] = 0

    mean_peak_level = np.convolve(ppg_squared, np.ones((peak_duration,)) / peak_duration, mode='same')
    mean_beat_level = np.convolve(ppg_squared, np.ones((aver_pulse_rate,)) / aver_pulse_rate, mode='same')

    thresh1 = np.add(mean_beat_level,
                     mean_coef_for_threshold * np.convolve(ppg_squared,
                                                           np.ones((aver_level_window,)) / aver_level_window,
                                                           mode='same'))
    block_of_interest = np.zeros(signal_length)
    block_of_interest[mean_peak_level > thresh1] = 1

    block_edges = np.diff(block_of_interest)
    block_start = np.add(np.where(block_edges == 1), 1)[0]
    if block_start.size == 0:
        return np.array([]), np.array([])
    else:
        block_end = np.where(block_edges == -1)[0]

        if block_end.size == 0:
            return np.array([]), np.array([])

        if block_start[0] > block_end[0]:
            block_start = np.insert(block_start, 0, 1, axis=0)

        if block_start[-1] > block_end[-1]:
            block_end = np.append(block_end, signal_length)

        if len(block_start) != len(block_end):
            return np.array([]), np.array([])

        length_block = np.subtract(block_end, block_start)
        correct_blocks = np.where(length_block > peak_duration)

        peak_pos = np.zeros(len(correct_blocks[0]))
        i_peak = 0
        for iBlock in correct_blocks[0]:
            block_of_interest = ppg_squared[block_start[iBlock]:block_end[iBlock]]
            peak_pos[i_peak] = max(range(len(block_of_interest)), key=block_of_interest.__getitem__)
            peak_pos[i_peak] = peak_pos[i_peak] + (block_start[iBlock] - 1)
            i_peak += 1

        interpeak_threshold_coeff = 0.65
        max_over_average = 1.15
        need_check = True
        while need_check:
            interpeak = np.diff(peak_pos)

            if interpeak.size == 0:
                return np.array([]), np.array([])

            mean_interpeak = np.mean(interpeak)
            interpeak_double = np.insert(np.add(interpeak[0:-1], interpeak[1:]), 0, 2 * interpeak[0], axis=0)
            interpeak_thresh = np.insert(interpeak_double[0:-2], 0, [2 * mean_interpeak, 2 * mean_interpeak], axis=0)
            interpeak_thresh[interpeak_thresh > 2 * max_over_average * mean_interpeak] = 2 * max_over_average \
                                                                                         * mean_interpeak
            interpeak_thresh = interpeak_thresh * interpeak_threshold_coeff
            index_short_interval = np.where(interpeak_double < interpeak_thresh)[0]

            if index_short_interval.size != 0:
                peak_pos = np.delete(peak_pos, index_short_interval.tolist())
            else:
                need_check = False

        # Add valley (simple detection)
        valley_pos = []
        for start, end in zip(peak_pos[0:-1].astype('int'), peak_pos[1:].astype('int')):
            valley_pos.append(min(range(len(ppg[start:end])), key=ppg[start:end].__getitem__) + start)

        # Addition because I missed it somewhere in the code...but i cant find where
        return np.add(peak_pos, 1).astype('int'), np.array(valley_pos)
