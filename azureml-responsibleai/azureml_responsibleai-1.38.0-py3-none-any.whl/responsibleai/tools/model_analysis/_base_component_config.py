# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the base run config used for adding RAI components to a model analysis.

This can be submitted as a child run of a ModelAnalysisRun
"""

import copy
import joblib
import pathlib
import shutil
import tempfile
import uuid

from typing import List

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml.core import Experiment
from azureml.core import RunConfiguration, ScriptRunConfig
from azureml.exceptions import UserErrorException

from azureml.responsibleai.common._errors.error_definitions import MismatchedExperimentName
from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._compute_dto import ComputeDTO
from azureml.responsibleai.tools.model_analysis._requests.request_dto import RequestDTO


@experimental
class BaseComponentConfig:

    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None):
        """Instantiate instance of class."""
        self._model_analysis_run = model_analysis_run
        self._workspace = model_analysis_run.experiment.workspace
        self._run_configuration = run_configuration

    def _compute_requests(self,
                          experiment_name: str,
                          requests: RequestDTO,
                          **kwargs):
        if experiment_name != self._model_analysis_run.experiment.name:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    MismatchedExperimentName,
                    expected=self._model_analysis_run.experiment.name,
                    actual=experiment_name
                )
            )
        script_name = '_compute_script.py'

        script_temp_dir = self._make_dir_and_copy_files([script_name])

        # Create the DTO
        config_dto = ComputeDTO(
            experiment_name=experiment_name,
            model_analysis_run_id=self._model_analysis_run.id,
            requests=requests
        )

        # Pickle the configuration DTO
        config_filename = "config-{0}.pkl".format(uuid.uuid4())

        joblib.dump(value=config_dto,
                    filename=str(script_temp_dir / config_filename))

        rc = self._generate_run_configuration()

        script_arguments = [
            '--settings_filepath', config_filename
        ]

        script_run_config = ScriptRunConfig(source_directory=str(script_temp_dir),
                                            script=script_name,
                                            run_config=rc,
                                            arguments=script_arguments)

        experiment = Experiment(self._workspace,
                                experiment_name)
        script_run = experiment.submit(script_run_config, **kwargs)
        self._rai_component_run = ModelAnalysisRun(experiment, script_run.id)
        return self._rai_component_run

    def _generate_run_configuration(self) -> RunConfiguration:
        # Copy the run configuration
        rc: RunConfiguration = copy.deepcopy(self._run_configuration)

        # Set the environment
        rc.environment = self._model_analysis_run.get_environment()

        return rc

    def _make_dir_and_copy_files(self, target_files: List[str]):
        script_temp_dir = pathlib.Path(tempfile.mkdtemp())

        current_dir = pathlib.Path(__file__).parent

        for target in target_files:
            src_path = current_dir / target
            shutil.copy(str(src_path), str(script_temp_dir))

        return script_temp_dir.resolve()
