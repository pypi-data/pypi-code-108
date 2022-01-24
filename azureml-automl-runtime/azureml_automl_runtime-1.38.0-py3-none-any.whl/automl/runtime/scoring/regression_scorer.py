# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scorer for Accuracy."""
from typing import Any, Optional, cast
import logging

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import DataErrorException
from azureml.automl.runtime.shared.score import scoring, utilities

from .abstract_scorer import AbstractScorer

import numpy as np
from sklearn.base import BaseEstimator


logger = logging.getLogger(__name__)


class RegressionScorer(AbstractScorer):
    """Default Scorer for Regression."""

    def __init__(self, metric_name: str = "r2_score",
                 task: str = constants.Tasks.REGRESSION, *args: Any, **kwargs: Any) -> None:
        """Initialize the object."""
        # Required for methods inherited from AbstractScorer to work
        super(RegressionScorer, self).__init__(metric_name, task, *args, **kwargs)

        # Small number to avoid divide by zero errors when r2_score is 1.
        self._smoothing = 0.0001

    def score(self, estimator: BaseEstimator,
              valid_features: np.ndarray,
              y_actual: np.ndarray
              ) -> float:
        """Calculate the performance of an estimator."""
        y_pred = estimator.predict(valid_features)
        self._n_rows = len(y_actual)
        ret = cast(float, scoring.score_regression(y_actual, y_pred, [self.metric_name])[self.metric_name])
        logger.info("Feature sweep calculation: {metric_name} = {metric_value}.".format(
            metric_name=self.metric_name, metric_value=ret))
        return ret

    def _get_required_delta(self,
                            n_rows: Optional[int],
                            epsilon: float) -> float:
        """
        Heuristic for what delta is big enough for an experiment to be better than default.

        For now epsilon is passed directly as the required additive delta.

        :param n_rows: number of rows in the dataset
        :param epsilon: the required absolute score increase at 10000 rows.
        """
        logger.debug("Feature sweeping required additive delta = {}".format(epsilon))
        return epsilon

    def calculate_lift(self, baseline_score: float, experiment_score: float) -> float:
        """
        Calculate improvement in *error* rate.

        Calculating lift from error rate (as opposed to accuracy) means transforms
        that give lift on columns with high information content/high scores will be considered
        more important.  Example: Transforms that move some columns from 0.95 --> 0.96 will have
        higher lift than other transforms that move some columns from 0.6 --> 0.65

        :param baseline_score: The baseline score.
        :param experiment_score: Experiment score.
        :return: the relative improvement in error rate
        """
        if utilities.minimize_or_maximize(self.metric_name) == constants.OptimizerObjectives.MAXIMIZE:
            # The higher the experiment score the higher the lift
            ret = (experiment_score - baseline_score) / (baseline_score + self._smoothing)
        else:  # Minimize
            # The lower the experiment score the higher the lift
            ret = (-experiment_score + baseline_score) / (baseline_score + self._smoothing)
        return ret

    def is_experiment_better_than_baseline(self, baseline_score: float, experiment_score: float,
                                           epsilon: float, **kwargs: Any) -> bool:
        """
        Override this to provide comparison between two experiment outputs.

        :param baseline_score: The baseline score.
        :param experiment_score: Experiment score.
        :param epsilon: Minimum delta considered gain/loss.
        :param kwargs: Keyword arguments for this scorer.
        :return: Whether or not the experiment score is better than baseline.
        """
        if self._n_rows is None:
            raise DataErrorException(
                "{cls} score method should be called first.".format(
                    cls=self.__class__.__name__), has_pii=False,
                reference_code="regression_scorer.RegressionScorer.is_experiment_better_than_baseline")

        if utilities.minimize_or_maximize(self.metric_name) == constants.OptimizerObjectives.MAXIMIZE:
            harder_baseline_score = baseline_score + self._get_required_delta(self._n_rows, epsilon)
        else:
            harder_baseline_score = baseline_score - self._get_required_delta(self._n_rows, epsilon)
        return self.is_experiment_score_better(
            baseline_score_with_mod=harder_baseline_score,
            experiment_score=experiment_score)
