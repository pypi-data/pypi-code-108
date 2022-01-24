import numpy as np
from scipy.signal import welch
from scipy.stats import entropy, skew, kurtosis, iqr, linregress
import pandas as pd
import itertools
from cr_features.helper_functions import checkForFeature


def max(array):
    """ Return the maximum value of the given list.

    :param array: the given array
    :return: the maximum value of the list
    """
    return np.max(array, axis=1)

def min(array):
    """ Return the minimum value of the given list.

    :param array: the given array
    :return: the maximum value of the list
    """
    return np.min(array, axis=1)


def countAboveMean(signal):
    """ Returns the number of values in x that are higher than the mean of x

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    mean = np.mean(signal, axis=1)
    return (signal.T - mean > 0).T.sum(axis=1)


def countBelowMean(signal):
    """ Returns the number of values in x that are lower than the mean of x

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    mean = np.mean(signal, axis=1)
    return (signal.T - mean < 0).T.sum(axis=1)


def meanAbsChange(signal):
    """ Returns the mean of absolute differences between subsequent time series values

    :param signal: input signal
    :return: mean of absolute differences
    """
    return np.mean(np.abs(np.diff(signal)), axis=1)


def stdDev(arrayX):
    """ Calculates the standard deviation of the given array

    :param arrayX: the array on which to calculate standard deviation
    :return: standard deviation of the given array
    """
    return np.std(arrayX, axis=1)


def meanChange(signal):
    """ Returns the mean over the differences between subsequent time series values

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    return np.mean(np.diff(signal), axis=1)


def numberOfZeroCrossings(signal):
    """ Calculates the number of crossings of x on 0. A crossing is defined as two sequential values where the first
    value is lower than 0 and the next is greater, or vice-versa.

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    positive = signal > 0
    return np.diff(positive).sum(axis=1)


def numberOfMeanCrossings(signal):
    """ Calculates the number of crossings of x on 0. A crossing is defined as two sequential values where the first
    value is lower than 0 and the next is greater, or vice-versa.

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    mean = signal.mean()
    positive = (signal.T-mean > 0).T
    return np.diff(positive).sum(axis=1)

def absEnergy(signal):
    """
    Returns the absolute energy of the time series which is the sum over the squared values

    .. math::

        E = \\sum_{i=1,\\ldots, n} x_i^2

    :param signal: the time series to calculate the feature of
    :type x: numpy.ndarray
    :return: the value of this feature
    :return type: float
    """

    return np.einsum('ij,ij->i', signal, signal)


def ratioBeyondRSigma(signal, r):
    """ Ratio of values that are more than r*std(x) (so r sigma) away from the mean of x.

    :param signal: the time series to calculate the feature of
    :param r: the ratio to compare with
    :return: the value of this feature
    """
    return np.sum(np.abs((signal.T - np.mean(signal, axis=1))) > r * np.std(signal, axis=1), axis=0) / signal.shape[1]


def autocorrelation(signal, lag):
    """Compute the lag-N autocorrelation.

    This method computes the Pearson correlation between
    the Series and its shifted self.
    :param signal: the signal to preform the autocorrelation on
    :param lag: Number of lags to apply before performing autocorrelation.
    :return:
    """
    signal = pd.DataFrame(signal)
    return signal.apply(lambda x: x.autocorr(lag), axis=1)


def autocorrelations(signal):
    """ This method computes autocorrelations for each lag from 0 to len(signal2D[0]) * 0.7

    :param signal: input signal on which to calculate autocorrelations
    :return: array of autocorrelations
    """
    nlags = int(signal.shape[1] * 0.7)
    autocorrs = []
    for lag in range(nlags):
        autocorrs.append(autocorrelation(signal, lag))
    return np.array(autocorrs).T

def calcArea(data):
    """
    Calculates sum of component
    :param data: data from accelerometer for selected axis (low-pass filtered)
    :return: area
    """
    return np.sum(data, axis=1)

def calcSumPerComponent(data, time):
    """
    Calculates calcSumPerComponent feature
    :param data: data from accelerometer for selected axis
    :param time: array of timestamps
    :return: sum of Xi*dT
    """
    diff = np.diff(time) / 1000
    diff = np.hstack([np.ones((diff.shape[0], 1)), diff])
    res =  np.einsum('ij,ij->i', np.abs(data), diff)
    return res

def magnitudeVector(x, y, z):
    """ Calculates magnitudes of vectors x, y and z

    :param x: x axis
    :param y: y axis
    :param z: z axis
    :return: numpy array of magnitudes
    """
    return np.sqrt(np.square(x) + np.square(y) + np.square(z))

def calcMeanKineticEnergy(data, time):
    """
    Calculates mean kinetic energy for the selected axis
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :param time: array of timestamps
    :return: mean kinetic energy 1/2*mV^2
    """
    weight = 60.0
    diff = np.diff(time) / 1000
    diff = np.hstack([np.ones((diff.shape[0], 1)), diff])
    weighted_data = data*diff

    velocity = np.cumsum(weighted_data, axis=1)
    kinetic_added = 0.5 * weight * velocity * velocity * diff
    kinetic = np.sum(kinetic_added, axis=1)

    return kinetic

def computeACVelocity(data, time):
    """
    Calculates velocity feature
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :param time: array of timestamps
    :return: velocity for selected axis
    """
    diff = np.diff(time) / 1000
    diff = np.hstack([np.ones((diff.shape[0], 1)), diff])
    weighted_data = data * diff
    return np.sum(weighted_data, axis=1)

def calcTotalKineticEnergy(x, y, z, time):
    """
    Calculates total kinetic energy for all axes
    :param x: data from accelerometer for X axis (band-pass filtered)
    :param y: data from accelerometer for Y axis (band-pass filtered)
    :param z: data from accelerometer for Z axis (band-pass filtered)
    :param t: array of timestamps
    :return: total kinetic energy 1/2*mV^2
    """

    total_time = (time[:, -1] - time[:, 0]) / 1000.0
    weight = 60.0
    diff = np.diff(time) / 1000
    diff = np.hstack([np.ones((diff.shape[0], 1)), diff])

    weighted_x = x * diff
    weighted_y = y * diff
    weighted_z = z * diff

    velocity_x = np.cumsum(weighted_x, axis=1)
    velocity_y = np.cumsum(weighted_y, axis=1)
    velocity_z = np.cumsum(weighted_z, axis=1)
    kinetic_added_x = 0.5 * weight * velocity_x * velocity_x * diff
    kinetic_added_y = 0.5 * weight * velocity_y * velocity_y * diff
    kinetic_added_z = 0.5 * weight * velocity_z * velocity_z * diff

    kinetic_x = np.cumsum(kinetic_added_x, axis=1)
    kinetic_y = np.cumsum(kinetic_added_y, axis=1)
    kinetic_z = np.cumsum(kinetic_added_z, axis=1)

    total_energy = kinetic_x.sum(axis=1) + kinetic_y.sum(axis=1) + kinetic_z.sum(axis=1)

    return total_energy / total_time

def calcAcAbsoluteArea(x, y, z):
    """
    Calculates a vector with sums of absolute values for the given sensor
    :param x: x component (band-pass filtered)
    :param y: y component (band-pass filtered)
    :param z: z component (band-pass filtered)
    :return: [sumX, sumY, sumZ]
    """
    return np.array([np.sum(np.abs(x), axis=1),
                     np.sum(np.abs(y), axis=1),
                     np.sum(np.abs(z), axis=1)]).T

def magnitudes(data):
    """ Calculates the sum of squares of given array

    :param data: given array
    :return: sum of squares
    """
    return np.sum(np.square(data), axis=1)

def calcAbsoluteMean(data):
    """

    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: mean (sum)/N
    """
    return np.sum(np.abs(data), axis=1) / data.shape[1]

def calcTotalMagnitude(x, y, z):
    """
    Calculates total magnitude of AC signal for the given sensor
    :param x: x component (band-pass filtered)
    :param y: y component (band-pass filtered)
    :param z: z component (band-pass filtered)
    :return: sqrt(sum(x^2+y^2+z^2))
    """
    return np.sqrt(magnitudes(x) + magnitudes(y) + magnitudes(z))


def calcPostureDistance(meanX, meanY, meanZ):
    """
    Calculates difference between mean values for a given sensor (low-pass filtered)
    :param meanX: mean for X components
    :param meanY: mean for Y components
    :param meanZ: mean for Z components
    :return: [X-Y, X-Z, Y-Z]
    """
    return np.array([meanX - meanY, meanX - meanZ, meanY - meanZ]).T

def calcSkewness(data):
    """
    Calculates skewness for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: skewness for selected vector
    """
    mean = calcAbsoluteMean(data)

    pow3 = np.sum(np.power((data.T - mean).T, 3), axis=1)
    pow2 = np.sum(np.power((data.T - mean).T, 2), axis=1)

    return np.sqrt(data.shape[1]) * pow3 / np.power(pow2, 1.5)

def calcKurtosis(data):
    """
    Calculates Kurtosis for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: kurtosis for selected vector
    """
    mean = calcAbsoluteMean(data)
    pow4 = np.sum(np.power((data.T - mean).T, 4), axis=1)
    pow2 = np.sum(np.power((data.T - mean).T, 2), axis=1)

    return data.shape[1] * pow4 / np.square(pow2) - 3

def calcQuartiles(data):
    """
    Quartiles at 25%, 50% and 75% per signal
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: [accQ25, accQ50, accQ75]
    """
    quantiles = np.quantile(data, [0.25, 0.5, 0.75], axis=1, interpolation="nearest").T
    return quantiles


def calcInterQuartileRange(qData):
    """
    Calculates interquartile range
    :param qData: quartiles vector
    :return: range for the selected axis
    """
    return qData[:, 2] - qData[:, 0]

from cr_features import feature_functions as f

def calcVariance(data):
    """
    Calculates variance for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: variance
    """
    #temp = f.calcVariance(data[0, :])
    #print(list(data[0, :]))
    res = data.var(axis=1)
    return res



def calcCoefficientOfVariation(data):
    """
    Calculates dispersion for a given vector component
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: dispersion
    """
    s = np.sum(np.absolute(data), axis=1)

    return np.sqrt(calcVariance(data)) / s * 100

def calcAmplitude(data):
    """
    Calculates dispersion for a given vector component
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: dispersion
    """
    return np.max(data, axis=1) - np.min(data, axis=1)


def covariance(array1, array2):
    """
    Covariance between two arrays
    :param array1: first array of values
    :param array2: second array of values
    :return: covariance(array1, array2)
    """
    return np.array([np.cov(np.vstack([row1, row2]))[0, 1] for row1, row2 in zip(array1, array2)])


def calcCorrelation(a, b):
    """
    Calculates Pearson's correlation between sensor axis
    :param a: first component (band-pass filtered)
    :param b: second component (band-pass filtered)
    :return: correlation between a and b
    """
    selfCovarianceA = covariance(a, a)
    selfCovarianceB = covariance(b, b)
    s = np.sqrt(selfCovarianceA * selfCovarianceB)
    return covariance(a, b) / s



def calcAreaUnderAccelerationMagnitude(magnitudes, time):
    """
    Calculates AreaUnderAccelerationMagnitude feature
    :param magnitudes: vector of magnitudes
    :param time: array of timestamps
    :return: AreaUnderAccelerationMagnitude for the selected axis
    """

    diff = np.diff(time)
    diff = np.hstack([np.ones((diff.shape[0], 2))*35, diff])[:, :-1]
    return np.einsum('ij,ij->i', np.abs(magnitudes), diff)


def calcMean(data):
    """
    Calculates mean value for a given vector
    :param data: data from accelerometer for selected axis (low-pass filtered)
    :return: mean (sum)/N
    """
    return np.mean(data, axis=1)