from enum import Enum


class FeatureGeneratorType(Enum):
    """
    Contains a variety of techniques used to generate new features from a dataset's columns.
    """

    AUTO_LAG = "autolag"
    """ Creates optimal lag transforms based on the auto-correlation of a feature. """

    EWMA = "ewma"
    """ Exponentially weighted moving average. """

    LAG = "lag"
    """
    Produces a delayed copy of the same feature, where the delay is based on the series
    `total` length.
    """

    LOGARITHM = "logarithm"
    """ Applies the natural logarithm function to all values in a feature. """

    ROLLING_AVERAGE = "rolling_average"
    """ Applies a rolling average transform on a feature. """

    CALENDAR = "calendar"
    """ Extracts a new feature based on the calendar components of the time index. """

    PERCENT_CHANGE = "perc_change"
    """ Produces a percent change of a feature along specific lags. """

    NUMBER_OF_PEAKS = "num_peaks"
    """ Counts the number of peaks in recent data. """

    ONE_HOT_ENCODING = "one_hot_encode"
    """ Used to convert non-numeric data into numeric data. """


class StationarizationStrategy(Enum):
    """ Describe how to treat results of the stationarization stage. """

    KEEP_FAILED = "keep_fail"
    """ Keep original columns even if they cannot be stationarized. """

    DISCARD_FAILED = "discard_fail"
    """ Drop columns that cannot be stationarized. """

    NONE = "none"
    """ Do nothing, return original columns. """


class TargetTransformType(Enum):
    """ Indicates whether target columns should be transformed. """

    DO_NOTHING = "DoNothing"
    """ Columns are kept as they originally appear in the data. """

    HORIZON_LAG_DIFF = "HorizonLagDiff"
    """ Applies a difference function across a lag equal to the current horizon. """

    HORIZON_LAG_DIFF_RATIO = "HorizonLagDiffRatio"
    """ Similar to the above, but taken as a ratio between values. """


class CorrelationMethod(Enum):
    """ Describes which metric is used to compute correlation between features. """

    MUTUAL_INFORMATION = "mutual_info"
    SPEARMAN = "spearman"
    PEARSON = "pearson"
    KENDALL = "kendall"


class RegressorType(Enum):
    """
    Indicates which regression algorithm is used to produce a regression model.
    """

    RANDOM_FOREST = "RandomForest"
    MARTINGALE = "Martingale"
    VBLINREG = "VBLinReg"
    MONDRIAN_FOREST = "MondrianForest"
    XGBOOST = "XGBoost"
