# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module performing static featurization for timeseries."""
from typing import cast, Any, Dict, List, Optional, Set, Tuple, Type, Union
from collections import OrderedDict
import copy
from enum import Enum
import inspect
import logging
import math
import warnings

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from statsmodels.tsa import stattools

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty

from azureml.automl.core.constants import (
    FeatureType,
    SupportedTransformers,
    SupportedTransformersInternal,
    TransformerParams
)
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities, utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    FeaturizationConfigColumnMissing,
    GrainContainsEmptyValues,
    InvalidArgumentWithSupportedValues,
    TimeseriesDfInvalidValAllGrainsContainSingleVal,
    TimeseriesDfMissingColumn
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import (
    TimeSeries,
    TimeSeriesInternal,
    ShortSeriesHandlingValues
)
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ClientException,
    ConfigException,
    DataException
)
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime import frequency_fixer
from azureml.automl.runtime.featurizer.transformer.timeseries.category_binarizer import CategoryBinarizer
from azureml.automl.runtime.featurizer.transformer.timeseries.\
    datetime_column_featurizer import DatetimeColumnFeaturizer
from azureml.automl.runtime.featurizer.transformer.timeseries.drop_columns import DropColumns
from azureml.automl.runtime.featurizer.transformer.timeseries.\
    forecasting_base_estimator import AzureMLForecastTransformerBase
from azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_heuristic_utils import (
    analyze_pacf_per_grain,
    frequency_based_lags,
    get_heuristic_max_horizon
)
from azureml.automl.runtime.featurizer.transformer.timeseries.grain_index_featurizer import GrainIndexFeaturizer
from azureml.automl.runtime.featurizer.transformer.timeseries.lag_lead_operator import LagLeadOperator
from azureml.automl.runtime.featurizer.transformer.timeseries.max_horizon_featurizer import MaxHorizonFeaturizer
from azureml.automl.runtime.featurizer.transformer.timeseries.\
    missingdummies_transformer import MissingDummiesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries.numericalize_transformer import NumericalizeTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries.\
    restore_dtypes_transformer import RestoreDtypesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries.rolling_window import RollingWindow
from azureml.automl.runtime.featurizer.transformer.timeseries.short_grain_dropper import ShortGrainDropper
from azureml.automl.runtime.featurizer.transformer.timeseries.stl_featurizer import STLFeaturizer
from azureml.automl.runtime.featurizer.transformer.timeseries.time_index_featurizer import TimeIndexFeaturizer
from azureml.automl.runtime.featurizer.transformer.timeseries.time_series_imputer import TimeSeriesImputer
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import (
    TimeSeriesPipelineType,
    get_boolean_col_names,
    _get_categorical_columns,
    _get_date_columns,
    _get_excluded_columns,
    _get_included_columns,
    _get_numerical_columns,
    _get_numerical_imputer_value,
    _get_target_imputer,
    _has_valid_customized_imputer
)
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame, construct_tsdf
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType

logger = logging.getLogger(__name__)
REMOVE_LAG_LEAD_WARN = "The lag-lead operator was removed due to memory limitation."
REMOVE_ROLLING_WINDOW_WARN = "The rolling window operator was removed due to memory limitation."


def suggest_featurizers_timeseries(
    X: pd.DataFrame,
    y: Optional[np.ndarray],
    featurization_config: FeaturizationConfig,
    timeseries_param_dict: Dict[str, Any],
    pipeline_type: TimeSeriesPipelineType,
    categories_by_grain_cols: Optional[Dict[str, List[Any]]] = None,
    categories_by_non_grain_cols: Optional[Dict[str, List[Any]]] = None,
) -> Tuple[Pipeline, Dict[str, Any], bool, List[str]]:
    """
    Execute internal fitting logic and prepare the featurization pipeline.

    :param X: Dataframe representing text, numerical or categorical input.
    :type X: pandas.DataFrame
    :param y: To match fit signature.
    :type y: numpy.ndarray
    :param featurization_config: The featurization config to be used for featurization suggestion.
    :type featurization_config: FeaturizationConfig
    :param timeseries_param_dict: The timeseries parameters to be used for featurization suggestion. Some of these
        parameters may be "auto" or heuristic placeholders. These "auto" params will be computed here, and returned
        as part of featurization suggestion.
    :type timeseries_param_dict: Dict
    :param pipeline_type: The type of pipeline we are creating. This will either be a "full" or "cv reduced". This
        parameter is used as an optimization to skip expensive computations which can be reused.
    :type pipeline_type: TimeSeriesPipelineType
    :param categories_by_grain_cols: Dictionary of grain column names to unique categories in those columns
    :type categories_by_grain_cols: Optional[Dict[str, List[Any]]]
    :param categories_by_non_grain_cols: Dictionary of categorical column names to unique categories in those columns
    :type categories_by_non_grain_cols: Optional[Dict[str, List[Any]]]
    :return: The Pipeline, the timeseries param dict with heuristics modified, bool whether lookback
        features were removed due to memory constraints, and the time_index_non_holiday_features list
    :raises: DataException for non-dataframe.
    """
    _transforms = {}  # type: Dict[str, TransformerMixin]

    max_horizon = TimeSeriesInternal.MAX_HORIZON_DEFAULT  # type: int
    # Check if TimeSeries.MAX_HORIZON is not set to TimeSeries.AUTO
    if isinstance(timeseries_param_dict.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT), int):
        max_horizon = timeseries_param_dict.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT)

    use_stl = timeseries_param_dict.get(TimeSeries.USE_STL, TimeSeriesInternal.USE_STL_DEFAULT)
    if use_stl is not None and use_stl not in TimeSeriesInternal.STL_VALID_OPTIONS:
        raise ConfigException._with_error(
            AzureMLError.create(
                InvalidArgumentWithSupportedValues, target=TimeSeries.USE_STL,
                arguments="{} ({})".format(TimeSeries.USE_STL, use_stl),
                supported_values=TimeSeriesInternal.STL_VALID_OPTIONS,
                reference_code=ReferenceCodes._TST_WRONG_USE_STL
            )
        )
    seasonality = timeseries_param_dict.get(
        TimeSeries.SEASONALITY,
        TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT
    )
    force_time_index_features = timeseries_param_dict.get(
        TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME,
        TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_DEFAULT
    )
    time_index_non_holiday_features = []  # type: List[str]

    if TimeSeries.TIME_COLUMN_NAME not in timeseries_param_dict.keys():
        raise ConfigException._with_error(
            AzureMLError.create(
                ArgumentBlankOrEmpty, target=TimeSeries.TIME_COLUMN_NAME,
                argument_name=TimeSeries.TIME_COLUMN_NAME,
                reference_code=ReferenceCodes._TST_NO_TIME_COLNAME_TS_TRANS_INIT
            )
        )
    time_column_name = cast(str, timeseries_param_dict[TimeSeries.TIME_COLUMN_NAME])
    grains = timeseries_param_dict.get(TimeSeries.GRAIN_COLUMN_NAMES)
    if isinstance(grains, str):
        grains = [grains]
    grain_column_names = cast(List[str], grains)
    drop_column_names = cast(List[Any], timeseries_param_dict.get(TimeSeries.DROP_COLUMN_NAMES))
    if featurization_config.drop_columns is not None and \
            len(featurization_config.drop_columns) > 0:
        drop_column_names_set = set(drop_column_names)
        for col in featurization_config.drop_columns:
            if col not in drop_column_names_set:
                drop_column_names.append(col)

    # Used to make data compatible with timeseries dataframe
    target_column_name = TimeSeriesInternal.DUMMY_TARGET_COLUMN
    origin_column_name = \
        timeseries_param_dict.get(
            TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
            TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT
        )
    dummy_grain_column = TimeSeriesInternal.DUMMY_GRAIN_COLUMN

    # For the same purpose we need to store the imputer for y values.
    country_or_region = timeseries_param_dict.get(TimeSeries.COUNTRY_OR_REGION, None)
    boolean_columns = []  # type: List[str]
    pipeline = None  # type: Optional[Pipeline]
    freq_offset = timeseries_param_dict.get(TimeSeries.FREQUENCY)  # type: Optional[pd.DateOffset]

    Validation.validate_type(
        X, "X", expected_types=pd.DataFrame, reference_code=ReferenceCodes._TST_PARTIAL_FIT_ARG_WRONG_TYPE)
    Validation.validate_non_empty(X, "X", reference_code=ReferenceCodes._TST_PARTIAL_FIT_ARG_WRONG_TYPE_EMP)

    # Replace auto parameters with the heuristic values.
    # max_horizon
    params_copy = copy.deepcopy(timeseries_param_dict)
    if timeseries_param_dict.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT) == TimeSeries.AUTO:
        # Get heuristics only if we are fitting the first time.
        max_horizon = get_heuristic_max_horizon(
            X,
            time_column_name,
            grain_column_names)
        params_copy[TimeSeries.MAX_HORIZON] = max_horizon
        timeseries_param_dict[TimeSeries.MAX_HORIZON] = max_horizon

    # Make heuristics for lags and rolling window if needed.
    # Figure out if we need auto lags or rolling window.
    lags_to_construct = timeseries_param_dict.get(TimeSeriesInternal.LAGS_TO_CONSTRUCT)
    autolags = lags_to_construct is not None and lags_to_construct.get(target_column_name) == [TimeSeries.AUTO]
    autorw = (
        timeseries_param_dict.get(TimeSeriesInternal.WINDOW_SIZE) == TimeSeries.AUTO
        and timeseries_param_dict.get(TimeSeriesInternal.TRANSFORM_DICT) is not None
    )
    # If we need automatic lags or rolling window, run the PACF analysis.
    if (autolags or autorw):
        X[target_column_name] = y
        lags, rw = analyze_pacf_per_grain(
            X,
            time_column_name,
            target_column_name,
            grain_column_names)
        X.drop(target_column_name, axis=1, inplace=True)
        # FIXME: We need to design the EffectiveConfig which will include the
        # heuristic parameters, rather then swapping parameters here.
        # Swap lags and rw in the copied parameters if needed.
        if autolags:
            if lags != 0:
                params_copy[TimeSeriesInternal.LAGS_TO_CONSTRUCT] = {
                    target_column_name: [lag for lag in range(1, lags + 1)]
                }
            else:
                del params_copy[TimeSeriesInternal.LAGS_TO_CONSTRUCT]

        if autorw:
            if rw != 0:
                params_copy[TimeSeriesInternal.WINDOW_SIZE] = rw
            else:
                del params_copy[TimeSeriesInternal.WINDOW_SIZE]

    # Create Lag lead operator or rolling window if needed.
    if (TimeSeriesInternal.LAGS_TO_CONSTRUCT in params_copy.keys()):
        # We need to backfill the cache to avoid problems with shape.
        # As of 11/2020 do not need to backfill anymore since we
        # now impute the full training set
        params_copy['backfill_cache'] = False
        _transforms[TimeSeriesInternal.LAG_LEAD_OPERATOR] = _get_transformer_params(
            LagLeadOperator,
            **params_copy
        )
    if (TimeSeriesInternal.WINDOW_SIZE in params_copy.keys()
            and TimeSeriesInternal.TRANSFORM_DICT in params_copy.keys()):
        # We need to disable the horizon detection, because it is very slow on large data sets.
        params_copy['check_max_horizon'] = False
        # We need to backfill the cache to avoid problems with shape.
        # As of 11/2020 do not need to backfill anymore since we
        # now impute the full training set
        params_copy['backfill_cache'] = False
        _transforms[TimeSeriesInternal.ROLLING_WINDOW_OPERATOR] = _get_transformer_params(
            RollingWindow,
            **params_copy
        )

    # After we defined automatic parameters set these parameters to timeseries_param_dict.
    timeseries_param_dict[TimeSeries.TARGET_LAGS] = _get_lag_from_operator_may_be(
        _transforms.get(TimeSeriesInternal.LAG_LEAD_OPERATOR),
        target_column_name)
    timeseries_param_dict[TimeSeries.TARGET_ROLLING_WINDOW_SIZE] = _get_rw_from_operator_may_be(
        _transforms.get(TimeSeriesInternal.ROLLING_WINDOW_OPERATOR))
    # If there are columns of dtype boolean, remember them for further encoding.
    # Note, we can not rely on dtypes, because when the data frame is constructed from the
    # array as in
    boolean_columns = get_boolean_col_names(X)
    # Remove backwards compat handling as this will only be called from newer SDKs
    # if not self._keep_missing_dummies_on_target_safe():
    #     # Revert to old behavior - Add an order to column to X
    #     # This is included only for backward compatibility
    #     X.reset_index(inplace=True, drop=True)
    #     X[TimeSeriesInternal.DUMMY_ORDER_COLUMN] = X.index
    #     tsdf = self.construct_tsdf(X, y)
    #     X.drop(TimeSeriesInternal.DUMMY_ORDER_COLUMN, axis=1, inplace=True)
    # else:
    if timeseries_param_dict[TimeSeries.GRAIN_COLUMN_NAMES] is None:
        grain_column_names = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
    tsdf = construct_tsdf(
        X,
        y,
        target_column_name,
        time_column_name,
        origin_column_name,
        grain_column_names,
        boolean_columns
    )
    all_drop_column_names = [x for x in tsdf.columns if np.sum(tsdf[x].notnull()) == 0]
    if isinstance(drop_column_names, str):
        all_drop_column_names.extend([drop_column_names])
    elif drop_column_names is not None:
        all_drop_column_names.extend(drop_column_names)
    drop_column_names = all_drop_column_names
    timeseries_param_dict[TimeSeries.DROP_COLUMN_NAMES] = all_drop_column_names

    # Save the data types found in the dataset
    detected_column_purposes = \
        {
            FeatureType.Numeric:
                _get_numerical_columns(tsdf, target_column_name, drop_column_names, featurization_config),
            FeatureType.Categorical:
                _get_categorical_columns(tsdf, target_column_name, drop_column_names, featurization_config),
            FeatureType.DateTime:
                _get_date_columns(tsdf, drop_column_names, featurization_config)
        }  # type: Dict[str, List[str]]

    if freq_offset is not None:
        freq_offset = frequency_fixer.str_to_offset_safe(
            freq_offset,
            ReferenceCodes._TST_WRONG_FREQ
        )
    else:
        min_points = utilities.get_min_points(
            timeseries_param_dict[TimeSeries.TARGET_ROLLING_WINDOW_SIZE],
            timeseries_param_dict[TimeSeries.TARGET_LAGS],
            max_horizon,
            timeseries_param_dict.get(TimeSeriesInternal.CROSS_VALIDATIONS),
            timeseries_param_dict.get(TimeSeries.CV_STEP_SIZE)
        )
        one_grain_freq = None
        for grain, df_one in tsdf.groupby_grain():
            if all(pd.isnull(v) for v in df_one.ts_value):
                raise DataException._with_error(
                    AzureMLError.create(GrainContainsEmptyValues, target='time_series_id_values',
                                        reference_code=ReferenceCodes._TST_NO_DATA_IN_GRAIN,
                                        time_series_id=str(grain))
                )
            if freq_offset is None:
                if one_grain_freq is None:
                    one_grain_freq = df_one.infer_freq(False)
                elif len(df_one) >= min_points:
                    one_grain_freq = df_one.infer_freq(False)
        freq_offset = one_grain_freq

        # If the data frame has one row or less, then validation did not worked correctly
        # and hence the frequency can not be calculated properly.
        # It is a ClientException because validation should not allow this error to go through.
        if freq_offset is None:
            raise ClientException._with_error(
                AzureMLError.create(TimeseriesDfInvalidValAllGrainsContainSingleVal, target='freq_offset',
                                    reference_code=ReferenceCodes._TST_ALL_GRAINS_CONTAINS_SINGLE_VAL)
            )

    timeseries_param_dict[TimeSeries.FREQUENCY] = freq_offset

    # Calculate seasonality with frequency
    if seasonality == TimeSeries.AUTO:
        # Get heuristics if user did not provide seasonality.

        # For short series models, we will use frequency to detect seasonality, since standard error of ACF will be
        # large for short histories.
        # frequency_based_lags() method calculates frequency & seasonality similarly
        freq_based_lags = frequency_based_lags(freq_offset)
        seasonality = freq_based_lags if freq_based_lags > 0 else 1
        timeseries_param_dict[TimeSeries.SEASONALITY] = seasonality

    # Define the columns which will be in the final data frame.
    columns = set(X.columns.values).difference(set(drop_column_names))
    timeseries_param_dict[TimeSeriesInternal.ARIMAX_RAW_COLUMNS] = list(columns)  # is a list of values

    pipeline, time_index_non_holiday_features = _construct_pre_processing_pipeline(
        tsdf,
        featurization_config,
        drop_column_names,
        freq_offset,
        pipeline_type,
        use_stl,
        time_column_name,
        target_column_name,
        max_horizon,
        _transforms,
        seasonality,
        boolean_columns,
        grain_column_names,
        origin_column_name,
        dummy_grain_column,
        country_or_region,
        force_time_index_features,
        detected_column_purposes,
        timeseries_param_dict,
        categories_by_grain_cols,
        categories_by_non_grain_cols
    )
    # Override the parent class fit method to define if there is enough memory
    # for using LagLeadOperator and RollingWindow.
    remove_lookback = _should_remove_lag_lead_and_rw(X, y, max_horizon, _transforms)
    lookback_removed = False
    if remove_lookback:
        step_warning_tuple = [
            (TimeSeriesInternal.MAX_HORIZON_FEATURIZER, None),
            (TimeSeriesInternal.LAG_LEAD_OPERATOR, REMOVE_LAG_LEAD_WARN),
            (TimeSeriesInternal.ROLLING_WINDOW_OPERATOR, REMOVE_ROLLING_WINDOW_WARN)
        ]
        remove_steps = set()
        for step_name, warning in step_warning_tuple:
            remove_steps.add(step_name)
            if step_name in _transforms.keys():
                del _transforms[step_name]
            if warning is not None:
                print(warning)
        if pipeline:
            pipeline.steps[:] = [(key, step) for key, step in pipeline.steps if key not in remove_steps]
        lookback_removed = True
    return (
        pipeline, timeseries_param_dict, lookback_removed,
        time_index_non_holiday_features
    )


def _get_lag_from_operator_may_be(lag_operator: Optional[LagLeadOperator], target_column_name: str) -> List[int]:
    """
    Get target lag from the lag lead operator.

    :param lag_operator: The lag lead operator.
    :return: The list of lags or [0] if there is no target lags or lag_operator is None.
    """
    if lag_operator is None:
        return [0]
    lags = lag_operator.lags_to_construct.get(target_column_name)
    if lags is None:
        return [0]
    else:
        if isinstance(lags, int):
            return [lags]
        return lags


def _get_rw_from_operator_may_be(rolling_window: Optional[RollingWindow]) -> int:
    """
    Ret the rolling window size.

    :param rolling_window: The rolling window operator.
    :return: The size of rolling window.
    """
    if rolling_window is None:
        return 0
    return cast(int, rolling_window.window_size)


def _get_transformer_params(
    cls: 'Type[AzureMLForecastTransformerBase]',
    **kwargs: Any
) -> Any:
    """
    Create the transformer of type cls.

    :param cls: the class of transformer to be constructed.
    :type cls: type
    :param kwargs: the dictionary of parameters to be parsed.
    :type kwargs: dict
    """
    rw = {}
    valid_args = inspect.getfullargspec(cls.__init__).args
    for k, v in kwargs.items():
        if k in valid_args:
            rw[k] = v

    return cls(**rw)


def _should_remove_lag_lead_and_rw(
    df: pd.DataFrame,
    y: Optional[np.ndarray],
    max_horizon: int,
    transforms: Dict[str, TransformerMixin]
) -> bool:
    """
    Remove the LagLead and or RollingWindow operator from the pipeline if there is not enough memory.

    :param df: DataFrame representing text, numerical or categorical input.
    :type df: pandas.DataFrame
    :param y: To match fit signature.
    :type y: numpy.ndarray
    :param num_features: number of numeric features to be lagged
    :type num_features: int
    """
    memory_per_df = memory_utilities.get_data_memory_size(df)
    if y is not None:
        memory_per_df += memory_utilities.get_data_memory_size(y)
    remove_ll_rw = True
    total_num_of_lags = 0

    if transforms.get(TimeSeriesInternal.LAG_LEAD_OPERATOR) is not None:
        lag_op = transforms.get(TimeSeriesInternal.LAG_LEAD_OPERATOR)
        # In the first if() statement we implicitly check if lag_op is not None.
        Contract.assert_value(lag_op, "lag_op")
        lag_op = cast(LagLeadOperator, lag_op)

        lag_list = list(lag_op.lags_to_construct.values())  # list of lags
        num_lags_per_variable = [(len(x) if isinstance(x, list) else 1) for x in lag_list]
        total_num_of_lags = sum(num_lags_per_variable)

    try:
        total_memory = memory_utilities.get_all_ram()
        memory_horizon_based = max_horizon * memory_per_df
        total_num_columns = df.shape[1]
        feature_lag_adjustment = (total_num_of_lags / total_num_columns) if (total_num_columns > 0) else 0
        memory_usage_frac = (memory_horizon_based / total_memory) * (1 + feature_lag_adjustment)
        remove_ll_rw = TimeSeriesInternal.MEMORY_FRACTION_FOR_DF < memory_usage_frac
    except Exception:
        pass

    return remove_ll_rw


def _construct_pre_processing_pipeline(
    tsdf: TimeSeriesDataFrame,
    featurization_config: FeaturizationConfig,
    drop_column_names: Optional[List[str]],
    freq_offset: Optional[pd.DateOffset],
    pipeline_type: TimeSeriesPipelineType,
    use_stl: str,
    time_column_name: str,
    target_column_name: str,
    max_horizon: int,
    transforms: Dict[str, TransformerMixin],
    seasonality: Union[int, str],
    boolean_columns: List[str],
    grain_column_names: List[str],
    origin_column_name: str,
    dummy_grain_column: str,
    country_or_region: str,
    force_time_index_features: bool,
    detected_column_purposes: Dict[str, List[str]],
    timeseries_param_dict: Dict[str, Any],
    categories_by_grain_cols: Optional[Dict[str, List[Any]]] = None,
    categories_by_non_grain_cols: Optional[Dict[str, List[Any]]] = None,
) -> Tuple[Pipeline, List[str]]:
    """Return the featurization pipeline."""
    logger.info('Start construct pre-processing pipeline')
    if drop_column_names is None:
        drop_column_names = []

    # At this point we should know that the freq_offset is not None,
    # because it had to be set or imputed in the fit() method.
    Contract.assert_value(freq_offset, "freq_offset")

    numerical_columns = detected_column_purposes.get(
        FeatureType.Numeric, [])  # type: List[str]

    imputation_dict = {col: tsdf[col].median() for col in numerical_columns}

    datetime_columns = _get_date_columns(tsdf, drop_column_names, featurization_config)
    # In forecasting destination date function, neither forward or backward will work
    # have to save the last non null value to impute
    # TODO: make both numeric and this imputation grain aware
    datetime_imputation_dict = {col: tsdf.loc[tsdf[col].last_valid_index()][col]
                                for col in datetime_columns}

    impute_missing = _get_x_imputer(
        tsdf,
        numerical_columns,
        datetime_columns,
        imputation_dict,
        datetime_imputation_dict,
        featurization_config,
        time_column_name,
        target_column_name,
        drop_column_names,
        grain_column_names,
        freq_offset
    )

    default_pipeline = Pipeline([
        (TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES, MissingDummiesTransformer(numerical_columns)),
        (TimeSeriesInternal.IMPUTE_NA_NUMERIC_DATETIME, impute_missing)])

    # If desired, we need to create the transform which will handle the short series.
    if _is_short_grain_handled(timeseries_param_dict) and pipeline_type == TimeSeriesPipelineType.FULL:
        # Set parameters target_lags and target_rolling_window_size for ShortGrainDropper.
        timeseries_param_dict[TimeSeries.TARGET_LAGS] = _get_lag_from_operator_may_be(
            transforms.get(TimeSeriesInternal.LAG_LEAD_OPERATOR),
            target_column_name
        )
        timeseries_param_dict[TimeSeries.TARGET_ROLLING_WINDOW_SIZE] = _get_rw_from_operator_may_be(
            transforms.get(TimeSeriesInternal.ROLLING_WINDOW_OPERATOR))

        params = timeseries_param_dict.copy()
        params[TimeSeries.MAX_HORIZON] = max_horizon
        default_pipeline.steps.append((TimeSeriesInternal.SHORT_SERIES_DROPPEER, ShortGrainDropper(**params)))

    # After imputation we need to restore the data types using restore_dtypes_transformer RESTORE_DTYPES
    default_pipeline.steps.append((
        TimeSeriesInternal.RESTORE_DTYPES,
        RestoreDtypesTransformer(tsdf, featurization_config=featurization_config)
    ))

    # If we have datetime columns (other than time index), make calendar features from them
    if len(datetime_columns) > 0:
        default_pipeline.steps.append((
            TimeSeriesInternal.MAKE_DATETIME_COLUMN_FEATURES,
            DatetimeColumnFeaturizer(datetime_columns=datetime_columns)
        ))

    # We introduce the STL transform, only if we need it after the imputation,
    # but before the lag lead operator and rolling window because STL does not support
    # origin time index.
    if use_stl is not None:
        only_season_feature = use_stl == TimeSeries.STL_OPTION_SEASON
        default_pipeline.steps.append((
            TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND,
            STLFeaturizer(
                seasonal_feature_only=only_season_feature,
                seasonality=seasonality
            )
        ))

    # Return the pipeline after STL featurizer if it is for reduced CV featurization
    # (i.e. the output of a full pipeline will be re-used for other features like lag, RW, etc)
    if pipeline_type is TimeSeriesPipelineType.CV_REDUCED:
        return default_pipeline, []

    # Insert the max horizon featurizer to make horizon rows and horizon feature
    # Must be *before* lag and rolling window transforms
    if TimeSeriesInternal.LAG_LEAD_OPERATOR in transforms or \
            TimeSeriesInternal.ROLLING_WINDOW_OPERATOR in transforms:
        default_pipeline.steps.append((
            TimeSeriesInternal.MAX_HORIZON_FEATURIZER,
            MaxHorizonFeaturizer(
                max_horizon,
                origin_time_colname=origin_column_name,
                horizon_colname=TimeSeriesInternal.HORIZON_NAME
            )
        ))
    if TimeSeriesInternal.LAG_LEAD_OPERATOR in transforms and \
            timeseries_param_dict.get(TimeSeries.FEATURE_LAGS) == TimeSeries.AUTO:
        lag_op = transforms.get(TimeSeriesInternal.LAG_LEAD_OPERATOR)
        # In the first if() statement we implicitely check if lag_op is not None.
        # Added assert to avoid mypy gate failure
        Contract.assert_value(lag_op, "lag_op")
        lag_op = cast(LagLeadOperator, lag_op)

        target_lag_list = lag_op.lags_to_construct.get(target_column_name)
        # exclude original boolean columns from potential features to be lagged
        real_numerical_columns = set(numerical_columns) - set(boolean_columns)
        if target_lag_list is not None:
            features_to_lag = {}
            for feature in real_numerical_columns:
                feature_lag = tsdf.groupby(grain_column_names).apply(
                    _grangertest_one_grain_feature,
                    time_column_name=time_column_name,
                    response_col=target_column_name,
                    effect_col=feature)
                max_lag = feature_lag.max()  # type: int
                if max_lag > 0:
                    feature_lag_list = list(range(1, max_lag + 1))
                    features_to_lag.update({feature: feature_lag_list})
            if len(features_to_lag) > 0:
                lag_op.lags_to_construct.update(features_to_lag)

    # Lag and rolling window transformer
    # To get the determined behavior sort the transforms.
    transforms_ordered = sorted(transforms.keys())
    for transform in transforms_ordered:
        # Add the transformer to the default pipeline
        default_pipeline.steps.append((transform, transforms[transform]))

    # Don't apply grain featurizer when there is single time series
    if dummy_grain_column not in grain_column_names:
        grain_index_featurizer = GrainIndexFeaturizer(overwrite_columns=True,
                                                      categories_by_grain_cols=categories_by_grain_cols)
        default_pipeline.steps.append((TimeSeriesInternal.MAKE_GRAIN_FEATURES, grain_index_featurizer))

    if categories_by_non_grain_cols is not None and len(categories_by_non_grain_cols) == 0:
        # categories_by_non_grain_cols is None --> means no pre calculations were done
        # categories_by_non_grain_cols is empty --> means  pre calculations were done but found no categorical columns
        logger.info('skipping NumericalizeTransformer because no categorical columns were found @ pre calculations')
    else:
        # If we have generated/have the category columns, we want to convert it to numerical values.
        # To avoid generation of 1000+ columns on some data sets.
        # NumericalizeTransformer is an alternative to the CategoryBinarizer: it will find the categorical
        # features and will turn them to integer numbers and this will allow to avoid detection of these
        # features by the CategoryBinarizer.
        cat_cols = _get_included_columns(tsdf, FeatureType.Categorical, featurization_config)
        other_cols = _get_excluded_columns(tsdf, FeatureType.Categorical, featurization_config)
        default_pipeline.steps.append((
            TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC,
            NumericalizeTransformer(
                include_columns=cat_cols - set(drop_column_names),
                exclude_columns=other_cols,
                categories_by_col=categories_by_non_grain_cols
            )
        ))

    # We are applying TimeIndexFeaturizer transform after the NumericalizeTransformer because we want to
    # one hot encode holiday features.
    # Add step to preprocess datetime
    tr_params = featurization_config.transformer_params
    params = {}
    if tr_params is not None and SupportedTransformersInternal.TimeIndexFeaturizer in tr_params:
        # Params are stored a list of (list of column, params dict) tuples
        # For now in some scenarios we store desired holiday params in this config
        # object.
        params = tr_params[SupportedTransformersInternal.TimeIndexFeaturizer][0][-1]

    time_index_featurizer = TimeIndexFeaturizer(
        overwrite_columns=True,
        country_or_region=country_or_region,
        freq=freq_offset,
        force_feature_list=force_time_index_features,
        **params
    )
    time_index_non_holiday_features = time_index_featurizer.preview_non_holiday_feature_names(tsdf)
    default_pipeline.steps.append((TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES, time_index_featurizer))

    # Add step to preprocess categorical data
    default_pipeline.steps.append((
        TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT,
        CategoryBinarizer()
    ))

    # Don't add dropColumn transfomer if there is nothing to drop
    if drop_column_names is not None and len(drop_column_names) > 0:
        default_pipeline.steps.insert(0, (
            'drop_irrelevant_columns',
            DropColumns(drop_column_names)
        ))
    logger.info('Finish Construct Pre-Processing Pipeline')
    return default_pipeline, time_index_non_holiday_features


def _get_x_imputer(
    tsdf: TimeSeriesDataFrame,
    numerical_columns: List[str],
    datetime_columns: List[str],
    imputation_dict: Dict[str, float],
    datetime_imputation_dict: Dict[str, float],
    featurization_config: FeaturizationConfig,
    time_column_name: str,
    target_column_name: str,
    drop_column_names: List[str],
    grain_column_names: List[str],
    freq_offset: Optional[pd.DateOffset]
) -> TimeSeriesImputer:
    """
    Get a chained x value imputer based on the featurization config.

    :param input_column_list: All the imputation value list.
    :param default_imputation_dict: The default value for x imputation.
    """
    ffill_columns = []
    if _has_valid_customized_imputer(featurization_config):
        for cols, params in featurization_config.transformer_params[SupportedTransformers.Imputer]:
            # Replace the imputation parameter to custom if we can.
            # Remove the special columns from imputer parameters
            # even if user has specified imputer for time or grain column.
            special_columns = grain_column_names + \
                [time_column_name, target_column_name] + drop_column_names
            for col in filter(lambda x: x not in special_columns, cols):
                if col not in tsdf.columns:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            FeaturizationConfigColumnMissing, target='X', columns=col,
                            sub_config_name="transformer_params", all_columns=list(tsdf.columns),
                            reference_code=ReferenceCodes._TST_FEATURIZATION_TRANSFORM
                        )
                    )
                if params.get(TransformerParams.Imputer.Strategy) != TransformerParams.Imputer.Ffill:
                    imputation_dict[col] = _get_numerical_imputer_value(
                        col, cast(float, imputation_dict.get(col)), tsdf, params
                    )
                else:
                    # remove the default filling value to avoid time_series_imputer to impute this value
                    imputation_dict.pop(col, None)
                    ffill_columns.append(col)

    for col in datetime_columns:
        if col not in ffill_columns:
            ffill_columns.append(col)

    imputation_method = OrderedDict({'ffill': ffill_columns})
    imputation_value = imputation_dict
    if len(datetime_columns) > 0:
        imputation_method['bfill'] = datetime_columns
        imputation_value.update(datetime_imputation_dict)

    impute_missing = TimeSeriesImputer(
        option='fillna',
        input_column=numerical_columns + datetime_columns,
        method=imputation_method,
        value=imputation_value,
        freq=freq_offset
    )
    impute_missing.fit(X=tsdf)

    return impute_missing


def _is_short_grain_handled(timeseries_param_dict: Dict[str, Any]) -> bool:
    """
    Return if we need to handle (drop) the short series.

    This method is used to handle the legacy short_series_handling and
    new short_series_handling_configuration parameters.
    :return: if the short series needs to be handled (dropped).
    """
    is_short_grains_handled = False  # type: bool
    if TimeSeries.SHORT_SERIES_HANDLING in timeseries_param_dict.keys():
        is_short_grains_handled = cast(bool, timeseries_param_dict.get(TimeSeries.SHORT_SERIES_HANDLING))
    if TimeSeries.SHORT_SERIES_HANDLING_CONFIG in timeseries_param_dict.keys():
        handling = timeseries_param_dict.get(TimeSeries.SHORT_SERIES_HANDLING_CONFIG)
        is_short_grains_handled = (handling == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO
                                   or handling == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP)
    return is_short_grains_handled


def _grangertest_one_grain_feature(
    df: pd.DataFrame,
    time_column_name: str,
    response_col: str,
    effect_col: str,
    add_const: bool = True,
    max_lag: Optional[int] = None,
    test_type: Optional[str] = None,
    crit_pval: Optional[float] = None
) -> Optional[int]:
    """
    Test if a single feature (x) granger causes response variable (y).
    * Input data frame must contain 2 columns. Current version of statsmodels supports only one way test.
    * Missing values are not imputed on purpose. If there are missing dates, lag_by_occurrence option is used and
    granger test is consistent with such approach.
    * Response variable (y) must be the first column in the data frame.

    :param response_col: name of the target column (y)
    :param effect_col: name of the feature column (x)
    :return: lag order for the feature in question
    """
    if test_type is None:
        test_type = TimeSeriesInternal.GRANGER_DEFAULT_TEST
    if crit_pval is None:
        crit_pval = TimeSeriesInternal.GRANGER_CRITICAL_PVAL
    # Select required columns and sort by date
    granger_df = df[[response_col, effect_col]]
    granger_df.sort_index(level=time_column_name, inplace=True)
    # Determine max allowable lag. Test fails if lag is too big.
    # Source: https://github.com/statsmodels/statsmodels/blob/master/statsmodels/tsa/stattools.py#L1250
    if max_lag is None:
        max_lag = ((granger_df.shape[0] - int(add_const)) / 3) - 1
        max_lag = math.floor(max_lag) if (max_lag > 0) else 0
    try:
        test = stattools.grangercausalitytests(granger_df, max_lag, verbose=False)
    except BaseException as e:
        msg = "Granger causality test failed. This feature does not granger-cause response variable."
        logger.warning(msg)
        logging_utilities.log_traceback(e, logger, is_critical=False,
                                        override_error_msg=msg)
        return int(0)

    lags = list(range(1, max_lag + 1))  # to pull appropriate lags
    pvals = [test[lag][0][test_type][1] for lag in lags]
    sig_bool = [val < crit_pval for val in pvals]
    # Get the first significant lag
    if not any(sig_bool):
        lag_granger = 0  # if all insignificant
    elif all(sig_bool):
        lag_granger = 1  # if all significant
    else:
        lag_granger = np.argmax(sig_bool) + 1  # add 1 to covert index to lag
    return int(lag_granger)
