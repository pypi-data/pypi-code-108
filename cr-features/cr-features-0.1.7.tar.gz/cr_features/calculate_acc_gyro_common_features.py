from cr_features import feature_functions as f
import numpy as np


def calculateFeaturesAcc(ax, ay, az, time, axBand, ayBand, azBand, axLow, ayLow, azLow, featureNames=None):
    """ Calculate features for the accelerometer

    :param ax2d: 2D array including the X axis
    :param ay2d: 2D array including the Y axis
    :param az2d: 2D array including the Z axis
    :param time2d: 2D array of times, denoting when each measurement occurred
    :param afs: sampling frequency of the accelerometer
    :param prefix: prefix for column names in returned dataframe
    :return: features of the accelerometer
    """
    if ay is not None:
        magnitudes = f.magnitudeVector(ax, ay, az)
        magnitudesLow = f.magnitudeVector(axLow, ayLow, azLow)
        magnitudesBand = f.magnitudeVector(axBand, ayBand, azBand)
    else:
        magnitudes = ax
        magnitudesLow = axLow
        magnitudesBand = axBand

    ACsumPerXBand = f.calcSumPerComponent(axBand, time)
    if ay is not None:
        ACsumPerYBand = f.calcSumPerComponent(ayBand, time)
        ACsumPerZBand = f.calcSumPerComponent(azBand, time)

    meanKineticEnergyX = f.calcMeanKineticEnergy(axBand, time)
    if ay is not None:
        meanKineticEnergyY = f.calcMeanKineticEnergy(ayBand, time)
        meanKineticEnergyZ = f.calcMeanKineticEnergy(azBand, time)
        totalKineticEnergy = f.calcTotalKineticEnergy(axBand, ayBand, azBand, time)

        roll = f.calcRoll(ayLow, azLow)
        pitch = f.calcPitch(axLow, ayLow, azLow)

        acAbsoluteArea = f.calcAcAbsoluteArea(axBand, ayBand, azBand)

    row = {}
    if f.checkForFeature("meanLow", featureNames):
        row["mean_XLow"] = f.calcMean(axLow)
        if ay is not None:
            row["mean_YLow"] = f.calcMean(ayLow)
            row["mean_ZLow"] = f.calcMean(azLow)
            row["totalMeanLow"] = (row["mean_XLow"] + row["mean_YLow"] + row["mean_ZLow"]) * len(ax) / 3

    if f.checkForFeature("areaLow", featureNames):
        row["area_XLow"] = f.calcArea(axLow)
        if ay is not None:
            row["area_YLow"] = f.calcArea(ayLow)
            row["area_ZLow"] = f.calcArea(azLow)

    if ay is not None:
        if f.checkForFeature("totalAbsoluteAreaBand", featureNames):
            row["totalAbsoluteAreaBand"] = f.calcTotalAbsoluteArea(f.calcAcAbsoluteArea(axBand, ayBand, azBand))

        if f.checkForFeature("totalMagnitudeBand", featureNames):
            row["totalMagnitudeBand"] = f.calcTotalMagnitude(axBand, ayBand, azBand)

        # Measures of body posture
        if f.checkForFeature("postureDistanceLow", featureNames):
            postureDistance = f.calcPostureDistance(row["mean_XLow"], row["mean_YLow"],
                                                    row["mean_ZLow"]) if "mean_XLow" in row \
                else f.calcPostureDistance(f.calcMean(axLow), f.calcMean(ayLow), f.calcMean(azLow))
            row["postureDistance_XLow"] = postureDistance[0]
            row["postureDistance_YLow"] = postureDistance[1]
            row["postureDistance_ZLow"] = postureDistance[2]

    if f.checkForFeature("entropyBand", featureNames):
        row["entropy_XBand"] = f.calcEntropy(axBand)
        if ay is not None:
            row["entropy_YBand"] = f.calcEntropy(ayBand)
            row["entropy_ZBand"] = f.calcEntropy(azBand)

    if f.checkForFeature("skewnessBand", featureNames):
        row["skewness_XBand"] = f.calcSkewness(axBand)
        if ay is not None:
            row["skewness_YBand"] = f.calcSkewness(ayBand)
            row["skewness_ZBand"] = f.calcSkewness(azBand)

    if f.checkForFeature("kurtosisBand", featureNames):
        row["kurtosis_XBand"] = f.calcKurtosis(axBand)
        if ay is not None:
            row["kurtosis_YBand"] = f.calcKurtosis(ayBand)
            row["kurtosis_ZBand"] = f.calcKurtosis(azBand)

    # Measures of motion shape
    if f.checkForFeature("absoluteMeanBand", featureNames):
        row["absoluteMean_XBand"] = f.calcMean(axBand)
        if ay is not None:
            row["absoluteMean_YBand"] = f.calcMean(ayBand)
            row["absoluteMean_ZBand"] = f.calcMean(azBand)

    if f.checkForFeature("absoluteAreaBand", featureNames):
        row["absoluteArea_XBand"] = f.calcArea(axBand)
        if ay is not None:
            row["absoluteArea_YBand"] = f.calcArea(ayBand)
            row["absoluteArea_ZBand"] = f.calcArea(azBand)
            row["absoluteAreaAllBand"] = f.calcTotalAbsoluteArea(acAbsoluteArea)

    acQuartilesX = f.calcQuartiles(axBand)
    if ay is not None:
        acQuartilesY = f.calcQuartiles(ayBand)
        acQuartilesZ = f.calcQuartiles(azBand)

    if f.checkForFeature("quartilesBand", featureNames):
        row["quartilesQ1_XBand"] = acQuartilesX[0]
        row["quartilesQ2_XBand"] = acQuartilesX[1]
        row["quartilesQ3_XBand"] = acQuartilesX[2]
        if ay is not None:
            row["quartilesQ1_YBand"] = acQuartilesY[0]
            row["quartilesQ2_YBand"] = acQuartilesY[1]
            row["quartilesQ3_YBand"] = acQuartilesY[2]

            row["quartilesQ1_ZBand"] = acQuartilesZ[0]
            row["quartilesQ2_ZBand"] = acQuartilesZ[1]
            row["quartilesQ3_ZBand"] = acQuartilesZ[2]

    if f.checkForFeature("interQuartileRangeBand", featureNames):
        row["interQuartileRange_XBand"] = f.calcInterQuartileRange(acQuartilesX)
        if ay is not None:
            row["interQuartileRange_YBand"] = f.calcInterQuartileRange(acQuartilesY)
            row["interQuartileRange_ZBand"] = f.calcInterQuartileRange(acQuartilesZ)

    # Measures of motion variation
    if f.checkForFeature("varianceBand", featureNames):
        row["variance_XBand"] = f.calcVariance(axBand)
        if ay is not None:
            row["variance_YBand"] = f.calcVariance(ayBand)
            row["variance_ZBand"] = f.calcVariance(azBand)

    if f.checkForFeature("coefficientOfVariationBand", featureNames):
        row["coefficientOfVariation_XBand"] = f.calcCoefficientOfVariation(axBand)
        if ay is not None:
            row["coefficientOfVariation_YBand"] = f.calcCoefficientOfVariation(ayBand)
            row["coefficientOfVariation_ZBand"] = f.calcCoefficientOfVariation(azBand)

    if f.checkForFeature("amplitudeBand", featureNames):
        row["amplitude_XBand"] = f.calcAmplitude(axBand)
        if ay is not None:
            row["amplitude_YBand"] = f.calcAmplitude(ayBand)
            row["amplitude_ZBand"] = f.calcAmplitude(azBand)

    if f.checkForFeature("totalEnergyBand", featureNames):
        row["totalEnergy_XBand"] = f.calcTotalEnergy(axBand)
        if ay is not None:
            row["totalEnergy_YBand"] = f.calcTotalEnergy(ayBand)
            row["totalEnergy_ZBand"] = f.calcTotalEnergy(azBand)

    if f.checkForFeature("dominantFrequencyEnergyBand", featureNames):
        row["dominantFrequencyEnergy_XBand"] = f.calcDominantFrequencyEnergy(axBand)
        if ay is not None:
            row["dominantFrequencyEnergy_YBand"] = f.calcDominantFrequencyEnergy(ayBand)
            row["dominantFrequencyEnergy_ZBand"] = f.calcDominantFrequencyEnergy(azBand)

    if f.checkForFeature("meanCrossingRateBand", featureNames):
        row["meanCrossingRate_XBand"] = f.calcMeanCrossingRate(axBand)
        if ay is not None:
            row["meanCrossingRate_YBand"] = f.calcMeanCrossingRate(ayBand)
            row["meanCrossingRate_ZBand"] = f.calcMeanCrossingRate(azBand)

    if ay is not None:
        if f.checkForFeature("correlationBand", featureNames):
            row["correlation_X_YBand"] = f.calcCorrelation(axBand, ayBand)
            row["correlation_X_ZBand"] = f.calcCorrelation(axBand, azBand)
            row["correlation_Y_ZBand"] = f.calcCorrelation(ayBand, azBand)

    acQuartilesMagnitude = f.calcQuartiles(magnitudesBand)
    if f.checkForFeature("quartilesMagnitudesBand", featureNames):
        row["quartilesMagnitudes_XBand"] = acQuartilesMagnitude[0]
        row["quartilesMagnitudes_YBand"] = acQuartilesMagnitude[1]
        row["quartilesMagnitudes_ZBand"] = acQuartilesMagnitude[2]

    if f.checkForFeature("interQuartileRangeMagnitudesBand", featureNames):
        row["interQuartileRangeMagnitudesBand"] = f.calcInterQuartileRange(acQuartilesMagnitude)

    if f.checkForFeature("areaUnderAccelerationMagnitude", featureNames):
        row["areaUnderAccelerationMagnitude"] = f.calcAreaUnderAccelerationMagnitude(magnitudes, time)

    if f.checkForFeature("peaksDataLow", featureNames):
        peakCount = f.calcPeakCount(magnitudesLow)
        row["peaksCountLow"] = peakCount[0]
        row["peaksSumLow"] = peakCount[1]
        row["peaksAmplitudeAvgLow"] = peakCount[3]
        row["peaksPeakAvgLow"] = peakCount[2]

    if f.checkForFeature("sumPerComponentBand", featureNames):
        row["sumPerComponent_XBand"] = ACsumPerXBand
        if ay is not None:
            row["sumPerComponent_YBand"] = ACsumPerYBand
            row["sumPerComponent_ZBand"] = ACsumPerZBand

    if f.checkForFeature("velocityBand", featureNames):
        row["velocity_XBand"] = f.computeACVelocity(axBand, time)
        if ay is not None:
            row["velocity_YBand"] = f.computeACVelocity(ayBand, time)
            row["velocity_ZBand"] = f.computeACVelocity(azBand, time)

    if f.checkForFeature("meanKineticEnergyBand", featureNames):
        row["meanKineticEnergy_XBand"] = meanKineticEnergyX
        if ay is not None:
            row["meanKineticEnergy_YBand"] = meanKineticEnergyY
            row["meanKineticEnergy_ZBand"] = meanKineticEnergyZ

    if ay is not None:
        if f.checkForFeature("totalKineticEnergyBand", featureNames):
            row["totalKineticEnergyBand"] = totalKineticEnergy

    ACsumPerX = f.calcSumPerComponent(ax, time)
    acSumSquaredX = pow(ACsumPerX, 2)
    if ay is not None:
        ACsumPerY = f.calcSumPerComponent(ay, time)
        ACsumPerZ = f.calcSumPerComponent(az, time)
        acSumSquaredY = pow(ACsumPerY, 2)
        acSumSquaredZ = pow(ACsumPerZ, 2)

    if f.checkForFeature("squareSumOfComponent", featureNames):
        row["squareSumOfComponent_X"] = acSumSquaredX
        if ay is not None:
            row["squareSumOfComponent_Y"] = acSumSquaredY
            row["squareSumOfComponent_Z"] = acSumSquaredZ

    if f.checkForFeature("averageVectorLength", featureNames):
        row["averageVectorLength"] = f.calcAverageVectorLength(magnitudes)

    if f.checkForFeature("averageVectorLengthPower", featureNames):
        row["averageVectorLengthPower"] = f.calcAverageVectorLengthPower(magnitudes)

    if ay is not None:
        if f.checkForFeature("rollAvgLow", featureNames):
            row["rollAvgLow"] = (f.max(roll) - f.min(roll))

        if f.checkForFeature("pitchAvgLow", featureNames):
            row["pitchAvgLow"] = (f.max(pitch) - f.min(pitch))

        if f.checkForFeature("rollStdDevLow", featureNames):
            row["rollStdDevLow"] = f.stdDev(roll)

        if f.checkForFeature("pitchStdDevLow", featureNames):
            row["pitchStdDevLow"] = f.stdDev(pitch)

        if f.checkForFeature("rollMotionAmountLow", featureNames):
            row["rollMotionAmountLow"] = f.rollMotionAmount(roll)

        if f.checkForFeature("rollMotionRegularityLow", featureNames):
            row["rollMotionRegularityLow"] = f.rollMotionRegularity(roll)

        if f.checkForFeature("manipulationLow", featureNames):
            row["manipulationLow"] = f.manipulation(axLow, ayLow, azLow, roll, pitch)

        if f.checkForFeature("rollPeaks", featureNames):
            roll_peaks = f.calcPeakCount(roll)
            row["rollPeak0"] = roll_peaks[0]
            row["rollPeak1"] = roll_peaks[1]
            row["rollPeak2"] = roll_peaks[2]
            row["rollPeak3"] = roll_peaks[3]

        if f.checkForFeature("pitchPeaks", featureNames):
            pitch_peaks = f.calcPeakCount(pitch)
            row["pitchPeak0"] = pitch_peaks[0]
            row["pitchPeak1"] = pitch_peaks[1]
            row["pitchPeak2"] = pitch_peaks[2]
            row["pitchPeak3"] = pitch_peaks[3]

        if f.checkForFeature("rollPitchCorrelation", featureNames):
            row["rollPitchCorrelation"] = f.calcCorrelation(roll, pitch)
    return row


def calcCommonFeatures(x, y, z, time, featureNames=None):
    """ Calculate common features of accelerometer and gyroscope

    :param prefix: prefix of all feature names
    :param x: array including the X axis
    :param y: array including the Y axis
    :param z: array including the Z axis
    :return: pandas dataframe with the calculated features
    """
    row = {}
    if f.checkForFeature("autocorrelations", featureNames):
        row.update(calcAutocorrelations(x, "_X"))
        if y is not None:
            row.update(calcAutocorrelations(y, "_Y"))
            row.update(calcAutocorrelations(z, "_Z"))

    if f.checkForFeature("countAboveMean", featureNames):
        row["countAboveMean_X"] = f.countAboveMean(x)
        if y is not None:
            row["countAboveMean_Y"] = f.countAboveMean(y)
            row["countAboveMean_Z"] = f.countAboveMean(z)

    if f.checkForFeature("countBelowMean", featureNames):
        row["countBelowMean_X"] = f.countBelowMean(x)
        if y is not None:
            row["countBelowMean_Y"] = f.countBelowMean(y)
            row["countBelowMean_Z"] = f.countBelowMean(z)

    if f.checkForFeature("maximum", featureNames):
        row["maximum_X"] = f.max(x)
        if y is not None:
            row["maximum_Y"] = f.max(y)
            row["maximum_Z"] = f.max(z)

    if f.checkForFeature("minimum", featureNames):
        row["minimum_X"] = f.min(x)
        if y is not None:
            row["minimum_Y"] = f.min(y)
            row["minimum_Z"] = f.min(z)

    if f.checkForFeature("meanAbsChange", featureNames):
        row["meanAbsChange_X"] = f.meanAbsChange(x)
        if y is not None:
            row["meanAbsChange_Y"] = f.meanAbsChange(y)
            row["meanAbsChange_Z"] = f.meanAbsChange(z)

    if f.checkForFeature("longestStrikeAboveMean", featureNames):
        row["longestStrikeAboveMean_X"] = f._calcMaxLengthOfSequenceTrueOrOne(x > np.mean(x))
        if y is not None:
            row["longestStrikeAboveMean_Y"] = f._calcMaxLengthOfSequenceTrueOrOne(y > np.mean(y))
            row["longestStrikeAboveMean_Z"] = f._calcMaxLengthOfSequenceTrueOrOne(z > np.mean(z))

    if f.checkForFeature("longestStrikeBelowMean", featureNames):
        row["longestStrikeBelowMean_X"] = f._calcMaxLengthOfSequenceTrueOrOne(x < np.mean(x))
        if y is not None:
            row["longestStrikeBelowMean_Y"] = f._calcMaxLengthOfSequenceTrueOrOne(y < np.mean(y))
            row["longestStrikeBelowMean_Z"] = f._calcMaxLengthOfSequenceTrueOrOne(z < np.mean(z))

    if f.checkForFeature("stdDev", featureNames):
        row["stdDev_X"] = f.stdDev(x)
        if y is not None:
            row["stdDev_Y"] = f.stdDev(y)
            row["stdDev_Z"] = f.stdDev(z)

    if f.checkForFeature("median", featureNames):
        row["median_X"] = np.median(x)
        if y is not None:
            row["median_Y"] = np.median(y)
            row["median_Z"] = np.median(z)

    if f.checkForFeature("meanChange", featureNames):
        row["meanChange_X"] = f.meanChange(x)
        if y is not None:
            row["meanChange_Y"] = f.meanChange(y)
            row["meanChange_Z"] = f.meanChange(z)

    if f.checkForFeature("numberOfZeroCrossings", featureNames):
        row["numberOfZeroCrossings_X"] = f.numberOfZeroCrossings(x)
        if y is not None:
            row["numberOfZeroCrossings_Y"] = f.numberOfZeroCrossings(y)
            row["numberOfZeroCrossings_Z"] = f.numberOfZeroCrossings(z)

    if f.checkForFeature("absEnergy", featureNames):
        row["absEnergy_X"] = f.absEnergy(x)
        if y is not None:
            row["absEnergy_Y"] = f.absEnergy(y)
            row["absEnergy_Z"] = f.absEnergy(z)

    if f.checkForFeature("linearTrendSlope", featureNames):
        row["linearTrendSlope_X"] = f.linearTrendSlope(x)
        if y is not None:
            row["linearTrendSlope_Y"] = f.linearTrendSlope(y)
            row["linearTrendSlope_Z"] = f.linearTrendSlope(z)

    if f.checkForFeature("ratioBeyondRSigma", featureNames):
        r = 2.5
        row["ratioBeyondRSigma_X"] = f.ratioBeyondRSigma(x, r)
        if y is not None:
            row["ratioBeyondRSigma_Y"] = f.ratioBeyondRSigma(y, r)
            row["ratioBeyondRSigma_Z"] = f.ratioBeyondRSigma(z, r)

    if f.checkForFeature("binnedEntropy", featureNames):
        max_bins = 10
        row["binnedEntropy_X"] = f.binnedEntropy(x, max_bins)
        if y is not None:
            row["binnedEntropy_Y"] = f.binnedEntropy(y, max_bins)
            row["binnedEntropy_Z"] = f.binnedEntropy(z, max_bins)

    autocorrelationsX = f.autocorrelations(x)
    if y is not None:
        autocorrelationsY = f.autocorrelations(y)
        autocorrelationsZ = f.autocorrelations(z)

    if f.checkForFeature("numOfPeaksAutocorr", featureNames):
        row["numOfPeaksAutocorr_X"] = f.calcPeakCount(autocorrelationsX)[0]
        if y is not None:
            row["numOfPeaksAutocorr_Y"] = f.calcPeakCount(autocorrelationsY)[0]
            row["numOfPeaksAutocorr_Z"] = f.calcPeakCount(autocorrelationsZ)[0]

    if f.checkForFeature("numberOfZeroCrossingsAutocorr", featureNames):
        row["numberOfZeroCrossingsAutocorr_X"] = f.numberOfZeroCrossings(autocorrelationsX)
        if y is not None:
            row["numberOfZeroCrossingsAutocorr_Y"] = f.numberOfZeroCrossings(autocorrelationsY)
            row["numberOfZeroCrossingsAutocorr_Z"] = f.numberOfZeroCrossings(autocorrelationsZ)

    if f.checkForFeature("areaAutocorr", featureNames):
        row["areaAutocorr_X"] = f.calcArea(autocorrelationsX)
        if y is not None:
            row["areaAutocorr_Y"] = f.calcArea(autocorrelationsY)
            row["areaAutocorr_Z"] = f.calcArea(autocorrelationsZ)

    if f.checkForFeature("calcMeanCrossingRateAutocorr", featureNames):
        row["calcMeanCrossingRateAutocorr_X"] = f.calcMeanCrossingRate(autocorrelationsX)
        if y is not None:
            row["calcMeanCrossingRateAutocorr_Y"] = f.calcMeanCrossingRate(autocorrelationsY)
            row["calcMeanCrossingRateAutocorr_Z"] = f.calcMeanCrossingRate(autocorrelationsZ)

    if f.checkForFeature("countAboveMeanAutocorr", featureNames):
        row["countAboveMeanAutocorr_X"] = f.countAboveMean(autocorrelationsX)
        if y is not None:
            row["countAboveMeanAutocorr_Y"] = f.countAboveMean(autocorrelationsY)
            row["countAboveMeanAutocorr_Z"] = f.countAboveMean(autocorrelationsZ)

    GCsumPerX_gyro = f.calcSumPerComponent(x, time)
    if y is not None:
        GCsumPerY_gyro = f.calcSumPerComponent(y, time)
        GCsumPerZ_gyro = f.calcSumPerComponent(z, time)

    if f.checkForFeature("sumPer", featureNames):
        row["sumPer_X"] = GCsumPerX_gyro
        if y is not None:
            row["sumPer_Y"] = GCsumPerY_gyro
            row["sumPer_Z"] = GCsumPerZ_gyro

    GCsumSquaredX = pow(GCsumPerX_gyro, 2)
    if y is not None:
        GCsumSquaredY = pow(GCsumPerY_gyro, 2)
        GCsumSquaredZ = pow(GCsumPerZ_gyro, 2)

    if f.checkForFeature("sumSquared", featureNames):
        row["sumSquared_X"] = GCsumSquaredX
        if y is not None:
            row["sumSquared_Y"] = GCsumSquaredY
            row["sumSquared_Z"] = GCsumSquaredZ

    if y is not None:
        if f.checkForFeature("squareSumOfComponent", featureNames):
            row["squareSumOfComponent"] = pow((GCsumSquaredX + GCsumSquaredY + GCsumSquaredZ), 2)

        if f.checkForFeature("sumOfSquareComponents", featureNames):
            row["sumOfSquareComponents"] = pow(GCsumSquaredX, 2) + pow(GCsumSquaredY, 2) + pow(GCsumSquaredZ, 2)

    return row


def calcAutocorrelations(signal, suffix):
    """ Calculate autocorrelations of the given signal with lags 5, 10, 20, 30, 50, 75 and 100

    :param signal: signal on which to calculate the autocorrelations
    :param suffix: suffix of the feature name
    :return: dict with calculated autocorrelations
    """
    row = {}
    for i in [5, 10, 20, 30, 50, 75, 100]:
        row["autocorrelation_" + str(i) + suffix] = f.autocorrelation(signal, i)
    return row


def calculateFeaturesGyro(gx, gy, gz, time, gxLow, gyLow, gzLow, featureNames=None):
    """

    :param gx2d: 2D array including the X axis of the gyroscope
    :param gy2d: 2D array including the Y axis of the gyroscope
    :param gz2d: 2D array including the Z axis of the gyroscope
    :param gtime2d: 2D array of times, denoting when each measurement of the gyroscope occurred
    :param gFs: sampling frequency of the gyroscope
    :return: pandas dataframe including the calculated features
    """
    if gy is not None:
        magnitudesLow_gyro = f.magnitudeVector(gxLow, gyLow, gzLow)
    else:
        magnitudesLow_gyro = gxLow

    row = {}

    if f.checkForFeature("meanLow", featureNames):
        row["mean_XLow"] = f.calcMean(gxLow)
        if gy is not None:
            row["mean_YLow"] = f.calcMean(gyLow)
            row["mean_ZLow"] = f.calcMean(gzLow)
            row["totalMeanLow"] = (row["mean_XLow"] + row["mean_YLow"] + row["mean_ZLow"]) * len(gx) / 3

    if f.checkForFeature("areaLow", featureNames):
        row["area_XLow"] = f.calcArea(gxLow)
        if gy is not None:
            row["area_YLow"] = f.calcArea(gyLow)
            row["area_ZLow"] = f.calcArea(gzLow)

    if gy is not None:
        if f.checkForFeature("totalAbsoluteAreaLow", featureNames):
            row["totalAbsoluteAreaLow"] = f.calcTotalAbsoluteArea(f.calcAcAbsoluteArea(gxLow, gyLow, gzLow))

        if f.checkForFeature("totalMagnitudeLow", featureNames):
            row["totalMagnitudeLow"] = f.calcTotalMagnitude(gxLow, gyLow, gzLow)

    if f.checkForFeature("entropyLow", featureNames):
        row["entropy_XLow"] = f.calcEntropy(gxLow)
        if gy is not None:
            row["entropy_YLow"] = f.calcEntropy(gyLow)
            row["entropy_ZLow"] = f.calcEntropy(gzLow)

    if f.checkForFeature("skewnessLow", featureNames):
        row["skewness_XLow"] = f.calcSkewness(gxLow)
        if gy is not None:
            row["skewness_YLow"] = f.calcSkewness(gyLow)
            row["skewness_ZLow"] = f.calcSkewness(gzLow)

    if f.checkForFeature("kurtosisLow", featureNames):
        row["kurtosis_XLow"] = f.calcKurtosis(gxLow)
        if gy is not None:
            row["kurtosis_YLow"] = f.calcKurtosis(gyLow)
            row["kurtosis_ZLow"] = f.calcKurtosis(gzLow)

    gcQuartilesX = f.calcQuartiles(gxLow)
    if gy is not None:
        gcQuartilesY = f.calcQuartiles(gyLow)
        gcQuartilesZ = f.calcQuartiles(gzLow)

    if f.checkForFeature("quartilesLow", featureNames):
        row["quartiles_Q1_XLow"] = gcQuartilesX[0]
        row["quartiles_Q2_XLow"] = gcQuartilesX[1]
        row["quartiles_Q3_XLow"] = gcQuartilesX[2]

        if gy is not None:
            row["quartiles_Q1_YLow"] = gcQuartilesY[0]
            row["quartiles_Q2_YLow"] = gcQuartilesY[1]
            row["quartiles_Q3_YLow"] = gcQuartilesY[2]

            row["quartiles_Q1_ZLow"] = gcQuartilesZ[0]
            row["quartiles_Q2_ZLow"] = gcQuartilesZ[1]
            row["quartiles_Q3_ZLow"] = gcQuartilesZ[2]

    if f.checkForFeature("interQuartileRangeLow", featureNames):
        row["interQuartileRange_XLow"] = f.calcInterQuartileRange(gcQuartilesX)
        if gy is not None:
            row["interQuartileRange_YLow"] = f.calcInterQuartileRange(gcQuartilesY)
            row["interQuartileRange_ZLow"] = f.calcInterQuartileRange(gcQuartilesZ)

    # Measures of motion variation
    if f.checkForFeature("varianceLow", featureNames):
        row["variance_XLow"] = f.calcVariance(gxLow)
        if gy is not None:
            row["variance_YLow"] = f.calcVariance(gyLow)
            row["variance_ZLow"] = f.calcVariance(gzLow)

    if f.checkForFeature("coefficientOfVariationLow", featureNames):
        row["coefficientOfVariation_XLow"] = f.calcCoefficientOfVariation(gxLow)
        if gy is not None:
            row["coefficientOfVariation_YLow"] = f.calcCoefficientOfVariation(gyLow)
            row["coefficientOfVariation_ZLow"] = f.calcCoefficientOfVariation(gzLow)

    if f.checkForFeature("amplitudeLow", featureNames):
        row["amplitude_XLow"] = f.calcAmplitude(gxLow)
        if gy is not None:
            row["amplitude_YLow"] = f.calcAmplitude(gyLow)
            row["amplitude_ZLow"] = f.calcAmplitude(gzLow)

    if f.checkForFeature("totalEnergyLow", featureNames):
        row["totalEnergy_XLow"] = f.calcTotalEnergy(gxLow)
        if gy is not None:
            row["totalEnergy_YLow"] = f.calcTotalEnergy(gyLow)
            row["totalEnergy_ZLow"] = f.calcTotalEnergy(gzLow)

    if f.checkForFeature("dominantFrequencyEnergyLow", featureNames):
        row["dominantFrequencyEnergy_XLow"] = f.calcDominantFrequencyEnergy(gxLow)
        if gy is not None:
            row["dominantFrequencyEnergy_YLow"] = f.calcDominantFrequencyEnergy(gyLow)
            row["dominantFrequencyEnergy_ZLow"] = f.calcDominantFrequencyEnergy(gzLow)

    if f.checkForFeature("meanCrossingRateLow", featureNames):
        row["meanCrossingRate_XLow"] = f.calcMeanCrossingRate(gxLow)
        if gy is not None:
            row["meanCrossingRate_YLow"] = f.calcMeanCrossingRate(gyLow)
            row["meanCrossingRate_ZLow"] = f.calcMeanCrossingRate(gzLow)

    if gy is not None:
        if f.checkForFeature("correlationLow", featureNames):
            row["correlation_X_YLow"] = f.calcCorrelation(gxLow, gyLow)
            row["correlation_X_ZLow"] = f.calcCorrelation(gxLow, gzLow)
            row["correlation_Y_ZLow"] = f.calcCorrelation(gyLow, gzLow)

    gcQuartilesMagnitude = f.calcQuartiles(magnitudesLow_gyro)

    if f.checkForFeature("quartilesMagnitudeLow", featureNames):
        row["quartilesMagnitudeLow_Q1"] = gcQuartilesMagnitude[0]
        row["quartilesMagnitudeLow_Q2"] = gcQuartilesMagnitude[1]
        row["quartilesMagnitudeLow_Q3"] = gcQuartilesMagnitude[2]

    if f.checkForFeature("interQuartileRangeMagnitudesLow", featureNames):
        row["interQuartileRangeMagnitudesLow"] = f.calcInterQuartileRange(gcQuartilesMagnitude)

    if gy is not None:
        if f.checkForFeature("areaUnderMagnitude", featureNames):
            row["areaUnderMagnitude"] = f.calcAreaUnderAccelerationMagnitude(f.magnitudeVector(gx, gy, gz), time)

    if f.checkForFeature("peaksCountLow", featureNames):
        peaksCount_gyro = f.calcPeaks(magnitudesLow_gyro)
        row["peaksCountLow_Q1"] = peaksCount_gyro[0]
        row["peaksCountLow_Q2"] = peaksCount_gyro[1]
        row["peaksCountLow_Q3"] = peaksCount_gyro[0]
        row["peaksCountLow_Q4"] = peaksCount_gyro[1]

    if f.checkForFeature("averageVectorLengthLow", featureNames):
        row["averageVectorLengthLow"] = f.calcAverageVectorLength(magnitudesLow_gyro)

    if f.checkForFeature("averageVectorLengthPowerLow", featureNames):
        row["averageVectorLengthPowerLow"] = f.calcAverageVectorLengthPower(magnitudesLow_gyro)

    return row
