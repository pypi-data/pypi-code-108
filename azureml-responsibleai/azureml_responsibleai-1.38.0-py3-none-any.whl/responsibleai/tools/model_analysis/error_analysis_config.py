# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains the config used for adding error analysis reports to a model analysis.

This can be submitted as a child run of a ModelAnalysisRun
"""
from typing import List, Optional

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._requests.error_analysis_request import ErrorAnalysisRequest
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
class ErrorAnalysisConfig(BaseComponentConfig):
    """Class to configure an error-report-generating Run."""

    @experiment_method(submit_function=component_submit)
    @track(_get_logger, custom_dimensions={'app_name': 'ErrorAnalysisConfig'}, activity_type=LogCons.PUBLIC_API)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None,
                 comment: Optional[str] = None):
        """Instantiate instance of class.

        :param model_analysis_run: The model analysis parent run.
        :type model_analysis_run: azureml.responsibleai.model_analysis.model_analysis_run
        :param run_configuration: The run configuration for ErrorAnalysisConfig run.
        :type run_configuration: azureml.core.RunConfiguration
        :param comment: Comment to identify the error analysis configuration.
        :type comment: str
        """
        super(ErrorAnalysisConfig, self).__init__(
            model_analysis_run,
            run_configuration
        )
        self._requests: List[ErrorAnalysisRequest] = []

    @track(_get_logger, custom_dimensions={'app_name': 'ErrorAnalysisConfig'}, activity_type=LogCons.PUBLIC_API)
    def add_request(self,
                    max_depth: Optional[int] = None,
                    num_leaves: Optional[int] = None,
                    filter_features: Optional[List[str]] = None,
                    comment: Optional[str] = None):
        """Add an Error Analysis Report to the configuration.

        :param max_depth: The maximum depth of the error analysis tree.
        :type max_depth: int
        :param num_leaves: The number of leaves in the tree.
        :type num_leaves: int
        :param filter_features: List of features to use for the matrix view.
            At least two features are required for matrix view.
        :type filter_features: list
        :param comment: Comment to identify the error analysis configuration.
        :type comment: str
        """
        self._requests.append(ErrorAnalysisRequest(max_depth=max_depth,
                                                   num_leaves=num_leaves,
                                                   filter_features=filter_features,
                                                   comment=comment))

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(error_analysis_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
