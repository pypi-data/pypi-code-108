from enum import Enum
import logging
from typing import Dict, List, Optional, Union

from numpy import ndarray
from pandas import DataFrame

from aporia.core.errors import AporiaError
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldCategory, FieldType
from aporia.core.utils import generate_features_schema_from_shape
from aporia.pandas.pandas_utils import infer_type_from_dtype_and_data

logger = logging.getLogger(LOGGER_NAME)


class TrainingDataset(Enum):
    """Training dataset names."""

    TRAINING = "training"
    TEST = "test"


class TrainingDataType(Enum):
    """Training data types."""

    FEATURES = "features"
    LABELS = "labels"
    PREDICTIONS = "predictions"
    RAW_INPUTS = "raw inputs"

    def to_field_category(self) -> FieldCategory:
        """Converts training data type to corresponding field category."""
        if self is TrainingDataType.FEATURES:
            return FieldCategory.FEATURES
        elif self is TrainingDataType.PREDICTIONS or self is TrainingDataType.LABELS:
            return FieldCategory.PREDICTIONS
        elif self is TrainingDataType.RAW_INPUTS:
            return FieldCategory.RAW_INPUTS

        # This is unreachable, the if-elif cluases above should cover all possible values
        raise AporiaError("Invalid training data type")


class TrainingValidator:
    """Training data validator."""

    def __init__(
        self, dataset_type: TrainingDataset, schema: Dict[FieldCategory, Dict[str, FieldType]]
    ):
        """Initializes a training validator.

        Args:
            dataset_type: Type of dataset (training or test)
            schema: Model version schema
        """
        self.dataset_type = dataset_type
        self.schema = schema

    def validate_field_category_is_in_schema(self, training_data_type: TrainingDataType):
        """Validates that a field category was defined in the model version schema.

        Args:
            training_data_type: Training data type of the dataframe that is being validated.
        """
        if training_data_type.to_field_category() not in self.schema:
            raise AporiaError(
                "Cannot report {} set {}, because it was not defined during model "
                "version creation.".format(self.dataset_type.value, training_data_type.value)
            )

    def validate_no_field_mismatch_in_category(
        self, columns: List[str], training_data_type: TrainingDataType
    ):
        """Validates that no fields (columns) are missing or undefined.

        Args:
            columns: List of columns in the dataframe.
            training_data_type: Training data type of the dataframe that is being validated.
        """
        columns_set = set(columns)
        field_category = training_data_type.to_field_category()

        # Check for missing fields
        missing_fields = self.schema[field_category].keys() - columns_set
        if len(missing_fields) > 0:
            logger.warning(
                "Detected missing {training_type} in the {dataset} data - the following "
                "{training_type} were defined during model version creation but are "
                "not present in the {dataset} data: {missing_fields}".format(
                    training_type=training_data_type.value,
                    dataset=self.dataset_type.value,
                    missing_fields=missing_fields,
                )
            )

        # Check for undefined fields
        undefined_fields = columns_set - self.schema[field_category].keys()
        if len(undefined_fields) > 0:
            logger.warning(
                "Detected undefined {training_type} in the {dataset} data - the following "
                "{training_type} were found in the {dataset} data, but were not defined "
                "during model version creation: {undefined_fields}".format(
                    training_type=training_data_type.value,
                    dataset=self.dataset_type.value,
                    undefined_fields=undefined_fields,
                )
            )

    def _validate_field_types_match_schema(self, field_category: FieldCategory, data: DataFrame):
        missing_fields = self.schema[field_category].keys() - set(data.columns)

        for field_name, field_type in self.schema[field_category].items():
            if field_name in missing_fields:
                continue

            column_data_without_nulls = data[field_name].dropna().infer_objects()
            inferred_field_type = infer_type_from_dtype_and_data(
                dtype=column_data_without_nulls.dtype, data=column_data_without_nulls  # type: ignore
            )

            # Don't verify boolean fields, since we're going to cast them anyway
            if field_type != FieldType.BOOLEAN and field_type != inferred_field_type:
                logger.warning(
                    "Detected type mismatch on field {field_name}: expected {expected_type} "
                    "type, got {actual_type}".format(
                        field_name=field_name,
                        expected_type=field_type.value,
                        actual_type=column_data_without_nulls.dtype,
                    )
                )

    def _validate_feature_count(self, features: ndarray):
        feature_count = len(generate_features_schema_from_shape(features.shape[1:]))
        expected_feature_count = len(self.schema[FieldCategory.FEATURES])
        if feature_count != expected_feature_count:
            raise AporiaError(
                f"Detected length mismatch on {self.dataset_type.value} set features ndarray, "
                f"expected {expected_feature_count}, got {feature_count}."
            )

    def validate(
        self,
        features: Union[DataFrame, ndarray],
        labels: DataFrame,
        predictions: Optional[DataFrame] = None,
        raw_inputs: Optional[DataFrame] = None,
    ):
        """Validates training dataframes.

        Args:
            features: Features dataframe or ndarray
            labels: Labels (predictions) dataframe
            predictions: Predictions dataframe
            raw_inputs: Raw inputs dataframe
        """
        tabular_features = None
        if isinstance(features, DataFrame):
            tabular_features = features
        else:
            self._validate_feature_count(features)

        for training_data_type, data in [
            (TrainingDataType.FEATURES, tabular_features),
            (TrainingDataType.LABELS, labels),
            (TrainingDataType.PREDICTIONS, predictions),
            (TrainingDataType.RAW_INPUTS, raw_inputs),
        ]:
            if data is None:
                continue

            self.validate_field_category_is_in_schema(training_data_type)
            self.validate_no_field_mismatch_in_category(
                columns=data.columns, training_data_type=training_data_type
            )
            self._validate_field_types_match_schema(
                field_category=training_data_type.to_field_category(), data=data
            )
