from cr_features import feature_functions as f
from cr_features import feature_functions_fast as ff
from cr_features.helper_functions import checkForFeatures
import numpy as np
import pandas as pd


def calc_features_common(x, y, z, time, featureNames=None):
    """ Calculate common features of accelerometer and gyroscope

    :param prefix: prefix of all feature names
    :param x: array including the X axis
    :param y: array including the Y axis
    :param z: array including the Z axis
    :return: pandas dataframe with the calculated features
    """
    features = pd.DataFrame()
    if f.checkForFeature("autocorrelations", featureNames):
        calcAutocorrelations(x, "_X", features)
        if y is not None:
            calcAutocorrelations(y, "_Y", features)
            calcAutocorrelations(z, "_Z", features)

    if f.checkForFeature("countAboveMean", featureNames):
        features["countAboveMean_X"] = ff.countAboveMean(x)
        if y is not None:
            features["countAboveMean_Y"] = ff.countAboveMean(y)
            features["countAboveMean_Z"] = ff.countAboveMean(z)

    if f.checkForFeature("countBelowMean", featureNames):
        features["countBelowMean_X"] = ff.countBelowMean(x)
        if y is not None:
            features["countBelowMean_Y"] = ff.countBelowMean(y)
            features["countBelowMean_Z"] = ff.countBelowMean(z)

    if f.checkForFeature("maximum", featureNames):
        features["maximum_X"] = ff.max(x)
        if y is not None:
            features["maximum_Y"] = ff.max(y)
            features["maximum_Z"] = ff.max(z)

    if f.checkForFeature("minimum", featureNames):
        features["minimum_X"] = ff.min(x)
        if y is not None:
            features["minimum_Y"] = ff.min(y)
            features["minimum_Z"] = ff.min(z)

    if f.checkForFeature("meanAbsChange", featureNames):
        features["meanAbsChange_X"] = ff.meanAbsChange(x)
        if y is not None:
            features["meanAbsChange_Y"] = ff.meanAbsChange(y)
            features["meanAbsChange_Z"] = ff.meanAbsChange(z)

    if f.checkForFeature("longestStrikeAboveMean", featureNames):
        features["longestStrikeAboveMean_X"] = [f._calcMaxLengthOfSequenceTrueOrOne(row > np.mean(row)) for row in x]
        if y is not None:
            features["longestStrikeAboveMean_Y"] = [f._calcMaxLengthOfSequenceTrueOrOne(row > np.mean(row)) for row in y]
            features["longestStrikeAboveMean_Z"] = [f._calcMaxLengthOfSequenceTrueOrOne(row > np.mean(row)) for row in z]

    if f.checkForFeature("longestStrikeBelowMean", featureNames):
        features["longestStrikeBelowMean_X"] = [f._calcMaxLengthOfSequenceTrueOrOne(row < np.mean(row)) for row in x]
        if y is not None:
            features["longestStrikeBelowMean_Y"] = [f._calcMaxLengthOfSequenceTrueOrOne(row < np.mean(row)) for row in y]
            features["longestStrikeBelowMean_Z"] = [f._calcMaxLengthOfSequenceTrueOrOne(row < np.mean(row)) for row in z]

    if f.checkForFeature("stdDev", featureNames):
        features["stdDev_X"] = ff.stdDev(x)
        if y is not None:
            features["stdDev_Y"] = ff.stdDev(y)
            features["stdDev_Z"] = ff.stdDev(z)

    if f.checkForFeature("median", featureNames):
        features["median_X"] = np.median(x, axis=1)
        if y is not None:
            features["median_Y"] = np.median(y, axis=1)
            features["median_Z"] = np.median(z, axis=1)

    if f.checkForFeature("meanChange", featureNames):
        features["meanChange_X"] = ff.meanChange(x)
        if y is not None:
            features["meanChange_Y"] = ff.meanChange(y)
            features["meanChange_Z"] = ff.meanChange(z)

    if f.checkForFeature("numberOfZeroCrossings", featureNames):
        features["numberOfZeroCrossings_X"] = ff.numberOfZeroCrossings(x)
        if y is not None:
            features["numberOfZeroCrossings_Y"] = ff.numberOfZeroCrossings(y)
            features["numberOfZeroCrossings_Z"] = ff.numberOfZeroCrossings(z)

    if f.checkForFeature("absEnergy", featureNames):
        features["absEnergy_X"] = ff.absEnergy(x)
        if y is not None:
            features["absEnergy_Y"] = ff.absEnergy(y)
            features["absEnergy_Z"] = ff.absEnergy(z)

    if f.checkForFeature("linearTrendSlope", featureNames):
        features["linearTrendSlope_X"] = [f.linearTrendSlope(row) for row in x]
        if y is not None:
            features["linearTrendSlope_Y"] = [f.linearTrendSlope(row) for row in y]
            features["linearTrendSlope_Z"] = [f.linearTrendSlope(row) for row in z]

    if f.checkForFeature("ratioBeyondRSigma", featureNames):
        r = 2.5
        features["ratioBeyondRSigma_X"] = ff.ratioBeyondRSigma(x, r)
        if y is not None:
            features["ratioBeyondRSigma_Y"] = ff.ratioBeyondRSigma(y, r)
            features["ratioBeyondRSigma_Z"] = ff.ratioBeyondRSigma(z, r)

    if f.checkForFeature("binnedEntropy", featureNames):
        max_bins = 10
        features["binnedEntropy_X"] = [f.binnedEntropy(row, max_bins) for row in x]
        if y is not None:
            features["binnedEntropy_Y"] = [f.binnedEntropy(row, max_bins) for row in y]
            features["binnedEntropy_Z"] = [f.binnedEntropy(row, max_bins) for row in z]

    autocorrelation_list = ["numOfPeaksAutocorr", "numberOfZeroCrossingsAutocorr", "areaAutocorr",
                            "calcMeanCrossingRateAutocorr", "countAboveMeanAutocorr"]

    autocorrelations_x = autocorrelations_y = autocorrelations_z = None
    if checkForFeatures(autocorrelation_list, featureNames):
        autocorrelations_x = ff.autocorrelations(x)
        if y is not None:
            autocorrelations_y = ff.autocorrelations(y)
            autocorrelations_z = ff.autocorrelations(z)

    if f.checkForFeature("numOfPeaksAutocorr", featureNames):
        features["numOfPeaksAutocorr_X"] = [f.calcPeakCount(row)[0] for row in autocorrelations_x]
        if y is not None:
            features["numOfPeaksAutocorr_Y"] = [f.calcPeakCount(row)[0] for row in autocorrelations_y]
            features["numOfPeaksAutocorr_Z"] = [f.calcPeakCount(row)[0] for row in autocorrelations_z]

    if f.checkForFeature("numberOfZeroCrossingsAutocorr", featureNames):
        features["numberOfZeroCrossingsAutocorr_X"] = ff.numberOfZeroCrossings(autocorrelations_x)
        if y is not None:
            features["numberOfZeroCrossingsAutocorr_Y"] = ff.numberOfZeroCrossings(autocorrelations_y)
            features["numberOfZeroCrossingsAutocorr_Z"] = ff.numberOfZeroCrossings(autocorrelations_z)

    if f.checkForFeature("areaAutocorr", featureNames):
        features["areaAutocorr_X"] = ff.calcArea(autocorrelations_x)
        if y is not None:
            features["areaAutocorr_Y"] = ff.calcArea(autocorrelations_y)
            features["areaAutocorr_Z"] = ff.calcArea(autocorrelations_y)

    if f.checkForFeature("calcMeanCrossingRateAutocorr", featureNames):
        features["calcMeanCrossingRateAutocorr_X"] = ff.numberOfMeanCrossings(autocorrelations_x)
        if y is not None:
            features["calcMeanCrossingRateAutocorr_Y"] = ff.numberOfMeanCrossings(autocorrelations_y)
            features["calcMeanCrossingRateAutocorr_Z"] = ff.numberOfMeanCrossings(autocorrelations_z)

    if f.checkForFeature("countAboveMeanAutocorr", featureNames):
        features["countAboveMeanAutocorr_X"] = ff.countAboveMean(autocorrelations_x)
        if y is not None:
            features["countAboveMeanAutocorr_Y"] = ff.countAboveMean(autocorrelations_y)
            features["countAboveMeanAutocorr_Z"] = ff.countAboveMean(autocorrelations_z)

    sum_per_component_list = ["sumPer", "sumSquared", "squareSumOfComponent", "sumOfSquareComponents"]
    sum_component_x = sum_component_y = sum_component_z = None
    squared_component_x = squared_component_y = squared_component_z = None
    if checkForFeatures(sum_per_component_list, featureNames):
        sum_component_x = ff.calcSumPerComponent(x, time)
        if y is not None:
            sum_component_y = ff.calcSumPerComponent(y, time)
            sum_component_z = ff.calcSumPerComponent(z, time)

        squared_component_x = np.square(sum_component_x)
        if y is not None:
            squared_component_y = np.square(sum_component_y)
            squared_component_z = np.square(sum_component_z)

    if f.checkForFeature("sumPer", featureNames):
        features["sumPer_X"] = sum_component_x
        if y is not None:
            features["sumPer_Y"] = sum_component_y
            features["sumPer_Z"] = sum_component_z

    if f.checkForFeature("sumSquared", featureNames):
        features["sumSquared_X"] = squared_component_x
        if y is not None:
            features["sumSquared_Y"] = squared_component_y
            features["sumSquared_Z"] = squared_component_z

    if y is not None:
        if f.checkForFeature("squareSumOfComponent", featureNames):
            features["squareSumOfComponent"] = np.square(sum_component_x + sum_component_y + sum_component_z)

        if f.checkForFeature("sumOfSquareComponents", featureNames):
            features["sumOfSquareComponents"] = sum_component_x + sum_component_y + sum_component_z

    return features


def calcAutocorrelations(signal, suffix, df):
    """ Calculate autocorrelations of the given signal with lags 5, 10, 20, 30, 50, 75 and 100

    :param signal: signal on which to calculate the autocorrelations
    :param suffix: suffix of the feature name
    :return: dict with calculated autocorrelations
    """
    for i in [5, 10, 20, 30, 50, 75, 100]:
        df["autocorrelation_" + str(i) + suffix] = ff.autocorrelation(signal, i)