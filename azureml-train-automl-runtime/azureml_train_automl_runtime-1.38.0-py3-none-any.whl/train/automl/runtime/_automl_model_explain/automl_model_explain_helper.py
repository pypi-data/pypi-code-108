# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Tuple
import logging
import time

from sklearn.model_selection import train_test_split
from nimbusml import DprepDataStream
from interpret_community.common.exception import ScenarioNotSupportedException

from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RunStatus
from azureml.interpret.mimic_wrapper import MimicWrapper
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExplainabilityPackageMissing
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from azureml.automl.runtime.training_utilities import _upgrade_sparse_matrix_type, _is_sparse_matrix_int_type
from azureml.automl.runtime.training_utilities import LargeDatasetLimit
from azureml.train.automl.exceptions import ConfigException
from azureml.train.automl.runtime.automl_explain_utilities import MaximumEvaluationSamples, NumberofBestRunRetries, \
    _get_user_friendly_surrogate_model_name
from azureml.train.automl.runtime.run import AutoMLRun


logger = logging.getLogger(__name__)


SamplingRandomState = 777


def _automl_auto_mode_get_explainer_data() -> Tuple[
    DataInputType, DataInputType,
    DataSingleColumnInputType,
    DataSingleColumnInputType
]:
    """Get X, X_valid, y, y_valid data to explain from the ExperimentStore."""
    expr_store = ExperimentStore.get_instance()
    X, y, _ = expr_store.data.materialized.get_train()
    X_valid, y_valid, _ = expr_store.data.materialized.get_valid()

    if _is_sparse_matrix_int_type(X):
        logger.info("Integer type detected for X, need to upgrade to float type")
    if _is_sparse_matrix_int_type(X_valid):
        logger.info("Integer type detected for X_valid, need to upgrade to float type")
    # If the training data is in integer format, then the data needs to reformatted into float data
    # for LightGBM surrogate model. For different types of workloads, following needs to done:-
    # 1. If this is non-preprocessing/non-timeseries experiment then copy needs to be made via this
    #    conversion.
    # 2. If this is preprocessing/timeseries, then we should read from file cache and update the type
    #    in inplace. Currently we can't. TODO: Once the training data is read from the cache, then update
    #    the code below to change the type inplace.
    explainer_data_X = _upgrade_sparse_matrix_type(X)
    explainer_data_X_valid = _upgrade_sparse_matrix_type(X_valid)
    explainer_data_y = y
    explainer_data_y_valid = y_valid
    return explainer_data_X, explainer_data_X_valid, explainer_data_y, explainer_data_y_valid


def _automl_auto_mode_get_raw_data() -> Tuple[
    DataInputType, DataInputType, DataSingleColumnInputType, DataSingleColumnInputType
]:
    """Get X, X_valid, y, y_valid raw data to upload with explanations from the ExperimentStore."""
    expr_store = ExperimentStore.get_instance()
    X_raw, y_raw, X_valid_raw, y_valid_raw = expr_store.data.materialized.get_raw()

    return X_raw, X_valid_raw, y_raw, y_valid_raw


def _automl_auto_mode_get_explainer_data_streaming() -> Tuple[
    DataInputType,
    DataInputType,
    DataSingleColumnInputType,
    DataSingleColumnInputType
]:
    """Get X, X_valid, y, y_valid lazy data to explain from the ExperimentStore."""
    expr_store = ExperimentStore.get_instance()
    X, y, _ = expr_store.data.lazy.get_train()
    X_valid, y_valid, _ = expr_store.data.lazy.get_valid()

    # Obtain a subsample of the data to pass to Azure explainability library
    # (since the library requires all data to fit in memory).
    # TODO: Right now, for classification datasets, subsampling might leave out some
    # classes. One possible fix is to subsample the data stratified by label column
    X = X.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE)
    X_valid = X_valid.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE)
    preprocessor = expr_store.transformers.get_nimbus_preprocessor()
    if preprocessor is None:
        explainer_data_X = X.to_pandas_dataframe(extended_types=False)
        explainer_data_X_valid = X_valid.to_pandas_dataframe(extended_types=False)
    else:
        logger.debug("Transforming subsampled raw X for streaming explainability")
        explainer_data_X = preprocessor.transform(DprepDataStream(X), as_csr=True)
        logger.debug("Transforming subsampled raw X_valid for streaming explainability")
        explainer_data_X_valid = preprocessor.transform(DprepDataStream(X_valid), as_csr=True)
    explainer_data_y = y.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False).values
    explainer_data_y_valid = y_valid.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False).values
    return explainer_data_X, explainer_data_X_valid, explainer_data_y, explainer_data_y_valid


def _automl_auto_mode_get_raw_data_streaming() -> Tuple[
    DataInputType,
    DataInputType,
    DataSingleColumnInputType,
    DataSingleColumnInputType
]:
    """Get X, X_valid, y, y_valid raw data to upload with explanations from the ExperimentStore."""

    expr_store = ExperimentStore.get_instance()
    X_raw_def, y_raw_def, X_valid_raw_def, y_valid_raw_def = expr_store.data.lazy.get_raw()

    X_raw = X_raw_def.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False)
    X_valid_raw = X_valid_raw_def.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False)
    y_raw = y_raw_def.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False).values
    y_valid_raw = y_valid_raw_def.take(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).to_pandas_dataframe(
        extended_types=False).values
    return X_raw, X_valid_raw, y_raw, y_valid_raw


def _automl_pick_evaluation_samples_explanations(X: DataInputType,
                                                 y: DataSingleColumnInputType,
                                                 X_valid: Optional[DataInputType] = None,
                                                 y_valid: Optional[DataSingleColumnInputType] = None,
                                                 is_classification: Optional[bool] = False) -> Tuple[
                                                     DataInputType, DataSingleColumnInputType]:
    """
    Pick subsamples of featurized data if the number of rows in featurized data is large.

    :param X: Training design matrix.
    :type X: DataInputType
    :param y: Training target column.
    :type y: DataSingleColumnInputType
    :param X_valid: Validation design matrix.
    :type X_valid: DataInputType
    :param y_valid: Validation target column.
    :type y_valid: DataSingleColumnInputType
    :param is_classification: Bool to capture if this split is needed for classification or otherwise.
    :type is_classification: bool
    :return: Sub-sample of train/validation data
    """
    X_eval = X_valid if X_valid is not None else X
    y_eval = y_valid if y_valid is not None else y

    n_samples = X_eval.shape[0]
    if n_samples <= MaximumEvaluationSamples:
        return X_eval, y_eval

    sample_fraction = 1.0 * MaximumEvaluationSamples / n_samples
    log_message_format = "Successfully downsampled the evaluation samples using {} splits"
    try:
        stratified_split = y_eval if is_classification else None
        X_eval_sampled, _, y_eval_sampled, _ = train_test_split(
            X_eval, y_eval, train_size=sample_fraction,
            random_state=SamplingRandomState,
            stratify=stratified_split)
        if stratified_split is not None:
            logger.info(log_message_format.format('stratified'))
        else:
            logger.info(log_message_format.format('random'))
    except ValueError:
        # in case stratification fails, fall back to non-stratify train/test split
        X_eval_sampled, _, y_eval_sampled, _ = train_test_split(
            X_eval, y_eval, random_state=SamplingRandomState, train_size=sample_fraction)
        logger.info(log_message_format.format('random'))

    return X_eval_sampled, y_eval_sampled


def _check_model_explain_packages() -> None:
    """Check if model explain packages are importable."""
    try:
        from interpret_community.mimic.models.lightgbm_model import LGBMExplainableModel
        from interpret_community.mimic.models.linear_model import LinearExplainableModel
        from interpret_community.common.constants import MimicSerializationConstants, ResetIndex
        from azureml.interpret.mimic_wrapper import MimicWrapper
        logger.info("All dependent explainability packages are importable")
    except ImportError as e:
        logger.warning("Package {0} not importable".format(str(e.name)))
        raise ConfigException._with_error(AzureMLError.create(
            ExplainabilityPackageMissing, target="explain_model", missing_packages=e.name,
            reference_code=ReferenceCodes._MODEL_EXPLAIN_MISSING_DEPENDENCY_EXCEPTION),
            inner_exception=e
        ) from e


def _should_query_for_best_run(parent_run: AutoMLRun) -> bool:
    """
    Check if we can query the run history to find the best run.

    :param parent_run: The automated ML parent run.
    :type parent_run: azureml.train.automl.run.AutoMLRun
    :return: bool
    """
    number_of_child_runs_in_artifacts = 0

    children = parent_run.get_children(
        _rehydrate_runs=False,
        status=RunStatus.COMPLETED,
        properties={'runTemplate': 'automl_child'})
    number_of_complete_child_runs = len(list(children))

    number_of_retries = 0
    time_to_wait = 10
    back_off_factor = 2
    while number_of_complete_child_runs > number_of_child_runs_in_artifacts:
        try:
            number_of_child_runs_in_artifacts = len(parent_run.get_metrics(recursive=True))
        except Exception:
            pass
        if number_of_retries >= NumberofBestRunRetries:
            break
        logger.info('The number of completed child runs {0} is greater than child runs in artifacts {1}'.format(
            number_of_complete_child_runs, number_of_child_runs_in_artifacts))
        time.sleep(time_to_wait)
        time_to_wait *= back_off_factor
        number_of_retries += 1

    if number_of_retries >= NumberofBestRunRetries:
        return False
    return True


def _log_blackbox_explainer_replication_measure(mimic_explainer: MimicWrapper, training_data: DataInputType,
                                                run_algorithm: Optional[str] = None) -> None:
    """Log the replication measure if we are able to compute it."""
    run_algorithm_name = run_algorithm if run_algorithm else "unknown"
    try:
        replication_score = mimic_explainer.explainer._get_surrogate_model_replication_measure(
            training_data=training_data)
        logger.info("The replication score for teacher model {0} with surrogate model {1} is:- {2}".format(
            run_algorithm_name,
            _get_user_friendly_surrogate_model_name(mimic_explainer.explainer.surrogate_model),
            replication_score))
    except Exception as e:
        error_str = None  # type: Optional[str]
        if isinstance(e, ScenarioNotSupportedException):
            error_str = str(e)
        logger.info("The replication score for teacher model {0} with surrogate model {1} could not be found. "
                    "Reason {2}".format(run_algorithm_name,
                                        _get_user_friendly_surrogate_model_name(
                                            mimic_explainer.explainer.surrogate_model),
                                        error_str))
