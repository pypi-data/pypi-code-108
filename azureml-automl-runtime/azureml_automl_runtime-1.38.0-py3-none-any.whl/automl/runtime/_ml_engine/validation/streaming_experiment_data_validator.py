# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Optional, Tuple, cast

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.runtime.dataprep_utilities import materialize_dataflow

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.constants import FeaturizationConfigMode
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InconsistentColumnTypeInTrainValid, \
    MissingColumnsInData
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime import dataprep_utilities
from azureml.automl.runtime._runtime_params import ExperimentDataSettings
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime._ml_engine.validation import MaterializedTabularDataValidator, \
    RawExperimentDataValidator, RawExperimentDataValidatorSettings
from azureml.automl.runtime._ml_engine.validation.streaming_tabular_data_validator import StreamingTabularDataValidator
from azureml.dataprep import Dataflow, DataPrepException

logger = logging.getLogger(__name__)


class StreamingExperimentDataValidator(RawExperimentDataValidator):
    """
    RawExperimentData validations for large data.

    Metadata checks (such as verifying the feature datatypes) are done on the original training / validation datasets,
    while the other checks (common to regular AutoML sklearn transformers/learners) are done on a sub-sampled
    version of the dataset.
    """

    def __init__(self, validation_settings: RawExperimentDataValidatorSettings, data_settings: ExperimentDataSettings):
        super(StreamingExperimentDataValidator, self).__init__(validation_settings)
        self.label_column_name = data_settings.label_column_name
        self.weight_column_name = data_settings.weight_column_name
        self.validation_size = data_settings.validation_size

    # override
    def validate_raw_experiment_data(self, raw_experiment_data: RawExperimentData) -> None:
        """
        Given raw experiment data, check if it is valid to run through the featurization and model training pipelines

        :param raw_experiment_data: RawExperimentData, as provided by the user
        :return: None
        :raises: DataException, ValidationException
        """
        training_data = raw_experiment_data.training_data
        validation_data = raw_experiment_data.validation_data

        # Subsample and materialize the data to feed into data validations
        X, y, weights, X_valid, y_valid, weights_valid = self._get_subsampled_data(training_data, validation_data)

        # Create a raw experiment data with the sub-sampled dataset
        raw_experiment_data_internal = RawExperimentData(
            X=X,
            y=y,
            weights=weights,
            X_valid=X_valid,
            y_valid=y_valid,
            weights_valid=weights_valid,
            target_column_name=self.label_column_name,
            weight_column_name=self.weight_column_name,
            validation_size=self.validation_size,
            n_cross_validations=self._validation_settings.n_cross_validations,
        )

        # call into the common data validations for regression + classification
        super().validate_raw_experiment_data(raw_experiment_data_internal)

    # override
    def get_tabular_data_validator(self) -> MaterializedTabularDataValidator:
        """Return a custom streaming tabular data validator"""
        control_settings = self._validation_settings.control_settings
        return StreamingTabularDataValidator(
            task_type=control_settings.task_type,
            primary_metric=control_settings.primary_metric,
            is_featurization_required=control_settings.featurization != FeaturizationConfigMode.Off
        )

    def _get_subsampled_data(
        self, training_data: Dataflow, validation_data: Optional[Dataflow] = None
    ) -> Tuple[
        pd.DataFrame,
        np.ndarray,
        Optional[np.ndarray],
        Optional[pd.DataFrame],
        Optional[np.ndarray],
        Optional[np.ndarray],
    ]:
        """
        If streaming is enabled, we do a best effort based validation of the inputs (due to potentially large data
        sizes), in order to not run out of memory.

        Sub-sampling the input Dataflows to numpy arrays this allows the validation flow (which
        can handle numpy arrays but not Dataflows directly at the moment) to proceed.

        :param training_data: The input Dataset containing training columns + target column
        :param automl_settings: AutoMLBaseSettings for this dataset
        :param validation_data: An optional validation dataset with the same schema as training_data
        :return: A materialized tuple of:
            X (pd.DataFrame), y (np.ndarray), weights (np.ndarray),
            X_valid (pd.DataFrame), y_valid (np.ndarray), weights (np.ndarray)
        """
        # TODO: move to StreamingTabularDataValidator
        Validation.validate_value(
            training_data, "training_data", reference_code=ReferenceCodes._STREAMING_MISSING_TRAINING_DATA
        )
        Validation.validate_type(training_data, "training_data", expected_types=Dataflow)
        Validation.validate_value(self.label_column_name, "label_column_name")
        Validation.validate_type(self.label_column_name, "label_column_name", expected_types=str)

        try:
            X, y, sample_weight = self._materialize_data_for_validation(training_data, "training_data")

            X_valid = None  # type: Optional[pd.DataFrame]
            y_valid = None  # type: Optional[np.ndarray]
            sample_weight_valid = None  # type: Optional[np.ndarray]

            # validate that the Datatypes are the same for X and y (for training, validation and sample weight data)
            if validation_data is not None:
                Validation.validate_type(validation_data, "validation_data", expected_types=Dataflow)
                self._check_train_valid_datatypes(training_data, validation_data)

                # Don't set X_valid / y_valid in case the user specified validation_size, since in this case the
                # validation data is just a part of the overall training data.
                if self.validation_size == 0:
                    X_valid, y_valid, sample_weight_valid = self._materialize_data_for_validation(validation_data,
                                                                                                  "validation_data")

            return X, y, sample_weight, X_valid, y_valid, sample_weight_valid
        except DataPrepException as e:
            logging_utilities.log_traceback(e, logger)
            dataprep_utilities.dataprep_error_handler(e)

    def _materialize_data_for_validation(
        self, dataset: Dataflow, data_name: str
    ) -> Tuple[pd.DataFrame, np.ndarray, Optional[np.ndarray]]:
        """
        Pulls and loads a fixed number of records from the Dataflow into an in-memory pandas DataFrame, and separates
        the training and target (or weights) features (i.e. X, y, weights)

        For cases when data is remote and potentially large (e.g., streaming scenario), this method will only load a
        fixed (usually small) number of records and materialize them into an appropriate format for each of the
        components of the data. X is returned as a pandas DataFrame, while y and weights are returned as a numpy array.

        :param dataset: Pointer to the data
        :param count: The number of records to fetch and load in-memory
        :return: A tuple of
            X (training data, pd.DataFrame), y (target column, np.ndarray), weights (weights column, np.ndarray)
        """
        # TODO: Move this constant out of training_utilities
        from azureml.automl.runtime.training_utilities import LargeDatasetLimit
        count = LargeDatasetLimit.VALIDATION_SUBSAMPLE_SIZE

        non_training_columns = [self.label_column_name]
        if self.weight_column_name:
            non_training_columns.append(self.weight_column_name)

        dataflow_X = dataset.drop_columns(non_training_columns)
        dataflow_y = dataset.keep_columns(self.label_column_name)
        dataflow_weights = dataset.keep_columns(self.weight_column_name) if self.weight_column_name else None

        materialized_X = materialize_dataflow(dataflow_X.take(count))

        if len(dataflow_y.head(1).columns) != 1:
            raise DataException._with_error(AzureMLError.create(
                MissingColumnsInData, target="label_column_name", data_object_name=data_name,
                columns="{} (label_column_name)".format(self.label_column_name),
                reference_code=ReferenceCodes._STREAMING_DATA_VALIDATOR_LABEL_MISSING)
            )
        materialized_y = materialize_dataflow(dataflow_y.take(count), as_numpy=True)

        materialized_weights = None  # type: Optional[np.ndarray]
        if dataflow_weights:
            if len(dataflow_weights.head(1).columns) != 1:
                raise DataException._with_error(AzureMLError.create(
                    MissingColumnsInData, target="weight_column_name", data_object_name=data_name,
                    columns="{} (weight_column_name)".format(self.weight_column_name),
                    reference_code=ReferenceCodes._STREAMING_DATA_VALIDATOR_WEIGHT_MISSING)
                )
            materialized_weights = materialize_dataflow(dataflow_weights.take(count), as_numpy=True)

        return materialized_X, materialized_y, materialized_weights

    def _check_train_valid_datatypes(self, training_data: Dataflow, validation_data: Dataflow) -> None:
        """
        Verifies that data types for columns in the training and validation datasets are the same

        :param training_data: The input Dataset containing training columns + target column
        :param validation_data: An optional validation dataset with the same schema as training_data
        :return None
        """
        # TODO: Move this constant out of training_utilities
        from azureml.automl.runtime.training_utilities import LargeDatasetLimit
        count = LargeDatasetLimit.VALIDATION_SUBSAMPLE_SIZE

        for obj, obj_name in [(training_data, "training_data"), (validation_data, "validation_data")]:
            Contract.assert_type(
                obj, obj_name, expected_types=Dataflow, reference_code=ReferenceCodes._STREAMING_INVALID_DATATYPE
            )

        if training_data is not None and validation_data is not None:
            train_dtypes = training_data.take(count).dtypes.items()
            valid_dtypes = validation_data.take(count).dtypes.items()

            for (train_col, train_datatype), (valid_col, valid_datatype) in zip(train_dtypes, valid_dtypes):
                if train_datatype != valid_datatype and train_col == valid_col:
                    raise DataException(azureml_error=AzureMLError.create(
                        InconsistentColumnTypeInTrainValid,
                        target=train_col, column_name=train_col, train_dtype=train_datatype,
                        validation_dtype=valid_datatype)
                    )
