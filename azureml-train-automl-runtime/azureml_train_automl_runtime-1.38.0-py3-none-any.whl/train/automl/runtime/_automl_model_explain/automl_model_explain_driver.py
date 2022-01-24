# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
from typing import List, Optional, Any

import joblib
import numpy as np
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ModelExplanationsUnsupportedForAlgorithm, ModelExplanationsDataMetadataDimensionMismatch,
    ModelExplanationsFeatureNameLengthMismatch)
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared.constants import MODEL_PATH, Transformers
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.core import Run
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_helper import (
    _automl_pick_evaluation_samples_explanations, _automl_auto_mode_get_explainer_data,
    _automl_auto_mode_get_raw_data)
from azureml.train.automl.runtime.automl_explain_utilities import (
    AutoMLExplainerSetupClass, MaximumEvaluationSamples, automl_check_model_if_explainable,
    _get_feature_map, _get_estimator_non_streaming, _automl_pick_surrogate_model_and_set_params)

from azureml.train.automl.exceptions import ConfigException

logger = logging.getLogger(__name__)


class AutoMLModelExplainDriver:
    """
    This class implements the model explain data and configuration for explaining an AutoML model.

    The functions in this class implement the setup of training data, evaluation data, class labels,
    feature names and learners for explanations. Any other AutoML model which requires a different
    implementation of the aforementioned setup can implement an inherited version of this class and
    overide the methods in this class. A new inherited class will need to override the functions
    setup_model_explain_train_data(), setup_estimator_pipeline(), setup_model_explain_metadata(),
    setup_class_labels(), setup_surrogate_model_and_params(), setup_model_explain_data() and
    should_upload_raw_dataset(). The functions log_explanation_data_stats() and
    validate_model_explain_driver() are static functions to log the explain data stats and
    validate the explain data.
    """

    def __init__(self, automl_child_run: Run,
                 max_cores_per_iteration: int,
                 top_k: Optional[int] = None,
                 num_test_data_samples: Optional[int] = MaximumEvaluationSamples):
        """
        Class for model explain configuration for AutoML models.

        :param automl_child_run: The automated ML child run.
        :type automl_child_run: azureml.core.Run
        :param max_cores_per_iteration: Number of cores configuration used for AutoML models.
        :type max_cores_per_iteration: int
        :param top_k: Number of top-k feature importance values to compute for AutoML models.
        :type top_k: int
        :param num_test_data_samples: Number of samples in evaluation set for computing explanations.
        :type num_test_data_samples: int
        """
        self._automl_explain_config_obj = AutoMLExplainerSetupClass()
        if top_k is not None:
            self._automl_explain_config_obj._top_k = top_k
        self._num_test_data_samples = num_test_data_samples
        self._automl_child_run = automl_child_run
        self._max_cores_per_iteration = max_cores_per_iteration
        self._should_upload_raw_eval_dataset = True

    def setup_model_explain_train_data(self, is_classification: bool) -> None:
        """Training/Evaluation data to explain and down-sampling if configured."""

        # Setup the training and test samples for explanations
        explainer_train_data, explainer_test_data, explainer_data_y, explainer_data_y_test = \
            _automl_auto_mode_get_explainer_data()

        # Sub-sample the validation set for the explanations
        explainer_test_data, explainer_data_y_test = _automl_pick_evaluation_samples_explanations(
            explainer_train_data, explainer_data_y, explainer_test_data, explainer_data_y_test,
            is_classification=is_classification)

        # Setup the featurized data for training the explainer
        self._automl_explain_config_obj._X_transform = explainer_train_data
        self._automl_explain_config_obj._X_test_transform = explainer_test_data
        self._automl_explain_config_obj._y = explainer_data_y
        self._automl_explain_config_obj._y_test = explainer_data_y_test

        logger.info("Preparation of training data for model explanations completed.")

        if self._should_upload_raw_eval_dataset:
            # Setup the raw data for uploading with the explanations
            raw_train_data, raw_test_data, raw_y, raw_y_test = \
                _automl_auto_mode_get_raw_data()

            # Sub-sample the raw data validation set for the explanations upload
            raw_test_data, raw_y_test = _automl_pick_evaluation_samples_explanations(
                raw_train_data, raw_y, raw_test_data, raw_y_test,
                is_classification=is_classification)
            self._automl_explain_config_obj._X_test_raw = raw_test_data
            self._automl_explain_config_obj._y_test_raw = raw_y_test

            logger.info("Preparation of raw data for model explanations completed.")

    def _rehydrate_automl_fitted_model(self) -> None:
        """Load the trained AutoML pipeline from the pickle file."""
        downloaded_model_file_name = 'model_{}.pkl'.format(self._automl_child_run.id)
        try:
            # Download the best model from the artifact store
            self._automl_child_run.download_file(
                name=MODEL_PATH, output_file_path=downloaded_model_file_name, _validate_checksum=True)

            # Load the AutoML model into memory
            self._automl_explain_config_obj._automl_pipeline = joblib.load(downloaded_model_file_name)

            logger.info("Successfully downloaded and loaded the model for explanations")
        except Exception:
            logger.error("Error downloading and loading the model")
        finally:
            try:
                # Try and remove the downloaded file
                if os.path.exists(downloaded_model_file_name):
                    os.remove(downloaded_model_file_name)
            except Exception:
                pass

    def setup_estimator_pipeline(self) -> None:
        """Estimator pipeline."""
        self._rehydrate_automl_fitted_model()
        self._automl_explain_config_obj._automl_estimator = _get_estimator_non_streaming(
            self._automl_explain_config_obj._automl_pipeline)

    def setup_model_explain_metadata(self) -> None:
        """Engineered, raw feature names and feature maps."""
        expr_store = ExperimentStore.get_instance()
        transformers = expr_store.transformers.get_transformers()
        nimbus_transformer = expr_store.transformers.get_nimbus_preprocessor()
        if nimbus_transformer is not None:
            columns = nimbus_transformer.get_engineered_feature_names()
        elif transformers.get(Transformers.TIMESERIES_TRANSFORMER) is not None:
            columns = transformers[Transformers.TIMESERIES_TRANSFORMER].get_engineered_feature_names()
        elif transformers.get(Transformers.X_TRANSFORMER) is not None:
            columns = transformers[Transformers.X_TRANSFORMER].get_engineered_feature_names()
        else:
            columns = None

        # Convert columns from type ndarray to list
        if columns is not None and isinstance(columns, np.ndarray):
            columns = columns.tolist()
        self._automl_explain_config_obj._engineered_feature_names = columns

        x_raw_column_names = expr_store.metadata.X_raw_column_names
        num_raw_features = None  # type: Optional[int]
        raw_feature_names = None  # type: Optional[List[str]]
        if x_raw_column_names is not None:
            raw_feature_names = x_raw_column_names
        else:
            num_raw_features = self._automl_explain_config_obj.X_transform.shape[1]
        self._automl_explain_config_obj._raw_feature_names = raw_feature_names
        self._automl_explain_config_obj._feature_map = \
            [_get_feature_map(fitted_model=self._automl_explain_config_obj._automl_pipeline,
                              raw_feature_names_list=raw_feature_names,
                              number_of_raw_features=num_raw_features)]

    def setup_class_labels(self) -> None:
        """Get the class labels for classification problems."""
        self._automl_explain_config_obj._classes = None

    def setup_surrogate_model_and_params(self, should_reset_index: bool = False) -> None:
        """Choose surrogate model class and its parameters."""
        self._automl_explain_config_obj._surrogate_model, self._automl_explain_config_obj._surrogate_model_params = \
            _automl_pick_surrogate_model_and_set_params(
                explainer_test_data=self._automl_explain_config_obj.X_test_transform,
                num_cpu_cores=self._max_cores_per_iteration,
                should_reset_index=should_reset_index)

    def setup_model_explain_data(self) -> None:
        """Generate the model explanations data."""
        pass

    def should_upload_raw_dataset(self) -> bool:
        """Determine whether we can upload the raw data to explanation artifacts."""
        if self._automl_explain_config_obj.X_test_raw is not None:
            num_evaluation_samples = self._automl_explain_config_obj.X_test_transform.shape[0]
            num_raw_samples = self._automl_explain_config_obj.X_test_raw.shape[0]
            if num_evaluation_samples != num_raw_samples:
                logger.debug("Number of evaluation samples {0} is not same as {1} raw samples".format(
                    num_evaluation_samples, num_raw_samples))
                return False
            else:
                return True
        return False

    @staticmethod
    def log_explanation_data_stats(automl_model_explain_driver: Any) -> None:
        """Log stats about the explanation training and evaluation samples."""
        try:
            logger.info("Dimensionality of engineered initialization samples:- {0} samples {1} features".format(
                automl_model_explain_driver._automl_explain_config_obj.X_transform.shape[0],
                automl_model_explain_driver._automl_explain_config_obj.X_transform.shape[1]))
            logger.info("Dimensionality of engineered evaluation samples:- {0} samples {1} features".format(
                automl_model_explain_driver._automl_explain_config_obj.X_test_transform.shape[0],
                automl_model_explain_driver._automl_explain_config_obj.X_test_transform.shape[1]))

            if automl_model_explain_driver._automl_explain_config_obj.X_test_raw is not None:
                logger.info("Dimensionality of raw evaluation samples:- {0} samples {1} features".format(
                    automl_model_explain_driver._automl_explain_config_obj.X_test_raw.shape[0],
                    automl_model_explain_driver._automl_explain_config_obj.X_test_raw.shape[1]))

            if automl_model_explain_driver._automl_explain_config_obj._feature_map is not None:
                logger.info(
                    "Dimensionality of feature map:- {0} raw features"
                    " {1} engineered features".format(
                        automl_model_explain_driver._automl_explain_config_obj._feature_map[0].shape[0],
                        automl_model_explain_driver._automl_explain_config_obj._feature_map[0].shape[1])
                )
            if automl_model_explain_driver._automl_explain_config_obj.engineered_feature_names is not None:
                logger.info("Number of engineered feature names are:- {}".format(
                    len(automl_model_explain_driver._automl_explain_config_obj.engineered_feature_names)
                ))
            if automl_model_explain_driver._automl_explain_config_obj.raw_feature_names is not None:
                logger.info("Number of raw feature names are:- {}".format(
                    len(automl_model_explain_driver._automl_explain_config_obj.raw_feature_names)
                ))
        except Exception:
            logger.error("Logging of explainer data stats failed")

    @staticmethod
    def validate_model_explain_driver(explain_driver: Any) -> None:
        """
        Check if the child run is explainable.

        If not throw an exception to the caller. Call the child_run.get_properties()
        to refresh the child run's run_dto by requesting to the RH service.
        """
        explain_driver._automl_child_run.get_properties()
        if not automl_check_model_if_explainable(run=explain_driver._automl_child_run,
                                                 need_refresh_run=False):
            algorithm_name = explain_driver._automl_child_run.properties.get('run_algorithm')
            ensembled_algos = explain_driver._automl_child_run.properties.get('ensembled_algorithms')
            if ensembled_algos is not None:
                algorithm_name += " ({})".format(ensembled_algos)

            logger.warning(
                AutoMLErrorStrings.MODEL_EXPLANATIONS_UNSUPPORTED_FOR_ALGORITHM.format(
                    algorithm_name=algorithm_name))

            raise ConfigException._with_error(AzureMLError.create(
                ModelExplanationsUnsupportedForAlgorithm, target="model_explainability",
                algorithm_name=algorithm_name,
                reference_code=ReferenceCodes._MODEL_EXPLAIN_UNSUPPORTED_MODELS_EXCEPTION)
            )

        # Validate the number of engineered features against the number of engineered features
        if explain_driver._automl_explain_config_obj.engineered_feature_names is not None:
            if explain_driver._automl_explain_config_obj.X_transform.shape[1] != \
                    len(explain_driver._automl_explain_config_obj.engineered_feature_names):
                logger.error(AutoMLErrorStrings.MODEL_EXPLANATIONS_DATA_METADATA_DIMENSION_MISMATCH.format(
                    number_of_features=explain_driver._automl_explain_config_obj.X_transform.shape[1],
                    number_of_feature_names=len(
                        explain_driver._automl_explain_config_obj.engineered_feature_names)))
                rc = ReferenceCodes._MODEL_EXPLAIN_TRAIN_ENGINEERED_FEATURES_AND_FEATURE_NAMES_MISMATCH_EXCEPTION
                raise DataException._with_error(AzureMLError.create(
                    ModelExplanationsDataMetadataDimensionMismatch, target="model_explainability",
                    number_of_features=explain_driver._automl_explain_config_obj.X_transform.shape[1],
                    number_of_feature_names=len(explain_driver._automl_explain_config_obj.engineered_feature_names),
                    reference_code=rc)
                )

            if explain_driver._automl_explain_config_obj.X_test_transform.shape[1] != \
                    len(explain_driver._automl_explain_config_obj.engineered_feature_names):
                logger.error(AutoMLErrorStrings.MODEL_EXPLANATIONS_DATA_METADATA_DIMENSION_MISMATCH.format(
                    number_of_features=explain_driver._automl_explain_config_obj.X_test_transform.shape[1],
                    number_of_feature_names=len(explain_driver._automl_explain_config_obj.engineered_feature_names)))
                rc = ReferenceCodes._MODEL_EXPLAIN_TEST_ENGINEERED_FEATURES_AND_FEATURE_NAMES_MISMATCH_EXCEPTION
                raise DataException._with_error(AzureMLError.create(
                    ModelExplanationsDataMetadataDimensionMismatch, target="model_explainability",
                    number_of_features=explain_driver._automl_explain_config_obj.X_test_transform.shape[1],
                    number_of_feature_names=len(explain_driver._automl_explain_config_obj.engineered_feature_names),
                    reference_code=rc)
                )
            if (explain_driver._automl_explain_config_obj.feature_map and
                    len(explain_driver._automl_explain_config_obj.engineered_feature_names) !=
                    explain_driver._automl_explain_config_obj.feature_map[0].shape[1]):
                logger.error(AutoMLErrorStrings.MODEL_EXPLANATIONS_FEATURE_NAME_LENGTH_MISMATCH.format(
                    number_of_feature_names=len(
                        explain_driver._automl_explain_config_obj.engineered_feature_names),
                    dimension_of_feature_map=explain_driver._automl_explain_config_obj.feature_map[0].shape[1]))
                rc = ReferenceCodes._MODEL_EXPLAIN_FEATURE_MAP_ENGINEERED_FEATURE_NAMES_LENGTH_MISMATCH_EXCEPTION
                raise DataException._with_error(
                    AzureMLError.create(
                        ModelExplanationsFeatureNameLengthMismatch, target="model_explainability",
                        number_of_feature_names=len(
                            explain_driver._automl_explain_config_obj.engineered_feature_names),
                        dimension_of_feature_map=explain_driver._automl_explain_config_obj.feature_map[0].shape[1],
                        reference_code=rc)
                )

        # Validate the number of raw features against the number of raw features
        if explain_driver._automl_explain_config_obj.raw_feature_names is not None:
            if explain_driver._automl_explain_config_obj.feature_map is not None and \
                len(explain_driver._automl_explain_config_obj.raw_feature_names) != \
                    explain_driver._automl_explain_config_obj.feature_map[0].shape[0]:
                logger.error(AutoMLErrorStrings.MODEL_EXPLANATIONS_FEATURE_NAME_LENGTH_MISMATCH.format(
                    number_of_feature_names=len(explain_driver._automl_explain_config_obj.raw_feature_names),
                    dimension_of_feature_map=explain_driver._automl_explain_config_obj.feature_map[0].shape[0]))
                rc = ReferenceCodes._MODEL_EXPLAIN_FEATURE_MAP_RAW_FEATURE_NAMES_LENGTH_MISMATCH_EXCEPTION
                raise DataException._with_error(
                    AzureMLError.create(
                        ModelExplanationsFeatureNameLengthMismatch, target="model_explainability",
                        number_of_feature_names=len(explain_driver._automl_explain_config_obj.raw_feature_names),
                        dimension_of_feature_map=explain_driver._automl_explain_config_obj.feature_map[0].shape[0],
                        reference_code=rc
                    )
                )

            if explain_driver._automl_explain_config_obj.X_test_raw is not None:
                if explain_driver._automl_explain_config_obj.X_test_raw.shape[1] != \
                        len(explain_driver._automl_explain_config_obj.raw_feature_names):
                    logger.error(AutoMLErrorStrings.MODEL_EXPLANATIONS_DATA_METADATA_DIMENSION_MISMATCH.format(
                        number_of_features=explain_driver._automl_explain_config_obj.X_test_raw.shape[1],
                        number_of_feature_names=len(explain_driver._automl_explain_config_obj.raw_feature_names)))
                    rc = ReferenceCodes._MODEL_EXPLAIN_TEST_RAW_FEATURES_AND_FEATURE_NAMES_MISMATCH_EXCEPTION
                    raise DataException._with_error(AzureMLError.create(
                        ModelExplanationsDataMetadataDimensionMismatch, target="model_explainability",
                        number_of_features=explain_driver._automl_explain_config_obj.X_test_raw.shape[1],
                        number_of_feature_names=len(explain_driver._automl_explain_config_obj.raw_feature_names),
                        reference_code=rc)
                    )
