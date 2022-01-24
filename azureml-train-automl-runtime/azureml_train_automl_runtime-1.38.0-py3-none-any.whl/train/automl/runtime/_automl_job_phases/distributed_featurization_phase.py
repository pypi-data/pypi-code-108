# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import random
import uuid
from typing import Dict, List, Any, Tuple, Callable, cast

import azureml.dataprep as dprep
import dask
import gc
import pandas as pd
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.core import Run
from azureml.data import TabularDataset
from azureml.train.automl import _constants_azureml
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil
from azureml.train.automl.runtime._worker_initiator import EXPERIMENT_STATE_PLUGIN
from azureml.train.automl.runtime._worker_initiator import get_worker_variables
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain, \
    _to_partitioned_dask_dataframe, _to_dask_dataframe_of_random_grains
from dask.distributed import WorkerPlugin
from dask.distributed import get_client, get_worker
from joblib import Parallel, delayed, parallel_backend

from azureml.automl.runtime import _ml_engine as ml_engine, data_context
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer import TimeSeriesPipelineType, TimeSeriesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import \
    AutoMLAggregateTransformer, distributed_timeseries_util
from azureml.automl.runtime.featurizer.transformer.timeseries. \
    forecasting_base_estimator import _GrainBasedStatefulTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries.time_index_featurizer import TimeIndexFeaturizer
from azureml.automl.runtime.shared.time_series_data_frame import construct_tsdf

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

TRANSFORM_GRAIN_PLUGIN = 'transform_grain_plugin'


class TransformGrainPlugin(WorkerPlugin):
    def __init__(self,
                 featurized_data_dir: str,
                 training_dataset: TabularDataset,
                 validation_dataset: TabularDataset,
                 ts_transformer: TimeSeriesTransformer):
        self.featurized_data_dir = featurized_data_dir
        self.training_dataset = TabularDataset._create(training_dataset._dataflow,
                                                       training_dataset._properties,
                                                       telemetry_info=training_dataset._telemetry_info)
        self.validation_dataset = TabularDataset._create(validation_dataset._dataflow,
                                                         validation_dataset._properties,
                                                         telemetry_info=validation_dataset._telemetry_info)
        self.ts_transformer = ts_transformer


class DistributedFeaturizationPhase:
    """AutoML job phase that featurizes the data."""

    @staticmethod
    def run(workspace_getter: Callable[..., Any],
            current_run: Run,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            training_dataset: TabularDataset,
            validation_dataset: TabularDataset,
            all_grain_key_values: List[Dict[str, Any]]) -> None:

        PhaseUtil.log_with_memory("Beginning distributed featurization")
        client = get_client()

        with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.FEATURIZATION
            ),
            user_facing_name=constants.TelemetryConstants.FEATURIZATION_USER_FACING
        ):
            with logging_utilities.log_activity(logger=logger, activity_name='FindingUniqueCategories'):
                categories_by_grain_cols, categories_by_non_grain_cols = _get_categories_by_columns(
                    training_dataset,
                    all_grain_key_values,
                    automl_settings.grain_column_names)

            gc.collect()
            PhaseUtil.log_with_memory("Finished FindingUniqueCategories")

            with logging_utilities.log_activity(logger=logger, activity_name='BuildPipeline'):
                ts_transformer = _build_pipeline_for_fitting(
                    training_dataset,
                    all_grain_key_values,
                    automl_settings,
                    categories_by_grain_cols,
                    categories_by_non_grain_cols
                )

            featurized_data_dir = '{}_{}_featurized_{}'.format(current_run.experiment.name,
                                                               parent_run_id,
                                                               str(uuid.uuid4()))

            transform_grain_plugin = TransformGrainPlugin(featurized_data_dir,
                                                          training_dataset,
                                                          validation_dataset,
                                                          ts_transformer)
            client.register_worker_plugin(transform_grain_plugin, TRANSFORM_GRAIN_PLUGIN)

            with logging_utilities.log_activity(logger=logger, activity_name='DistributedTransformation'):
                with parallel_backend('dask'):
                    # This will return a list of dictionaries mapping grain_col_values to dictionaries
                    # of transformer names to transformers for all stateful transformers
                    # [{grain_id: {tr_name: tr_obj}}]
                    stateful_trs_list = Parallel(n_jobs=-1)(delayed(_transform_one_grain)(
                        grain_key_values
                    ) for grain_key_values in all_grain_key_values)

            gc.collect()
            PhaseUtil.log_with_memory("Finished DistributedTransformation")

            expr_store = ExperimentStore.get_instance()
            # Reload experiment store to update its state. This is required for fetching models
            # trained on individual grains
            expr_store.unload()
            expr_store.load()

            with logging_utilities.log_activity(logger=logger, activity_name='BuildDistributedTransformer'):
                aggregate_timeseries_transformer = _build_transformer_for_all_grains(
                    training_dataset,
                    automl_settings.label_column_name,
                    automl_settings.grain_column_names,
                    all_grain_key_values,
                    ts_transformer,
                    stateful_trs_list
                )

            gc.collect()
            PhaseUtil.log_with_memory("Finished BuildDistributedTransformer")

            expr_store.transformers.set_transformers(
                {constants.Transformers.TIMESERIES_TRANSFORMER: aggregate_timeseries_transformer}
            )

            with logging_utilities.log_activity(logger=logger, activity_name='SavingFeaturizedTrainDataset'):
                expr_store.data.partitioned.save_featurized_train_dataset(
                    workspace_getter(),
                    featurized_data_dir + "/train",
                    training_dataset.partition_keys
                )

            with logging_utilities.log_activity(logger=logger, activity_name='SavingPreparedValidationDataset'):
                expr_store.data.partitioned.save_featurized_valid_dataset(
                    workspace_getter(),
                    featurized_data_dir + "/validation",
                    training_dataset.partition_keys
                )

            problem_info = expr_store.metadata.timeseries.series_stats.__dict__

            # Add placeholder problem info. This is required today by Jasmine.
            current_run.add_properties({
                _constants_azureml.Properties.PROBLEM_INFO: json.dumps(problem_info)
            })

            with logging_utilities.log_activity(logger=logger, activity_name='SavingGlobalStatistics'):
                set_global_statistics(expr_store, all_grain_key_values)

            expr_store.unload()

        PhaseUtil.log_with_memory("Ending distributed featurization")


def _transform_one_grain(grain_keys_values: Dict[str, Any]) -> Dict[str, Dict[str, _GrainBasedStatefulTransformer]]:
    worker = get_worker()
    experiment_state_plugin = worker.plugins[EXPERIMENT_STATE_PLUGIN]
    transform_grain_plugin = worker.plugins[TRANSFORM_GRAIN_PLUGIN]

    default_datastore_for_worker, workspace_for_worker, expr_store_for_worker = get_worker_variables(
        experiment_state_plugin.workspace_getter, experiment_state_plugin.parent_run_id)

    training_dataset_for_grain = _get_dataset_for_grain(grain_keys_values, transform_grain_plugin.training_dataset)
    valid_dataset_for_grain = _get_dataset_for_grain(grain_keys_values, transform_grain_plugin.validation_dataset)

    os.makedirs(transform_grain_plugin.featurized_data_dir, exist_ok=True)

    # load pandas dataframe for one grain
    train_X_grain = training_dataset_for_grain.to_pandas_dataframe()
    train_y_grain = train_X_grain.pop(experiment_state_plugin.automl_settings.label_column_name).values
    validation_X_grain = valid_dataset_for_grain.to_pandas_dataframe()
    validation_y_grain = validation_X_grain.pop(
        experiment_state_plugin.automl_settings.label_column_name).values

    # transform one grain
    train_transformed_data = transform_grain_plugin.ts_transformer.fit_transform(train_X_grain, train_y_grain)
    validation_transformed_data = transform_grain_plugin.ts_transformer.transform(
        validation_X_grain,
        validation_y_grain)

    for transformed_data, split in \
            zip([train_transformed_data, validation_transformed_data], ['train', 'validation']):
        # write one grain to local file
        # drop the grain columns since they will be part of the path and hence
        # they will be reconstructed as part of reading partitioned dataset
        transformed_data.reset_index(inplace=True)
        transformed_data.drop(columns=experiment_state_plugin.automl_settings.grain_column_names, inplace=True)
        featurized_file_name = '{}-{}.parquet'.format(split, str(uuid.uuid4()))
        featurized_file_path = '{}/{}'.format(transform_grain_plugin.featurized_data_dir, featurized_file_name)
        transformed_data.to_parquet(featurized_file_path)

        # construct the path to which data will be written to on the default blob store
        target_path_array = [transform_grain_plugin.featurized_data_dir, split]
        for val in grain_keys_values.values():
            target_path_array.append(str(val))
        target_path = '/'.join(target_path_array)

        # upload data to default store
        expr_store_for_worker.data.partitioned.write_file(featurized_file_path, target_path)
        logger.info("transformed one grain and uploaded data")

    # upload profile of the training data to cache for consumption into training
    data_profile = dprep.read_pandas_dataframe(train_transformed_data, in_memory=True).get_profile()
    expr_store_for_worker.metadata.timeseries.set_featurized_data_profile_by_grain(grain_keys_values,
                                                                                   data_profile)

    # Retrieve stateful transformers to return to the primary node for aggregation
    stateful_transformers = {}
    for step in transform_grain_plugin.ts_transformer.pipeline.steps:
        if not isinstance(step[1], _GrainBasedStatefulTransformer):
            continue
        else:
            stateful_transformers[step[0]] = step[1]

    return {distributed_timeseries_util.convert_grain_dict_to_str(grain_keys_values): stateful_transformers}


def unique_by_partition_columns(all_grain_key_values: List[Dict[str, Any]],
                                grain_col: str) -> List[Any]:
    categories_for_grain_col = set()
    for key_val in all_grain_key_values:
        categories_for_grain_col.add(key_val[grain_col])
    unique_vals = list(categories_for_grain_col)
    logger.info("Calculated uniques for one grain column")
    return unique_vals


def _get_categories_by_columns(partitioned_dataset: TabularDataset,
                               all_grain_key_values: List[Dict[str, Any]],
                               grain_column_names: List[str]) -> Tuple[Dict[str, List[Any]], Dict[str, List[Any]]]:

    categories_by_grain_cols = {col: pd.Categorical(unique_by_partition_columns(all_grain_key_values,
                                                                                col)).categories
                                for col in grain_column_names}
    PhaseUtil.log_with_memory("Calculated uniques for all grain columns")

    # randomly chose about 5 grains to find types for columns
    ddf_sampled = _to_dask_dataframe_of_random_grains(partitioned_dataset, all_grain_key_values, 5)
    categorical_cols_with_grains_cols = ddf_sampled.select_dtypes(['object', 'category', 'bool']).columns
    categorical_cols = [col for col in categorical_cols_with_grains_cols if col not in grain_column_names]
    logger.info("found {} categorical columns excluding grain columns".format(len(categorical_cols)))

    categories_by_non_grain_cols = {}
    if len(categorical_cols) > 0:
        ddf = _to_partitioned_dask_dataframe(partitioned_dataset, all_grain_key_values)
        uniques_delayed = [ddf[col].unique() for col in categorical_cols]
        uniques = dask.compute(*uniques_delayed)
        categories_by_non_grain_cols = {col: pd.Categorical(uniques).categories for col, uniques
                                        in zip(categorical_cols, uniques)}
        PhaseUtil.log_with_memory("Calculated uniques for all non grain columns")

    return categories_by_grain_cols, categories_by_non_grain_cols


def _build_pipeline_for_fitting(
    training_dataset: TabularDataset,
    all_grain_key_values: List[Dict[str, Any]],
    automl_settings: AzureAutoMLSettings,
    categories_by_grain_cols: Dict[str, List[Any]],
    categories_by_non_grain_cols: Dict[str, List[Any]]
) -> TimeSeriesTransformer:

    expr_store = ExperimentStore.get_instance()

    # We currently subsample 100 grains to handle cases of large number of time series
    # To handle case of large history in addition to large number of time series we need following 2 solutions
    # 1) limit history per time series  2) Keep a tab on memory and limit total rows to fixed count at all costs
    subsampled_grains_ddf = _to_dask_dataframe_of_random_grains(training_dataset, all_grain_key_values, 100)
    subsampled_X = subsampled_grains_ddf.compute()
    subsampled_Y = subsampled_X.pop(automl_settings.label_column_name).values

    # Disable lags and rolling windows for FTCN
    automl_settings.window_size = None
    automl_settings.lags = None

    data_context_params = data_context.DataContextParams(automl_settings)

    pipeline_type = TimeSeriesPipelineType.FULL
    ts_params = cast(Dict[str, Any], data_context_params.control_params.timeseries_param_dict)
    featurization_config = data_context_params.control_params.featurization
    # Timeseries currently doesn't reject "off" as input and currently converts "auto"/"off" to the object
    # during the featurize_data_timeseries method. Since we bypass that call and call suggest directly, we
    # need to convert from string to object here.
    if isinstance(featurization_config, str):
        featurization_config = FeaturizationConfig()

    tsdf = construct_tsdf(
        subsampled_X,
        subsampled_Y,
        data_context_params.data_params.label_column_name,  # type: ignore
        ts_params[TimeSeries.TIME_COLUMN_NAME],
        ts_params.get(TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME, TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT),
        ts_params.get(TimeSeries.GRAIN_COLUMN_NAMES, [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]),
        None  # type: ignore
    )

    # Force all TimeIndexFeaturizers to have the same feature list.
    tif = TimeIndexFeaturizer()
    ts_params[TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME] = tif.preview_time_feature_names(tsdf)

    holiday_start_time = expr_store.metadata.timeseries.global_series_start
    holiday_end_time = expr_store.metadata.timeseries.global_series_end

    featurization_config.add_transformer_params(
        "TimeIndexFeaturizer",
        [],
        {"holiday_start_time": holiday_start_time, "holiday_end_time": holiday_end_time}
    )

    (
        forecasting_pipeline,
        timeseries_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = ml_engine.suggest_featurizers_timeseries(
        subsampled_X,
        subsampled_Y,
        featurization_config,
        ts_params,
        pipeline_type,
        categories_by_grain_cols,
        categories_by_non_grain_cols
    )

    ts_transformer = TimeSeriesTransformer(
        forecasting_pipeline,
        pipeline_type,
        featurization_config,
        time_index_non_holiday_features,
        lookback_removed,
        **timeseries_param_dict
    )

    PhaseUtil.log_with_memory("Suggest featurization invoked and transformer pipeline is ready to be fit")
    return ts_transformer


def _build_transformer_for_all_grains(
    training_dataset: TabularDataset,
    label_column_name: str,
    grain_column_names: List[str],
    all_grain_key_values: List[Dict[str, Any]],
    ts_transformer_to_merge: TimeSeriesTransformer,
    stateful_trs_list: List[Dict[str, Dict[str, _GrainBasedStatefulTransformer]]]
) -> TimeSeriesTransformer:
    """
    Build a single timeseries transformer, replacing any GrainBasedStatefulTransformer with an AggregateTransformer.

    :param training_dataset: A partitioned tabular dataset used to create the TSTs for each grain.
        This is used to re-fit a single TST to capture stateless transformers.
    :param label_column_name: The label column of the dataset.
    :param grain_column_names: A list of grain column names to be used in the aggregate transformers.
    :param all_grain_key_values: A list of dictionaries mapping grain column name to grain values.
    :ts_transforer_to_merge: An unfit timeseries transformer with all transformers present.
    :param statusful_trs_list: list of dictionaries mapping grain_col_values to dictionaries
        of transformer names to transformers for all stateful transformers
        [{grain_id: {tr_name: tr_obj}}]
    """
    PhaseUtil.log_with_memory("Beginning timeseries transformer aggregation")

    # Grab a TST to bootstrap the aggregation (allowing re-use of non-stateful transformers)
    grain_key_values = all_grain_key_values[0]
    training_dataset_for_grain = _get_dataset_for_grain(grain_key_values, training_dataset)
    bootstrap_X_grain = training_dataset_for_grain.to_pandas_dataframe()
    bootstrap_y_grain = bootstrap_X_grain.pop(label_column_name).values
    ts_transformer_to_merge.fit_transform(bootstrap_X_grain, bootstrap_y_grain)

    grain_based_trs_to_combine = {}  # type: Dict[str, Dict[str, _GrainBasedStatefulTransformer]]
    for grain_to_trs_dict in stateful_trs_list:
        grain_id, transformers_dict = next(iter(grain_to_trs_dict.items()))
        for transformer_name, transformer in transformers_dict.items():
            if transformer_name in grain_based_trs_to_combine:
                grain_based_trs_to_combine[transformer_name][grain_id] = transformer
            else:
                grain_based_trs_to_combine[transformer_name] = {grain_id: transformer}

    for tr_name, tr_dict in grain_based_trs_to_combine.items():
        agg_tr = AutoMLAggregateTransformer(grain_column_names, tr_dict)
        for idx, step in enumerate(ts_transformer_to_merge.pipeline.steps):  # type: ignore
            if step[0] == tr_name:
                break
        ts_transformer_to_merge.pipeline.steps[idx] = (tr_name, agg_tr)  # type: ignore
    PhaseUtil.log_with_memory("Ending timeseries transformer aggregation")
    return ts_transformer_to_merge


def set_global_statistics(expr_store: ExperimentStore,
                          all_grain_key_values: List[Dict[str, Any]]) -> None:
    grain_count_for_profile_stat = 100
    random_grain_key_values = all_grain_key_values
    if grain_count_for_profile_stat < len(all_grain_key_values):
        random_grain_key_values = random.sample(all_grain_key_values, grain_count_for_profile_stat)

    data_profiles = [expr_store.metadata.timeseries.get_featurized_data_profile_by_grain(grain_key_values)
                     for grain_key_values in random_grain_key_values]

    # TBD: Apply appropriate logic here to decide whether log transform is required for label column
    if len(data_profiles) > grain_count_for_profile_stat:
        expr_store.metadata.timeseries.apply_log_transform_for_label = True
