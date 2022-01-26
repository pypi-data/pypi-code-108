from functools import lru_cache
import logging
from typing import Dict, List, Optional, Tuple, Union

from numpy import ndarray
from pandas import DataFrame

from aporia.core.base_model import BaseModel, validate_model_ready
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldCategory, FieldType
from aporia.core.utils import generate_features_schema_from_shape
from .api.get_model_version import get_model_version
from .api.log_training import (
    FieldTrainingData,
    log_test_data,
    log_training_data,
    log_training_sample_data,
)
from .training import calculate_dataframe_training_data
from .training_validator import TrainingDataset, TrainingValidator

logger = logging.getLogger(LOGGER_NAME)


SAMPLE_SIZE = 1000


class TrainingModel(BaseModel):
    """Model object for logging training events."""

    def __init__(self, model_id: str, model_version: str):
        """Initializes a TrainingModel object.

        Args:
            model_id: Model identifier, as received from the Aporia dashboard.
            model_version: Model version - this can be any string that represents the model
                version, such as "v1" or a git commit hash.
        """
        super().__init__(model_id=model_id, model_version=model_version, set_ready_when_done=True)

    @validate_model_ready
    def log_training_set(
        self,
        features: Union[DataFrame, ndarray],
        labels: DataFrame,
        raw_inputs: Optional[DataFrame] = None,
    ):
        """See aporia.model.Model."""
        logger.debug("Logging training set.")
        with self.handle_error("Logging training set failed, error: {}"):
            version_schema = self.get_version_schema()
            validator = TrainingValidator(
                dataset_type=TrainingDataset.TRAINING, schema=version_schema
            )
            validator.validate(features=features, labels=labels, raw_inputs=raw_inputs)

            raw_inputs_training_data = None
            if raw_inputs is not None:
                raw_inputs_training_data = calculate_dataframe_training_data(
                    raw_inputs, version_schema[FieldCategory.RAW_INPUTS]
                )

            if isinstance(features, DataFrame):
                features_dataframe = features
                features_schema = version_schema[FieldCategory.FEATURES]
            else:
                features_dataframe, features_schema = self._build_features_dataframe_and_schema(
                    features=features
                )

            self.log_training_sample(features=features_dataframe, labels=labels)
            self.log_training_set_aggregations(
                features=calculate_dataframe_training_data(features_dataframe, features_schema),
                labels=calculate_dataframe_training_data(
                    labels, version_schema[FieldCategory.PREDICTIONS]
                ),
                raw_inputs=raw_inputs_training_data,
            )

    @validate_model_ready
    def log_test_set(
        self,
        features: Union[DataFrame, ndarray],
        predictions: DataFrame,
        labels: DataFrame,
        raw_inputs: Optional[DataFrame] = None,
        confidences: Optional[ndarray] = None,
    ):
        """See aporia.model.Model."""
        logger.debug("Logging test set.")
        with self.handle_error("Logging test set failed, error: {}"):
            version_schema = self.get_version_schema()
            validator = TrainingValidator(dataset_type=TrainingDataset.TEST, schema=version_schema)
            validator.validate(
                features=features, labels=labels, predictions=predictions, raw_inputs=raw_inputs
            )

            raw_inputs_training_data = None
            if raw_inputs is not None:
                raw_inputs_training_data = calculate_dataframe_training_data(
                    raw_inputs, version_schema[FieldCategory.RAW_INPUTS]
                )

            if isinstance(features, DataFrame):
                features_dataframe = features
                features_schema = version_schema[FieldCategory.FEATURES]
            else:
                features_dataframe, features_schema = self._build_features_dataframe_and_schema(
                    features=features
                )

            self.log_test_set_aggregations(
                features=calculate_dataframe_training_data(features_dataframe, features_schema),
                predictions=calculate_dataframe_training_data(
                    predictions, version_schema[FieldCategory.PREDICTIONS]
                ),
                labels=calculate_dataframe_training_data(
                    labels, version_schema[FieldCategory.PREDICTIONS]
                ),
                raw_inputs=raw_inputs_training_data,
            )

    @validate_model_ready
    def log_training_set_aggregations(
        self,
        features: List[FieldTrainingData],
        labels: List[FieldTrainingData],
        raw_inputs: Optional[List[FieldTrainingData]] = None,
    ):
        """Logs training set training aggregations.

        Args:
            features: Feature field aggregations
            labels: Label (prediction) field aggregations
            raw_inputs: Raw Inputs aggregations
        """
        self._event_loop.run_coroutine(
            log_training_data(
                http_client=self._http_client,
                model_id=self.model_id,
                model_version=self.model_version,
                features=features,
                labels=labels,
                raw_inputs=raw_inputs,
            )
        )

    @validate_model_ready
    def log_test_set_aggregations(
        self,
        features: List[FieldTrainingData],
        predictions: List[FieldTrainingData],
        labels: List[FieldTrainingData],
        raw_inputs: Optional[List[FieldTrainingData]] = None,
    ):
        """Logs test set training aggregations.

        Args:
            features: Feature field aggregations
            predictions: Prediction field aggregations
            labels: Label (prediction) field aggregations
            raw_inputs: Raw Inputs aggregations
        """
        self._event_loop.run_coroutine(
            log_test_data(
                http_client=self._http_client,
                model_id=self.model_id,
                model_version=self.model_version,
                features=features,
                predictions=predictions,
                labels=labels,
                raw_inputs=raw_inputs,
            )
        )

    @validate_model_ready
    def log_training_sample(
        self,
        features: Union[DataFrame, ndarray],
        labels: DataFrame,
    ):
        """Logs training sample.

        Args:
            features: Training set features
            labels: Training set labels

        Notes:
            * As this is a sample for analytical purpose, we log a maximum of 1000 rows.
        """
        if isinstance(features, ndarray):
            features, _ = self._build_features_dataframe_and_schema(features)

        features_sample = features.sample(min(SAMPLE_SIZE, len(features)))
        labels_sample = labels.sample(min(SAMPLE_SIZE, len(labels)))

        self._event_loop.run_coroutine(
            log_training_sample_data(
                http_client=self._http_client,
                model_id=self.model_id,
                model_version=self.model_version,
                features=features_sample.to_dict("records"),
                labels=labels_sample.to_dict("records"),
            )
        )

    @lru_cache(maxsize=1)
    @validate_model_ready
    def get_version_schema(self) -> Dict[FieldCategory, Dict[str, FieldType]]:
        """Fetches the schema of this model version.

        Returns:
            Model version schema
        """
        return self._event_loop.run_coroutine(
            get_model_version(
                http_client=self._http_client,
                model_id=self.model_id,
                model_version=self.model_version,
            )
        )

    @staticmethod
    def _build_features_dataframe_and_schema(
        features: ndarray,
    ) -> Tuple[DataFrame, Dict[str, FieldType]]:
        features_schema = generate_features_schema_from_shape(features.shape[1:])
        for feature_name in features_schema:
            features_schema[feature_name] = FieldType(features_schema[feature_name])

        flattened_data = features.reshape(features.shape[0], len(features_schema))
        features_dataframe = DataFrame(
            data=flattened_data, columns=list(features_schema.keys()), copy=False
        )

        return features_dataframe, features_schema
