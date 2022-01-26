from biosip_tools.eeg import EEG_BANDS
import mne
import numpy as np

def filter_eeg(data: np.array, l_freq: float, h_freq: float, sample_rate = 500) -> np.array:
    """[summary]

    :param data: [description]
    :type data: np.array
    :param l_freq: [description]
    :type l_freq: float
    :param h_freq: [description]
    :type h_freq: float
    :param sample_rate: [description], defaults to 500
    :type sample_rate: int, optional
    :return: [description]
    :rtype: np.array
    """
    return mne.filter.filter_data(data, sample_rate, l_freq, h_freq)


def filter_bands(data: np.array):
    """[summary]

    :param data: [description]
    :type data: np.array
    :return: [description]
    :rtype: list
    """
    return [(band,filter_eeg(data, value[0], value[1])) for band, value in EEG_BANDS.items()]