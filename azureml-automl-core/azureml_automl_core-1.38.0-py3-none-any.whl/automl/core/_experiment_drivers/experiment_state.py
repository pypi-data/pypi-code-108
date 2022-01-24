# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holds metadata for a submitted or currently running experiment."""
from typing import Optional, Any, TypeVar
from datetime import datetime
import sys
import os
import os.path
import shutil
import warnings
import logging
from pathlib import Path
from types import ModuleType
from azureml.automl.core.console_writer import ConsoleWriter
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import NotFound
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.shared import import_utilities, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    RuntimeModuleDependencyMissing,
    SnapshotLimitExceeded,
)
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ClientException,
    ConfigException,
    ValidationException,
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes


logger = logging.getLogger(__name__)


class ExperimentState:

    def __init__(self) -> None:
        self.console_writer = ConsoleWriter(sys.stdout)

        self.parent_run_id = None   # type: Optional[str]
        self.current_iteration = 0
        self.onnx_cvt = None    # type: Optional[Any]
        self.user_script = None  # type: Optional[ModuleType]
        # self.input_data = None  # type: Optional[Dict[str, Union[Any, Any]]]
        self.experiment_start_time = None   # type: Optional[datetime]
        self.best_score = float('nan')  # type: float
