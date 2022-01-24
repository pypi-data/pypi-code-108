# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional

from azureml.train.automl.constants import HTSConstants
from azureml.train.automl.runtime._many_models.pipeline_parameters import (
    InferencePipelineParameters,
    TrainPipelineParameters,
)


class HTSTrainParameters(TrainPipelineParameters):
    """Parameters for HTS train pipeline."""
    def __init__(
            self,
            automl_settings: Dict[str, Any],
            hierarchy_column_names: List[str],
            training_level: str,
            enable_engineered_explanations: Optional[bool] = False
    ):
        """
        Parameters for HTS train pipeline.

        :param automl_settings: The dict containing automl settings.
        :param hierarchy_column_names: The hierarchy column names.
        :param training_level: The HTS training level.
        :param enable_engineered_explanations: The switch controls engineered explanations.
        """
        super(HTSTrainParameters, self).__init__(automl_settings)

        self.enable_engineered_explanations = enable_engineered_explanations
        self.hierarchy_column_names = hierarchy_column_names
        self.training_level = training_level
        self._modify_automl_settings()

    def validate(self):
        super(HTSTrainParameters, self).validate()

    def _modify_automl_settings(self):
        self.automl_settings[HTSConstants.HIERARCHY] = self.hierarchy_column_names
        self.automl_settings[HTSConstants.TRAINING_LEVEL] = self.training_level


class HTSInferenceParameters(InferencePipelineParameters):
    """Parameters for HTS inference pipeline."""
    def __init__(
            self,
            hierarchy_forecast_level: str,
            allocation_method: Optional[str] = HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE,
    ):
        """
        Parameters for HTS inference pipeline.

        :param hierarchy_forecast_level: The hts forecast level.
        :param allocation_method: The allocation methods. We currently support `'average_historical_proportions'` and
            `'proportions_of_historical_average'`.
        """
        super(HTSInferenceParameters, self).__init__()

        self.hierarchy_forecast_level = hierarchy_forecast_level
        self.allocation_method = allocation_method

    def validate(self):
        super(HTSInferenceParameters, self).validate()
