import numpy as np
import mne
from biosip_tools.eeg import EEG_BANDS


class EEGSeries():
 
    def __init__(self, path: str, sample_rate: int = 500) -> None:
        """Class for EEG time series.
        
        :param path: Path to .npy array. Expected shape is (n_subjects, n_channels, n_samples)
        :type path: str
        :param sample_rate: [description], defaults to 500
        :type sample_rate: int, optional
        """
        self.data = np.load(path)
        self.sample_rate = sample_rate

    def filter(self, l_freq: float, h_freq: float,  verbose=False, **kwargs) -> np.array:
        """Apply a FIR filter to the EEG data. Accepts arguments for mne.filter.filter_data.

        :param l_freq: Lower pass-band edge.
        :type l_freq: float
        :param h_freq: Upper pass-band edge.
        :type h_freq: float
        :return: Filtered data
        :rtype: np.array
        """
        return mne.filter.filter_data(self.data, self.sample_rate, l_freq, h_freq, verbose=verbose, **kwargs)

    def filter_bands(self, **kwargs) -> dict:
        """Return a dictionary of filtered EEG data. 

        :return: Dictionary of filtered data. {band_name: data}
        :rtype: dict
        """
        return {band_name: self.filter(band_range[0], band_range[1], **kwargs) for band_name, band_range in EEG_BANDS.items()}

