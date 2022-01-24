from tqdm import tqdm

from cr_features.common_mapper import calc_features_common
from cr_features.acceleration_mapper import calc_features_acc
from cr_features.gyro_mapper import calc_features_gyro
from cr_features.helper_functions import *
import cr_features.gsr as gsr
import cr_features.hrv as hrv
from cr_features.calculate_acc_gyro_common_features import *
import time

ALPHA_LOW = 0.3
ALPHA_BAND_LOW = 0.3
ALPHA_BAND_HIGH = 0.6

DEFAULT_DELTA_TIME = 0.02

MIN_INPUT_ARRAY_WIDTH = 4


def calculate_features(x2d, y2d=None, z2d=None, time2d=None, fs=None, prefix=None, feature_names=None, show_progress=True):
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
    :param feature_names: list of features to calculate. If it is None, all features will be calculated
    :return: pandas DataFrame of the calculated features
    """

    starting_index = None
    if type(x2d) is pd.DataFrame:
        starting_index = x2d.index

    if type(x2d) is list or type(x2d) is pd.DataFrame:
        x2d = np.asarray(x2d)

    if type(y2d) is list or type(x2d) is pd.DataFrame:
        y2d = np.asarray(y2d)

    if type(z2d) is list or type(x2d) is pd.DataFrame:
        z2d = np.asarray(z2d)

    if type(time2d) is list or type(x2d) is pd.DataFrame:
        time2d = np.asarray(time2d)

    if len(x2d[0]) < MIN_INPUT_ARRAY_WIDTH:
        raise Exception("Input 2D array width has to be at least " + str(MIN_INPUT_ARRAY_WIDTH))

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

    #if y2d is None:
    #    y2d = z2d = [None] * len(x2d)

    x2d = np.array(x2d)
    if y2d is not None:
        y2d = np.array(y2d)
        z2d = np.array(z2d)
    time2d = np.array(time2d)

    point1 = time.time()

    features_acc = []
    features_gyro = []
    features_common = []
    slice_num = 10
    slice_size = x2d.shape[0] / slice_num
    progress = range(slice_num)
    motion_features = features_gyro + features_acc + features_common
    if show_progress and len(set(motion_features) & set(feature_names))>0:
        progress = tqdm(range(slice_num), total=slice_num)
    for i in progress:
        #print("Processing part: "+str(i))

        x_slice = x2d[int(i * slice_size):int((i + 1) * slice_size), :]
        y_slice = z_slice = None
        if y2d is not  None:
            y_slice = y2d[int(i * slice_size):int((i + 1) * slice_size), :]
            z_slice = z2d[int(i * slice_size):int((i + 1) * slice_size), :]
        t_slice = time2d[int(i * slice_size):int((i + 1) * slice_size), :]
        point_a = time.time()
        x_band, y_band, z_band, x_low, y_low, z_low = filter_data(x_slice, y_slice, z_slice)
        #x_band, y_band, z_band = x2d, y2d, z2d
        #x_low, y_low, z_low = x2d, y2d, z2d
        point_b = time.time()
        features_acc.append(calc_features_acc(x_slice, y_slice, z_slice, t_slice,
                                              x_band, y_band, z_band, x_low, y_low, z_low, feature_names))
        point_c = time.time()
        features_gyro.append(calc_features_gyro(x_slice, y_slice, z_slice, t_slice, x_low, y_low, z_low, feature_names))
        point_d = time.time()
        features_common.append(calc_features_common(x_slice, y_slice, z_slice, t_slice, feature_names))
        point_e = time.time()
        #print(point_b-point_a, point_c-point_b, point_d-point_c, point_e-point_d)
    features_acc = pd.concat(features_acc)
    features_gyro = pd.concat(features_gyro)
    features_common = pd.concat(features_common)
    #features_all = pd.concat(features_acc, features_gyro, features_common)
    point3 = time.time()
    #print(point2 - point1)
    #print(point3 - point1)

    feature_rest_list = frequency_features + hrv_features + gsr_features
    features_rest = pd.DataFrame()
    if set(feature_rest_list) & set(feature_names):
        features_rest = calculate_rest(x2d, y2d, z2d, time2d, fs, feature_names, show_progress)

    features_all = pd.concat([features_acc, features_gyro, features_common, features_rest], axis=1)

    if prefix is not None:
        dfNewCols = []
        for col in features_all.columns:
            dfNewCols.append(prefix + "_" + col)
        features_all.columns = dfNewCols

    if starting_index is not None:
        features_all.index = starting_index

    return features_all


def filter_data(x, y, z):
    x_band = np.array([f.bandPassFilter(row, ALPHA_BAND_LOW, ALPHA_BAND_HIGH) for row in x])
    x_low = np.array([f.lowPassFilter(row, ALPHA_LOW) for row in x])
    y_band = z_band = y_low = z_low = None
    if y is not None:
        y_band = np.array([f.bandPassFilter(row, ALPHA_BAND_LOW, ALPHA_BAND_HIGH) for row in y])
        z_band = np.array([f.bandPassFilter(row, ALPHA_BAND_LOW, ALPHA_BAND_HIGH) for row in z])
        y_low = np.array([f.lowPassFilter(row, ALPHA_LOW) for row in y])
        z_low = np.array([f.lowPassFilter(row, ALPHA_LOW) for row in z])
    return x_band, y_band, z_band, x_low, y_low, z_low


def calculate_rest(x2d, y2d, z2d, time2d, fs, feature_names, show_progress):
    features_rest = pd.DataFrame()
    if y2d is None:
        y2d = [None]*len(x2d)
    if z2d is None:
        z2d = [None]*len(x2d)

    progress = zip(x2d, y2d, z2d, time2d)
    if show_progress:
        progress = tqdm(zip(x2d, y2d, z2d, time2d), total=len(x2d))

    for x, y, z, time in progress:
        row = {}
        # Add frequency features
        if len(set(feature_names) & set(frequency_features)) > 0:
            row.update({str(key) + "_X": val for key, val in f.computeFreqFeatures(x, fs, feature_names).items()})
            if y is not None:
                row.update({str(key) + "_Y": val for key, val in f.computeFreqFeatures(y, fs, feature_names).items()})
                row.update({str(key) + "_Z": val for key, val in f.computeFreqFeatures(z, fs, feature_names).items()})

        # EDA features
        if len(set(feature_names) & set(gsr_features)) > 0:
            row.update({str(key) + "_X": val for key, val in
                    gsr.extractGsrFeatures(x, sampleRate=fs, featureNames=feature_names).items()})
            if y is not None:
                row.update({str(key) + "_Y": val for key, val in
                            gsr.extractGsrFeatures(y, sampleRate=fs, featureNames=feature_names).items()})
                row.update({str(key) + "_Z": val for key, val in
                            gsr.extractGsrFeatures(z, sampleRate=fs, featureNames=feature_names).items()})

        # BVP features
        if len(set(feature_names) & set(hrv_features)) > 0:
            row.update({str(key) + "_X": val for key, val in
                        hrv.extractHrvFeatures(x, sampling=fs, featureNames=feature_names).items()})
            if y is not None:
                row.update({str(key) + "_Y": val for key, val in
                            hrv.extractHrvFeatures(y, sampling=fs, featureNames=feature_names).items()})
                row.update({str(key) + "_Z": val for key, val in
                            hrv.extractHrvFeatures(z, sampling=fs, featureNames=feature_names).items()})

        features_rest = features_rest.append(row, ignore_index=True)
    return features_rest
