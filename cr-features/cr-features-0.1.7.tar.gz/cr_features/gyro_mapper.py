from cr_features import feature_functions as f
from cr_features import feature_functions_fast as ff
from cr_features.helper_functions import checkForFeatures
import numpy as np
import pandas as pd

def calc_features_gyro(gx, gy, gz, time, gxLow, gyLow, gzLow, featureNames=None):
    """

    :param gx2d: 2D array including the X axis of the gyroscope
    :param gy2d: 2D array including the Y axis of the gyroscope
    :param gz2d: 2D array including the Z axis of the gyroscope
    :param gtime2d: 2D array of times, denoting when each measurement of the gyroscope occurred
    :param gFs: sampling frequency of the gyroscope
    :return: pandas dataframe including the calculated features
    """

    magnitude_list = ["peaksCountLow","averageVectorLengthLow", "averageVectorLengthPowerLow", "quartilesMagnitudeLow",
                      "interQuartileRangeMagnitudesLow", "areaUnderMagnitude"]
    magnitudesLow_gyro = None
    if checkForFeatures(magnitude_list, featureNames):
        if gy is not None:
            magnitudesLow_gyro = ff.magnitudeVector(gxLow, gyLow, gzLow)
        else:
            magnitudesLow_gyro = gxLow

    features = pd.DataFrame()

    #if f.checkForFeature("meanLow", featureNames):
    #    features["mean_XLow"] = ff.calcMean(gxLow)
    #    if gy is not None:
    #        features["mean_YLow"] = ff.calcMean(gyLow)
    #        features["mean_ZLow"] = ff.calcMean(gzLow)
    #        features["totalMeanLow"] = (features["mean_XLow"] + features["mean_YLow"] +
    #                                    features["mean_ZLow"]) * gx.shape[1] / 3

    #if f.checkForFeature("areaLow", featureNames):
    #    features["area_XLow"] = ff.calcArea(gxLow)
    #    if gy is not None:
    #        features["area_YLow"] = ff.calcArea(gyLow)
    #        features["area_ZLow"] = ff.calcArea(gzLow)

    if gy is not None:
        if f.checkForFeature("totalAbsoluteAreaLow", featureNames):
            features["totalAbsoluteAreaLow"] = ff.calcArea(ff.calcAcAbsoluteArea(gxLow, gyLow, gzLow))

        if f.checkForFeature("totalMagnitudeLow", featureNames):
            features["totalMagnitudeLow"] = ff.calcTotalMagnitude(gxLow, gyLow, gzLow)

    if f.checkForFeature("entropyLow", featureNames):
        features["entropy_XLow"] = [f.calcEntropy(row) for row in gxLow]
        if gy is not None:
            features["entropy_YLow"] = [f.calcEntropy(row) for row in gyLow]
            features["entropy_ZLow"] = [f.calcEntropy(row) for row in gzLow]

    if f.checkForFeature("skewnessLow", featureNames):
        features["skewness_XLow"] = ff.calcSkewness(gxLow)
        if gy is not None:
            features["skewness_YLow"] = ff.calcSkewness(gyLow)
            features["skewness_ZLow"] = ff.calcSkewness(gzLow)

    if f.checkForFeature("kurtosisLow", featureNames):
        features["kurtosis_XLow"] = ff.calcKurtosis(gxLow)
        if gy is not None:
            features["kurtosis_YLow"] = ff.calcKurtosis(gyLow)
            features["kurtosis_ZLow"] = ff.calcKurtosis(gzLow)

    quartile_list = ["quartilesLow", "interQuartileRangeLow"]
    gcQuartilesX = gcQuartilesY = gcQuartilesZ = None
    if checkForFeatures(quartile_list, featureNames):
        gcQuartilesX = ff.calcQuartiles(gxLow)
        if gy is not None:
            gcQuartilesY = ff.calcQuartiles(gyLow)
            gcQuartilesZ = ff.calcQuartiles(gzLow)

    if f.checkForFeature("quartilesLow", featureNames):
        features["quartiles_Q1_XLow"] = gcQuartilesX[:, 0]
        features["quartiles_Q2_XLow"] = gcQuartilesX[:, 1]
        features["quartiles_Q3_XLow"] = gcQuartilesX[:, 2]

        if gy is not None:
            features["quartiles_Q1_YLow"] = gcQuartilesY[:, 0]
            features["quartiles_Q2_YLow"] = gcQuartilesY[:, 1]
            features["quartiles_Q3_YLow"] = gcQuartilesY[:, 2]

            features["quartiles_Q1_ZLow"] = gcQuartilesZ[:, 0]
            features["quartiles_Q2_ZLow"] = gcQuartilesZ[:, 1]
            features["quartiles_Q3_ZLow"] = gcQuartilesZ[:, 2]

    if f.checkForFeature("interQuartileRangeLow", featureNames):
        features["interQuartileRange_XLow"] = ff.calcInterQuartileRange(gcQuartilesX)
        if gy is not None:
            features["interQuartileRange_YLow"] = ff.calcInterQuartileRange(gcQuartilesY)
            features["interQuartileRange_ZLow"] = ff.calcInterQuartileRange(gcQuartilesZ)

    # Measures of motion variation
    if ff.checkForFeature("varianceLow", featureNames):
        features["variance_XLow"] = ff.calcVariance(gxLow)
        if gy is not None:
            features["variance_YLow"] = ff.calcVariance(gyLow)
            features["variance_ZLow"] = ff.calcVariance(gzLow)

    if f.checkForFeature("coefficientOfVariationLow", featureNames):
        features["coefficientOfVariation_XLow"] = ff.calcCoefficientOfVariation(gxLow)
        if gy is not None:
            features["coefficientOfVariation_YLow"] = ff.calcCoefficientOfVariation(gyLow)
            features["coefficientOfVariation_ZLow"] = ff.calcCoefficientOfVariation(gzLow)

    if f.checkForFeature("amplitudeLow", featureNames):
        features["amplitude_XLow"] = ff.calcAmplitude(gxLow)
        if gy is not None:
            features["amplitude_YLow"] = ff.calcAmplitude(gyLow)
            features["amplitude_ZLow"] = ff.calcAmplitude(gzLow)

    if f.checkForFeature("totalEnergyLow", featureNames):
        features["totalEnergy_XLow"] = [f.calcTotalEnergy(row) for row in gxLow]
        if gy is not None:
            features["totalEnergy_YLow"] = [f.calcTotalEnergy(row) for row in gyLow]
            features["totalEnergy_ZLow"] = [f.calcTotalEnergy(row) for row in gzLow]

    if f.checkForFeature("dominantFrequencyEnergyLow", featureNames):
        features["dominantFrequencyEnergy_XLow"] = [f.calcDominantFrequencyEnergy(row) for row in gxLow]
        if gy is not None:
            features["dominantFrequencyEnergy_YLow"] = [f.calcDominantFrequencyEnergy(row) for row in gyLow]
            features["dominantFrequencyEnergy_ZLow"] = [f.calcDominantFrequencyEnergy(row) for row in gzLow]

    if f.checkForFeature("meanCrossingRateLow", featureNames):
        features["meanCrossingRate_XLow"] = ff.numberOfMeanCrossings(gxLow)
        if gy is not None:
            features["meanCrossingRate_YLow"] = ff.numberOfMeanCrossings(gyLow)
            features["meanCrossingRate_ZLow"] = ff.numberOfMeanCrossings(gzLow)

    if gy is not None:
        if f.checkForFeature("correlationLow", featureNames):
            features["correlation_X_YLow"] = ff.calcCorrelation(gxLow, gyLow)
            features["correlation_X_ZLow"] = ff.calcCorrelation(gxLow, gzLow)
            features["correlation_Y_ZLow"] = ff.calcCorrelation(gyLow, gzLow)

    gcQuartilesMagnitude = None
    quartile_magnitude_list = ["quartilesMagnitudeLow", "interQuartileRangeMagnitudesLow"]
    if checkForFeatures(quartile_magnitude_list, featureNames):
        gcQuartilesMagnitude = ff.calcQuartiles(magnitudesLow_gyro)

    if f.checkForFeature("quartilesMagnitudeLow", featureNames):
        features["quartilesMagnitudeLow_Q1"] = gcQuartilesMagnitude[:, 0]
        features["quartilesMagnitudeLow_Q2"] = gcQuartilesMagnitude[:, 1]
        features["quartilesMagnitudeLow_Q3"] = gcQuartilesMagnitude[:, 2]

    if f.checkForFeature("interQuartileRangeMagnitudesLow", featureNames):
        features["interQuartileRangeMagnitudesLow"] = ff.calcInterQuartileRange(gcQuartilesMagnitude)

    if gy is not None:
        if f.checkForFeature("areaUnderMagnitude", featureNames):
            features["areaUnderMagnitude"] = ff.calcAreaUnderAccelerationMagnitude(ff.magnitudeVector(gx, gy, gz), time)

    if ff.checkForFeature("peaksCountLow", featureNames):
        peaks0, peaks1, peaks2, peaks3 = get_peaks(magnitudesLow_gyro)
        features["peaksCountLow_Q1"] = peaks0
        features["peaksCountLow_Q2"] = peaks1
        features["peaksCountLow_Q3"] = peaks2
        features["peaksCountLow_Q4"] = peaks3

    if checkForFeatures(["averageVectorLengthLow", "averageVectorLengthPowerLow"], featureNames):
        features["averageVectorLengthLow"] = np.mean(magnitudesLow_gyro, axis=1)

    if f.checkForFeature("averageVectorLengthPowerLow", featureNames):
        features["averageVectorLengthPowerLow"] = np.square(features["averageVectorLengthLow"])

    return features


def get_peaks(data):
    peak0 = np.zeros(data.shape[0])
    peak1 = np.zeros(data.shape[0])
    peak2 = np.zeros(data.shape[0])
    peak3 = np.zeros(data.shape[0])
    for i, row in enumerate(data):
        peakCount = f.calcPeakCount(row)
        peak0[i] = peakCount[0]
        peak1[i] = peakCount[1]
        peak2[i] = peakCount[2]
        peak3[i] = peakCount[3]
    return peak0, peak1, peak2, peak3
