# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Configuration for counterfactual analysis runs.

This can be submitted as a child run of a ModelAnalysisRun
"""
from responsibleai._managers.counterfactual_manager import CounterfactualConstants
from typing import Dict, List, Optional, Union

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._requests.counterfactual_request import CounterfactualRequest
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
class CounterfactualConfig(BaseComponentConfig):
    """Configuration for counterfactual analysis runs."""

    @experiment_method(submit_function=component_submit)
    @track(_get_logger, custom_dimensions={'app_name': 'CounterFactualConfig'}, activity_type=LogCons.PUBLIC_API)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None):
        """Construct a CounterfactualConfig.

        :param model_analysis_run: The model analysis parent run.
        :type model_analysis_run: azureml.responsibleai.model_analysis.model_analysis_run
        :param run_configuration: The run configuration for CounterfactualConfig run.
        :type run_configuration: azureml.core.RunConfiguration
        """
        super(CounterfactualConfig, self).__init__(model_analysis_run, run_configuration)
        self._requests: List[CounterfactualRequest] = []

    @track(_get_logger, custom_dimensions={'app_name': 'CounterFactualConfig'}, activity_type=LogCons.PUBLIC_API)
    def add_request(self,
                    total_CFs: int,
                    method: str = CounterfactualConstants.RANDOM,
                    desired_class: Union[str, int] = CounterfactualConstants.OPPOSITE,
                    desired_range: Optional[List[float]] = None,
                    feature_importance: bool = True,
                    features_to_vary: Union[List[str], str] = 'all',
                    permitted_range: Optional[Dict[str, List[float]]] = None,
                    comment: Optional[str] = "counterfactual_request"):
        """Add a counterfactual request to the configuration.

            :param total_CFs: Total number of counterfactuals required.
            :type total_CFs: int
        :param method: Type of dice-ml explainer. Either of "random", "genetic" or "kdtree".
        :type method: str
        :param desired_class: Desired counterfactual class. For binary
                              classification, this needs to be set as
                              "opposite".
        :type desired_class: string or int
        :param desired_range: For regression problems,
                              contains the outcome range
                              to generate counterfactuals in.
        :type desired_range: list[float]
        :param permitted_range: Dictionary with feature names as keys and
                                permitted range in list as values.
                                Defaults to the range inferred from training
                                data.
        :type permitted_range: dict
        :param features_to_vary: Either a string "all" or a list of
                                 feature names to vary.
        :type features_to_vary: list
        :param feature_importance: Flag to compute feature importance using
                                   dice-ml.
        :type feature_importance: bool
        :param comment: Comment to identify the counterfactual configuration.
        :type comment: str
        """
        request = CounterfactualRequest(total_CFs=total_CFs,
                                        method=method,
                                        desired_class=desired_class,
                                        desired_range=desired_range,
                                        feature_importance=feature_importance,
                                        permitted_range=permitted_range,
                                        features_to_vary=features_to_vary,
                                        comment=comment)
        self._requests.append(request)

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(counterfactual_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
