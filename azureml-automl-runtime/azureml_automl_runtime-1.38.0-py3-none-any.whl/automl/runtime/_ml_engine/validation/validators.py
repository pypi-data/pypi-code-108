# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from abc import ABC, abstractmethod
from typing import Union, cast

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._data_definition import MaterializedTabularData, RawExperimentData, LazyTabularData, \
    TabularData

logger = logging.getLogger(__name__)

Data = Union[RawExperimentData, TabularData]


class AbstractDataValidator(ABC):
    """Common interface for all things data validation."""

    @abstractmethod
    def validate(self, data: Data) -> None:
        """
        Run validations on the user provided data inputs

        :param data: The data to validate.
        :return: None
        """
        raise NotImplementedError


class AbstractRawExperimentDataValidator(AbstractDataValidator):
    """
    Interface for data validations on the user provided RawExperimentData, across different task types.

    The different types refers to the different shapes and sizes that a machine learning
    dataset can come in, such as columns or tabular data, and for different task types such as
    Classification, Regression, Forecasting.
    """

    # A reference code for errors originating from this class.
    _REFERENCE_CODE = ReferenceCodes._ABSTRACT_RAW_EXPERIMENT_DATA_VALIDATOR

    def validate(self, data: Data) -> None:
        """
        Run validations on the user provided data inputs

        :param data: The data to validate.
        :return: None, raises an exception if validation fails.
        """
        Contract.assert_value(
            data, "raw_experiment_data", reference_code=AbstractRawExperimentDataValidator._REFERENCE_CODE
        )
        Contract.assert_type(
            data,
            "raw_experiment_data",
            expected_types=RawExperimentData,
            reference_code=AbstractRawExperimentDataValidator._REFERENCE_CODE,
        )

        raw_experiment_data = cast(RawExperimentData, data)

        try:
            self.validate_raw_experiment_data(raw_experiment_data)
        except (DataException, ValidationException):
            raise
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            new_exception = ValidationException.from_exception(e, target="RawExperimentDataValidation")
            raise new_exception.with_traceback(e.__traceback__)

    @abstractmethod
    def validate_raw_experiment_data(self, raw_experiment_data: RawExperimentData) -> None:
        """
        Given raw experiment data, check if it is valid to run through the featurization and model training pipelines

        :param raw_experiment_data: RawExperimentData, as provided by the user
        :return: None
        """
        raise NotImplementedError


class AbstractTabularDataValidator(AbstractDataValidator):
    """
    Interface for data validations on a TabularData.
    """

    # A reference code for errors originating from this class.
    _REFERENCE_CODE = ReferenceCodes._ABSTRACT_MATERIALIZED_TABULAR_DATA_VALIDATOR

    def validate(self, data: Data) -> None:
        """
        Run validations on the user provided data inputs (such as training and validation datasets)

        :param data: Data to run validations on.
        :return: None
        """
        Contract.assert_value(data, "tabular_data",
                              reference_code=AbstractTabularDataValidator._REFERENCE_CODE)
        Contract.assert_type(data, "tabular_data", expected_types=(MaterializedTabularData, LazyTabularData),
                             reference_code=AbstractTabularDataValidator._REFERENCE_CODE)

        tabular_data = cast(Union[MaterializedTabularData, LazyTabularData], data)

        try:
            self.validate_tabular_data(tabular_data)
        except (DataException, ValidationException):
            # tabular data validations failed
            raise
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            new_exception = ValidationException.from_exception(e, target=self.__class__.__name__)
            raise new_exception.with_traceback(e.__traceback__)

    @abstractmethod
    def validate_tabular_data(self, tabular_data: TabularData) -> None:
        """
        Run validations on the provided tabular data.

        :param tabular_data: Data consisting of X, y and weights to validate
        :return: None
        """
        raise NotImplementedError
