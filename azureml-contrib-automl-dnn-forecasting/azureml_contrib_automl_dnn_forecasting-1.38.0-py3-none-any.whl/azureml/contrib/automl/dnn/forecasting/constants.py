# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing Forecast Constants."""

import importlib
importlib.import_module('azureml.automl.core')
importlib.import_module('azureml.automl.runtime')
# Above import sets the path needed to import the below module automl.client.
import azureml.automl.core.shared.constants as constants   # noqa E402


class ForecastConstant:
    """Constants for Forecast DNN training."""

    Deep4Cast = 'Deep4Cast'
    ForecastTCN = 'TCNForecaster'
    model = 'model'
    output_dir = 'output_dir'
    primary_metric = 'primary_metric'
    default_primary_metric = 'normalized_root_mean_squared_error'
    report_interval = 'report_interval'
    dataset_json = 'dataset_json'
    dataset_json_file = 'dataset_json_file'
    num_epochs = 'num_epochs'
    Learning_rate = 'learning_rate'
    Horizon = 'max_horizon'
    Lookback = 'lookback'
    LabelColumnName = 'label_column_name'
    Batch_size = 'batch_size'
    Optim = 'optim'
    Loss = 'loss'
    Device = 'device'
    n_layers = 'n_layers'
    year_iso_col = 'year_iso'
    year_col = 'year'
    automl_year = '_automl_year'
    automl_year_iso = '_automl_year_iso'
    namespace = 'azureml.contrib.automl.dnn.forecasting'
    automl_settings = 'automl_settings'
    config_json = 'config_json'
    config_json_default = 'settings.json'
    apply_timeseries_transform = 'apply_timeseries_transform'
    time_column_name = constants.TimeSeries.TIME_COLUMN_NAME
    max_horizon_default = constants.TimeSeriesInternal.MAX_HORIZON_DEFAULT
    auto = constants.TimeSeries.AUTO
    grain_column_names = constants.TimeSeries.GRAIN_COLUMN_NAMES
    drop_column_names = constants.TimeSeries.DROP_COLUMN_NAMES
    country_region = constants.TimeSeries.COUNTRY_OR_REGION
    dummy_grain_column = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
    cross_validations = constants.TimeSeriesInternal.CROSS_VALIDATIONS
    time_series_internal = constants.TimeSeriesInternal
    time_series = constants.TimeSeries
    automl_constants = constants
    dataset_definition_key = 'datasets.json'

    FORECAST_VALID_SETTINGS = [apply_timeseries_transform,
                               drop_column_names,
                               country_region,
                               dummy_grain_column,
                               grain_column_names,
                               time_column_name,
                               LabelColumnName,
                               cross_validations,
                               Horizon,
                               time_series.FREQUENCY,
                               time_series.SEASONALITY,
                               time_series.HOLIDAY_COUNTRY,
                               time_series.SHORT_SERIES_HANDLING,
                               time_series.SHORT_SERIES_HANDLING_CONFIG,
                               time_series.USE_STL,
                               time_series.TARGET_AGG_FUN
                               ]
    SMALL_DATASET_MAX_ROWS = 10000
    CURRENT_EPOCH = 'current_epoch'
    MEDIAN_PREDICTION_INDEX = 2  # index of the median prediction, forecast tcn is predicting multiple percentiles.
    NRMSE = 'normalized_root_mean_squared_error'
    NRMAE = 'normalized_mean_absolute_error'
    DEFAULT_EARLY_TERM_METRIC = NRMSE  # default metric for early termination.
    QUANTILES = [0.1, 0.25, 0.5, 0.75, 0.9]  # Quantiles used in optimizing the model while training.
    PREFIX_FOR_GRAIN_FEATURIZARTION = 'grain_'
    # Whether to consume output (featurized data and featurizers) from the distributed featurization stage
    CONSUME_DIST_FEATURIZATION_OUTPUT = 'consume_distributed_featurization_output'
    EXCLUDE_AUTOML_SETTINGS = [constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT,
                               constants.TimeSeriesInternal.WINDOW_SIZE,
                               constants.TimeSeries.TARGET_ROLLING_WINDOW_SIZE,
                               constants.TimeSeries.TARGET_LAGS]


# TODO: remove FeatureType class once we have new automl sdk and this code is in prod,
# we need to update automl-core dependency in requirements.txt once we move to use latest code.
class FeatureType:
    """Names for feature types that are recognized."""

    Numeric = 'Numeric'
    DateTime = 'DateTime'
    Categorical = 'Categorical'
    CategoricalHash = 'CategoricalHash'
    Text = 'Text'
    Hashes = 'Hashes'
    Ignore = 'Ignore'
    AllNan = 'AllNan'


class TCNForecastParameters:
    """Model parameters constants for TCN Model."""

    NUM_CELLS = 'num_cells'  # Number of cells for backbone
    MULTILEVEL = 'multilevel'  # MultilevelType for backbones
    DEPTH = 'depth'  # Cell depth
    NUM_CHANNELS = 'num_channels'  # Number of channels
    DROPOUT_RATE = 'dropout_rate'  # Dropout rate
    DILATION = 'dilation'  # Dilation for tcn.
    DILATION_DEFAULT = 2  # Default dialation.
    # Parameter in DNN Params for number of epochs to wait before evaluationg early stoping.
    EARLY_STOPPING_DELAY_STEPS = 'EARLY_STOPPING_DELAY_STEPS'
    # Parameter in DNN Params for relative improvements to continue training.
    EARLY_STOPPING_MIN_IMPROVEMENTS = 'EARLY_STOPPING_MIN_IMPROVEMENTS'
    # Lr decay factor
    LR_DECAY_FACTOR = 'LR_DECAY_FACTOR'
    EARLY_STOPPING_DELAY_STEPS_DEFAULT = 20  # Number of epohs to wait to evaluate early stopping.
    EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT = 0.001  # Miminum improvements from the pervious step
    LR_DECAY_FACTOR_DEFAULT = 0.5  # Default LR Decay Factor if not specified by user.
    MAX_EMBEDDING_DIM = 100  # Maximum embedding size
    MIN_EMBEDDING_DIM = 3  # Minimum embedding size
    EMBEDDING_THRESHOLD = 2  # categories that have values above threshold would be embedded.
    MIN_GRAIN_SIZE_FOR_EMBEDDING = "MIN_GRAIN_SIZE_FOR_EMBEDDING"
    MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT = 10  # Minimum number of grains needed enable embedding.
    EMBEDDING_TARGET_CALC_TYPE = "EMBEDDING_TARGET_CALC_TYPE"  # Parameter name in the python script.
    MULT = "MULT"  # embedding target size calculations based on multiplication
    ROOT = "ROOT"  # embedding target size calculations based on root
    NONE = "NONE"  # NO embedding
    EMBEDDING_TARGET_CALC_TYPE_DEFAULT = NONE  # Default to no embedding.
    EMBEDDING_MULT_FACTOR = "EMBEDDING_MULT_FACTOR"
    EMBEDDING_MULT_FACTOR_DEFAULT = 0.05  # embedding size target size = EMBEDDING_MULT_FACTOR * grain count.
    EMBEDDING_ROOT = "EMBEDDING_ROOT"
    EMBEDDING_ROOT_DEFAULT = 4  # embedding size target size = EMBEDDING_ROOT th root of (grain count).


DROP_COLUMN_LIST = {constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN, ForecastConstant.year_col,
                    ForecastConstant.year_iso_col, ForecastConstant.automl_year, ForecastConstant.automl_year_iso}
