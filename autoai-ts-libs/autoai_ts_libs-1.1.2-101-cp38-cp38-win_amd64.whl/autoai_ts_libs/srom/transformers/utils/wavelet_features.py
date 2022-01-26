import numpy as np
from collections import Counter
import scipy.stats

def calculate_wavelet_features_for_band(list_values):
    counter_values = Counter(list_values).most_common()
    probabilities = [elem[1]/len(list_values) for elem in counter_values]
    entropy = scipy.stats.entropy(probabilities)

    n5 = np.nanpercentile(list_values, 5)
    n25 = np.nanpercentile(list_values, 25)
    n75 = np.nanpercentile(list_values, 75)
    n95 = np.nanpercentile(list_values, 95)
    median = np.nanpercentile(list_values, 50)
    mean = np.nanmean(list_values)
    std = np.nanstd(list_values)
    var = np.nanvar(list_values)
    rms = np.nanmean(np.sqrt(list_values**2))

    zero_crossing_indices = np.nonzero(np.diff(np.array(list_values) > 0))[0]
    no_zero_crossings = len(zero_crossing_indices)
    mean_crossing_indices = np.nonzero(np.diff(np.array(list_values) > np.nanmean(list_values)))[0]
    no_mean_crossings = len(mean_crossing_indices)
    [no_zero_crossings, no_mean_crossings]

    return [entropy] + [no_zero_crossings, no_mean_crossings] + [n5, n25, n75, n95, median, mean, std, var, rms]

from pywt import wavedec
def get_Haar_Wavelet(x):
    list_coeff = wavedec(x, 'haar')
    features = []
    for coeff in list_coeff:
        features += calculate_wavelet_features_for_band(coeff)
    return features