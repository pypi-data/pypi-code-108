# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import joblib
import logging

from typing import Any

from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RunStatus
from azureml.core import Run, Workspace
from azureml.exceptions import AzureMLException, UserErrorException

from responsibleai import ModelAnalysis

from azureml.responsibleai.common.model_loader import ModelLoader

from azureml.responsibleai.common._errors.error_definitions import (
    AnalysisInitFailedSystemError,
    AnalysisInitFailedUserError,
    AnalysisInitNotCompletedError,
    MismatchedExperimentName,
    UnexpectedObjectType
)
from azureml.responsibleai.common._errors.error_definitions import MismatchedWorkspaceName
from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig  # noqa: F401
from azureml.responsibleai.tools.model_analysis._compute_dto import ComputeDTO


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def _run_all_and_upload(compute_dto: ComputeDTO, current_run: Run):
    try:
        if current_run.experiment.name != compute_dto.experiment_name:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    MismatchedExperimentName,
                    expected=compute_dto.experiment_name,
                    actual=current_run.experiment.name
                )
            )

        if not isinstance(compute_dto, ComputeDTO):
            raise AzureMLException._with_error(
                AzureMLError.create(
                    UnexpectedObjectType,
                    expected='ComputeDTO',
                    actual=str(type(compute_dto))
                )
            )

        _logger.info("Getting the parent run")

        rai_computation_name = compute_dto.requests._get_rai_computation_name()
        current_run.display_name = rai_computation_name

        model_analysis_run = ModelAnalysisRun(current_run.experiment,
                                              compute_dto.model_analysis_run_id)

        _logger.info("Loading the data")
        train_df = model_analysis_run.get_train_data()
        test_df = model_analysis_run.get_test_data()

        _logger.info("Loading the estimator")
        estimator = ModelLoader.load_model_from_workspace(model_analysis_run.experiment.workspace,
                                                          model_analysis_run.settings.model_loader,
                                                          model_analysis_run.settings.model_id)

        _logger.info("Creating the local model analysis")
        model_analysis = ModelAnalysis(
            model=estimator,
            train=train_df,
            test=test_df,
            target_column=model_analysis_run.settings.target_column_name,
            task_type=model_analysis_run.settings.model_type,
            categorical_features=model_analysis_run.settings.categorical_column_names,
        )

        model_analysis_run._compute_and_upload(compute_dto.requests, model_analysis, current_run)
    except Exception as e:
        current_run.fail(error_details=str(e))
        raise e


def _parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('--settings_filepath', type=str, required=True,
                        help="Path to the pickled settings")

    return parser.parse_args()


def _compute_wrapper():
    args = _parse_command_line()

    settings: ComputeDTO = joblib.load(args.settings_filepath)
    current_run = Run.get_context()

    _run_all_and_upload(settings, current_run)


def component_submit(
        config: BaseComponentConfig,
        workspace: Workspace,
        experiment_name: str,
        **kwargs: Any):
    """
    Common submit method for all component configs.config

    Each config will process its specific requests via _compute_requests.
    """
    if workspace.name != config._workspace.name:
        raise UserErrorException._with_error(
            AzureMLError.create(
                MismatchedWorkspaceName,
                expected=config._workspace.name,
                actual=workspace.name
            )
        )
    parent_status = config._model_analysis_run.get_status()
    if parent_status == RunStatus.FAILED:
        error_code = config._model_analysis_run.get_details().get('error', {}).get('code')
        if error_code.startswith("User"):
            raise UserErrorException._with_error(
                AzureMLError.create(
                    AnalysisInitFailedUserError,
                    portal_url=config._model_analysis_run.get_portal_url()
                )
            )
        else:
            raise AzureMLException._with_error(
                AzureMLError.create(
                    AnalysisInitFailedSystemError,
                    portal_url=config._model_analysis_run.get_portal_url()
                )
            )
    elif parent_status != RunStatus.COMPLETED:
        raise UserErrorException._with_error(
            AzureMLError.create(
                AnalysisInitNotCompletedError,
                portal_url=config._model_analysis_run.get_portal_url()
            )
        )
    return config._compute_requests(experiment_name, **kwargs)
