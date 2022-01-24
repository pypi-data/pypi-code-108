# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the configuration used for initializing a model analysis in Azure Machine Learning.

This config is submitted as a run to an experiment and will create the initial data snapshots that will be used
by other model analysis steps to evaluate various things about the model.
"""
import copy
import joblib
import logging
import pathlib
import shutil
import tempfile
import time
import uuid

from typing import Any, List, Optional, Union  # noqa: F401

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml.core import Dataset, Experiment, Model, Run, RunConfiguration, ScriptRunConfig, Workspace
from azureml.core._experiment_method import experiment_method
from azureml.core.conda_dependencies import CondaDependencies, DEFAULT_SDK_ORIGIN
from azureml.exceptions import UserErrorException

from azureml.responsibleai import SELF_VERSION as RAI_VERSION
from azureml.responsibleai.common._errors.error_definitions import AnalysisInitNotExecutedError
from azureml.responsibleai.common.model_loader import ModelLoader
from azureml.responsibleai.tools._common.constants import DEFAULT_MAXIMUM_ROWS_FOR_TEST_DATASET
from azureml.responsibleai.tools.model_analysis._aml_init_dto import AMLInitDTO
from azureml.responsibleai.tools.model_analysis._model_analysis_settings import ModelAnalysisSettings
from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


_CUSTOM_ENV_NAME_FORMAT = "rai-custom-environment-{0}"


def _initialize_analysis_submit(config: 'ModelAnalysisConfig',
                                workspace: Workspace,
                                experiment_name: str,
                                **kwargs: Any) -> Run:
    """
    Submit a run to create the model analysis dashboard assets.

    :param config:
    :param workspace:
    :param experiment_name:
    :param kwargs:
    :return:
    """
    config._analysis_settings.workspace = workspace
    return config._initialize_azureml(experiment_name, **kwargs)


@experimental
class ModelAnalysisConfig:
    """Class to perform RAI model analysis."""

    @track(_get_logger, custom_dimensions={'app_name': 'ModelAnalysis'}, activity_type=LogCons.PUBLIC_API)
    @experiment_method(submit_function=_initialize_analysis_submit)
    def __init__(self,
                 title: str,
                 model: Model,
                 model_loader: Union[ModelLoader, str],
                 model_type: str,
                 train_dataset: Dataset,
                 test_dataset: Dataset,
                 X_column_names: List[str],
                 target_column_name: str,
                 confidential_datastore_name: str,
                 datastore_prefix: Optional[str] = None,
                 run_configuration: RunConfiguration = None,
                 maximum_rows_for_test_dataset: int = DEFAULT_MAXIMUM_ROWS_FOR_TEST_DATASET,
                 categorical_column_names: Optional[List[str]] = None):
        """
        Instantiate an instance of the class.

        :param title: The name to assign to this model analysis
        :param model: The model to analyse
        :param model_type: What type of model it is 'binary_classification' or 'regression'
        :param train_dataset: The training dataset to use for this analysis.
        :param test_dataset: The test dataset to use for this analysis.
        :param X_column_names: The names of the columns in the train dataset.
        :param target_column_name: The name of the target column.
        :param confidential_datastore_name: The name of the confidential datastore where the analyses will be uploaded.
        :param datastore_prefix: The file path prefix to save the the data to in the datastore.
        :param model_loader: The model loader module for loading the model. Specify 'mlflow' to load using mlflow.
        :param run_configuration: The RunConfiguration specifying the compute on which this analysis will be computed.
        :param maximum_rows_for_test_dataset: Maximum rows allowed in test dataset before erroring.
        :param categorical_column_names: List of all categorical columns in the dataset.
        """
        # Create the configuration object
        self._analysis_settings = ModelAnalysisSettings(
            workspace=None,
            title=title,
            model=model,
            model_type=model_type,
            train_dataset=train_dataset,
            test_dataset=test_dataset,
            X_column_names=X_column_names,
            target_column_name=target_column_name,
            confidential_datastore_name=confidential_datastore_name,
            datastore_prefix=datastore_prefix,
            model_loader=model_loader,
            run_configuration=run_configuration,
            maximum_rows_for_test_dataset=maximum_rows_for_test_dataset,
            categorical_column_names=categorical_column_names,
        )

        # Mark AzureML as uninitialised
        self._azureml_is_initialized = False
        self._model_analysis_run: Optional[ModelAnalysisRun] = None

    @property
    def azureml_is_initialized(self):
        """Property to determine if the model analysis initialization has been completed."""
        if self._model_analysis_run:
            return self._model_analysis_run._is_completed
        else:
            raise UserErrorException._with_error(
                AzureMLError.create(AnalysisInitNotExecutedError))

    def _initialize_azureml(self, experiment_name: str, **kwargs) -> ModelAnalysisRun:
        """Submit a script run to create the initial analysis artifacts like data snapshots."""
        script_name = '_azureml_init_script.py'

        script_temp_dir = self._make_dir_and_copy_files([script_name])

        # Create the DTO
        config_dto = AMLInitDTO(self._analysis_settings)

        # Pickle the configuration
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

        experiment = Experiment(
            self._analysis_settings.workspace, experiment_name)
        script_run = experiment.submit(script_run_config, **kwargs)
        self._model_analysis_run = ModelAnalysisRun(
            experiment=experiment,
            run_id=script_run.id,
            run_display_name=self._analysis_settings.title)
        return self._model_analysis_run

    def _generate_run_configuration(self) -> RunConfiguration:
        # Copy the run configuration
        rc = copy.deepcopy(self._analysis_settings.run_configuration)

        # Add the dependencies we need
        passed_in_packages = [
            CondaDependencies._get_package_name_with_extras(x)
            for x in
            rc.environment.python.conda_dependencies.pip_packages
        ]

        pip_packages = [
            'azureml-responsibleai=={}'.format(RAI_VERSION)
        ]

        for p in pip_packages:
            # Don't override a package that a user passed in
            p_with_extras = CondaDependencies._get_package_name_with_extras(p)
            if p_with_extras not in passed_in_packages:
                rc.environment.python.conda_dependencies.add_pip_package(p)

        # If the SDK was consumed from a private index, we want to make sure the index is present
        source_url = CondaDependencies.sdk_origin_url().rstrip('/')
        dependencies = rc.environment.python.conda_dependencies
        if source_url != DEFAULT_SDK_ORIGIN:
            env_name = _CUSTOM_ENV_NAME_FORMAT.format(str(int(time.time())))
            logging.warn("Renaming environment from {0} to {1}".format(rc.environment.name, env_name))
            rc.environment.name = env_name
            existing_options = [x.rstrip('/') for x in rc.environment.python.conda_dependencies.pip_options]
            if any(["--index-url" in option for option in existing_options]):
                logging.warn("Index url detected in conda dependencies. Using user provided indices.")
            else:
                # Remove any --extra-index-url so that
                # --index-url and --extra-index-url are added in the correct order.
                dependencies.remove_pip_option('--extra-index-url')
                dependencies.set_pip_option("--index-url " + source_url)
                dependencies.set_pip_option("--extra-index-url " + DEFAULT_SDK_ORIGIN)
                rc.environment.python.conda_dependencies = dependencies

                # If the user provided extra indices, make sure we add them back in since set_pip_option overrides
                if len(existing_options) > 0:
                    options_to_add_back = \
                        [x for x in existing_options
                         if not x.endswith(source_url) and not x.endswith(DEFAULT_SDK_ORIGIN)]
                    for dependency in rc.environment.python.conda_dependencies._conda_dependencies['dependencies']:
                        if isinstance(dependency, dict) and 'pip' in dependency:
                            dependency['pip'].extend(options_to_add_back)
        return rc

    def _make_dir_and_copy_files(self, target_files: List[str]):
        script_temp_dir = pathlib.Path(tempfile.mkdtemp())

        current_dir = pathlib.Path(__file__).parent

        for target in target_files:
            src_path = current_dir / target
            shutil.copy(str(src_path), str(script_temp_dir))

        return script_temp_dir.resolve()
