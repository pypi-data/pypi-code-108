# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Configuration for causal analysis runs.

This can be submitted as a child run of a ModelAnalysisRun
"""

from typing import List, Optional, Union

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import RunConfiguration
from azureml.core._experiment_method import experiment_method

from azureml.responsibleai.tools.model_analysis.model_analysis_run import ModelAnalysisRun
from azureml.responsibleai.tools.model_analysis._base_component_config import BaseComponentConfig
from azureml.responsibleai.tools.model_analysis._requests.causal_request import CausalRequest
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


class _CausalConstants:
    LINEAR_MODEL = 'linear'
    AUTOML_MODEL = 'automl'

    DEFAULT_ALPHA = 0.05
    DEFAULT_UPPER_BOUND_ON_CAT_EXPANSION = 50
    DEFAULT_TREATMENT_COST = 0
    DEFAULT_MIN_TREE_LEAF_SAMPLES = 2
    DEFAULT_MAX_TREE_DEPTH = 2
    DEFAULT_SKIP_CAT_LIMIT_CHECKS = False
    DEFAULT_CATEGORIES = 'auto'
    DEFAULT_N_JOBS = -1
    DEFAULT_VERBOSE = 0
    DEFAULT_RANDOM_STATE = None

    DEFAULT_COMMENT = 'Causal analysis'


@experimental
class CausalConfig(BaseComponentConfig):
    """Configuration for causal analysis runs."""

    @experiment_method(submit_function=component_submit)
    @track(_get_logger, custom_dimensions={'app_name': 'CausalConfig'}, activity_type=LogCons.PUBLIC_API)
    def __init__(self,
                 model_analysis_run: ModelAnalysisRun,
                 run_configuration: RunConfiguration = None):
        """Construct a CausalConfig.

        :param model_analysis_run: The model analysis parent run.
        :type model_analysis_run: azureml.responsibleai.model_analysis.model_analysis_run
        :param run_configuration: The run configuration for CausalConfig run.
        :type run_configuration: azureml.core.RunConfiguration
        """
        super(CausalConfig, self).__init__(model_analysis_run, run_configuration)
        self._requests: List[CausalRequest] = []

    @track(_get_logger, custom_dimensions={'app_name': 'CausalConfig'}, activity_type=LogCons.PUBLIC_API)
    def add_request(
        self,
        treatment_features: List[str],
        heterogeneity_features: Optional[List[str]] = None,
        nuisance_model: str = _CausalConstants.LINEAR_MODEL,
        heterogeneity_model: Optional[str] = _CausalConstants.LINEAR_MODEL,
        alpha: Optional[float] = _CausalConstants.DEFAULT_ALPHA,
        upper_bound_on_cat_expansion: int = _CausalConstants.DEFAULT_UPPER_BOUND_ON_CAT_EXPANSION,
        treatment_cost: float = _CausalConstants.DEFAULT_TREATMENT_COST,
        min_tree_leaf_samples: int = _CausalConstants.DEFAULT_MIN_TREE_LEAF_SAMPLES,
        max_tree_depth: int = _CausalConstants.DEFAULT_MAX_TREE_DEPTH,
        skip_cat_limit_checks: bool = _CausalConstants.DEFAULT_SKIP_CAT_LIMIT_CHECKS,
        n_jobs: int = _CausalConstants.DEFAULT_N_JOBS,
        categories: Union[str, list] = _CausalConstants.DEFAULT_CATEGORIES,
        verbose: int = _CausalConstants.DEFAULT_VERBOSE,
        random_state: Union[None, int] = _CausalConstants.DEFAULT_RANDOM_STATE,
        comment: Optional[str] = _CausalConstants.DEFAULT_COMMENT,
    ) -> None:
        """Add a causal insights request to the configuration.

        :param treatment_features: Treatment feature names.
        :type treatment_features: list[str]
        :param heterogeneity_features: Features that mediate the causal effect.
        :type heterogeneity_features: list[str]
        :param nuisance_model: Model type to use for nuisance estimation.
        :type nuisance_model: str
        :param heterogeneity_model: Model type to use for
                                    treatment effect heterogeneity.
        :type heterogeneity_model: str
        :param alpha: Confidence level of confidence intervals.
        :type alpha: float
        :param upper_bound_on_cat_expansion: Maximum expansion for
                                             categorical features.
        :type upper_bound_on_cat_expansion: int
        :param treatment_cost: Cost of treatment. If 0, all treatments will
            have zero cost. If a list is passed, then each element will be
            applied to each treatment feature. Each element can be a scalar
            value to indicate a constant cost of applying that treatment or
            an array indicating the cost for each sample. If the treatment
            is a discrete treatment, then the array for that feature should
            be two dimensional with the first dimension representing samples
            and the second representing the difference in cost between the
            non-default values and the default value.
        :type treatment_cost: None, List of float or array
        :param min_tree_leaf_samples: Minimum number of samples per leaf
            in policy tree.
        :type min_tree_leaf_samples: int
        :param max_tree_depth: Maximum depth of policy tree.
        :type max_tree_depth: int
        :param skip_cat_limit_checks:
            By default, categorical features need to have several instances
            of each category in order for a model to be fit robustly.
            Setting this to True will skip these checks.
        :type skip_cat_limit_checks: bool
        :param n_jobs: Degree of parallelism to use when training models
            via joblib.Parallel
        :type n_jobs: int
        :param categories: 'auto' or list of category values, default 'auto'
            What categories to use for the categorical columns.
            If 'auto', then the categories will be inferred for all
            categorical columns. Otherwise, this argument should have
            as many entries as there are categorical columns.
            Each entry should be either 'auto' to infer the values for
            that column or the list of values for the column.
            If explicit values are provided, the first value is treated
            as the "control" value for that column against which other
            values are compared.
        :type categories: str or list
        :param verbose: Controls the verbosity when fitting and predicting.
        :type verbose: int
        :param random_state: Controls the randomness of the estimator.
        :type random_state: int or RandomState or None
        :param comment: Comment to identify the causal effect configuration.
        :type comment: str
        """
        request = CausalRequest(
            treatment_features,
            heterogeneity_features=heterogeneity_features,
            nuisance_model=nuisance_model,
            heterogeneity_model=heterogeneity_model,
            alpha=alpha,
            upper_bound_on_cat_expansion=upper_bound_on_cat_expansion,
            treatment_cost=treatment_cost,
            min_tree_leaf_samples=min_tree_leaf_samples,
            max_tree_depth=max_tree_depth,
            skip_cat_limit_checks=skip_cat_limit_checks,
            n_jobs=n_jobs,
            categories=categories,
            verbose=verbose,
            random_state=random_state,
            comment=comment,
        )
        self._requests.append(request)

    def _compute_requests(self,
                          experiment_name: str,
                          requests: Optional[RequestDTO] = None,
                          **kwargs):
        if not requests:
            requests = RequestDTO(causal_requests=self._requests)
        return super()._compute_requests(experiment_name, requests, **kwargs)
