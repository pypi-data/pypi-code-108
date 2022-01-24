# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union

from azureml.core import Run
from azureml.automl.core._run.abstract_run import AbstractRun

# Single type representing an object that exposes Run APIs
RunType = Union[AbstractRun, Run]
