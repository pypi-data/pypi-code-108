import numpy as np
import pandas as pd


def convert_to2d(input, windowLength, overlap=0):
    """Convert input into 2d matrix with width = numCols. The last row is padded with zeros to match the other rows.

    Overlap has to be smaller than window length

    :param input: the one dimensional array
    :param windowLength: window length, expressed in number of samples
    :param overlap: Amount of overlap
    :return: 2D matrix
    """

    if windowLength <= overlap:
        raise Exception("Overlap has to be smaller than window length")

    inputWasList = True
    if type(input) != list:
        inputWasList = False
        input = input.tolist()

    out = [input[i: i + windowLength] for i in range(0, len(input), windowLength - overlap)]
    out[-1].extend([0] * (windowLength - len(out[-1])))
    return out if inputWasList else np.asarray(out)


def convert_to2d_time(data, timestamps, window_size=None, time_thresholds=None,
                      min_samples=10, max_samples=100, fill_value=0):
    """ Convert input array into 2D matrix by time interval. If window_size is specified, each window ends after
    this value. If time_thresholds are specified, i-th window ends after timestamps exceeds time_thresholds[i].
    Each row will be truncated to "max_samples" sensor readings, or filled with "fill_value" if shorter.

    :param data: an iterable containing data
    :param timestamps: an iterable containing timestamps that correspond to data
    :param window_size: length (in time uinits) of the window
    :param time_thresholds: custom specified ends of each window
    :param min_samples: a window with less than min_samples values will be discarded
    :param max_samples: every row in the returned matrix will contain max_row samples
    :param fill_value: if less then max_samples are in each row, the rest is filled with fill_value
    :return: 2D matrix of values, time thresholds
    """

    if bool(window_size) == bool(time_thresholds):
        raise ValueError("Exactly one of window_size and time_threshold must be specified")

    outData = [[]]
    outTime = [[]]
    start_time = timestamps[0]
    index = 1
    for d, t in zip(data, timestamps):

        while inCurrentWindow(t, start_time, window_size, index, time_thresholds):
            index += 1
            outData.append([])
            outTime.append([])
        outData[-1].append(d)
        outTime[-1].append(t)

    data_windows = []
    data_time = []
    for p, t in zip(outData, outTime):
        if (min_samples is not None) and (len(p) < min_samples):
            continue
        p = p[:max_samples]
        p += [fill_value] * (max_samples - len(p))
        data_windows.append(p)
        timestamp = 0
        if len(t) > 0:
            timestamp = t[-1]
        elif len(data_time) > 0:
            timestamp = data_time[-1]
        data_time.append(timestamp)

    raw = np.array(data_windows)
    return raw, data_time


def inCurrentWindow(t, start_time, window_size, index, time_thesholds):
    condition = False
    if window_size:
        condition = t - start_time >= window_size * index
    if time_thesholds:
        condition = (index < len(time_thesholds)) and (t > time_thesholds[index])
    return condition


def empatica1d_to_array(pathToEmpaticaCsvFile):
    """ Convert 1D empatica file to array

    :param pathToEmpaticaCsvFile: path to Empatica csv file
    :return: array of data, starting timestamp of data, sample rate of data
    """
    df = pd.read_csv(pathToEmpaticaCsvFile, names=["name"])
    startTimeStamp = df.name[0]
    sampleRate = df.name[1]
    df.drop([0, 1], inplace=True)
    data = df.name.ravel()
    return data, startTimeStamp, sampleRate


def empatica3d_to_array(pathToEmpaticaCsvFile):
    """ Convert 3D empatica file to array

    :param pathToEmpaticaCsvFile: path to Empatica csv file
    :return: array of data, starting timestamp of data, sample rate of data
    """
    df = pd.read_csv(pathToEmpaticaCsvFile, names=["x", "y", "z"])
    startTimeStamp = df.x[0]
    sampleRate = df.x[1]
    df.drop([0, 1], inplace=True)
    data = np.vstack((df.x.ravel(), df.y.ravel(), df.z.ravel()))
    return data, startTimeStamp, sampleRate


def checkForFeature(featureName, featureNames):
    return featureNames is None or featureName in featureNames


def checkForFeatures(featureList, featureNames):
    return featureNames is None or len(set(featureList) & set(featureNames))


def resample(df, f_from, f_to):
    n_from = len(df.columns)
    n_to = n_from * (f_to / f_from)
    ratio = n_from / n_to
    #print(n_from, f_to, f_from, n_to, ratio)#
    indices = [df.columns[int(x)] for x in np.arange(0,n_from-1, ratio)]
    return df[indices].copy()

frequency_features = ["fqHighestPeakFreqs", "fqHighestPeaks", "fqEnergyFeat", "fqEntropyFeat", "fqHistogramBins",
                         "fqAbsMean", "fqSkewness", "fqKurtosis", "fqInterquart"]

generic_features = ["autocorrelations", "countAboveMean", "countBelowMean", "maximum", "minimum", "meanAbsChange",
                       "longestStrikeAboveMean", "longestStrikeBelowMean", "stdDev", "median", "meanChange",
                       "numberOfZeroCrossings", "absEnergy", "linearTrendSlope", "ratioBeyondRSigma", "binnedEntropy",
                       "numOfPeaksAutocorr", "numberOfZeroCrossingsAutocorr", "areaAutocorr",
                       "calcMeanCrossingRateAutocorr", "countAboveMeanAutocorr", "sumPer", "sumSquared",
                       "squareSumOfComponent", "sumOfSquareComponents"]

accelerometer_features = ["meanLow", "areaLow", "totalAbsoluteAreaBand", "totalMagnitudeBand", "entropyBand",
                             "skewnessBand", "kurtosisBand", "postureDistanceLow", "absoluteMeanBand",
                             "absoluteAreaBand", "quartilesBand", "interQuartileRangeBand",
                             "varianceBand", "coefficientOfVariationBand", "amplitudeBand", "totalEnergyBand",
                             "dominantFrequencyEnergyBand", "meanCrossingRateBand", "correlationBand",
                             "quartilesMagnitudesBand",
                             "interQuartileRangeMagnitudesBand", "areaUnderAccelerationMagnitude", "peaksDataLow",
                             "sumPerComponentBand", "velocityBand", "meanKineticEnergyBand",
                             "totalKineticEnergyBand", "squareSumOfComponent", "sumOfSquareComponents",
                             "averageVectorLength", "averageVectorLengthPower", "rollAvgLow", "pitchAvgLow",
                             "rollStdDevLow", "pitchStdDevLow",
                             "rollMotionAmountLow", "rollMotionRegularityLow", "manipulationLow", "rollPeaks",
                             "pitchPeaks",
                             "rollPitchCorrelation"]

gyroscope_features = ["meanLow", "areaLow", "totalAbsoluteAreaLow", "totalMagnitudeLow", "entropyLow", "skewnessLow",
                         "kurtosisLow",
                         "quartilesLow", "interQuartileRangeLow", "varianceLow", "coefficientOfVariationLow",
                         "amplitudeLow",
                         "totalEnergyLow", "dominantFrequencyEnergyLow", "meanCrossingRateLow", "correlationLow",
                         "quartilesMagnitudeLow", "interQuartileRangeMagnitudesLow", "areaUnderMagnitude",
                         "peaksCountLow",
                         "averageVectorLengthLow", "averageVectorLengthPowerLow"]

gsr_features = ['mean', 'std', 'q25', 'q75', 'qd', 'deriv', 'power', 'numPeaks', 'ratePeaks', 'powerPeaks',
                   'sumPosDeriv', 'propPosDeriv', 'derivTonic', 'sigTonicDifference', 'freqFeats',
                   'maxPeakAmplitudeChangeBefore', 'maxPeakAmplitudeChangeAfter',
                   'avgPeakAmplitudeChangeBefore', 'avgPeakAmplitudeChangeAfter', 'avgPeakChangeRatio',
                   'maxPeakIncreaseTime', 'maxPeakDecreaseTime', 'maxPeakDuration', 'maxPeakChangeRatio',
                   'avgPeakIncreaseTime', 'avgPeakDecreaseTime', 'avgPeakDuration', 'maxPeakResponseSlopeBefore',
                   'maxPeakResponseSlopeAfter', 'signalOverallChange', 'changeDuration', 'changeRate',
                   'significantIncrease', 'significantDecrease']

hrv_features = ['meanHr', 'ibi', 'sdnn', 'sdsd', 'rmssd', 'pnn20', 'pnn50', 'sd', 'sd2', 'sd1/sd2', 'numRR']

slow_features = ["numberOfZeroCrossingsAutocorr", "areaAutocorr", "calcMeanCrossingRateAutocorr", "countAboveMeanAutocorr",
        "numOfPeaksAutocorr"]

medium_slow_features = ["entropyBand", "dominantFrequencyEnergyBand", "totalEnergyBand", "peaksDataLow", "rollAvgLow",
          "rollStdDevLow", "rollMotionAmountLow", "rollMotionRegularityLow", "manipulationLow", "rollPeaks",
          "rollPitchCorrelation", "pitchAvgLow", "pitchStdDevLow", "pitchPeaks", "autocorrelations",
          "longestStrikeAboveMean", "longestStrikeBelowMean", "peaksCountLow", "dominantFrequencyEnergyLow",
          "totalEnergyLow", "entropyLow"]