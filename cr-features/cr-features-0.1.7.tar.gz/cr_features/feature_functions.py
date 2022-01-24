import numpy as np
from scipy.signal import welch
from scipy.stats import entropy, skew, kurtosis, iqr, linregress
import pandas as pd
import itertools
from cr_features.helper_functions import checkForFeature


def computeFreqFeatures(data, Fs, featureNames=None):
    """ Computes frequency features of the given array. The signal is converted to power spectral density signal and
    features are calculated on that signal

    :param data: data on which to calculate the features
    :param featureNames: names of features to calculate
    :param Fs: sampling rate of the given data
    :return: the calculated features (names of the features are given in array "freqFeatureNames")
    """
    features = {}
    
    ## 3 highest peaks and corresponding freqs
    if len(data) < 256:
        f, Pxx_den = welch(data, Fs, nperseg=len(data))  # f: array of sample frequencies, Pxx_den: power spectrum of data
    else:
        f, Pxx_den = welch(data, Fs)  # f: array of sample frequencies, Pxx_den: power spectrum of data

    # arr.argsort() returns an array of indices of the same shape as arr that that would sort the array
    # arr[arr.argsort()] returns the sorted array arr (if one-dimensional)
    indices_of_max = Pxx_den.argsort()[-3:][::-1]  # last three values (=highest peaks), reversed (?)

    if checkForFeature("fqHighestPeakFreqs", featureNames):
        highestPeakFreqs = f[indices_of_max]  # three frequencies corresponding to the largest peaks added to features
        features["fqHighestPeakFreq1"] = highestPeakFreqs[0]
        features["fqHighestPeakFreq2"] = highestPeakFreqs[1]
        features["fqHighestPeakFreq3"] = highestPeakFreqs[2]

    if checkForFeature("fqHighestPeaks", featureNames):
        highestPeaks = Pxx_den[indices_of_max]  # three largest peaks added to features
        features["fqHighestPeak1"] = highestPeaks[0]
        features["fqHighestPeak2"] = highestPeaks[1]
        features["fqHighestPeak3"] = highestPeaks[2]

    ## Energy and Entropy
    # np.fft.fft() computes the one-dimensional n-point discrete Fourier Transform (DFT) with the efficient FFT algorithm
    Y = np.fft.fft(data)
    # energy calculated as the sum of the squared FFT component magnitudes, and normalized
    Y_abs = np.abs(Y)
    energy_feat = np.sum(np.square(Y_abs)) / len(data)  # np.abs = absolute value

    entropy_feat = entropy(np.abs(Y)) if Y_abs.any() else np.NaN

    if checkForFeature("fqEnergyFeat", featureNames):
        features["fqEnergyFeat"] = energy_feat

    if checkForFeature("fqEntropyFeat", featureNames):
        features["fqEntropyFeat"] = entropy_feat

    # Binned distribution (histogram)
    # First, the PSD is split into 10 equal-sized bins ranging from 0 Hz to 25 Hz.
    # Then, the fraction of magnitudes falling into each bin is calculated.
    if checkForFeature("fqHistogramBins", featureNames):
        total_fft_sum = np.sum(np.square(Pxx_den))

        def getBin(start, end):
            return np.nan if total_fft_sum == 0 else np.sum(np.square(Pxx_den[start:end])) / total_fft_sum

        features["fqHistogramBin1"] = getBin(0, 5)
        features["fqHistogramBin2"] = getBin(5, 10)
        features["fqHistogramBin3"] = getBin(10, 15)
        features["fqHistogramBin4"] = getBin(15, 20)
        features["fqHistogramBin5"] = getBin(20, 25)
        features["fqHistogramBin6"] = getBin(25, 30)
        features["fqHistogramBin7"] = getBin(30, 35)
        features["fqHistogramBin8"] = getBin(35, 40)
        features["fqHistogramBin9"] = getBin(40, 45)
        features["fqHistogramBin10"] = getBin(45, len(Pxx_den))

    # Statistical features
    if checkForFeature("fqAbsMean", featureNames):
        features["fqAbsMean"] = np.mean(np.abs(data))  # this on raw signal
    if checkForFeature("fqAbsMean", featureNames):
        features["fqSkewness"] = skew(Pxx_den)  # this on "distribution-like" periodogram
    if checkForFeature("fqKurtosis", featureNames):
        features["fqKurtosis"] = kurtosis(Pxx_den)  # this on "distribution-like" periodogram
    if checkForFeature("fqInterquart", featureNames):
        features["fqInterquart"] = iqr(data)  # this on raw signal

    return features


def calcAreaUnderAccelerationMagnitude(magnitudes, time):
    """
    Calculates AreaUnderAccelerationMagnitude feature
    :param magnitudes: vector of magnitudes
    :param time: array of timestamps
    :return: AreaUnderAccelerationMagnitude for the selected axis
    """

    eeArea = 0.0
    dT = 35

    for i in range(len(magnitudes)):
        eeArea += magnitudes[i] * dT  # - gravity
        if i > 0:
            dT = time[i] - time[i - 1]
        else:
            dT = 35
    return eeArea


def calcAverageVectorLength(magnitudes):
    """
    Calculates mean of magnitude vector
    :param magnitudes: vector of magnitudes
    :return: mean of magnitude vector
    """
    return np.sum(magnitudes) / (len(magnitudes))


def calcAverageVectorLengthPower(magnitudes):
    """
    Calculates square mean of magnitude vector
    :param magnitudes: vector of magnitudes
    :return: mean of magnitude vector squared
    """
    return np.square(calcAverageVectorLength(magnitudes))


def calcMeanKineticEnergy(data, time):
    """
    Calculates mean kinetic energy for the selected axis
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :param time: array of timestamps
    :return: mean kinetic energy 1/2*mV^2
    """
    weight = 60.0
    dT = 1.0
    velocity = 0.0
    kinetic = 0.0

    for i in range(len(data)):
        velocity += data[i] * dT
        kinetic += 0.5 * weight * velocity * velocity * dT
        if i < len(time) - 1:
            dT = (time[i + 1] - time[i]) / 1000.0

    return kinetic


def calcPeaks(magnitudes):
    """
    Calculates number of peaks and sum of values
    :param magnitudes: vector of magnitudes
    :return: array of double - [0] number of peaks, [1] sum of peak values
    """
    maxValue = 500.0
    previous = -200.0
    threshold = 3
    peaks = np.empty(0)
    sumOfPeakValues = 0.0
    peak = False

    for curMagnitude in magnitudes:
        if curMagnitude > threshold:
            if curMagnitude >= maxValue:
                maxValue = curMagnitude
                peak = True
            elif curMagnitude < maxValue:
                if peak and previous > curMagnitude:
                    peaks = np.append(peaks, maxValue)
                    peak = False
                    sumOfPeakValues += maxValue

            if curMagnitude > previous and not peak:
                peak = True
                maxValue = -200.0
            previous = curMagnitude

    return np.array([float(len(peaks)), sumOfPeakValues])


def calcTotalKineticEnergy(x, y, z, t):
    """
    Calculates total kinetic energy for all axes
    :param x: data from accelerometer for X axis (band-pass filtered)
    :param y: data from accelerometer for Y axis (band-pass filtered)
    :param z: data from accelerometer for Z axis (band-pass filtered)
    :param t: array of timestamps
    :return: total kinetic energy 1/2*mV^2
    """
    weight = 60.0
    totaltime = (t[-1] - t[0]) / 1000.0

    dT = 1.0
    velocityX = 0.0
    velocityY = 0.0
    velocityZ = 0.0
    kineticX = 0.0
    kineticY = 0.0
    kineticZ = 0.0
    totalEnergy = 0.0

    for i in range(len(x)):
        velocityX += x[i] * dT
        velocityY += y[i] * dT
        velocityZ += z[i] * dT

        kineticX += 0.5 * weight * velocityX * velocityX * dT
        kineticY += 0.5 * weight * velocityY * velocityY * dT
        kineticZ += 0.5 * weight * velocityZ * velocityZ * dT

        totalEnergy += kineticX + kineticY + kineticZ
        if i < t.size - 1:
            dT = (t[i + 1] - t[i]) / 1000.0

    return totalEnergy / totaltime


def calcAcAbsoluteArea(x, y, z):
    """
    Calculates a vector with sums of absolute values for the given sensor
    :param x: x component (band-pass filtered)
    :param y: y component (band-pass filtered)
    :param z: z component (band-pass filtered)
    :return: [sumX, sumY, sumZ]
    """
    return np.array([np.sum(np.absolute(x)), np.sum(np.absolute(y)), np.sum(np.absolute(z))])


def calcAbsoluteMean(data):
    """

    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: mean (sum)/N
    """
    return np.sum(np.absolute(data)) / len(data)


def calcAmplitude(data):
    """
    Calculates dispersion for a given vector component
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: dispersion
    """
    return np.max(data) - np.min(data)


def calcCoefficientOfVariation(data):
    """
    Calculates dispersion for a given vector component
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: dispersion
    """
    s = np.sum(np.absolute(data))
    if s == 0:
        return np.NaN
    return np.sqrt(calcVariance(data)) / s * 100


#
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
    if s == 0:
        return np.NaN
    return covariance(a, b) / s


def calcEntropy(data):
    """
    Calculates the degree of disorder
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: entropy for the selected axis
    """
    acc = 0
    for d in normalize(fftMagnitude(fft(data))):
        if d == 0:
            return np.NaN
        acc += d * np.log(d) / np.log(2.0)

    return -acc


#
def calcInterQuartileRange(qData):
    """
    Calculates interquartile range
    :param qData: quartiles vector
    :return: range for the selected axis
    """
    return qData[2] - qData[0]


def calcKurtosis(data):
    """
    Calculates Kurtosis for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: kurtosis for selected vector
    """
    mean = calcAbsoluteMean(data)

    acc = 0
    for d in data:
        acc += np.power(d - mean, 4.0)
    pow4 = acc

    acc = 0
    for d in data:
        acc += np.power(d - mean, 2.0)
    pow2 = acc
    if pow2 == 0:
        return np.NaN
    return len(data) * pow4 / np.square(pow2) - 3


def calcMeanCrossingRate(data):
    """
    Calculates the number of signal crossings with mean
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: number of mean crossings
    """
    mean = np.sum(np.abs(data)) / len(data)

    crossings = 0
    last = data[0] - mean

    for i in range(len(data)):
        current = data[i] - mean
        if last * current < 0:
            crossings += 1
        last = current

    return crossings


def calcQuartiles(data):
    """
    Quartiles at 25%, 50% and 75% per signal
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: [accQ25, accQ50, accQ75]
    """
    sorted1 = sorted(data)
    size = len(data)
    return np.array([sorted1[int(size / 4)], sorted1[int(size / 2)], sorted1[int(size * 3 / 4)]])


def calcSkewness(data):
    """
    Calculates skewness for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: skewness for selected vector
    """
    mean = calcAbsoluteMean(data)

    acc = 0
    for d in data:
        acc += np.power(d - mean, 3.0)
    pow3 = acc

    acc = 0
    for d in data:
        acc += np.power(d - mean, 2.0)
    pow2 = acc
    if pow2 == 0:
        return np.NaN
    return np.sqrt(float(len(data))) * pow3 / np.power(pow2, 1.5)


#
def calcTotalAbsoluteArea(area):
    """
    Calculates sum of component areas for selected sensor (@see calcAcAbsoluteArea)
    :param area: [sumX, sumY, sumZ] for given device (band-pass filtered) (@see calcAcAbsoluteArea)
    :return: sum of component sums
    """
    return np.sum(area)


def calcTotalEnergy(data):
    """
    Calculates total magnitude of AC signal for the given sensor
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: total energy for selected axis
    """
    fftMagnitudeTmp = fftMagnitude(fft(data))

    return np.sum(np.square(fftMagnitudeTmp[1:])) / len(fftMagnitudeTmp)


def calcDominantFrequencyEnergy(data):
    """
    Calculates ratio of energy in dominant frequency
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: energy ratio for selected axis
    """
    fftMagnitudeTmp = fftMagnitude(fft(data))
    sortedTmp = sorted(fftMagnitudeTmp)
    s = np.sum(sortedTmp)
    if s == 0:
        return np.NaN
    return sortedTmp[-1] / s


def calcTotalMagnitude(x, y, z):
    """
    Calculates total magnitude of AC signal for the given sensor
    :param x: x component (band-pass filtered)
    :param y: y component (band-pass filtered)
    :param z: z component (band-pass filtered)
    :return: sqrt(sum(x^2+y^2+z^2))
    """
    return np.sqrt(magnitudes(x) + magnitudes(y) + magnitudes(z))


def calcVariance(data):
    """
    Calculates variance for given vector
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :return: variance
    """
    acc = 0
    for d in data:
        acc = acc + np.square(d - calcAbsoluteMean(data)) / len(data)
    return acc


def calcArea(data):
    """
    Calculates sum of component
    :param data: data from accelerometer for selected axis (low-pass filtered)
    :return: area
    """
    return np.sum(data)


def calcMean(data):
    """
    Calculates mean value for a given vector
    :param data: data from accelerometer for selected axis (low-pass filtered)
    :return: mean (sum)/N
    """
    return np.sum(data) / len(data)


def calcPostureDistance(meanX, meanY, meanZ):
    """
    Calculates difference between mean values for a given sensor (low-pass filtered)
    :param meanX: mean for X components
    :param meanY: mean for Y components
    :param meanZ: mean for Z components
    :return: [X-Y, X-Z, Y-Z]
    """
    return np.array([meanX - meanY, meanX - meanZ, meanY - meanZ])


def calcTotalMean(sumPhone, sumBand):
    """
    Calculates mean of all sensors (low-pass filtered)
    :param sumPhone: meanX + meanY + meanZ
    :param sumBand: meanX + meanY + meanZ
    :return: mean of all means
    """
    return (sumPhone.sum() + sumBand.sum()) / 6


def calcPeakCount(magnitudes):
    """
    Calculates PeakCount feature
    :param magnitudes: vector of magnitudes
    :return: [numberOfPeaks, sumOfPeakValues, peakAvg, amplitudeAvg]
    """
    previous = 0.0
    eExpenditurePeaks = 0.0
    eExpenditureAmplitude = 0.0

    state = np.zeros(0)
    peaks = np.zeros(0)
    low = -1.0

    for currentmagnitude in magnitudes:
        if currentmagnitude > previous:
            state = np.append(state, True)
        else:
            state = np.append(state, False)

        if len(state) > 2:
            state = np.delete(state, 0)
            if state[0] and not state[1]:
                if low != -1.0:
                    eExpenditureAmplitude = previous - low
                else:
                    low = previous
                if previous - low > 1.0:
                    peaks = np.append(peaks, currentmagnitude)
                    eExpenditurePeaks += previous

            if not state[0] and state[1]:
                low = previous

        previous = currentmagnitude

    peaksReturn0 = len(peaks)
    peaksReturn1 = eExpenditurePeaks
    peaksReturn2 = 0.0
    peaksReturn3 = 0.0
    if len(peaks) > 0:
        peaksReturn2 = eExpenditurePeaks / len(peaks)
        peaksReturn3 = eExpenditureAmplitude / len(peaks)

    return np.array([float(peaksReturn0), peaksReturn1, peaksReturn2, peaksReturn3])


def calcSumPerComponent(data, time):
    """
    Calculates calcSumPerComponent feature
    :param data: data from accelerometer for selected axis
    :param time: array of timestamps
    :return: sum of Xi*dT
    """
    calc = 0.0
    dT = 1.0

    for i in range(len(data)):
        calc += np.abs(data[i]) * dT
        if i < len(data) - 1:
            dT = (time[i + 1] - time[i]) / 1000.0

    return calc


def computeACVelocity(data, time):
    """
    Calculates velocity feature
    :param data: data from accelerometer for selected axis (band-pass filtered)
    :param time: array of timestamps
    :return: velocity for selected axis
    """
    calc = 0.0
    dT = 1.0

    for i in range(len(data)):
        calc += data[i] * dT
        if i < data.size - 1:
            dT = (time[i + 1] - time[i]) / 1000.0

    return calc


def lowPassFilter(input, alpha=0.2):
    """ Low-pass filter implemented in discrete time

    :param input: input signal to be filtered
    :param alpha: smoothing factor
    :return: filtered signal
    """
    output = np.zeros(input.size)
    output[0] = input[0]
    for i in range(1, output.size):
        output[i] = output[i - 1] + alpha * (input[i] - output[i - 1])
    return output


def bandPassFilter(input, alphaLpf=0.2, alphaHpf=0.6):
    """ Band-pass filer implemented in discrete time

    :param input: input signal to be filtered
    :param alphaLpf: smoothing factor for LPF
    :param alphaHpf: smoothing factor for HPF
    :return: filtered signal
    """
    output = lowPassFilter(input, alphaLpf)
    output = highPassFilter(output, alphaHpf)
    return output


def highPassFilter(input, alpha=0.6):
    """ High-pass filter implemented in discrete time

    :param input: input signal to be filtered
    :param alpha: smoothing factor
    :return: filtered signal
    """
    output = np.zeros(input.size)
    output[0] = input[0]
    for i in range(1, output.size):
        output[i] = alpha * (output[i - 1] + input[i] - input[i - 1])
    return output


def magnitudeVector(x, y, z):
    """ Calculates magnitudes of vectors x, y and z

    :param x: x axis
    :param y: y axis
    :param z: z axis
    :return: numpy array of magnitudes
    """
    acc = np.zeros(x.size)
    for i in range(acc.size):
        acc[i] = np.sqrt(np.square(x[i]) + np.square(y[i]) + np.square(z[i]))
    return acc


def sum(data):
    """ Sums up the given array

    :param data: array to sum up
    :return: summed value
    """
    return np.sum(data)


def absoluteSum(data):
    """ Sums up absolute values of the given array

    :param data: array to sum up
    :return: summed value
    """
    return np.sum(np.abs(data))


def fft(data):
    """ Performs fast fourier transform on the given array

    :param data: the array on which fft should be performed
    :return: processed array
    """
    tmpArray = [None] * (len(data) * 2)
    for i in range(len(data)):
        tmpArray[i] = data[i]
    tmpArray = np.fft.fft(tmpArray, len(data))

    tmpArray2 = []
    for t in tmpArray:
        tmpArray2.append(t.real)
        tmpArray2.append(t.imag)

    if len(data) % 2 == 0:
        ret = np.zeros(len(data))
    else:
        ret = np.zeros(len(data) + 1)

    for i, _ in enumerate(ret):
        ret[i] = tmpArray2[i]
    return ret


def fftMagnitude(data):
    """

    :param data:
    :return:
    """
    ret = np.zeros(int(len(data) / 2))
    for i, _ in enumerate(ret):
        ret[i] = np.sqrt(np.square(data[2 * i]) + np.square(data[2 * i + 1]))
    return ret


def normalize(data):
    """ Normalize the given array

    :param data: the array to normalize
    :return: normalized array
    """
    ret = np.zeros(len(data))
    sum = np.sum(data)
    for i, _ in enumerate(data):
        if sum == 0:
            ret[i] = np.NaN
        else:
            ret[i] = data[i] / sum
    return ret


def covariance(array1, array2):
    """
    Covariance between two arrays
    :param array1: first array of values
    :param array2: second array of values
    :return: covariance(array1, array2)
    """
    cov = 0.0

    m1 = np.sum(np.abs(array1))
    m2 = np.sum(np.abs(array2))

    for i, _ in enumerate(array1):
        cov += (array1[i] - m1) * (array2[i] - m2)

    return cov


def magnitudes(data):
    """ Calculates the sum of squares of given array

    :param data: given array
    :return: sum of squares
    """
    acc = 0
    for d in data:
        acc += np.square(d)
    return acc


def calcRoll(arrayAy, arrayAz):
    """ Calculate the roll value of y and z axis

    :param arrayAy: array of y values
    :param arrayAz: array of z values
    :return: array of calculated roll values
    """
    roll = np.zeros(arrayAy.size)

    for i, _ in enumerate(arrayAy):
        roll[i] = np.arctan2(arrayAz[i], arrayAy[i])

    return roll


def calcPitch(arrayAx, arrayAy, arrayAz):
    """Calculate the pitch

    :param arrayAx: array of x values
    :param arrayAy: array of y values
    :param arrayAz: array of z values
    :return: array of calculated pitch values
    """
    pitch = np.zeros(arrayAx.size)

    for i, _ in enumerate(arrayAy):
        pitch[i] = np.arctan2(-arrayAx[i], (arrayAy[i] * arrayAy[i] + arrayAz[i] * arrayAz[i]))

    return pitch


def stdDev(arrayX):
    """ Calculates the standard deviation of the given array

    :param arrayX: the array on which to calculate standard deviation
    :return: standard deviation of the given array
    """
    std = 0.0

    mean = calcMean(arrayX)
    for cnt, _ in enumerate(arrayX):
        std += (arrayX[cnt] - mean) * (arrayX[cnt] - mean);

    return np.sqrt(std / arrayX.size)


def rollMotionAmount(roll):
    """
    amount of wrist roll motion
    Improving the Recognition of Eating Gestures Using Intergesture Sequential Dependencies [R.I. Ramos-Garcia]
    """
    meanRoll = calcMean(roll)
    rollMot_mean = np.zeros(roll.size)

    for i in range(roll.size):
        rollMot_mean[i] = np.abs(roll[i] - meanRoll)  # - gravity;

    return calcMean(rollMot_mean)


def rollMotionRegularity(roll):
    """
    regularity of wrist roll motion
    represents the percentage of time that the wrist is in roll motion
    Improving the Recognition of Eating Gestures Using Intergesture Sequential Dependencies [R.I. Ramos-Garcia]
    """
    rollBoundary = 10 * (np.pi / 180)
    instance_number = 0.0

    for i in range(roll.size):
        if np.abs(roll[i]) > rollBoundary:
            instance_number += 1.0

    return instance_number / roll.size


def manipulation(axLow, ayLow, azLow, roll, pitch):
    """

    :param axLow: low-pass filtered accelerometer's x axis
    :param ayLow: low-pass filtered accelerometer's y axis
    :param azLow: low-pass filtered accelerometer's z axis
    :param roll: roll value
    :param pitch: pitch value
    :return: manipulation array
    """
    man_velocity = np.zeros(roll.size)

    for i in range(roll.size):
        man_velocity[i] = \
            (np.abs(roll[i]) + np.abs(pitch[i])) / (np.abs(axLow[i]) + np.abs(ayLow[i]) + np.abs(azLow[i]))
    return calcMean(man_velocity)


def min(list):
    """ Return the minimum value of the given list.

    :param list: the given list
    :return: the minimum value of the list
    """
    return np.min(list)


def max(list):
    """ Return the maximum value of the given list.

    :param list: the given list
    :return: the maximum value of the list
    """
    return np.max(list)


def avg(list):
    """ Return the average value of the given list.

    :param list: the given list
    :return: the average value of the list
    """
    return np.average(list)


def countAboveMean(signal):
    """ Returns the number of values in x that are higher than the mean of x

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    mean = np.mean(signal)
    return np.where(signal > mean)[0].size


def countBelowMean(signal):
    """ Returns the number of values in x that are lower than the mean of x

    :param signal: the time series to calculate the feature of
    :return: the value of this feature
    """
    mean = np.mean(signal)
    return np.where(signal < mean)[0].size


def meanAbsChange(signal):
    """ Returns the mean of absolute differences between subsequent time series values

    :param signal: input signal
    :return: mean of absolute differences
    """
    return np.mean(np.abs(np.diff(signal)))


def autocorrelation(signal, lag):
    """Compute the lag-N autocorrelation.

    This method computes the Pearson correlation between
    the Series and its shifted self.
    :param signal: the signal to preform the autocorrelation on
    :param lag: Number of lags to apply before performing autocorrelation.
    :return:
    """
    signal = pd.Series(signal)
    return signal.autocorr(lag)


def autocorrelations(signal):
    """ This method computes autocorrelations for each lag from 0 to len(signal2D[0]) * 0.7

    :param signal: input signal on which to calculate autocorrelations
    :return: array of autocorrelations
    """
    nlags = int(len(signal) * 0.7)
    autocorrs = np.empty(nlags)
    for lag in range(nlags):
        autocorrs[lag] = autocorrelation(signal, lag)
    return autocorrs


def _calcMaxLengthOfSequenceTrueOrOne(signal):
    if len(signal) == 0:
        return 0
    else:
        res = [len(list(group)) for value, group in itertools.groupby(signal) if value == 1]
        return max(res) if len(res) > 0 else 0


def meanChange(x):
    """ Returns the mean over the differences between subsequent time series values

    :param x: the time series to calculate the feature of
    :return: the value of this feature
    """
    x = np.asarray(x)
    return (x[-1] - x[0]) / (len(x) - 1) if len(x) > 1 else np.NaN


def numberOfZeroCrossings(x):
    """ Calculates the number of crossings of x on 0. A crossing is defined as two sequential values where the first
    value is lower than 0 and the next is greater, or vice-versa.

    :param x: the time series to calculate the feature of
    :return: the value of this feature
    """
    x = np.asarray(x)
    positive = x > 0
    return np.where(np.diff(positive))[0].size


def ratioBeyondRSigma(x, r):
    """ Ratio of values that are more than r*std(x) (so r sigma) away from the mean of x.
    
    :param x: the time series to calculate the feature of
    :param r: the ratio to compare with
    :return: the value of this feature
    """
    return np.sum(np.abs(x - np.mean(x)) > r * np.std(x)) / x.size


def binnedEntropy(x, max_bins):
    """
    First bins the values of x into max_bins equidistant bins.
    Then calculates the value of

    .. math::

        - \\sum_{k=0}^{min(max\\_bins, len(x))} p_k log(p_k) \\cdot \\mathbf{1}_{(p_k > 0)}

    where :math:`p_k` is the percentage of samples in bin :math:`k`.

    :param x: the time series to calculate the feature of
    :type x: numpy.ndarray
    :param max_bins: the maximal number of bins
    :type max_bins: int
    :return: the value of this feature
    :return type: float
    """
    if not isinstance(x, (np.ndarray, pd.Series)):
        x = np.asarray(x)

    # nan makes no sense here
    if np.isnan(x).any():
        return np.nan

    hist, bin_edges = np.histogram(x, bins=max_bins)
    probs = hist / x.size
    probs[probs == 0] = 1.0
    return - np.sum(probs * np.log(probs))


def absEnergy(x):
    """
    Returns the absolute energy of the time series which is the sum over the squared values

    .. math::

        E = \\sum_{i=1,\\ldots, n} x_i^2

    :param x: the time series to calculate the feature of
    :type x: numpy.ndarray
    :return: the value of this feature
    :return type: float
    """
    if not isinstance(x, (np.ndarray, pd.Series)):
        x = np.asarray(x)
    return np.dot(x, x)


def linearTrendSlope(x):
    """
    Calculate a linear least-squares regression for the values of the time series versus the sequence from 0 to
    length of the time series minus one.
    This feature assumes the signal to be uniformly sampled. It will not use the time stamps to fit the model.
    The parameters control which of the characteristics are returned.

    :param x: the time series to calculate the feature of
    :return: slope of the model
    """
    slope, intercept, r_value, p_value, std_err = linregress(range(len(x)), x)

    return slope
