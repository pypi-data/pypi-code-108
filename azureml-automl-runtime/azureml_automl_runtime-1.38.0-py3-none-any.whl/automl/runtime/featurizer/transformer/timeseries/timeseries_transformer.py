# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for timeseries preprocessing."""
import copy
import inspect
import json
import logging
import math
import uuid
import warnings
from builtins import isinstance
from collections import OrderedDict, defaultdict, Counter
from enum import Enum
from itertools import chain
from typing import (Any, DefaultDict, Dict, List, Optional, Set, Tuple, Type, Union,
                    cast)

import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from sklearn.pipeline import Pipeline
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.constants import FeatureType, SupportedTransformers
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal
from azureml.automl.core.constants import (TransformerParams, _OperatorNames,
                                           _TransformerOperatorMappings)
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities, utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    FeaturizationConfigColumnMissing,
    GrainContainsEmptyValues,
    InvalidArgumentWithSupportedValues,
    TimeseriesTypeMismatchFullCV,
    TimeseriesTypeMismatchDropFullCV,
    TimeseriesDfMissingColumn,
    TimeseriesDfInvalidValAllGrainsContainSingleVal,
    TimeseriesGrainAbsent,
    TimeseriesDfDatesOutOfPhase,
    TimeseriesWrongTestColumnSet
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal,\
    ShortSeriesHandlingValues
from azureml.automl.core.shared.exceptions import (AutoMLException,
                                                   ClientException,
                                                   ConfigException,
                                                   DataException,
                                                   ValidationException)
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingDataException)
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.runtime import frequency_fixer, _freq_aggregator
from azureml.automl.runtime._engineered_feature_names import (
    _FeatureTransformers, _FeatureTransformersAsJSONObject,
    _RawFeatureFeaturizationInfo, _Transformer)
from azureml.automl.runtime.featurization_info_provider import FeaturizationInfoProvider
from azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_pipeline import AzureMLForecastPipeline
from azureml.automl.runtime.shared import memory_utilities, forecasting_utils
from azureml.automl.runtime.shared.forecasting_verify import is_iterable_but_not_string
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame, _create_tsdf_from_data
from azureml.automl.runtime.shared.types import (DataInputType,
                                                 DataSingleColumnInputType,
                                                 FeaturizationSummaryType)
from pandas.tseries.offsets import DateOffset
from sklearn.base import TransformerMixin
from statsmodels.tsa import stattools

from .category_binarizer import CategoryBinarizer
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from .forecasting_heuristic_utils import (analyze_pacf_per_grain,
                                          frequency_based_lags,
                                          get_heuristic_max_horizon)
from .lag_lead_operator import LagLeadOperator
from .max_horizon_featurizer import MaxHorizonFeaturizer
from .missingdummies_transformer import MissingDummiesTransformer
from .numericalize_transformer import NumericalizeTransformer
from .rolling_window import RollingWindow
from .stl_featurizer import STLFeaturizer
from .time_series_imputer import TimeSeriesImputer
from ..automltransformer import AutoMLTransformer
from ....frequency_fixer import fix_df_frequency
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.forecasting_parameters import ForecastingParameters
try:
    from azureml.automl.runtime.stats_computation.raw_stats import TimeSeriesStat
    back_comp_raw_stats = False
except ImportError:
    back_comp_raw_stats = True

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None

logger = logging.getLogger(__name__)


class TimeSeriesPipelineType(Enum):
    """
    Enum for type of pipeline to construct for time-series preprocessing.

    Full is a pipeline with all steps requested through AutoML settings.
    CV Reduced is a pipeline to be run on CV splits where only some steps need recomputing (e.g. STL Featurizer)
    """

    FULL = 1
    CV_REDUCED = 2


class TimeSeriesTransformer(AutoMLTransformer, FeaturizationInfoProvider):
    """Class for timeseries preprocess."""

    REMOVE_LAG_LEAD_WARN = "The lag-lead operator was removed due to memory limitation."
    REMOVE_ROLLING_WINDOW_WARN = "The rolling window operator was removed due to memory limitation."
    MISSING_Y = 'missing_y'  # attribute name to look for. Used for backward compatibility check.
    SERIES_STATS_DICT = 'series_stats_dict'  # the key name to serialize series_stats needed for ver 1.25

    @staticmethod
    def _join_reusable_features_for_cv(ts_transformer_cv: 'TimeSeriesTransformer', X_cv: pd.DataFrame,
                                       ts_transformer_full: 'TimeSeriesTransformer',
                                       X_full: pd.DataFrame) -> pd.DataFrame:
        """
        Join dataframes from CV_REDUCED and FULL preprocessing pipelines.

        Context: During CV, some features must be recomputed on split sets while others can be reused
        from preprocessing on the whole training set. The goal here is to add the "reuseable" features
        to the output of CV preprocessing where the "non-reuseable" features have been recomputed.
        This method dynamically determines which features should be taken from the re-computed CV pipeline
        and which can be re-used from the FULL pipeline. It does this by finding the intersection of transforms
        from the reduced and full pipelines, then retrieving the set of features created by these overlapping
        transforms.
        This is a private utility method that should only be used in the described context.

        :param ts_transformer_cv: Fitted TimeSeriesTransformer containing reduced/subset pipeline
        :param X_cv: Output from a CV_REDUCED transform pipeline
        :param ts_transformer_full: Fitted TimeSeriesTransformer containing full pipeline
        :param X_full: Output from a FULL transform pipeline
        :return: Joined dataframe
        """
        # First check validity of join - schema of full and cv should match
        Contract.assert_true(
            ts_transformer_full.target_column_name == ts_transformer_cv.target_column_name,
            "Transformer target column names must match",
            log_safe=True
        )
        Contract.assert_true(
            ts_transformer_full.grain_column_names == ts_transformer_cv.grain_column_names,
            "Transformer time series identifier column names must match",
            log_safe=True
        )
        Contract.assert_true(
            ts_transformer_full.time_column_name == ts_transformer_cv.time_column_name,
            "Transformer time column names must match",
            log_safe=True
        )
        Contract.assert_true(
            ts_transformer_full.origin_column_name == ts_transformer_cv.origin_column_name,
            "Transformer origin column names must match",
            log_safe=True
        )

        # The column purposes should match as well - if they don't then featurization
        # could be applied differently in full and cv and lead to undefined behavior.
        # Since this can happen for user data, this condition raises a DataException
        # To ensure backwards compat, check if the transforms have the detected attribute
        check_columns = \
            hasattr(ts_transformer_full, 'detected_column_purposes') and \
            hasattr(ts_transformer_cv, 'detected_column_purposes')

        if check_columns:
            bad_column_sets = \
                [(set(ts_transformer_full.detected_column_purposes[purpose])
                  .symmetric_difference(ts_transformer_cv.detected_column_purposes[purpose]))
                 for purpose in ts_transformer_full.detected_column_purposes]
            empty_set = set([])  # type: Set[str]
            bad_columns = empty_set.union(*bad_column_sets)  # type: Set[str]

            if len(bad_columns) > 0:
                cv_only_drop = set(
                    ts_transformer_cv.drop_column_names).difference(
                    ts_transformer_full.drop_column_names)
                if len(cv_only_drop) > 0:
                    raise DataException._with_error(
                        AzureMLError.create(
                            TimeseriesTypeMismatchDropFullCV, target='training_data',
                            reference_code=ReferenceCodes._TST_TYPE_MISMATCH_FULL_DROP_CV,
                            columns=list(cv_only_drop)
                        )
                    )
                raise DataException._with_error(
                    AzureMLError.create(
                        TimeseriesTypeMismatchFullCV, target='training_data',
                        reference_code=ReferenceCodes._TST_TYPE_MISMATCH_FULL_CV,
                        columns=list(bad_columns)
                    )
                )

        # Finally make sure that the CV transforms are a subset of the full transforms
        feat_dict_full = ts_transformer_full._get_features_by_transform()
        feat_dict_cv = ts_transformer_cv._get_features_by_transform()

        cv_unique_transforms = set(feat_dict_cv) - set(feat_dict_full)
        # We can safely format error message with the transforms
        # unique for CV, because they do not carry PII information.
        Contract.assert_true(
            len(cv_unique_transforms) == 0,
            ("CV pipeline transforms must be a subset of "
             "FULL pipeline transforms. CV-unique transforms: {}").format(cv_unique_transforms),
            log_safe=True
        )

        target_column_name = ts_transformer_full.target_column_name
        origin_column_name = ts_transformer_full.origin_column_name

        # Find the set of common transforms to both pipelines
        transforms_overlap = set(feat_dict_cv.keys()).intersection(set(feat_dict_full.keys()))
        feats_overlap = list()  # type: List[str]
        for trans in transforms_overlap:
            feats_overlap.extend(feat_dict_cv[trans])

        # Recompute features in the transform overlap and also the target
        feats_recompute = set(feats_overlap).union([target_column_name])

        # Drop recomputed columns from X_full prior to join
        X_temp = X_full.drop(columns=list(feats_recompute), errors='ignore')

        # If X_full has origin times and X_cv does not, temporarily move them out of the index.
        # If X_cv has origins, then X_full must also have origins, so don't need to handle reverse case
        cv_has_origin = origin_column_name in X_cv.index.names
        full_has_origin = origin_column_name in X_temp.index.names
        full_remove_origin = full_has_origin and (not cv_has_origin)
        if full_remove_origin:
            X_temp.reset_index(origin_column_name, inplace=True)

        # Do the join using the indices as the keys
        # Join type is inner (important in cases where e.g. FULL pipeline includes NaN removal from Lag/RW features)
        cols_drop_cv = set(X_cv.columns) - feats_recompute
        X_cv_new = (X_cv.drop(columns=list(cols_drop_cv), errors='ignore')
                    .merge(X_temp, how='inner', left_index=True, right_index=True, sort=True))

        # Put origins back in the index if they were removed before join
        if full_remove_origin:
            X_cv_new.set_index(origin_column_name, append=True, inplace=True)

        # Make sure we didn't lose or gain new any columns during the join
        # The only acceptable difference is the target column which could be popped off X_full
        # Using assert here because this should be determined entirely by internal code
        new_col_set_minus_target = set(X_cv_new.columns) - set([target_column_name])
        full_col_set_minus_target = set(X_full.columns) - set([target_column_name])
        if new_col_set_minus_target != full_col_set_minus_target:
            diff_col = Counter(
                TimeSeriesTransformer.get_col_internal_type(col)
                for col in new_col_set_minus_target.symmetric_difference(full_col_set_minus_target))
            cv_col_count = Counter(
                TimeSeriesTransformer.get_col_internal_type(col) for col in new_col_set_minus_target)
            full_col_count = Counter(
                TimeSeriesTransformer.get_col_internal_type(col) for col in full_col_set_minus_target)
            logger.warning(
                "Different number of columns are found in the featured cv and full datasets. "
                "The details for internal column types are as following:\n"
                "Full dataset internal column types: {}.\n"
                "CV dataset internal column types: {}\n"
                "Different internal column types are {}".format(full_col_count, cv_col_count, diff_col)
            )
        else:
            logger.info("No discrepancy are found in featured cv and full datasets.")
        Contract.assert_true(
            new_col_set_minus_target == full_col_set_minus_target,
            "Expected the joined dataframe to have the same set of columns as the full dataframe.",
            log_safe=True
        )

        # Return joined dataframe with same order as the full input set
        col_order = list(X_full.columns)
        if target_column_name in X_cv_new.columns and target_column_name not in X_full.columns:
            col_order.append(target_column_name)
        return X_cv_new[col_order]

    def __init__(
        self,
        pipeline: Pipeline,
        pipeline_type: TimeSeriesPipelineType,
        featurization_config: FeaturizationConfig,
        time_index_non_holiday_features: List[str],
        lookback_features_removed: bool,
        **kwargs: Any
    ) -> None:
        """
        Construct a TimeSeriesTransformer.

        :param pipeline_type: Type of pipeline to construct. Either Full or Reduced for CV split featurizing
        :type pipeline_type: TimeSeriesPipelineType
        :param featurization_config: The featurization config for customization.
        :type pipeline_type: FeaturizationConfig
        :param kwargs: dictionary contains metadata for TimeSeries.
                       time_column_name: The column containing dates.
                       grain_column_names: The set of columns defining the
                       multiple time series.
                       origin_column_name: latest date from which actual values
                       of all features are assumed to be known with certainty.
                       drop_column_names: The columns which will needs
                       to be removed from the data set.
                       group: the group column name.
        :type kwargs: dict
        """

        self._transforms = {}  # type: Dict[str, TransformerMixin]
        self.pipeline_type = pipeline_type  # type: TimeSeriesPipelineType

        self._max_horizon = TimeSeriesInternal.MAX_HORIZON_DEFAULT  # type: int
        # Check if TimeSeries.MAX_HORIZON is not set to TimeSeries.AUTO.
        if isinstance(kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT), int):
            self._max_horizon = kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT)

        self.use_stl = kwargs.get(TimeSeries.USE_STL,
                                  TimeSeriesInternal.USE_STL_DEFAULT)
        self.seasonality = kwargs.get(TimeSeries.SEASONALITY,
                                      TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT)
        self.force_time_index_features = kwargs.get(TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME,
                                                    TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_DEFAULT)
        self.time_index_non_holiday_features = time_index_non_holiday_features
        self._parameters = copy.deepcopy(kwargs)  # type: Dict[str, Any]
        self._lookback_features_removed = lookback_features_removed
        super().__init__()
        self.time_column_name = cast(str, kwargs[TimeSeries.TIME_COLUMN_NAME])
        grains = kwargs.get(TimeSeries.GRAIN_COLUMN_NAMES)
        if isinstance(grains, str):
            grains = [grains]
        self.grain_column_names = cast(List[str], grains)
        if self.grain_column_names is None:
            self.grain_column_names = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
        self.drop_column_names = cast(List[Any], kwargs.get(TimeSeries.DROP_COLUMN_NAMES))
        self._featurization_config = self._convert_featurization_config(featurization_config)
        if self._featurization_config.drop_columns is not None and \
                len(self._featurization_config.drop_columns) > 0:
            drop_column_names_set = set(self.drop_column_names)
            for col in self._featurization_config.drop_columns:
                if col not in drop_column_names_set:
                    self.drop_column_names.append(col)

        # Used to make data compatible with timeseries dataframe
        self.target_column_name = TimeSeriesInternal.DUMMY_TARGET_COLUMN
        self.origin_column_name = \
            kwargs.get(TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
                       TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT)
        self.dummy_grain_column = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
        self.group_column = kwargs.get(TimeSeries.GROUP_COLUMN, None)

        self.original_order_column = TimeSeriesInternal.DUMMY_ORDER_COLUMN
        self.engineered_feature_names = None  # type: Optional[List[str]]
        self._fit_column_order = []  # type: List[str]
        self._fit_column_order_no_ts_value = []  # type: List[str]
        self._engineered_feature_name_objects = {}  # type: Dict[str, Optional[Any]]
        # We keep the list of columns in case if the class is invoked without data frame.
        self._columns = None
        # For the same purpose we need to store the imputer for y values.
        self._y_imputers = {}  # type: Dict[str, TimeSeriesImputer]
        self.dict_latest_date = {}  # type: Dict[GrainType, pd.Timestamp]
        self.country_or_region = kwargs.get(TimeSeries.COUNTRY_OR_REGION, None)
        self.boolean_columns = []  # type: List[str]
        self.pipeline = pipeline  # type: Optional[Pipeline]
        freq_offset = kwargs.get(TimeSeries.FREQUENCY)  # type: Optional[Union[pd.DateOffset, str]]
        if isinstance(freq_offset, str):
            self.freq_offset = to_offset(freq_offset)
        else:
            self.freq_offset = freq_offset
        self.freq = self.freq_offset.freqstr if self.freq_offset else None  # type: Optional[str]
        self._unknown_train_part = None  # type: Optional[TimeSeriesDataFrame]
        self._known_train_part = None  # type: Optional[TimeSeriesDataFrame]
        self._in_fit_transform = False  # type: bool
        self.missing_y = self._init_missing_y()  # type: MissingDummiesTransformer
        self._target_imputation_marker_column_name = \
            MissingDummiesTransformer.get_column_name(self.target_column_name)

        # Feature flag for indicating if datetime gap filling is external with respect to the imputer
        # This flag is used to preserve compatibility between SDK releases
        self._datetime_gap_filler_external = True

        # Feature flag for indicating whether we should be keeping the missing dummies features for
        # the target column
        # This flag is used to preserve compatibility between SDK releases
        self._keep_missing_dummies_on_target = True

        # dictionary containing min/max/count/percentiles of grains. this stats is passed onto JOS
        # to determine the feasibility of DNN run along with DNN parameter choices.
        series_column_count = 1 if grains is None else len(grains)

        # Check backward compatibility with 1.25, need to remove in next release ****
        if not back_comp_raw_stats:
            self._series_stats = TimeSeriesStat(series_column_count)  # type: Optional[TimeSeriesStat]
        else:
            self._series_stats = None
        self._detected_grain_types = {}  # type: Dict[str, Any]

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = [
            _codegen_utilities.get_import(self.pipeline_type),
            _codegen_utilities.get_import(self._featurization_config)
        ]
        if self.pipeline is not None:
            imports.append(_codegen_utilities.get_import(self.pipeline))
            for step in self.pipeline.steps:
                imports.append(_codegen_utilities.get_import(step[1]))
                if hasattr(step[1], "_get_imports"):
                    imports.extend(step[1]._get_imports())
        return imports

    def get_params(self, deep=True):
        params = {
            TimeSeries.MAX_HORIZON: self._max_horizon,
            TimeSeries.USE_STL: self.use_stl,
            TimeSeries.SEASONALITY: self.seasonality,
            TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME: self.force_time_index_features,
            TimeSeries.GRAIN_COLUMN_NAMES: self.grain_column_names,
            TimeSeries.DROP_COLUMN_NAMES: self.drop_column_names,
            TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME: self.origin_column_name,
            TimeSeries.GROUP_COLUMN: self.group_column,
            TimeSeries.COUNTRY_OR_REGION: self.country_or_region,
            TimeSeries.FREQUENCY: self.freq,
            TimeSeries.TIME_COLUMN_NAME: self.time_column_name,
            "pipeline": self.pipeline,
            "pipeline_type": self.pipeline_type,
            "featurization_config": self._featurization_config,
            "time_index_non_holiday_features": self.time_index_non_holiday_features,
            "lookback_features_removed": self._lookback_features_removed
        }
        return params

    def __repr__(self):
        params = self.get_params(deep=False)
        pipeline_type = params.pop("pipeline_type")
        pipeline_type_str = "{}.{}".format(pipeline_type.__class__.__name__, pipeline_type.name)
        return _codegen_utilities.generate_repr_str(self.__class__, params, pipeline_type=pipeline_type_str)

    def __getstate__(self):
        """
        Create the dictionary of attribute of Transformer for serialization.

        :return: A dictionary of all attributes
        each incompatible attributes are separately serialized as dict so that it can be reconstructed in the
        compatible package versions.
        """

        state = self.__dict__.copy()
        # Set the incompatible attribute to None, so that the pickle won't attempt to create it while loading.
        state['_series_stats'] = None
        # Dump the incompatible object as dictionary
        state[TimeSeriesTransformer.SERIES_STATS_DICT] = self._series_stats.__dict__.copy()

        # Backwards compatibility for older SDKs that expect get_pipeline_step()
        pipeline = AzureMLForecastPipeline(self.pipeline.steps if self.pipeline else [])
        pipeline._pipeline = self.pipeline
        state["pipeline"] = pipeline
        return state

    def __setstate__(self, state):
        """
        Deserialize the TimeSeriesTransformer object from the state dict.

        :param state: a dictionary of attributes of the transformer.
        :type state: Dict[str, Any]
        """
        # Convert old AzureMLForecastPipeline to regular sklearn pipeline
        pipeline = state.get("pipeline", None)
        if pipeline is not None and isinstance(pipeline, AzureMLForecastPipeline):
            state["pipeline"] = pipeline._pipeline
        # Get the incompatible item from dict remove when 1.25 comp us no longer needed.
        series_stats_dict = state.get(TimeSeriesTransformer.SERIES_STATS_DICT, None)
        # Remove the incompatible item from state that is not part of the object.
        if TimeSeriesTransformer.SERIES_STATS_DICT in state:
            del state[TimeSeriesTransformer.SERIES_STATS_DICT]
        self.__dict__.update(state)
        self._series_stats = None

        # Non serializable attributes in prev versions. try to reconstruct.
        try:
            if series_stats_dict:
                series_stats = TimeSeriesStat(series_stats_dict.get('series_column_count', 0),
                                              series_stats_dict.get('series_count', 0),
                                              series_stats_dict.get('series_len_min', 0),
                                              series_stats_dict.get('series_len_max', 0),
                                              series_stats_dict.get('series_len_avg', 0.0),
                                              series_stats_dict.get('series_len_perc_25', 0.0),
                                              series_stats_dict.get('series_len_perc_50', 0.0),
                                              series_stats_dict.get('series_len_perc_75', 0.0))
                self._series_stats = series_stats
        except ImportError:
            pass
        except NameError:  # this exception is thrown when TimeSeriesStat is not found in the current context
            pass

    @property
    def target_imputation_marker_column_name(self) -> str:
        if hasattr(self, '_target_imputation_marker_column_name'):
            return self._target_imputation_marker_column_name
        else:
            return MissingDummiesTransformer.get_column_name(self.target_column_name)

    def _init_missing_y(self) -> MissingDummiesTransformer:
        """ Initialize missing_y column to the TimeSeriesDataFrame."""
        out = MissingDummiesTransformer(
            [self.target_column_name]
        )
        return out

    def _keep_missing_dummies_on_target_safe(self):
        return hasattr(self, '_keep_missing_dummies_on_target') and self._keep_missing_dummies_on_target

    def _create_feature_transformer_graph(self, X: pd.DataFrame,
                                          y: Optional[DataSingleColumnInputType] = None) -> None:
        """
        Create the feature transformer graph from pipeline steps.

        The transformer graph is stored as a dictionary where keys are engineered feature names
        and values are sequences of raw feature name, transform pairs.
        """
        Contract.assert_true(
            hasattr(self, 'pipeline') and getattr(self, 'pipeline') is not None,
            "Missing or null pipeline. Call fit method first to create the pipeline.",
            log_safe=True
        )

        # Convert X to a TimeSeriesDataFrame if it isn't one already
        if isinstance(X, TimeSeriesDataFrame):
            tsdf = X  # type: TimeSeriesDataFrame
        else:
            if y is None:
                Contract.assert_true(
                    self.target_column_name in X.columns,
                    "X must contain target column if y is not provided.",
                    log_safe=True
                )
            X_safe = X
            if y is not None:
                X_safe = X_safe.assign(**{self.target_column_name: y})
            if (self.dummy_grain_column in self.grain_column_names) and (self.dummy_grain_column not in X.columns):
                X_safe = X_safe.assign(**{self.dummy_grain_column: self.dummy_grain_column})

            tsdf = _create_tsdf_from_data(
                X_safe,
                time_column_name=self.time_column_name,
                origin_column_name=self.origin_column_name,
                boolean_column_names=self.boolean_columns,
                target_column_name=self.target_column_name,
                grain_column_names=self.grain_column_names
            )

        graph = defaultdict(list)  # type: DefaultDict[str, List[List[Union[str, TransformerMixin]]]]

        def append_node(feature_from: str, feature_to: str, transformer: AutoMLTransformer) -> None:
            """Append a feature transformation to a graph node."""
            if feature_to in graph:
                graph[feature_to].append([feature_from, transformer])
            else:
                if feature_from in graph:
                    # Deep copy the feature's pre transformers
                    graph[feature_to] = copy.deepcopy(graph[feature_from])
                    graph[feature_to].append([feature_from, transformer])
                else:
                    graph[feature_to] = [[feature_from, transformer]]

        # self.pipeline cannot None, because it is populated during fit.
        Contract.assert_value(self.pipeline, "self.pipeline")
        self.pipeline = cast(Pipeline, self.pipeline)

        for name, transformer in self.pipeline.steps:
            if name == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                for col in transformer.numerical_columns:
                    missing_dummy_name = MissingDummiesTransformer.get_column_name(col)
                    append_node(col, missing_dummy_name, name)
                # Also add the missing dummy column created for the target
                # The transform that makes them isn't technically in the pipeline
                if self._keep_missing_dummies_on_target_safe():
                    target_missing_dummy_name = \
                        MissingDummiesTransformer.get_column_name(tsdf.ts_value_colname)
                    append_node(tsdf.ts_value_colname, target_missing_dummy_name, name)
            elif name == TimeSeriesInternal.IMPUTE_NA_NUMERIC_DATETIME:
                for col in transformer.input_column:
                    append_node(col, col, name)
            elif name == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                for col in transformer.preview_time_feature_names(tsdf):
                    append_node(tsdf.time_colname, col, name)
            elif name == TimeSeriesInternal.MAKE_DATETIME_COLUMN_FEATURES:
                feature_dict = transformer.preview_datetime_column_feature_names()
                for raw_name in feature_dict:
                    for feature_name in feature_dict[raw_name]:
                        append_node(raw_name, feature_name, name)
            elif name == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                for col in tsdf.grain_colnames:
                    append_node(col, 'grain_' + col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                for col in transformer._categories_by_col.keys():
                    append_node(col, col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                for col in transformer._categories_by_col.keys():
                    for dst in transformer._categories_by_col[col]:
                        append_node(col, str(col) + '_' + str(dst), name)
            elif name == TimeSeriesInternal.MAX_HORIZON_FEATURIZER:
                for col in transformer.preview_column_names(tsdf):
                    append_node(tsdf.time_colname, col, name)
            elif name in [TimeSeriesInternal.LAG_LEAD_OPERATOR,
                          TimeSeriesInternal.ROLLING_WINDOW_OPERATOR]:
                for col in transformer.preview_column_names(tsdf):
                    if name == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                        features = transformer.lags_to_construct.keys()
                    else:
                        features = transformer.transform_dict.values()
                    raw_feature = tsdf.ts_value_colname
                    for feature in features:
                        if col.startswith(feature):
                            raw_feature = feature
                    append_node(raw_feature, col, name)
            elif name == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                raw_feature = tsdf.ts_value_colname
                for col in transformer.preview_column_names(tsdf):
                    append_node(raw_feature, col, name)

        self._feature_graph = graph

    def _create_feature_transformer_graph_if_not_set(self,
                                                     X: pd.DataFrame,
                                                     y: Optional[DataSingleColumnInputType] = None) -> None:
        """Create the feature transformer graph if it is not set as a TimeSeriesTranformer property."""
        if not hasattr(self, '_feature_graph'):
            self._create_feature_transformer_graph(X, y=y)

    def _get_features_by_transform(self) -> DefaultDict[str, List[str]]:
        """Get a dictionary of features indexed by TimeSeriesTransformer transform names."""
        Contract.assert_true(
            hasattr(self, '_feature_graph'),
            "TimeSeriesTransformer object does not have a feature graph.",
            log_safe=True
        )

        features_by_transform = defaultdict(list)  # type: DefaultDict[str, List[str]]

        for feature in self._feature_graph:
            # Get the last transform in the list for this feature - we assume other transforms are intermediate
            _, trans = self._feature_graph[feature][-1]
            trans_name = type(trans).__name__ if isinstance(trans, TransformerMixin) else trans
            features_by_transform[trans_name].append(feature)

        return features_by_transform

    def _generate_json_for_engineered_features(self, tsdf: TimeSeriesDataFrame) -> None:
        """
        Create the transformer json format for each engineered feature.

        :param tsdf: time series data frame
        """
        self._create_feature_transformer_graph(tsdf)

        if self.engineered_feature_names is None:
            # This can happen only if user invoked _generate_json_for_engineered_features
            # outside the transform function without setting engineered_feature_names.
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="engineered_feature_names", argument_name="engineered_feature_names",
                    reference_code=ReferenceCodes._TST_NO_ENGINEERING_FEATURE_NAMES
                )
            )

        graph = self._feature_graph
        for engineered_feature_name in self.engineered_feature_names or []:
            col_transformers = graph.get(engineered_feature_name, [])
            transformers = []  # type: List[_Transformer]
            val = ''
            for col, transformer in col_transformers:
                input_feature = col
                # for each engineered feature's transform path, only store the first transformer's
                # input which is raw feature name, other transformers' input are previous transformer
                if len(transformers) > 0:
                    input_feature = len(transformers)
                if transformer == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.ImputationMarker,
                            operator=None,
                            feature_type=FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.IMPUTE_NA_NUMERIC_DATETIME:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.Imputer,
                            operator=self._get_imputation_operator(input_feature),
                            feature_type=FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.DateTimeTransformer,
                            operator=None,
                            feature_type=FeatureType.DateTime,
                            should_output=True)
                    )
                    val = engineered_feature_name
                elif transformer == TimeSeriesInternal.MAKE_DATETIME_COLUMN_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.DateTimeTransformer,
                            operator=None,
                            feature_type=FeatureType.DateTime,
                            should_output=True)
                    )
                    val = engineered_feature_name
                elif transformer == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.GrainMarker,
                            operator=None,
                            feature_type=FeatureType.Ignore,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.LabelEncoder,
                            operator=None,
                            feature_type=FeatureType.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                    val = engineered_feature_name
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.OneHotEncoder,
                            operator=None,
                            feature_type=FeatureType.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAX_HORIZON_FEATURIZER:
                    val = engineered_feature_name
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.MaxHorizonFeaturizer,
                            operator=None,
                            feature_type=FeatureType.DateTime,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                    # engineered_feature_name of lag operation is %target_col_name%_[occurrence]_lag%size%%period"
                    # put the %size%%period% to val
                    # The "occurrence" will be present if the lag values are computed by-occurrence
                    final_suffix = engineered_feature_name.split('_')[-1]
                    val = final_suffix[3:]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.Lag,
                            operator=None,
                            feature_type=FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.ROLLING_WINDOW_OPERATOR:
                    # engineered_feature_name of rollingwindow operation is %target_col_name%_func%size%%period"
                    # put the %size%%period% to val
                    func_value = engineered_feature_name[len(col) + 1:].split("_", 2)
                    func = func_value[0]
                    val = func_value[1]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.RollingWindow,
                            operator=func,
                            feature_type=FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                    # engineered_feature_name of STL operation is %target_col_name%_seasonal"
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.STLFeaturizer,
                            operator=None,
                            feature_type=FeatureType.Numeric,
                            should_output=True)
                    )

            feature_transformers = _FeatureTransformers(transformers)
            # Create the JSON object
            transformation_json = feature_transformers.encode_transformations_from_list()
            transformation_json._set_value_tag(val)
            self._engineered_feature_name_objects[engineered_feature_name] = transformation_json

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> str:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
            whom JSON string is required
        :return: JSON string for engineered feature name
        """
        # If the JSON object is not valid, then return None
        if engineered_feature_name not in self._engineered_feature_name_objects:
            return json.dumps([])
        else:
            engineered_feature_name_json_obj = \
                cast(_FeatureTransformersAsJSONObject,
                     self._engineered_feature_name_objects[engineered_feature_name])._entire_transformation_json_data
            # Convert JSON into string and return
            return json.dumps(engineered_feature_name_json_obj)

    def get_json_strs_for_engineered_feature_names(self,
                                                   engi_feature_name_list: Optional[List[str]] = None) -> List[str]:
        """
        Return JSON string list for engineered feature names.

        :param engi_feature_name_list: Engineered feature names for
            whom JSON strings are required
        :return: JSON string list for engineered feature names
        """
        engineered_feature_names_json_str_list = []

        if engi_feature_name_list is None:
            engi_feature_name_list = self.get_engineered_feature_names()

        # Walk engineering feature name list and get the corresponding
        # JSON string
        for engineered_feature_name in cast(List[str], engi_feature_name_list):
            json_str = \
                self._get_json_str_for_engineered_feature_name(
                    engineered_feature_name)

            engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    def get_engineered_feature_names(self) -> Optional[List[str]]:
        """
        Get the transformed column names.

        :return: list of strings
        """
        return self.engineered_feature_names

    def get_featurization_summary(self, **kwargs: Any) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by TimeSeriesTransformer.
        :param kwargs:
            See below
        :Keyword Arguments:
            * is_user_friendly (``bool``) --
                If True, return individual transformer params as well,
                otherwise, only return the detailed featurization summary.
        :return: List of featurization summary for each input feature.
        """
        is_user_friendly = kwargs.get('is_user_friendly', True)
        engineered_feature_name_json_dict = {}
        distinct_feat_paths = set()
        feat_alias = 1
        alias_raw_feature_name_transformation_mapping = {}

        for feature_name, featurization_object in self._engineered_feature_name_objects.items():
            if featurization_object is None:
                # This condition is just to fix mypy errors. The typing around this object
                # should be improved.
                continue

            # Create the engineered_feature_name_json_dict. This is a mapping from engineered featured name
            # to the list of transformations used to create this feature.
            engineered_feature_name_json_dict[feature_name] = {
                "FinalTransformerName": featurization_object._entire_transformation_json_data["FinalTransformerName"],
                "Transformations": featurization_object._entire_transformation_json_data["Transformations"],
                "Value": feature_name
            }

            featurization_path = json.dumps(featurization_object._entire_transformation_json_data["Transformations"])
            # Also ensure the featurization paths are correctly configured. In the datatransformer - this is
            # mapping from monotonically increasing integer to featurization path (for instance a word
            # embedding feature would use the the same featurizer but map to a different output column). An
            # example of this in timeseries is the datatime transformer, which runs the same column through
            # a single transformer but spits out multiple columns. Unfortunately, the naming mechanism for
            # such columns, doesn't follow the same strategy as the datatransformer (naming columns based on
            # input col name, transformer, and postfix col name), so the matching infrastructure in the
            # engineered feature names code doesn't work as well for timeseries.
            if featurization_path in distinct_feat_paths:
                continue
            else:
                distinct_feat_paths.add(featurization_path)
                featurization_object._set_value_tag(None)
                alias_raw_feature_name_transformation_mapping[str(feat_alias)] = featurization_object
                feat_alias += 1

        entire_featurization_summary = _RawFeatureFeaturizationInfo.get_coalesced_raw_feature_featurization_mapping(
            alias_raw_feature_name_transformation_mapping, engineered_feature_name_json_dict)
        user_friendly_verion = []
        for featurization_summary in entire_featurization_summary:
            user_friendly_verion.append(
                featurization_summary.to_user_friendly_repr(include_transformation_params=not is_user_friendly)
            )
        return user_friendly_verion

    def _select_known_before_date(self, X: pd.DataFrame, date: pd.Timestamp,
                                  freq: pd.DateOffset) -> pd.DataFrame:
        """
        Select rows from X where all horizon dependent information is known prior to the requested date.

        This selection only makes sense for dataframes with origin times.
        """

        Contract.assert_true(
            self.origin_column_name in X.index.names,
            "X doesn't contain origin times.",
            log_safe=True
        )

        # Need some special logic for lag features. Here, the latest known date isn't necessarily the origin time.
        # Lags are defined with respect to the origin, so latest known is actually the origin + (min(lag_orders) - 1)
        latest_known_date = date
        if len(self._transforms) == 1 and TimeSeriesInternal.LAG_LEAD_OPERATOR in self._transforms:
            lag_setting = self._transforms[TimeSeriesInternal.LAG_LEAD_OPERATOR].lags_to_construct

            # Lag orders may be ints or list of ints. Get orders as a list of lists so we can safely iterate
            lag_orders_list = [[lag] if not is_iterable_but_not_string(lag) else lag for lag in lag_setting.values()]

            # minimum lag order determines the latest date we can consider
            min_lag_order = min(chain(*lag_orders_list))
            # pandas bug: https://github.com/pandas-dev/pandas/issues/33683
            # may result in weird behavior when freq * 0 is applied. For that reason,
            # only += by freq * lag if multiplier != 0.
            if min_lag_order != 1:
                latest_known_date += freq * (min_lag_order - 1)

        return X[X.index.get_level_values(self.origin_column_name) <= latest_known_date]

    def _select_latest_origin_dates(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Select rows from X with latest origin times within time-grain groups.

        Logic: Group X by time, grain -> Find latest origin in each group
        -> Return row containing latest origin for each group.
        """
        expected_lvls = [self.time_column_name] + self.grain_column_names + [self.origin_column_name]
        Contract.assert_true(
            list(X.index.names) == expected_lvls,
            "X.index doesn't contain expected levels.",
            log_safe=True
        )

        keys = [self.time_column_name] + self.grain_column_names

        def get_origin_vals(df: pd.DataFrame) -> pd.DatetimeIndex:
            return df.index.get_level_values(self.origin_column_name)

        # Pandas groupby no longer allows `by` to contain keys which are both column and index values (0.24)
        # pandas.pydata.org/pandas-docs/stable/whatsnew/v0.24.0.html#removal-of-prior-version-deprecations-changes
        # One way around this is to use the Grouper.
        groupers = []
        for key in keys:
            groupers.append(pd.Grouper(level=key))
        return (X.groupby(groupers, group_keys=False)
                .apply(lambda df: df[get_origin_vals(df) == get_origin_vals(df).max()]))

    def _handle_datetime_gaps(self, tsdf: TimeSeriesDataFrame, freq: pd.DateOffset) -> TimeSeriesDataFrame:
        if hasattr(self, '_datetime_gap_filler_external') and self._datetime_gap_filler_external:
            return cast(TimeSeriesDataFrame, tsdf.fill_datetime_gap(freq=freq))
        else:
            return tsdf

    def _fill_gaps_and_impute_target(self, tsdf: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        # Extract target column, fill datetime gaps, and impute its missing values
        target_tsdf = tsdf[[self.target_column_name]]
        target_tsdf_filled = self._handle_datetime_gaps(target_tsdf, self.freq_offset)
        target_tsdf_filled = self._impute_target_value(target_tsdf_filled)

        # Join the filled target column back into the original dataframe
        # The join will also fill the gaps in the original dataframe
        tsdf.drop(columns=[self.target_column_name], inplace=True)
        tsdf_filled = tsdf.merge(target_tsdf_filled, how='right', left_index=True, right_index=True)

        return cast(TimeSeriesDataFrame, tsdf_filled)

    def _get_fit_column_order_after_transform(self, tsdf_transformed: TimeSeriesDataFrame) -> List[str]:
        """Retrive a list of columns in a transformed DataFrame."""
        exclude_col_list = []  # type: List[str]
        if not self._keep_missing_dummies_on_target_safe():
            target_missing_dummy_name = self.target_imputation_marker_column_name
            exclude_col_list += [self.original_order_column, target_missing_dummy_name]
        fit_column_order = [nm for nm in tsdf_transformed.columns
                            if nm not in exclude_col_list]

        return cast(List[str], fit_column_order)

    def _transform_prep_common(self, df: DataInputType,
                               y: Optional[DataSingleColumnInputType] = None) -> Tuple[pd.DataFrame, bool, bool]:
        """
        Preparation steps common to transformations on training and scoring data.

        Common prep steps are as follows:
        1. Validate DataFrame input (feature matrix) type and not empty
        2. Reset the DataFrame index  - only relevant if input has a non-trivial index
        3. Add a dummy grain column if no time-series ID columns are set
        4. Append the target/y input to the DataFrame if the y input is not None

        This utility returns the prepared DataFrame and two booleans indicating if dummy grain and
        target columns, respectively, were added to the DataFrame.
        """
        Validation.validate_type(
            df, "X", pd.DataFrame, reference_code=ReferenceCodes._TST_TRANSFORM_ARG_WRONG_TYPE)
        Validation.validate_non_empty(df, "X", reference_code=ReferenceCodes._TST_TRANSFORM_ARG_WRONG_TYPE_EMP)
        self._raise_no_fit_exception_maybe(reference_code=ReferenceCodes._TST_FIT_NOT_CALLED)
        # We know that the pipeline is not None, because otherwise
        # _raise_no_fit_exception_maybe will throw the error.
        Contract.assert_value(self.pipeline, "self.pipeline")
        self.pipeline = cast(Pipeline, self.pipeline)

        df.reset_index(drop=True, inplace=True)
        has_dummy_grain = False
        if self.dummy_grain_column in self.grain_column_names:
            has_dummy_grain = True
            df[self.dummy_grain_column] = self.dummy_grain_column

        # Safely convert the column types to the ones in the training set.
        df = self._convert_grain_type_safe(df)

        if self._keep_missing_dummies_on_target_safe():
            # Add a temporary column to data that will mark which rows have been filled/imputed
            df[TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME] = 0
        else:
            # If we're not keeping the target missing value indicator, revert to old behavior
            # which is to add a column indicating row ordering
            # This column will also mark rows filled in due to gaps in the time index
            df[self.original_order_column] = df.index

        # If y is not None, append it to the input DataFrame
        appended_target = False
        if y is not None:
            try:
                df[self.target_column_name] = y
            except Exception as e:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        AutoMLInternal, error_details='Unable to append target column to input DataFrame.',
                        inner_exception=e
                    )
                )
            appended_target = True

        return df, has_dummy_grain, appended_target

    def _transform_finalize_common(self, tsdf: TimeSeriesDataFrame,
                                   transformed_data: TimeSeriesDataFrame) -> pd.DataFrame:
        """
        Finalization steps common to transformations on training and scoring data.

        Common finalization steps are as follows:
        1. Generate engineered feature graphs and JSON
        2. Convert transformed data to a plain Pandas DataFrame
        3. Remove rows with missing values that could be added by STLFeaturizer and lookback featurizers

        To preserve compatibility between SDK versions, there are additional steps activated by a feature
        flag that remove rows added by datetime gap filling, restore the row order from the input, and
        remove the missing value indicator column for the target.

        The utility returns the finalized DataFrame.
        """

        if self._keep_missing_dummies_on_target_safe():
            # Remove the imputed row marker column
            transformed_data.drop(columns=[TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME], inplace=True)
        else:
            # If we're not keeping the target missing value indicator, revert to old behavior
            # which is to drop rows that were filled in due to gaps in the time index
            # These gaps are marked by missing values in the temporary order column
            Contract.assert_true(self.original_order_column in transformed_data.columns,
                                 'transform expected order column in transformed_data',
                                 log_safe=True)
            transformed_data = transformed_data[transformed_data[self.original_order_column].notnull()]
            transformed_data.sort_values(by=[self.original_order_column], inplace=True)

            # Now drop the order column and the missing value indicator for the target
            target_missing_dummy_name = self.target_imputation_marker_column_name
            cols_to_drop = [self.original_order_column]
            if target_missing_dummy_name in transformed_data.columns:
                cols_to_drop += [target_missing_dummy_name]
            transformed_data.drop(columns=cols_to_drop, inplace=True)

        if self.engineered_feature_names is None:
            self.engineered_feature_names = transformed_data.columns.values.tolist()
            if self.target_column_name in self.engineered_feature_names:
                self.engineered_feature_names.remove(self.target_column_name)
            if TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME in self.engineered_feature_names:
                self.engineered_feature_names.remove(TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME)
            # Generate the json objects for engineered features
            self._generate_json_for_engineered_features(tsdf)

        transformed_data = pd.DataFrame(transformed_data)

        # if we have applied STL transform, we need to make sure that leading np.NaNs are removed
        # from the trend.
        # self.pipeline cannot be None, because it is populated during fit.
        # calling transform before fit will raise the error before this place.
        Contract.assert_value(self.pipeline, "self.pipeline")
        self.pipeline = cast(Pipeline, self.pipeline)  # Mypy hack

        stl = forecasting_utils.get_pipeline_step(self.pipeline, TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND)
        if stl:
            cols = stl.preview_column_names(target=self.target_column_name)
            for col in cols:
                if col.endswith(TimeSeriesInternal.STL_TREND_SUFFIX):
                    transformed_data = transformed_data[transformed_data[col].notnull()]

        # Origin columns created by look-back features could be found only in the FULL pipeline;
        if self.pipeline_type is TimeSeriesPipelineType.FULL:
            # Check if there is a by-occurrence origin column. If so, overwrite old origins
            if TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME in transformed_data.columns:
                old_idx_names = list(transformed_data.index.names)
                Contract.assert_true(self.origin_column_name in old_idx_names,
                                     'Expected transformed data to have an origin index',
                                     log_safe=True)
                transformed_data.reset_index(level=self.origin_column_name, drop=True, inplace=True)
                transformed_data.set_index(TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME,
                                           append=True, inplace=True)
                transformed_data.index.names = old_idx_names

        return transformed_data

    def _transform_training_data(self, df: DataInputType, y: DataSingleColumnInputType) -> pd.DataFrame:
        """Transform data for a training scenario."""
        Contract.assert_value(y, "y")
        Contract.assert_value(self.pipeline, "self.pipeline")
        self.pipeline = cast(Pipeline, self.pipeline)  # Mypy hack
        df, has_dummy_grain, _ = self._transform_prep_common(df, y)
        tsdf = _create_tsdf_from_data(
            df,
            time_column_name=self.time_column_name,
            origin_column_name=self.origin_column_name,
            boolean_column_names=self.boolean_columns,
            target_column_name=self.target_column_name,
            grain_column_names=self.grain_column_names
        )
        tsdf = self._fill_gaps_and_impute_target(tsdf)
        transformed_data = self.pipeline.fit_transform(tsdf)
        transformed_data = self._transform_finalize_common(tsdf, transformed_data)
        self._fit_column_order = self._get_fit_column_order_after_transform(transformed_data)
        self._fit_column_order_no_ts_value = [nm for nm in self._fit_column_order if nm != self.target_column_name]

        # Drop added columns from the input
        drop_transform_cols = [self.target_column_name]
        if has_dummy_grain:
            drop_transform_cols += [self.dummy_grain_column]
        if self._keep_missing_dummies_on_target_safe():
            drop_transform_cols += [TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME]
        else:
            drop_transform_cols += [self.original_order_column]
        df.drop(columns=drop_transform_cols, inplace=True)

        return transformed_data

    @function_debug_log_wrapped(logging.INFO)
    def fit(self,
            X: DataInputType,
            y: Optional[DataSingleColumnInputType] = None) -> 'TimeSeriesTransformer':
        """
        Fit the TimeSeriesTransformer.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: The target quantity.
        :type y: numpy.ndarray

        :return: TimeSeriesTransformer
        """
        # TimeSeriesTransformer is actually a pipeline, so "fit" really means "fit_transform"
        # but don't return the transformed data
        self.fit_transform(X, y)

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, df: DataInputType,
                  y: Optional[DataSingleColumnInputType] = None) -> pd.DataFrame:
        """
        Transform data for a scoring scenario.

        This transform has two different behaviors depending on whether y input is given -

        If y is not None, the output will contain the target quantity in the self.target_column_name
        column; this ensures that consumers of the transform can retrieve the target aligned to
        the transformed data. The transform will also fill time index gaps and impute missing target values
        when y is given. This behavior is usually best for in-sample scoring scenarios.

        If y is None, the output is just the transformed feature DataFrame and will not have time index
        gaps filled. This behavior is usually best for out-of-sample scoring scenarios.

        In either case, the output will contain the columns determined during fit/training and in the same
        order as that determined at fit/training.
        Please note that this method *does not specify* a contract for the rows of the output DataFrame.
        That is, the output may have a different number and ordering of rows than the input.

        The transform steps are:
        1. Common validation and preparation
        2. Remove rows that do not conform to the frequency determined during training
        3. If y input is given, append to the input, fill gaps and impute missing target values
        4. Infer the scoring data frequency and check that it is compatible with training frequency
        5. Call the internal pipeline's transform method
        6. Add an indicator column for missing target values
        7. Common finalization
        8. Restore column order determined during training

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: The target quantity (optional).
        :type y: numpy.ndarray

        :return: pandas.DataFrame
        """
        df, has_dummy_grain, appended_target = self._transform_prep_common(df, y)

        # Compare the input columns used during training (self.columns) and
        # during forecasting. We drop the columns, which may have generated
        # by model_wrapper or time series transformer.
        test_col_set = set(df.columns)
        test_col_set.discard(TimeSeriesInternal.DUMMY_TARGET_COLUMN)
        test_col_set.discard(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
        test_col_set.discard(TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        train_column_set = set(self.columns) if self.columns is not None else set()
        train_column_set.discard(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
        col_diff = train_column_set.difference(test_col_set)
        # If the training set contains the columns, not present in the
        # forecast set, the model will fail and here we provide the helpful
        # error message and fail the run.
        if col_diff:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesWrongTestColumnSet, target='scoring_set',
                    reference_code=ReferenceCodes._TSDF_WRONG_COLUMNS_IN_TEST,
                    train_cols=", ".join([str(col) for col in train_column_set.difference(test_col_set)])
                )
            )

        # Try to remove points from the data frame which are not aligned with
        # frequency obtained during fit time only if y was not provided only i.e. in the transform time.
        df_fixed = fix_df_frequency(
            df,
            self.time_column_name,
            self.grain_column_names,
            self.dict_latest_date,
            self.freq_offset)
        if df_fixed.shape[0] == 0:
            # We have removed all the data points, because all of them
            # were out of phase.
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesDfDatesOutOfPhase, target='scoring_set_frequency',
                    reference_code=ReferenceCodes._TSDF_FREQUENCY_OUT_OF_PHASE)
            )

        # Create a TimeSeriesDataFrame
        tsdf = _create_tsdf_from_data(
            df_fixed,
            time_column_name=self.time_column_name,
            origin_column_name=self.origin_column_name,
            boolean_column_names=self.boolean_columns,
            target_column_name=self.target_column_name if appended_target else None,
            grain_column_names=self.grain_column_names
        )

        # Try to conserve some memory
        del df_fixed

        if appended_target:
            # For in-sample scenarios, we need to fill gaps and impute missing target values
            # so that lookback featurizers will function properly
            tsdf = self._fill_gaps_and_impute_target(tsdf)
        else:
            # Need to manually add the target missing dummy column if the target wasn't appended
            # Here, we just set the missing indicator to False
            # Only add this column if doesn't already exist - some processes might add their own
            # imputation marker prior to transform e.g. ForecastPipelineWrapper
            target_missing_dummy_name = self.target_imputation_marker_column_name
            if target_missing_dummy_name not in tsdf.columns:
                not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
                not_imputed_val_type = np.dtype(type(not_imputed_val))
                tsdf[target_missing_dummy_name] = np.full(tsdf.shape[0], not_imputed_val, dtype=not_imputed_val_type)

        Contract.assert_value(self.pipeline, "self.pipeline")
        self.pipeline = cast(Pipeline, self.pipeline)  # Mypy hack
        transformed_data = self.pipeline.transform(tsdf)
        transformed_data = self._transform_finalize_common(tsdf, transformed_data)

        # Make sure that the order of columns is the same as that from fit_transform (training)
        if self.target_column_name in transformed_data.columns:
            has_fit_order = (self._fit_column_order is not None) and len(self._fit_column_order) > 0
            Contract.assert_true(has_fit_order, 'Transform expects column fit order has been set.')
            transformed_data = transformed_data[self._fit_column_order]
        else:
            # There are some situations where this list of columns can be empty
            # Namely in CV type pipelines - that's ok, so don't check the len here
            Contract.assert_value(self._fit_column_order_no_ts_value, 'has_fit_order_no_ts_value')
            transformed_data = transformed_data[self._fit_column_order_no_ts_value]

        # Remove extra columns we may have added to the input
        drop_transform_cols = []  # type: List[str]
        if has_dummy_grain:
            drop_transform_cols += [self.dummy_grain_column]
        if appended_target:
            drop_transform_cols += [self.target_column_name]
        if self._keep_missing_dummies_on_target_safe():
            drop_transform_cols += [TimeSeriesInternal.ROW_IMPUTED_COLUMN_NAME]
        else:
            drop_transform_cols += [self.original_order_column]
        if len(drop_transform_cols) > 0:
            df.drop(columns=drop_transform_cols, inplace=True)

        return transformed_data

    @function_debug_log_wrapped(logging.INFO)
    def fit_transform(self, df: DataInputType,
                      y: Optional[DataSingleColumnInputType] = None) -> pd.DataFrame:
        """
        Fit and transform data for a training scenario.

        Please note that there is *no* row data contract for the output DataFrame. That is,
        the output may have a different number and ordering of rows than the input.

        The steps here are:
        1. Fit the transformer: create the internal transform pipeline
        2. Common transform validation and preparation
        3. Fill datetime gaps and impute missing target values
        4. Call the internal pipeline's fit_transform method
        5. Common finalization
        6. Save the order of columns in the transformed data

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: The target quantity.
        :type y: numpy.ndarray

        :return: pandas.DataFrame
        """
        self._internal_fit(df, y)
        return self._transform_training_data(df, y)

    def _save_convert_grain_types(self, df: pd.DataFrame) -> None:
        """
        Detect the grain types if it is not in featurization config and save it.

        :param df: The data frame.
        """
        # Backward compatibility.
        if not hasattr(self, '_detected_grain_types'):
            self._detected_grain_types = {}
        if self.grain_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            return
        # The column may be marked as having object dtype
        # if it contains values of several different types.
        # This creates a problem of a type conversion. Here we
        # ensure that in this case all values will become strings.
        for grain in self.grain_column_names:
            if self._featurization_config.column_purposes is not None and \
                    self._featurization_config.column_purposes.get(grain) is not None:
                continue
            if df[grain].dtype == np.dtype('object') or df[grain].dtype == pd.Categorical:
                self._detected_grain_types[grain] = 'str'
            else:
                self._detected_grain_types[grain] = df[grain].dtype

    def _convert_grain_type_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Safely convert the grain type if it is possible.

        :param df: The data frame.
        """
        # Backwards compatibility.
        if not hasattr(self, '_detected_grain_types'):
            return df
        for grain in self.grain_column_names:
            if grain not in self._detected_grain_types:
                continue
            try:
                if self._detected_grain_types[grain] == 'str' and any(
                        not isinstance(val, str) for val in df[grain]):
                    warnings.warn('Mixed type time series identifiers '
                                  'were detected and were converted to string type.')
                if df[grain].dtype != self._detected_grain_types[grain]:
                    df[grain] = df[grain].astype(self._detected_grain_types[grain])
            except BaseException:
                logger.warning('The time series identifier column type conversion has failed.')
        return df

    def _internal_fit(self, df, y):
        self._columns = df.columns
        self._save_convert_grain_types(df)
        df, _, _ = self._transform_prep_common(df, y)
        tsdf = _create_tsdf_from_data(
            df,
            time_column_name=self.time_column_name,
            origin_column_name=self.origin_column_name,
            boolean_column_names=self.boolean_columns,
            target_column_name=self.target_column_name,
            grain_column_names=self.grain_column_names
        )

        # Create the imputer for y values and grain stats.
        series_count = []
        for grain, df_one in tsdf.groupby_grain():
            self.dict_latest_date[grain] = max(df_one.time_index)
            self._y_imputers[grain] = _get_target_imputer(
                self.target_column_name,
                self.freq_offset,
                self._featurization_config,
                tsdf=df_one
            )
            series_count.append(len(df_one))

        if self._series_stats:
            # Set the grain stats from the counts.
            self._series_stats.set_stats(series_count)
            # Log the series statistics for telemetry.
            logger.info(str(self._series_stats))

        # After we have got the frequency, set it to y imputers.
        for imputer in self._y_imputers.values():
            imputer.freq = self.freq_offset

        # Save the data types found in the dataset
        # TODO: save this as metadata prior to fit.
        self.detected_column_purposes = {
            FeatureType.Numeric: _get_numerical_columns(
                tsdf,
                self.target_column_name,
                self.drop_column_names,
                self._featurization_config
            ),
            FeatureType.Categorical: _get_categorical_columns(
                tsdf,
                self.target_column_name,
                self.drop_column_names,
                self._featurization_config
            ),
            FeatureType.DateTime: _get_date_columns(
                tsdf,
                self.drop_column_names,
                self._featurization_config
            )
        }  # type: Dict[str, List[str]]

    def remove_rows_with_imputed_target(self, X: pd.DataFrame, y: np.ndarray) -> Tuple[pd.DataFrame, np.ndarray]:
        Contract.assert_type(X, 'X', pd.DataFrame)
        if self.target_imputation_marker_column_name not in X.columns:
            logger.warning('Imputation marker column not found in input data, forgoing removal of imputed rows.')
            return X, y

        # Unexpected behavior could occur if the target is a column in X, we expect that it will be in the y input
        Contract.assert_true(self.target_column_name not in X.columns,
                             'Expected target column to be passed in y input, not as a column in X input.',
                             log_safe=True)
        try:
            X[self.target_column_name] = y
        except Exception as e:
            raise ValidationException._with_error(
                AzureMLError.create(
                    AutoMLInternal, error_details='Unable to append target column to input DataFrame.',
                    inner_exception=e
                )
            )

        not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
        X_sub = X[X[self.target_imputation_marker_column_name] == not_imputed_val]
        y_sub = X_sub.pop(self.target_column_name).values

        # Undo the target column append on the input
        X.drop(columns=[self.target_column_name], inplace=True)

        logger.info('Removed {} imputed rows.'.format(X.shape[0] - X_sub.shape[0]))

        return X_sub, y_sub

    def _remove_nans_from_look_back_features(
        self, X: pd.DataFrame, y: np.ndarray
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        Contract.assert_type(X, 'X', pd.DataFrame)

        # Unexpected behavior could occur if the target is a column in X, we expect that it will be in the y input
        Contract.assert_true(self.target_column_name not in X.columns,
                             'Expected target column to be passed in y input, not as a column in X input.',
                             log_safe=True)
        try:
            X[self.target_column_name] = y
        except Exception as e:
            raise ValidationException._with_error(
                AzureMLError.create(
                    AutoMLInternal, error_details='Unable to append target column to input DataFrame.',
                    inner_exception=e
                )
            )
        # remove the possible nans that brought by lags.
        # Lags could be found only in the FULL pipeline;
        # in CV reduced pipeline categorical values may have Nones in them.
        if self.pipeline_type is TimeSeriesPipelineType.FULL:
            check_columns = list(X.columns)
            check_columns.remove(self.target_column_name)
            X.dropna(axis=0, inplace=True, subset=check_columns)
        y = X.pop(self.target_column_name).values

        logger.info('Removed nans from look-back features.')

        return X, y

    def _raise_no_fit_exception_maybe(self, reference_code: str) -> None:
        """
        Raise the exception if fit was not called.

        :raises: ClientException
        """
        if not self.pipeline:
            raise ClientException.create_without_pii("Fit not called.", reference_code=reference_code)

    def _check_phase(self,
                     scoring_tsdf: TimeSeriesDataFrame,
                     scoring_freq: DateOffset,
                     freq_diff_exception: str,
                     has_pii: bool = True) -> None:
        """
        Check the phase of the data.

        If phases are different, raise the exception.
        **Note:** This method is not used anymore. It is retained for backward
        compatibility with elder models.
        :param scoring_tsdf: The time series data frame used for scoring/testing.
        :param scoring_freq: The frequency of scoring time series data frame.
        :param freq_diff_exception: The text of an exception if scores are different.
        :param has_pii: denote if the freq_diff_exception contains the PII (True by default).
        :raises: DataException
        """
        for grain, df_one in scoring_tsdf.groupby_grain():
            date_before = self.dict_latest_date.get(grain)
            if date_before is None:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesGrainAbsent, target='grain',
                                        reference_code=ReferenceCodes._TST_CHECK_PHASE_NO_GRAIN)
                )
            # Create a date grid.
            date_grid = pd.date_range(start=date_before,
                                      end=df_one.time_index.max(),
                                      freq=self.freq_offset)
        # Raise exception only if times are not align.
        # QS-JAN aligns with QS-OCT
        if any([tstamp not in date_grid for tstamp in df_one.time_index]):
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesDfDatesOutOfPhase, target='scoring_set_phase',
                    reference_code=ReferenceCodes._TST_CHECK_PHASE_FAIL)
            )

    def _encode_boolean_columns(self, tsdf: TimeSeriesDataFrame) -> None:
        """
        If the boolean columns were detected encode it as 0 and 1.

        *Note* this method modifies the data frame inplace.
        :param tsdf: The time series dataframe to be modified.

        """
        if self.boolean_columns:
            for col in self.boolean_columns:
                if col in tsdf.columns:
                    try:
                        tsdf[col] = tsdf[col].astype('float')
                    except BaseException:
                        warnings.warn('One of columns contains boolean values, '
                                      'but not all of them are able to be converted to float type.')

    def add_dummy_order_column(self, X: pd.DataFrame) -> None:
        """
        Add the dummy order column to the pandas data frame.

        :param X: The data frame which will undergo order column addition.
        """
        X.reset_index(inplace=True, drop=True)
        X[self.original_order_column] = X.index

    def get_auto_lag(self) -> Optional[List[int]]:
        """
        Return the heuristically inferred lag.

        If lags were not defined as auto, return None.
        ClientException is raised if fit was not called.
        :return: Heuristically defined target lag or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe(reference_code=ReferenceCodes._TST_AUTO_LAG_FIT_NOT_CALLED)
        lags = self.parameters.get(TimeSeriesInternal.LAGS_TO_CONSTRUCT)
        if lags is None:
            return None
        if lags.get(self.target_column_name) != [TimeSeries.AUTO]:
            return None
        return self.get_target_lags()

    def get_auto_window_size(self) -> Optional[int]:
        """
        Return the auto rolling window size.

        If rolling window was not defined as auto, return None.
        ClientException is raised if fit was not called.
        :return: Heuristically defined rolling window size or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe(reference_code=ReferenceCodes._TST_AUTO_RW_FIT_NOT_CALLED)
        rw_size = self.parameters.get(TimeSeriesInternal.WINDOW_SIZE)
        if rw_size is None or rw_size != TimeSeries.AUTO:
            return None
        return self.get_target_rolling_window_size()

    def get_auto_max_horizon(self) -> Optional[int]:
        """
        Return auto max horizon.

        If max_horizon was not defined as auto, return None.
        :return: Heuristically defined max_horizon or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe(reference_code=ReferenceCodes._TST_AUTO_MAX_HORIZON_FIT_NOT_CALLED)
        max_horizon = self.parameters.get(TimeSeries.MAX_HORIZON)  # type: Optional[int]
        if max_horizon is None or max_horizon != TimeSeries.AUTO:
            return None
        # Return learned max_horison.
        return self.max_horizon

    def _impute_target_value(self, tsdf: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """Perform the y imputation based on frequency."""
        if self._is_using_customized_target_imputer():
            target_imputer = _get_target_imputer(
                self.target_column_name,
                self.freq_offset,
                self._featurization_config,
                tsdf)
        else:
            target_imputer = _get_target_imputer(
                self.target_column_name,
                self.freq_offset,
                self._featurization_config
            )
        # Mark the places where target was null.
        if not hasattr(self, TimeSeriesTransformer.MISSING_Y):
            self.missing_y = self._init_missing_y()
        new_tsdf = self.missing_y.fit_transform(tsdf)
        return cast(TimeSeriesDataFrame, target_imputer.fit_transform(new_tsdf))

    def _is_using_customized_target_imputer(self) -> bool:
        """
        Return whether target imputer is customized.
        """
        if self._featurization_config.transformer_params is not None:
            imputer_settings = \
                self._featurization_config.transformer_params.get(SupportedTransformers.Imputer, zip([], {}))
            for cols, _ in imputer_settings:
                if self.target_column_name in cols:
                    return True
        return False

    def _get_imputation_operator(self, col: str) -> str:
        """
        Get the imputation operator based on featurization config. If nothing can be found, will return median.

        :param col: Column name.
        :return: The imputation operator string.
        """
        if not _has_valid_customized_imputer(self._featurization_config):
            return _OperatorNames.Median
        operator = _OperatorNames.Median
        for cols, params in self._featurization_config.transformer_params[SupportedTransformers.Imputer]:
            if col in cols:
                strategy = params.get(TransformerParams.Imputer.Strategy)
                mapped_operator = _TransformerOperatorMappings.Imputer.get(strategy)
                if mapped_operator is not None:
                    operator = mapped_operator
        return operator

    def _convert_featurization_config(
            self, featurization_config: Optional[Union[str, FeaturizationConfig]]
    ) -> FeaturizationConfig:
        """
        Convert the input featurization config for type checking.

        :param featurization_config: the featurization config could be None, str, FeaturizationConfig.
        :return: A FeaturizationConfig.
        """
        if featurization_config is not None and isinstance(featurization_config, FeaturizationConfig):
            return featurization_config
        else:
            return FeaturizationConfig()

    @property
    def columns(self) -> Optional[List[str]]:
        """
        Return the list of expected columns.

        :returns: The list of columns.
        :rtype: list

        """
        return self._columns

    @property
    def y_imputers(self) -> Dict[str, TimeSeriesImputer]:
        """
        Return the imputer for target column.

        :returns: imputer for target column.
        :rtype: dict

        """
        return self._y_imputers

    @property
    def max_horizon(self) -> int:
        """Return the max horizon."""
        return self._max_horizon

    def get_target_lags(self) -> List[int]:
        """Return target lags if any."""
        self._raise_no_fit_exception_maybe(ReferenceCodes._TST_GET_LAG_FIT_NOT_CALLED)
        # We know that the pipeline is not None, because we
        # explicitly check for it in _raise_no_fit_exception_maybe.
        # mypy requires for this assertion.
        pipeline = cast(Pipeline, self.pipeline)
        lag_operator = forecasting_utils.get_pipeline_step(pipeline, TimeSeriesInternal.LAG_LEAD_OPERATOR)
        if lag_operator is None:
            return [0]
        lags = lag_operator.lags_to_construct.get(self.target_column_name)
        if lags is None:
            return [0]
        else:
            if isinstance(lags, int):
                return [lags]
            return cast(List[int], lags)

    def get_target_rolling_window_size(self) -> int:
        """
        Return the size of rolling window.
        """
        self._raise_no_fit_exception_maybe(
            ReferenceCodes._TST_GET_RW_FIT_NOT_CALLED)
        # We know that the pipeline is not None, because otherwise
        # _raise_no_fit_exception_maybe will throw the error.
        # mypy do not see this assertion.
        pipeline = cast(Pipeline, self.pipeline)
        rolling_window = forecasting_utils.get_pipeline_step(pipeline, TimeSeriesInternal.ROLLING_WINDOW_OPERATOR)
        if rolling_window is None:
            return 0
        return cast(int, rolling_window.window_size)

    @property
    def parameters(self) -> Dict[str, Any]:
        """Return the parameters needed to reconstruct the time series transformer"""
        return self._parameters

    @property
    def lookback_features_removed(self) -> bool:
        """Returned true if lookback features were removed due to memory limitations."""
        return self._lookback_features_removed

    @staticmethod
    def get_col_internal_type(column_name: str) -> str:
        """
        Get the internal type of a featured column. If it is a reserved column, return the column name.
        If it is a lag/rolling window column, return corresponding types defined in the transformer class.
        If it is a user input column, return `other`.

        :param column_name: The column name.
        :return: If a column is generated by AutoML SDK, it will return the corresponding SDK type.
                 If not, it will return "other"
        """
        if column_name in TimeSeriesInternal.RESERVED_COLUMN_NAMES:
            return column_name

        for t in [LagLeadOperator, RollingWindow, MissingDummiesTransformer]:
            col_type = t.get_col_internal_type(column_name)  # type: ignore
            if col_type is not None:
                return cast(str, col_type)
        return "other"


def get_boolean_col_names(X: pd.DataFrame) -> List[str]:
    return [colname for colname in filter(
        lambda col: any(
            isinstance(val, bool) for val in X[col]),
        X.columns.values)]


def _get_date_columns(
    tsdf: TimeSeriesDataFrame,
    drop_column_names: List[str],
    featurization_config: FeaturizationConfig
) -> List[str]:
    """
    Get The date columns in the TimeseriesDataFrame.

    :param tsdf: The TimeseriesDataFrame.
    :return: A list of column names.
    """
    return _get_columns_by_type(tsdf, [np.datetime64], FeatureType.DateTime, drop_column_names, featurization_config)


def _get_numerical_columns(
    tsdf: TimeSeriesDataFrame,
    target_column_name: str,
    drop_column_names: Optional[List[str]],
    featurization_config: FeaturizationConfig
) -> List[str]:
    """
    Get The numerical columns in the TimeseriesDataFrame.

    :param tsdf: The TimeseriesDataFrame.
    :return: A list of column names.
    """
    numerical_columns = _get_columns_by_type(
        tsdf,
        [np.number],
        FeatureType.Numeric,
        drop_column_names,
        featurization_config
    )
    if target_column_name in numerical_columns:
        numerical_columns.remove(target_column_name)
    if TimeSeriesInternal.DUMMY_ORDER_COLUMN in numerical_columns:
        numerical_columns.remove(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
    return numerical_columns


def _get_categorical_columns(
    tsdf: TimeSeriesDataFrame,
    target_column_name: str,
    drop_column_names: Optional[List[str]],
    featurization_config: FeaturizationConfig
) -> List[str]:
    """
    Get the categorical columns in the TimeseriesDataFrame.

    :param tsdf: The TimeseriesDataFrame.
    :param target_column_name: The target column name
    :return: A list of column names.
    """
    categorical_columns = _get_columns_by_type(
        tsdf,
        ['object'],
        FeatureType.Categorical,
        drop_column_names,
        featurization_config
    )
    if target_column_name in categorical_columns:
        categorical_columns.remove(target_column_name)
    return categorical_columns


def _get_columns_by_type(
    tsdf: TimeSeriesDataFrame,
    selected_types: List[Any],
    selected_purpose: str,
    drop_column_names: Optional[List[str]],
    featurization_config: FeaturizationConfig
) -> List[str]:
    """
    Get the columns by column type and purpose.

    :param tsdf: The TimeSeriesDataFrame.
    :param selected_types: The selected types.
    :param selected_purpose: The selected column purpose.
    :return: A list of column names.
    """
    include_cols = _get_included_columns(tsdf, selected_purpose, featurization_config)
    exclude_cols = _get_excluded_columns(tsdf, selected_purpose, featurization_config)
    columns = [x for x in tsdf.select_dtypes(selected_types).columns
               if (x not in (drop_column_names or [])
                   and x not in exclude_cols and x not in include_cols)]
    for col in include_cols:
        # If we have dropped the column with correct purpose
        # because it does not have values, we need to exclude
        # it from the valid columns.
        if drop_column_names is None or col not in drop_column_names:
            columns.append(col)
    return columns


def _get_included_columns(
    tsdf: TimeSeriesDataFrame,
    include_purpose: str,
    featurization_config: FeaturizationConfig
) -> Set[str]:
    """
    Get the columns included by column purpose from featurization config.

    :param tsdf: The TimeSeriesDataFrame.
    :param include_purpose: the include purpose.
    :return: A set of column names.
    """
    if featurization_config.column_purposes is None:
        return set()
    return {col for col, purpose in featurization_config.column_purposes.items()
            if purpose == include_purpose and col in tsdf.columns}


def _get_excluded_columns(
    tsdf: TimeSeriesDataFrame,
    exclude_purpose: str,
    featurization_config: FeaturizationConfig
) -> Set[str]:
    """
    Get the columns exclude by column purpose from featurization config.

    :param tsdf: The TimeSeriesDataFrame.
    :param exclude_purpose: the exclude purpose.
    :return: A set of column names.
    """
    if featurization_config.column_purposes is None:
        return set()
    return {col for col, purpose in featurization_config.column_purposes.items()
            if purpose != exclude_purpose and col in tsdf.columns}


def _get_target_imputer(
    target_column_name: str,
    freq_offset: Optional[pd.DateOffset],
    featurization_config: FeaturizationConfig,
    tsdf: Optional[pd.DataFrame] = None
) -> TimeSeriesImputer:
    """
    Get target value imputer based on the featurization config.

    :param tsdf: A timeseries dataframe that contains target column for imputation.
    """
    imputer = None
    if tsdf is not None:
        imputer = _get_customized_target_imputer(tsdf, target_column_name, freq_offset, featurization_config)
    if imputer is None:
        imputer = _get_default_target_imputer(target_column_name, freq_offset)
    imputer.fit(tsdf)
    return imputer


def _get_customized_target_imputer(
    tsdf: TimeSeriesDataFrame,
    target_column_name: str,
    freq_offset: Optional[pd.DateOffset],
    featurization_config: FeaturizationConfig
) -> Optional[TimeSeriesImputer]:
    """
    Get target value imputer based on the featurization config.

    :param tsdf: A timeseries dataframe that contains target column for imputation.
    :return: Customized target imputer.
    """
    transformer_params = featurization_config.transformer_params
    if transformer_params is not None and transformer_params.get(SupportedTransformers.Imputer) is not None:
        for cols, params in transformer_params.get(SupportedTransformers.Imputer):
            if target_column_name in cols:
                strategy = params.get(TransformerParams.Imputer.Strategy)
                if strategy == TransformerParams.Imputer.Ffill:
                    return _get_default_target_imputer(target_column_name, freq_offset)
                else:
                    fill_value = _get_numerical_imputer_value(target_column_name, 0, tsdf, params)
                    imputer = TimeSeriesImputer(input_column=[target_column_name],
                                                option='fillna', value=fill_value, freq=freq_offset)
                    return imputer
    return None


def _get_default_target_imputer(
    target_column_name: str,
    freq_offset: Optional[pd.DateOffset],
    grain_df: Optional[pd.DataFrame] = None,
) -> TimeSeriesImputer:
    """
    Return the default target column imputer.

    :param grain_df: A timeseries dataframe that contains target column for imputation.
    :return: Default target timeseries imputer.
    """
    if grain_df is None:
        return TimeSeriesImputer(
            input_column=[target_column_name],
            option='fillna', method='ffill',
            freq=freq_offset)
    else:
        return TimeSeriesImputer(
            input_column=[target_column_name],
            value={target_column_name: grain_df[target_column_name].median()},
            freq=freq_offset)


def _get_numerical_imputer_value(
    col: str,
    default_value: Union[int, float],
    tsdf: TimeSeriesDataFrame,
    transformer_params: Dict[str, Any]
) -> Union[int, float]:
    """
    Get the numerical imputer value by using featurization config.

    :param col: The column name.
    :param default_value: The default value if no customized imputer is used.
    :param tsdf: The TimeSeriesDataFrame used for imputation.
    :param transformer_params: The parameters that define the transformer.
    :return: A numeric value.
    """
    strategy = transformer_params.get(TransformerParams.Imputer.Strategy)
    fill_value = transformer_params.get(TransformerParams.Imputer.FillValue)
    if strategy == TransformerParams.Imputer.Constant and fill_value is not None:
        return cast(Union[int, float], fill_value)
    elif strategy == TransformerParams.Imputer.Mean:
        return cast(Union[int, float], tsdf[col].mean())
    elif strategy == TransformerParams.Imputer.Median:
        return cast(Union[int, float], tsdf[col].median())
    elif strategy == TransformerParams.Imputer.Mode:
        return cast(Union[int, float], tsdf[col].mode()[0])
    return default_value


def _has_valid_customized_imputer(featurization_config: FeaturizationConfig) -> bool:
    """
    Check whether the featurization config has valid imputer or not.
    """
    return (
        featurization_config is not None
        and featurization_config.transformer_params is not None
        and featurization_config.transformer_params.get(SupportedTransformers.Imputer) is not None
    )
