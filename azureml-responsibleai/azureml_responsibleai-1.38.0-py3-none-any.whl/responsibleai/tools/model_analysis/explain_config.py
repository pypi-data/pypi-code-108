# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the config used for adding explanations to a model analysis.

This can be submitted as a child run of a ModelAnalysisRun
"""
from typing import List, Optional  # noqa: F401

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._requests.explain_request import ExplainRequest
from azureml.responsibleai.tools.model_analysis._requests.request_dto import RequestDTO
from azureml.responsibleai.tools.model_analysis._utilities import component_submit
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


@experimental
class ExplainConfig(BaseComponentConfig):
    """Class to configure an explanation-generating Run."""

    @experiment_method(submit_function=component_submit)
    @track(_get_logger, custom_dimensions={'app_name': 'ExplainConfig'}, activity_type=LogCons.PUBLIC_API)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None,
                 comment: Optional[str] = None):
        """Instantiate instance of class.

        :param model_analysis_run: The model analysis parent run.
        :type model_analysis_run: azureml.responsibleai.model_analysis.model_analysis_run
        :param run_configuration: The run configuration for ExplainConfig run.
        :type run_configuration: azureml.core.RunConfiguration
        :param comment: Comment to identify the explain configuration.
        :type comment: str
        """
        super(ExplainConfig, self).__init__(
            model_analysis_run,
            run_configuration
        )
        self._requests: List[ExplainRequest] = []

    @track(_get_logger, custom_dimensions={'app_name': 'ExplainConfig'}, activity_type=LogCons.PUBLIC_API)
    def add_request(self,
                    comment: Optional[str] = None):
        """Add an explanation to the configuration.

        :param comment: Comment to identify the explanation.
        :type comment: str
        """
        self._requests.append(ExplainRequest(comment))

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(explanation_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
