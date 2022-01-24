# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all sweepers."""
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

import logging
import json

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from azureml.automl.core.shared import activity_logger, constants, logging_utilities, exceptions as ex
from azureml.automl.runtime.sampling import DataProvider
from azureml.automl.runtime.scoring import AbstractScorer
from azureml.automl.runtime.featurizer.transformer import featurization_utilities


class AbstractSweeper(ABC):
    """Base class for all sweepers."""

    def __init__(self,
                 sweeper_class: str,
                 name: str,
                 data_provider: Optional[DataProvider] = None,
                 baseline: Optional[Pipeline] = None,
                 experiment: Optional[Pipeline] = None,
                 estimator: Optional[BaseEstimator] = None,
                 scorer: Optional[AbstractScorer] = None,
                 epsilon: float = 0.01,
                 scale_epsilon: bool = True,
                 include_baseline_features_in_experiment: bool = True,
                 task: str = constants.Tasks.CLASSIFICATION,
                 use_cross_validation: bool = False,
                 *args: Any, **kwargs: Any) -> None:
        """
        Initialize the abstract sweeper.

        :param sweeper_class: Sweeper class used for sweeping.
        :param data_provider: The provider that returns the already sampled data for sweeping.
        :param baseline: Baseline set of transformers to run.
        :param experiment: Experiment to compare with.
        :param estimator: Estimator to train.
        :param scorer: Scorer to use.
        :param epsilon: Epsilon for score comparison.
        :param scale_epsilon: Whether or not to scale epsilon inversely with sample size for this experiment.
        :param include_baseline_features_in_experiment: Whether or not include
                                                        baseline features in experiment.
        :param task: Task type
        :param use_cross_validation: Use cross validation or not.
        """
        self._data_provider = data_provider
        self._name = name
        self._baseline = baseline
        self._experiment = experiment
        self._estimator = estimator
        self._scorer = scorer
        self._epsilon = epsilon
        self._scale_epsilon = scale_epsilon
        self._include_baseline_features_in_experiment = include_baseline_features_in_experiment
        self._use_cross_validation = use_cross_validation
        self._task = task
        self._sweeper_type = sweeper_class
        self._validate()
        if scorer is not None and task != scorer._task:
            raise ex.ConfigException("The scorer task and the sweeper task should be the same.", has_pii=False)
        self._task = task

    @abstractmethod
    def sweep(self, column: Optional[Union[str, List[str]]] = None, *args: Any, **kwargs: Any) -> bool:
        """
        Sweep over parameters provided and return if experiment was better than baseline.

        :param column: The set of columns to sweep on.
        :return: To be enabled list of transforms.
        """
        raise NotImplementedError()

    def _validate(self) -> bool:
        """
        Validate if the current sweeper has all the needed stuff.

        :return: True if the validation passed. If not, false.
        """
        return self._baseline is not None and self._experiment is not None

    @property
    def config(self) -> str:
        """Return string presentation of the object."""
        metric_name = None
        if self._scorer is not None:
            metric_name = self._scorer.metric_name
        return json.dumps({"SweeperType": self._sweeper_type,
                           "DataProvider": type(self._data_provider).__name__,
                           "BaselineTransforms": featurization_utilities.get_transform_names(self._baseline),
                           "ExperimentTransforms": featurization_utilities.get_transform_names(self._experiment),
                           "Estimator": type(self._estimator).__name__,
                           "Scorer": type(self._scorer).__name__,
                           "MetricName": metric_name,
                           "Epsilon": self._epsilon,
                           "IncludeBaselineInExperiment": self._include_baseline_features_in_experiment,
                           "UseCrossValidation": self._use_cross_validation,
                           "Task": self._task})

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state picklable objects.

        :return: state
        """
        return self.__dict__

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)

    def __repr__(self) -> str:
        """Return string presentation of the object."""
        return self.config

    def __str__(self) -> str:
        """Return string presentation of the object."""
        return self.config
