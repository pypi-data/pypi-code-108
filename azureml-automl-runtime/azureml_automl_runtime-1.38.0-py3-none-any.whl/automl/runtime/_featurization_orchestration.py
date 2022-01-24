# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for ochestration of featurization across AuoML Tasks."""
import logging
from typing import Any, Dict, Optional, Union, cast

from azureml.automl.core._experiment_observer import ExperimentObserver
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime import _featurization_execution_timeseries, data_transformation
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime._featurization_execution import featurize_train_valid_data
from azureml.automl.runtime.data_context import RawDataContext, TransformedDataContext
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.featurizer.transformer.featurization_utilities import skip_featurization
from azureml.automl.runtime.shared._cv_splits import _CVSplits, FeaturizedCVSplit
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.streaming_data_context import StreamingTransformedDataContext
from scipy import sparse

logger = logging.getLogger(__name__)


def orchestrate_featurization(
    enable_streaming: bool,
    is_timeseries: bool,
    path: str,
    raw_data_context: RawDataContext,
    cache_store: CacheStore,
    verifier: VerifierManager,
    experiment_observer: ExperimentObserver,
    feature_sweeping_config: Dict[str, Any],
    feature_sweeped_state_container: Optional[FeatureSweepedStateContainer]
) -> Union[TransformedDataContext, StreamingTransformedDataContext]:
    """
    Orchestrate the execution of featurization.

    This method should be called after feature sweeping has occurred. This method orchestrates
    featurization execution. This method should live in the FeaturizationPhase but due to Native Client
    limitations, functionality was moved here to support both FeaturizationPhase and Native Client.

    Orchestration here happens around the following key decisions:
    1. Task type (classification/regression/timeseries)
    2. Data type (sparse/not sparse)
    3. Data size (streaming vs. non-streaming)

    Much of these decisions are based of the presence of the feature_sweeped_state_container.

    :param enable_streaming: Whether to enable streaming
    :param is_timeseries: Whether the data is timeseries
    :param path: the path to place temporary files in
    :param raw_data_context: The raw data context to be featurized.
    :param cache_store: The location where transformed data (and other metadata) will be cached.
    :param verifier: The object used to various verifications checked during featurization.
    :param experiment_observer: The experiment observer used to track featurization status on the run.
    :param feature_sweeping_config: The feature sweeping config used for the featurization run. While
        feature sweeping has already finished, this param is optionally used during class balancing within
        featurization. An empty dictionary implies no configuration.
    :param feature_sweeped_state_container: The object which holds results from feature sweeping. This only
        applies to classification/regression when streaming is disabled and data input from user was not sparse.
    :return: The transformed data context to be used downstream in creating a client dataset.
    """
    td_ctx = None  # type: Optional[Union[TransformedDataContext, StreamingTransformedDataContext]]

    if enable_streaming:
        # Get a snapshot of the raw data (without the label column and weight column),
        # that will become the schema that is used for inferences
        columns_to_drop = []
        if raw_data_context.label_column_name is not None:
            columns_to_drop.append(raw_data_context.label_column_name)
        if raw_data_context.weight_column_name is not None:
            columns_to_drop.append(raw_data_context.weight_column_name)
        data_snapshot_str = data_transformation._get_data_snapshot(
            data=raw_data_context.training_data.drop_columns(columns=columns_to_drop)
        )

        td_ctx = data_transformation.transform_data_streaming(
            raw_data_context,
            experiment_observer
        )
        output_snapshot_str = data_transformation._get_output_snapshot(td_ctx.y)
    elif is_timeseries:
        # Timeseries doesnt currently return a feature_sweeped_state_container
        # so we need to create the tdctx (this step is also crucial for removing nan
        # rows).
        td_ctx, y_transformer, X, y = \
            data_transformation.create_transformed_data_context_no_streaming(
                raw_data_context,
                cache_store,
                verifier
            )

        # Get a snapshot of the raw data that will become the
        # schema that is used for inference.
        # In time series we have already set it.
        data_snapshot_str = td_ctx.data_snapshot_str

        td_ctx = _featurization_execution_timeseries.featurize_data_timeseries(
            raw_data_context,
            td_ctx,
            experiment_observer,
            verifier,
            y_transformer
        )
        output_snapshot_str = data_transformation._get_output_snapshot(td_ctx.y_raw_cleaned)

        # Create featurized versions of cross validations if user configuration specifies cross validations
        if td_ctx._is_autofeaturization_scenario():
            logger.info("Autofeaturization run, no data split required.")
        elif td_ctx._is_cross_validation_scenario():
            _featurization_execution_timeseries.split_and_featurize_data_timeseries(
                td_ctx,
                raw_data_context,
                X,
                y,
                td_ctx.sample_weight,
                experiment_observer
            )
    else:
        # Classification/Regression
        if feature_sweeped_state_container is None:
            # Featurization set to "off" or Sparse Data as input
            # The following cleans the data (drops NaNs etc.), logs the raw data statistics, and does class balancing
            # checks
            td_ctx, _, X, y = \
                data_transformation.create_transformed_data_context_no_streaming(
                    raw_data_context,
                    cache_store,
                    verifier
                )
            data_transformer = None
        else:
            td_ctx = feature_sweeped_state_container.transformed_data_context
            X = feature_sweeped_state_container.X
            y = feature_sweeped_state_container.y
            data_transformer = feature_sweeped_state_container.data_transformer

        # Get a snapshot of the raw data that will become the
        # schema that is used for inference
        col_names_and_types = data_transformer._columns_types_mapping if data_transformer else None
        col_purposes = data_transformer.stats_and_column_purposes if data_transformer else None
        data_snapshot_str = data_transformation._get_data_snapshot(
            data=td_ctx.X,
            column_names_and_types=col_names_and_types,
            column_purposes=col_purposes
        )
        output_snapshot_str = data_transformation._get_output_snapshot(td_ctx.y_raw_cleaned)

        # If cross validation is required, initialize the CV object.
        # If featurization is enabled, this is used to generate each featurized individual fold.
        # If featurization is disabled, this is used to initialize the expeirment store later in the code
        # flow, so that model training can fetch each individual CV fold when required.
        if td_ctx._is_autofeaturization_scenario():
            logger.info("Autofeaturization run, no data split required.")
        elif td_ctx._is_cross_validation_scenario():
            td_ctx.cv_splits = _CVSplits(
                X, y,
                frac_valid=raw_data_context.validation_size,
                CV=raw_data_context.num_cv_folds,
                n_step=raw_data_context.n_step,
                cv_splits_indices=raw_data_context.cv_splits_indices,
                is_time_series=False,
                task=raw_data_context.task_type,
            )

        x_is_sparse = sparse.issparse(td_ctx.X)
        is_featurization_required = not x_is_sparse and not skip_featurization(raw_data_context.featurization)
        if is_featurization_required:
            Contract.assert_true(
                feature_sweeped_state_container is not None,
                "'feature_sweeped_state_container' is required to featurize train-valid data for "
                "Classification and Regression tasks.")
            # Featurize the raw training data.
            # If train-valid split was available, featurize the validation data using the model learnt from above.
            # If cross validation was required, then for each of the folds, fit a new model on the training fold, and
            # featurize the validation fold.
            td_ctx = featurize_train_valid_data(
                X, y,
                raw_data_context,
                path,
                experiment_observer,
                cast(FeatureSweepedStateContainer, feature_sweeped_state_container),
                feature_sweeping_config,
                verifier)
        else:
            # If featurization is required, we featurize the CV splits and upload them to the ExpStore during
            # featurize_train_valid_data. In the case of featurization disabled, we still need to upload cv
            # splits to the ExpStore - for now we'll do that here. In the long term we should move the upload to be
            # in a single place.
            if td_ctx.cv_splits is not None:
                expr_store = ExperimentStore.get_instance()
                for i, split in enumerate(td_ctx.cv_splits.apply_CV_splits(td_ctx.X, td_ctx.y, td_ctx.sample_weight)):
                    fcvs = FeaturizedCVSplit(split[0], split[1], split[2], split[3], split[4], split[5])
                    expr_store.data.materialized.cv_splits[
                        "new_" + TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(i)
                    ] = fcvs
            logger.info("Skipping data transformations as featurization was not required or enabled.")

    td_ctx._set_raw_data_snapshot_str(data_snapshot_str)
    td_ctx._set_output_snapshot_str(output_snapshot_str)
    return td_ctx
