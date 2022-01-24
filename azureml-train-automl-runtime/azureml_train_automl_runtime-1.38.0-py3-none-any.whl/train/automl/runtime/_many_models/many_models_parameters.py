# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional

from azureml.train.automl.runtime._many_models.pipeline_parameters import (
    InferencePipelineParameters,
    TrainPipelineParameters,
)


class ManyModelsTrainParameters(TrainPipelineParameters):
    """Parameters used for ManyModels train pipelines."""
    PARTITION_COLUMN_NAMES_KEY = "partition_column_names"

    def __init__(self, automl_settings: Dict[str, Any], partition_column_names: str):
        super(ManyModelsTrainParameters, self).__init__(automl_settings)

        self.partition_column_names = partition_column_names
        self._modify_automl_settings()

    def validate(self):
        super(ManyModelsTrainParameters, self).validate()

    def _modify_automl_settings(self):
        self.automl_settings[ManyModelsTrainParameters.PARTITION_COLUMN_NAMES_KEY] = self.partition_column_names


class ManyModelsInferenceParameters(InferencePipelineParameters):
    def __init__(
            self,
            partition_column_names: str,
            time_column_name: Optional[str] = None,
            target_column_name: Optional[str] = None
    ):
        super(ManyModelsInferenceParameters, self).__init__()

        self.partition_column_names = partition_column_names
        self.time_column_name = time_column_name
        self.target_column_name = target_column_name

    def validate(self):
        super(ManyModelsInferenceParameters, self).validate()
