# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains core contracts for AutoML Runs"""

from .abstract_run import AbstractRun
from .types import RunType

__all__ = [
    "AbstractRun",
    "RunType",
]
