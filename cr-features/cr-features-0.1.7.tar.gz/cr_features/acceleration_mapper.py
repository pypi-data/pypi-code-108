from cr_features import feature_functions as f
from cr_features import feature_functions_fast as ff
from cr_features.helper_functions import checkForFeatures
import numpy as np
import pandas as pd

def calc_features_acc(ax, ay, az, time, axBand, ayBand, azBand, axLow, ayLow, azLow, featureNames=None):
    """ Calculate features for the accelerometer

    :param ax2d: 2D array including the X axis
    :param ay2d: 2D array including the Y axis
    :param az2d: 2D array including the Z axis
    :param time2d: 2D array of times, denoting when each measurement occurred
    :param afs: sampling frequency of the accelerometer
    :param prefix: prefix for column names in returned dataframe
    :return: features of the accelerometer
    """

    magnitude_list = ["quartilesMagnitudesBand", "interQuartileRangeMagnitudesBand", "areaUnderAccelerationMagnitude",
                      "averageVectorLength", "averageVectorLengthPower", "peaksDataLow"]

    magnitudes = magnitudesLow = magnitudesBand = None
    if checkForFeatures(magnitude_list, featureNames):
        if ay is not None:
            magnitudes = ff.magnitudeVector(ax, ay, az)
            magnitudesLow = ff.magnitudeVector(axLow, ayLow, azLow)
            magnitudesBand = ff.magnitudeVector(axBand, ayBand, azBand)
        else:
            magnitudes = ax
            magnitudesLow = axLow
            magnitudesBand = axBand

    features = pd.DataFrame()
    mean_list = ["meanLow", "postureDistanceLow"]
    if checkForFeatures(mean_list, featureNames):
        features["mean_XLow"] = np.mean(axLow, axis=1)
        if ay is not None:
            features["mean_YLow"] = np.mean(ayLow, axis=1)
            features["mean_ZLow"] = np.mean(azLow, axis=1)
            features["totalMeanLow"] = (features["mean_XLow"] +
                                        features["mean_YLow"] +
                                        features["mean_ZLow"]) * ax.shape[1] / 3

    if checkForFeatures(["areaLow"], featureNames):
        features["area_XLow"] = ff.calcArea(axLow)
        if ay is not None:
            features["area_YLow"] = ff.calcArea(ayLow)
            features["area_ZLow"] = ff.calcArea(azLow)

    if ay is not None:
        if f.checkForFeature("totalAbsoluteAreaBand", featureNames):
            features["totalAbsoluteAreaBand"] = ff.calcArea(ff.calcAcAbsoluteArea(axBand, ayBand, azBand))

        if f.checkForFeature("totalMagnitudeBand", featureNames):
            features["totalMagnitudeBand"] = ff.calcTotalMagnitude(axBand, ayBand, azBand)

        # Measures of body posture
        if f.checkForFeature("postureDistanceLow", featureNames):
            postureDistance = ff.calcPostureDistance(features["mean_XLow"],
                                                     features["mean_YLow"],
                                                     features["mean_ZLow"])

            features["postureDistance_XLow"] = postureDistance[:, 0]
            features["postureDistance_YLow"] = postureDistance[:, 1]
            features["postureDistance_ZLow"] = postureDistance[:, 2]

    if f.checkForFeature("entropyBand", featureNames):
        features["entropy_XBand"] = [f.calcEntropy(row) for row in axBand]
        if ay is not None:
            features["entropy_YBand"] = [f.calcEntropy(row) for row in ayBand]
            features["entropy_ZBand"] = [f.calcEntropy(row) for row in azBand]

    if f.checkForFeature("skewnessBand", featureNames):
        features["skewness_XBand"] = ff.calcSkewness(axBand)
        if ay is not None:
            features["skewness_YBand"] = ff.calcSkewness(ayBand)
            features["skewness_ZBand"] = ff.calcSkewness(azBand)

    if f.checkForFeature("kurtosisBand", featureNames):
        features["kurtosis_XBand"] = ff.calcKurtosis(axBand)
        if ay is not None:
            features["kurtosis_YBand"] = ff.calcKurtosis(ayBand)
            features["kurtosis_ZBand"] = ff.calcKurtosis(azBand)

    # Measures of motion shape
    if f.checkForFeature("absoluteMeanBand", featureNames):
        features["absoluteMean_XBand"] = np.mean(np.abs(axBand), axis=1)
        if ay is not None:
            features["absoluteMean_YBand"] = np.mean(np.abs(ayBand), axis=1)
            features["absoluteMean_ZBand"] = np.mean(np.abs(azBand), axis=1)

    if f.checkForFeature("absoluteAreaBand", featureNames):
        features["absoluteArea_XBand"] = ff.calcArea(np.abs(axBand))
        if ay is not None:
            features["absoluteArea_YBand"] = ff.calcArea(np.abs(ayBand))
            features["absoluteArea_ZBand"] = ff.calcArea(np.abs(azBand))
            acAbsoluteArea = ff.calcAcAbsoluteArea(axBand, ayBand, azBand)
            features["absoluteAreaAllBand"] = ff.calcArea(acAbsoluteArea)

    acQuartilesX = acQuartilesY = acQuartilesZ = None
    quartile_list = ["quartilesBand", "interQuartileRangeBand"]
    if checkForFeatures(quartile_list, featureNames):
        acQuartilesX = ff.calcQuartiles(axBand)
        if ay is not None:
            acQuartilesY = ff.calcQuartiles(ayBand)
            acQuartilesZ = ff.calcQuartiles(azBand)

    if f.checkForFeature("quartilesBand", featureNames):
        features["quartilesQ1_XBand"] = acQuartilesX[:, 0]
        features["quartilesQ2_XBand"] = acQuartilesX[:, 1]
        features["quartilesQ3_XBand"] = acQuartilesX[:, 2]
        if ay is not None:
            features["quartilesQ1_YBand"] = acQuartilesY[:, 0]
            features["quartilesQ2_YBand"] = acQuartilesY[:, 1]
            features["quartilesQ3_YBand"] = acQuartilesY[:, 2]

            features["quartilesQ1_ZBand"] = acQuartilesZ[:, 0]
            features["quartilesQ2_ZBand"] = acQuartilesZ[:, 1]
            features["quartilesQ3_ZBand"] = acQuartilesZ[:, 2]

    if f.checkForFeature("interQuartileRangeBand", featureNames):
        features["interQuartileRange_XBand"] = ff.calcInterQuartileRange(acQuartilesX)
        if ay is not None:
            features["interQuartileRange_YBand"] = ff.calcInterQuartileRange(acQuartilesY)
            features["interQuartileRange_ZBand"] = ff.calcInterQuartileRange(acQuartilesZ)

    # Measures of motion variation
    if f.checkForFeature("varianceBand", featureNames):
        features["variance_XBand"] = ff.calcVariance(axBand)
        if ay is not None:
            features["variance_YBand"] = ff.calcVariance(ayBand)
            features["variance_ZBand"] = ff.calcVariance(azBand)

    if f.checkForFeature("coefficientOfVariationBand", featureNames):
        features["coefficientOfVariation_XBand"] = ff.calcCoefficientOfVariation(axBand)
        if ay is not None:
            features["coefficientOfVariation_YBand"] = ff.calcCoefficientOfVariation(ayBand)
            features["coefficientOfVariation_ZBand"] = ff.calcCoefficientOfVariation(azBand)

    if f.checkForFeature("amplitudeBand", featureNames):
        features["amplitude_XBand"] = ff.calcAmplitude(axBand)
        if ay is not None:
            features["amplitude_YBand"] = ff.calcAmplitude(ayBand)
            features["amplitude_ZBand"] = ff.calcAmplitude(azBand)

    if f.checkForFeature("totalEnergyBand", featureNames):
        features["totalEnergy_XBand"] = [f.calcTotalEnergy(row) for row in axBand]
        if ay is not None:
            features["totalEnergy_YBand"] = [f.calcTotalEnergy(row) for row in ayBand]
            features["totalEnergy_ZBand"] = [f.calcTotalEnergy(row) for row in azBand]

    if f.checkForFeature("dominantFrequencyEnergyBand", featureNames):
        features["dominantFrequencyEnergy_XBand"] = [f.calcDominantFrequencyEnergy(row) for row in axBand]
        if ay is not None:
            features["dominantFrequencyEnergy_YBand"] = [f.calcDominantFrequencyEnergy(row) for row in ayBand]
            features["dominantFrequencyEnergy_ZBand"] = [f.calcDominantFrequencyEnergy(row) for row in azBand]

    if f.checkForFeature("meanCrossingRateBand", featureNames):
        features["meanCrossingRate_XBand"] = ff.numberOfMeanCrossings(axBand)
        if ay is not None:
            features["meanCrossingRate_YBand"] = ff.numberOfMeanCrossings(ayBand)
            features["meanCrossingRate_ZBand"] = ff.numberOfMeanCrossings(azBand)

    if ay is not None:
        if f.checkForFeature("correlationBand", featureNames):
            features["correlation_X_YBand"] = ff.calcCorrelation(axBand, ayBand)
            features["correlation_X_ZBand"] = ff.calcCorrelation(axBand, azBand)
            features["correlation_Y_ZBand"] = ff.calcCorrelation(ayBand, azBand)

    acQuartilesMagnitude = None
    quartile_magnitude_list = ["quartilesMagnitudesBand", "interQuartileRangeMagnitudesBand"]
    if checkForFeatures(quartile_magnitude_list, featureNames):
        acQuartilesMagnitude = ff.calcQuartiles(magnitudesBand)
        if f.checkForFeature("quartilesMagnitudesBand", featureNames):
            features["quartilesMagnitudes_XBand"] = acQuartilesMagnitude[:, 0]
            features["quartilesMagnitudes_YBand"] = acQuartilesMagnitude[:, 1]
            features["quartilesMagnitudes_ZBand"] = acQuartilesMagnitude[:, 2]

    if f.checkForFeature("interQuartileRangeMagnitudesBand", featureNames):
        features["interQuartileRangeMagnitudesBand"] = ff.calcInterQuartileRange(acQuartilesMagnitude)

    if f.checkForFeature("areaUnderAccelerationMagnitude", featureNames):
        features["areaUnderAccelerationMagnitude"] = ff.calcAreaUnderAccelerationMagnitude(magnitudes, time)

    if f.checkForFeature("peaksDataLow", featureNames):
        peak0, peak1, peak2, peak3 = get_peaks(magnitudesLow)
        features["peaksCountLow"] = peak0
        features["peaksSumLow"] = peak1
        features["peaksAmplitudeAvgLow"] = peak3
        features["peaksPeakAvgLow"] = peak2

    if f.checkForFeature("sumPerComponentBand", featureNames):
        features["sumPerComponent_XBand"] = ff.calcSumPerComponent(axBand, time)
        if ay is not None:
            features["sumPerComponent_YBand"] = ff.calcSumPerComponent(ayBand, time)
            features["sumPerComponent_ZBand"] = ff.calcSumPerComponent(azBand, time)

    if f.checkForFeature("velocityBand", featureNames):
        features["velocity_XBand"] = ff.computeACVelocity(axBand, time)
        if ay is not None:
            features["velocity_YBand"] = ff.computeACVelocity(ayBand, time)
            features["velocity_ZBand"] = ff.computeACVelocity(azBand, time)

    if f.checkForFeature("meanKineticEnergyBand", featureNames):
        features["meanKineticEnergy_XBand"] = ff.calcMeanKineticEnergy(axBand, time)
        if ay is not None:
            features["meanKineticEnergy_YBand"] = ff.calcMeanKineticEnergy(ayBand, time)
            features["meanKineticEnergy_ZBand"] = ff.calcMeanKineticEnergy(azBand, time)

    if ay is not None:
        if f.checkForFeature("totalKineticEnergyBand", featureNames):
            features["totalKineticEnergyBand"] = ff.calcTotalKineticEnergy(axBand, ayBand, azBand, time)

    features = features.copy()

    if f.checkForFeature("squareSumOfComponent", featureNames):
        ACsumPerX = ff.calcSumPerComponent(ax, time)
        acSumSquaredX = np.power(ACsumPerX, 2)
        features["squareSumOfComponent_X"] = acSumSquaredX
        if ay is not None:
            ACsumPerY = ff.calcSumPerComponent(ay, time)
            ACsumPerZ = ff.calcSumPerComponent(az, time)
            acSumSquaredY = np.power(ACsumPerY, 2)
            acSumSquaredZ = np.power(ACsumPerZ, 2)
            features["squareSumOfComponent_Y"] = acSumSquaredY
            features["squareSumOfComponent_Z"] = acSumSquaredZ

    if checkForFeatures(["averageVectorLength", "averageVectorLengthPower"], featureNames):
        features["averageVectorLength"] = np.mean(magnitudes, axis=1)

    if f.checkForFeature("averageVectorLengthPower", featureNames):
        features["averageVectorLengthPower"] = np.square(features["averageVectorLength"])

    roll = pitch = None
    roll_list = ["rollAvgLow", "rollStdDevLow", "rollMotionAmountLow", "rollMotionRegularityLow", "manipulationLow",
                 "rollPeaks", "rollPitchCorrelation"]
    pitch_list = ["pitchAvgLow", "pitchStdDevLow", "manipulationLow", "pitchPeaks", "rollPitchCorrelation"]

    if ay is not None:
        if checkForFeatures(roll_list, featureNames):
            roll = np.array([f.calcRoll(row_y, row_z) for row_y, row_z in zip(ayLow, azLow)])
        if checkForFeatures(pitch_list, featureNames):
            pitch = np.array([f.calcPitch(row_x, row_y, row_z) for row_x, row_y, row_z in zip(axLow, ayLow, azLow)])

        if f.checkForFeature("rollAvgLow", featureNames):
            features["rollAvgLow"] = (ff.max(roll) - ff.min(roll))

        if f.checkForFeature("pitchAvgLow", featureNames):
            features["pitchAvgLow"] = (ff.max(pitch) - ff.min(pitch))

        if f.checkForFeature("rollStdDevLow", featureNames):
            features["rollStdDevLow"] = ff.stdDev(roll)

        if f.checkForFeature("pitchStdDevLow", featureNames):
            features["pitchStdDevLow"] = ff.stdDev(pitch)

        if f.checkForFeature("rollMotionAmountLow", featureNames):
            features["rollMotionAmountLow"] = [f.rollMotionAmount(r) for r in roll]

        if f.checkForFeature("rollMotionRegularityLow", featureNames):
            features["rollMotionRegularityLow"] = [f.rollMotionRegularity(r) for r in roll]

        if f.checkForFeature("manipulationLow", featureNames):
            features["manipulationLow"] = [f.manipulation(row_x, row_y, row_z, r, p) for row_x, row_y, row_z, r, p
                                           in zip(axLow, ayLow, azLow, roll, pitch)]

        if f.checkForFeature("rollPeaks", featureNames):
            peak0, peak1, peak2, peak3 = get_peaks(roll)
            features["rollPeak0"] = peak0
            features["rollPeak1"] = peak1
            features["rollPeak2"] = peak2
            features["rollPeak3"] = peak3

        if f.checkForFeature("pitchPeaks", featureNames):
            peak0, peak1, peak2, peak3 = get_peaks(pitch)
            features["pitchPeak0"] = peak0
            features["pitchPeak1"] = peak1
            features["pitchPeak2"] = peak2
            features["pitchPeak3"] = peak3

        if f.checkForFeature("rollPitchCorrelation", featureNames):
            features["rollPitchCorrelation"] = ff.calcCorrelation(roll, pitch)
    features = features.copy()
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
