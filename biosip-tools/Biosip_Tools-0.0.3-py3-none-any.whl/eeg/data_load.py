import numpy as np
from biosip_tools.eeg.timeseries import EEGSeries

def load_time_series(path: str) -> np.array: 
    """Load time series from file. e.g. EEG_X_X_X.npy

    :param path: path to file
    :type path: str
    :return: EEGSeries class
    :rtype: EEGSeries
    """
    return EEGSeries(np.load(path))


