# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict
from abc import ABC


class TrainPipelineParameters(ABC):
    def __init__(self, automl_settings: Dict[str, Any]):
        self.automl_settings = automl_settings

    def validate(self):
        pass


class InferencePipelineParameters(ABC):
    def __init__(self):
        pass

    def validate(self):
        pass
