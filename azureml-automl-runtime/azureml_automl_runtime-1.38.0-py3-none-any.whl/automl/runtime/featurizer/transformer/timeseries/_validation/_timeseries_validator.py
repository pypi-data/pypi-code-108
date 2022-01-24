# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for timeseries validation."""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any

import numpy as np
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.shared.types import DataInputType


class TimeseriesValidationParamName(Enum):
    AUTOML_SETTINGS = 0
    X = 1
    Y = 2
    X_VALID = 3
    Y_VALID = 4
    SAMPLE_WEIGHT = 5
    SAMPLE_WEIGHT_VALID = 6
    CV_SPLITS_INDICES = 7
    X_RAW_COLUMN_NAMES = 8
    GRAIN_SET = 9
    TIMESERIES_PARAM_DICT = 10
    LAGS = 11
    WINDOW_SIZE = 12
    FORECAST_HORIZON = 13
    MIN_POINTS = 14


class TimeseriesValidatorUtil(ABC):
    """The validation util base class."""

    def __init__(self) -> None:
        pass


class TimeseriesValidationParameter(ABC):
    """The validation parameter base class."""

    def __init__(self,
                 automl_settings: AutoMLBaseSettings,
                 X: DataInputType,
                 y: DataInputType,
                 X_valid: Optional[DataInputType] = None,
                 y_valid: Optional[DataInputType] = None,
                 sample_weight: Optional[np.ndarray] = None,
                 sample_weight_valid: Optional[np.ndarray] = None,
                 cv_splits_indices: Optional[List[List[Any]]] = None,
                 x_raw_column_names: Optional[np.ndarray] = None) -> None:
        self.params = {
            TimeseriesValidationParamName.AUTOML_SETTINGS: automl_settings,
            TimeseriesValidationParamName.X: X,
            TimeseriesValidationParamName.Y: y,
            TimeseriesValidationParamName.X_VALID: X_valid,
            TimeseriesValidationParamName.Y_VALID: y_valid,
            TimeseriesValidationParamName.SAMPLE_WEIGHT: sample_weight,
            TimeseriesValidationParamName.SAMPLE_WEIGHT_VALID: sample_weight_valid,
            TimeseriesValidationParamName.CV_SPLITS_INDICES: cv_splits_indices,
            TimeseriesValidationParamName.X_RAW_COLUMN_NAMES: x_raw_column_names
        }  # type: Dict[TimeseriesValidationParamName, Any]


class TimeseriesValidationWorkerBase(TimeseriesValidatorUtil):
    """Base class of the actual validation workers."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """validate the timeseries config/data."""
        raise NotImplementedError


class TimeseriesValidator(TimeseriesValidatorUtil):
    """
    The timeseries validator which holds actual validation workers.
    """

    def __init__(self, validation_workers: List[TimeseriesValidationWorkerBase]) -> None:
        Contract.assert_type(validation_workers, "validation_workers", expected_types=list)
        Contract.assert_true(
            len(validation_workers) > 0,
            "The validation workers should not be empty.",
            log_safe=True
        )
        Contract.assert_type(validation_workers[0],
                             "validation_workers",
                             expected_types=TimeseriesValidationWorkerBase)
        self._workers = validation_workers

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        for worker in self._workers:
            worker.validate(param)
