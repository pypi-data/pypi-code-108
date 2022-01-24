# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holds metadata for a submitted or currently running experiment running in Azure."""
from typing import Optional
import os
import os.path
import shutil
import warnings
import logging
from pathlib import Path
from azureml.train.automl import constants
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import NotFound
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core._run.types import RunType
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    RuntimeModuleDependencyMissing,
)
from azureml.automl.core.shared.exceptions import (
    ClientException,
    ConfigException,
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from ._azureautomlsettings import AzureAutoMLSettings
from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.jasmine_client import JasmineClient
from ._automl_feature_config_manager import AutoMLFeatureConfigManager
from azureml.automl.core._experiment_drivers.experiment_state import ExperimentState
from azureml.core import Experiment


logger = logging.getLogger(__name__)


class AzureExperimentState(ExperimentState):
    """
    Experiment state object for Azure-based experiments. Encapsulates state of an experiment as well as the
    relevant service objects needed to service the experiment.
    """

    def __init__(
        self,
        experiment: Experiment,
        automl_settings: AzureAutoMLSettings,
        _create_partial_client: bool=False
    ):
        """
        Create an AzureExperimentState.

        :param experiment: the experiment object
        :param automl_settings: the settings used for the experiment
        :param _create_partial_client: Whether to create a JasmineClient with all expected attrbutes or not.
            This bool should be used in cases where an Experiment is not availabe in the context yet. One such
            example is the AutoMLStep which has an experiment with name "placeholder" and no ID.
        """
        super().__init__()
        self.automl_settings = automl_settings
        self.current_run = None     # type: Optional[RunType]
        self.experiment = experiment
        if _create_partial_client:
            self.jasmine_client = JasmineClient(
                service_context=self.experiment.workspace.service_context,
                experiment_name=self.experiment.name,
                experiment_id=self.experiment.name,
                host=self.automl_settings.service_url
            )
        else:
            self.jasmine_client = JasmineClient(
                service_context=self.experiment.workspace.service_context,
                experiment_name=self.experiment.name,
                experiment_id=self.experiment.id,
                host=self.automl_settings.service_url,
            )
        self.feature_config_manager = AutoMLFeatureConfigManager(self.jasmine_client)
        self.experiment_client = ExperimentClient(
            service_context=self.experiment.workspace.service_context,
            experiment_name=self.experiment.name,
            experiment_id=self.experiment.id,
            host=self.automl_settings.service_url,
        )
        self._setup_data_script()

    def _setup_data_script(self) -> None:
        module_path = self.automl_settings.data_script
        if self.automl_settings.data_script is not None:
            # Show warnings to user when use the data_script.
            warnings.warn(
                "Please make sure in the data script the data script "
                "uses the paths of data files on the remote machine."
                "The data script is not recommended anymore, "
                "please take a look at the latest documentation to use the dprep interface."
            )

            is_data_script_in_proj_dir = True
            if not os.path.exists(self.automl_settings.data_script):
                # Check if the data_script is a relative sub path from the project path (automl_settings.path)
                script_path = os.path.join(
                    self.automl_settings.path, self.automl_settings.data_script
                )
                if os.path.exists(script_path):
                    module_path = script_path
                else:
                    raise ConfigException._with_error(
                        AzureMLError.create(NotFound, target="data_script", resource_name=script_path)
                    )
            else:
                # Check if the data_script path is under the project path or it's sub folders.
                try:
                    path_script = Path(self.automl_settings.data_script)
                    path_project = Path(self.automl_settings.path)
                    if path_project not in path_script.parents:
                        is_data_script_in_proj_dir = False
                except Exception:
                    is_data_script_in_proj_dir = False
                module_path = self.automl_settings.data_script

            # Check if the data_script path is actually a file path.
            if not os.path.isfile(module_path):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType,
                        target="data_script",
                        argument=str(module_path),
                        actual_type="Directory",
                        expected_types="File",
                    )
                )

            # Make sure the script_path (the data script path) has the script file named as DATA_SCRIPT_FILE_NAME.
            module_file_name = os.path.basename(module_path)
            if module_file_name != constants.DATA_SCRIPT_FILE_NAME:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues,
                        target="data_script",
                        arguments=module_file_name,
                        supported_values=constants.DATA_SCRIPT_FILE_NAME,
                    )
                )

            # If data_script is not in project folder, copy the data_script file into the project folder.
            # We'll take the snapshot of the project folder.
            if not is_data_script_in_proj_dir:
                # Need to copy the data script file.
                des_module_path = os.path.join(
                    self.automl_settings.path, constants.DATA_SCRIPT_FILE_NAME
                )
                if os.path.abspath(module_path) != os.path.abspath(des_module_path):
                    shutil.copy(os.path.abspath(module_path), des_module_path)
                module_path = des_module_path

            try:
                import azureml.train.automl.runtime
                from azureml.train.automl.runtime import utilities as utils
                from azureml.automl.runtime import training_utilities
                from azureml.automl.runtime.shared import utilities as runtime_utilities
                from azureml.automl.runtime._data_definition import RawExperimentData

                self.user_script = utils._load_user_script(module_path)
                input_data = training_utilities._extract_user_data(self.user_script)
                raw_experiment_data = RawExperimentData.create(
                    input_data,
                    self.automl_settings.label_column_name,
                    self.automl_settings.weight_column_name,
                    self.automl_settings.validation_size,
                    self.automl_settings.n_cross_validations)
                training_utilities.auto_block_models(raw_experiment_data, self.automl_settings)
            except AzureMLException:
                raise
            except ImportError as e:
                raise ConfigException._with_error(
                    AzureMLError.create(RuntimeModuleDependencyMissing, target="data_script", module_name=e.name),
                    inner_exception=e,
                ) from e
            except Exception as e:
                logging_utilities.log_traceback(e, logger)
                logger.error("Failed to load the data from user provided get_data script.")
                raise ClientException._with_error(
                    AzureMLError.create(
                        AutoMLInternal,
                        error_details=str(e),
                        target="data_script",
                        reference_code=ReferenceCodes._DATA_SCRIPT_INTERNAL_ERROR,
                    ),
                    inner_exception=e,
                ) from e
        else:
            self.user_script = None
