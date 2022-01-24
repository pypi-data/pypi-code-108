# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods related to setting problem info on local & remote azure orchestrated runs."""
import json
import logging
from typing import cast, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import scipy.sparse
from azureml.core import Run

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import TimeSeries
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.data_context import TransformedDataContext
from azureml.automl.runtime.featurizer.transformer.timeseries import TimeSeriesTransformer
from azureml.automl.runtime.shared import runtime_logging_utilities
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from azureml.automl.runtime.streaming_data_context import StreamingTransformedDataContext
from azureml.train.automl import _constants_azureml

logger = logging.getLogger(__name__)


def _subsampling_recommended(num_samples, num_features):
    """
    Recommend whether subsampling should be on or off based on shape of X.

    :param num_samples: Number of samples after preprocessing.
    :type num_samples: int
    :param num_features: Number of features after preprocessing.
    :type num_features: int
    :return: Flag indicate whether subsampling is recommended for given shape of X.
    :rtype: bool
    """
    # Ideally this number should be on service side.
    # However this number is proportional to the iteration overhead.
    # Which makes this specific number SDK specific.
    # For nativeclient or miroclient, this number will be different due to smaller overhead.
    # We will leave this here for now until we have a way of incorporating
    # hardware and network numbers in our model
    return num_samples * num_features > 300000000


def _get_series_stats(transformed_data_context: TransformedDataContext) -> Dict[str, Union[int, float]]:
    """
    Get the grain count and grain length min/max
    grain stats are used by JOS in determining the DNN availability.

    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext
    :return: Dictionary with string stats label and value.
    :rtype: dict
    """
    for transformer in transformed_data_context.transformers.values():
        # Timeseries Transformer sets the grain_stats during the fit.
        if isinstance(transformer, TimeSeriesTransformer) and transformer._series_stats:
            return cast(Dict[str, Union[int, float]], transformer._series_stats.__dict__.copy())
    return {}


def set_problem_info(
    X: DataInputType,
    y: DataSingleColumnInputType,
    enable_subsampling: bool,
    enable_streaming: Optional[bool],
    current_run: Run,
    cache_store: CacheStore,
    transformed_data_context: Optional[Union[TransformedDataContext,
                                             StreamingTransformedDataContext]] = None,
    is_adb_run: bool = False,
    enable_categorical_indicators: bool = False,
) -> None:
    """
    Set statistics about user data.

    :param X: The training features to use when fitting pipelines during AutoML experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels to use when fitting pipelines during AutoML experiment.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param enable_streaming: Whether to enable streaming or not
    :type enable_streaming: bool
    :param enable_subsampling: Whether to enable subsampling or not. Pass None for auto
    :type enable_subsampling: Optional[bool[
    :param current_run: The AutoMLRun to set the info for.
    :type current_run: azureml.core.run.Run
    :param transformed_data_context: Containing X, y and other transformed data info.
    :type transformed_data_context: TransformedDataContext or StreamingTransformedDataContext
    :param is_adb_run: flag whether this is a Azure Databricks run or not.
    :type is_adb_run: bool
    :return: None
    """
    with logging_utilities.log_activity(logger, activity_name='set_problem_info'):
        run_id = current_run.id
        logger.info("Logging dataset information for {}".format(run_id))
        runtime_logging_utilities.log_data_info(data_name="X", data=X,
                                                run_id=run_id, streaming=enable_streaming)
        runtime_logging_utilities.log_data_info(data_name="y", data=y,
                                                run_id=run_id, streaming=enable_streaming)

        if enable_subsampling is None:
            enable_subsampling = _subsampling_recommended(X.shape[0], X.shape[1])
        # Set extra cols boolean to be used by JOS for dynamically blocking Arimax when
        # only univariate time series are provided.
        has_extra_col = True
        if isinstance(transformed_data_context, TransformedDataContext):
            ts_dict = transformed_data_context.timeseries_param_dict
            if ts_dict:  # if the task is forecasting task
                total_num_col = transformed_data_context.X_raw_cleaned.shape[1]
                # timeseries param dict can be None on transformed_data_context so we
                # need to make sure we access it safely.
                drop_col_name = TimeSeries.DROP_COLUMN_NAMES
                grain_col_name = TimeSeries.GRAIN_COLUMN_NAMES
                drop_col_num = len(ts_dict.get(drop_col_name)) if ts_dict.get(drop_col_name) else 0
                grain_col_num = len(ts_dict.get(grain_col_name)) if ts_dict.get(grain_col_name) else 0
                # Except time col, drop cols and grain cols, X has no extra columns
                if (total_num_col - drop_col_num - grain_col_num - 1) == 0:
                    has_extra_col = False

        problem_info_dict = {
            "dataset_num_categorical": 0,
            "is_sparse": scipy.sparse.issparse(X),
            "subsampling": enable_subsampling,
            "has_extra_col": has_extra_col
        }

        if enable_categorical_indicators and transformed_data_context:
            dataset_categoricals = transformed_data_context._get_dataset_categoricals("X")
            if dataset_categoricals:
                problem_info_dict['dataset_categoricals'] = dataset_categoricals

        if enable_streaming:
            # Subsampling is set as typically based on the data characteristics which requires
            # enumeration of data rows and cols. If subsampling is enabled, streaming is
            # explicitly disabled - see _are_inputs_conducive_for_streaming for full set of
            # features incompatible with streaming.
            Contract.assert_true(
                enable_subsampling is not True,
                "Streaming and subsampling are not compatible.",
                target="problem_info",
                log_safe=True
            )
            # Note: when using incremental learning, we are not calculating
            # some problem info properties that Miro may use for recommendation. It's uncertain at
            # this point whether these properties are needed
            problem_info_dict["dataset_features"] = X.head(1).shape[1]
        else:
            problem_info_dict["dataset_classes"] = len(np.unique(y))
            problem_info_dict["dataset_features"] = X.shape[1]
            problem_info_dict["dataset_samples"] = X.shape[0]
            if isinstance(transformed_data_context, TransformedDataContext):
                problem_info_dict['single_frequency_class_detected'] = \
                    transformed_data_context._check_if_y_label_has_single_occurrence_class()
                # add grain count and min/max size for TCN param selection.
                if transformed_data_context.transformers is not None:
                    problem_info_dict.update(_get_series_stats(transformed_data_context))

        problem_info_str = json.dumps(problem_info_dict)

        # This is required since token may expire
        if is_adb_run:
            current_run = Run.get_context()

        current_run.add_properties({
            _constants_azureml.Properties.PROBLEM_INFO: problem_info_str
        })
