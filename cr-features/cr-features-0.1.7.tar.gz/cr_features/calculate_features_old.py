from tqdm import tqdm
from cr_features.helper_functions import *
import cr_features.gsr as gsr
import cr_features.hrv as hrv
from cr_features.calculate_acc_gyro_common_features import *

ALPHA_LOW = 0.3
ALPHA_BAND_LOW = 0.3
ALPHA_BAND_HIGH = 0.6

DEFAULT_DELTA_TIME = 0.02

MIN_INPUT_ARRAY_WIDTH = 256


def calculateFeatures(x2d, y2d=None, z2d=None, time2d=None, fs=None, prefix=None, featureNames=None):
    """ Calculate features for the given data
    Feature names are stored at the end of the "helper_functions.py" file in variables frequencyFeatureNames, genericFeatureNames,
    accelerometerFeatureNames, gyroscopeFeatureNames, edaFeatureNames and bvpFeatureNames. For information about features
    read the README.md file

    For calculation of features with 1D input shape (one axis), input only x2d parameter. Examples of inputs with 1D input shape
    are BVP and EDA signals.
    For calculation of features with 3D input shape (three axes), input also y2d and z2d parameter. Examples of inputs with 3D input
    shape are gyroscope and accelerometer signals.

    Each individual input axis has to be in a 2D shape. This means that input signals have to be split into rows.
    If BVP features are being calculated, width of window has to be at least 256. The conversion from 1D to 2D can be
    made with "convertInputInto2d()" function, located in the helper_functions.py file.

    If sampling frequency (fs) is not given, it will be calculated from time2d parameter.
    If array of times (time2d) is not given, it will be calculated from fs parameter.
    If none of them is given, fs will be calculated as 1/DEFAULT_DELTA_TIME

    :param x2d: 2D array including the X axis
    :param y2d: 2D array including the Y axis
    :param z2d: 2D array including the Z axis
    :param time2d: 2D array of times, denoting when each measurement occurred
    :param fs: sampling frequency
    :param prefix: prefix to append before each column name
    :param featureNames: list of features to calculate. If it is None, all features will be calculated
    :return: pandas DataFrame of the calculated features
    """

    if len(x2d[0]) < MIN_INPUT_ARRAY_WIDTH:
        raise Exception("Input 2D array width has to be at least " + str(MIN_INPUT_ARRAY_WIDTH))

    if type(x2d) is list:
        x2d = np.asarray(x2d)

    if type(y2d) is list:
        y2d = np.asarray(y2d)

    if type(z2d) is list:
        z2d = np.asarray(z2d)

    if type(time2d) is list:
        time2d = np.asarray(time2d)

    if (x2d is not None and y2d is not None and z2d is not None) or (x2d is not None and y2d is None and z2d is None):
        if y2d is not None and not (x2d.shape == y2d.shape and y2d.shape == z2d.shape):
            raise Exception("x2d, y2d, z2d shapes have to be the same!")
        # Verify fs and time array
        if time2d is not None and fs is not None and fs != 1 / (time2d[0, 1] - time2d[0, 0]):
            raise Exception("sampling frequency of the given time2D matrix and fs do not match!")
        if time2d is None:
            deltaTime = 1 / fs if fs is not None else DEFAULT_DELTA_TIME
            time2d = np.asarray(convert_to2d([i * deltaTime for i in range(x2d.size)], x2d.shape[1]))
        if fs is None:
            fs = 1 / (time2d[0][1] - time2d[0][0])

    else:
        raise Exception("Incorrect input! Either x2d, y2d and z2d are given, or only x2d is given!")

    fs = int(fs)

    if y2d is None:
        y2d = z2d = [None] * len(x2d)

    df = pd.DataFrame()
    for x, y, z, time in tqdm(zip(x2d, y2d, z2d, time2d), total=len(x2d)):
        xBand = f.bandPassFilter(x, ALPHA_BAND_LOW, ALPHA_BAND_HIGH)
        if y is not None:
            yBand = f.bandPassFilter(y, ALPHA_BAND_LOW, ALPHA_BAND_HIGH)
            zBand = f.bandPassFilter(z, ALPHA_BAND_LOW, ALPHA_BAND_HIGH)

        xLow = f.lowPassFilter(x, ALPHA_LOW)
        if y is not None:
            yLow = f.lowPassFilter(y, ALPHA_LOW)
            zLow = f.lowPassFilter(z, ALPHA_LOW)

        row = {}

        if y is not None:
            row.update(calculateFeaturesAcc(x, y, z, time, xBand, yBand, zBand, xLow, yLow, zLow, featureNames))
        else:
            row.update(calculateFeaturesAcc(x, y, z, time, xBand, None, None, xLow, None, None, featureNames))

        if y is not None:
            row.update(calculateFeaturesGyro(x, y, z, time, xLow, yLow, zLow, featureNames))
        else:
            row.update(calculateFeaturesGyro(x, y, z, time, xLow, None, None, featureNames))

        row.update(calcCommonFeatures(x, y, z, time, featureNames))

        # Add frequency features
        row.update({str(key) + "_X": val for key, val in f.computeFreqFeatures(x, featureNames, fs).items()})
        if y is not None:
            row.update({str(key) + "_Y": val for key, val in f.computeFreqFeatures(y, featureNames, fs).items()})
            row.update({str(key) + "_Z": val for key, val in f.computeFreqFeatures(z, featureNames, fs).items()})

        # EDA features
        row.update({str(key) + "_X": val for key, val in
                    gsr.extractGsrFeatures(x, sampleRate=fs, featureNames=featureNames).items()})
        if y is not None:
            row.update({str(key) + "_Y": val for key, val in
                        gsr.extractGsrFeatures(y, sampleRate=fs, featureNames=featureNames).items()})
            row.update({str(key) + "_Z": val for key, val in
                        gsr.extractGsrFeatures(z, sampleRate=fs, featureNames=featureNames).items()})

        # BVP features
        row.update({str(key) + "_X": val for key, val in
                    hrv.extractHrvFeatures(x, sampling=fs, featureNames=featureNames).items()})
        if y is not None:
            row.update({str(key) + "_Y": val for key, val in
                        hrv.extractHrvFeatures(y, sampling=fs, featureNames=featureNames).items()})
            row.update({str(key) + "_Z": val for key, val in
                        hrv.extractHrvFeatures(z, sampling=fs, featureNames=featureNames).items()})

        df = df.append(row, ignore_index=True)

    if prefix is not None:
        dfNewCols = []
        for col in df.columns:
            dfNewCols.append(prefix + "_" + col)
        df.columns = dfNewCols

    return df
