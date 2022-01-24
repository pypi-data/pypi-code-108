# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Sweeper that sweeps and returns whether or not to include the featurizer(s) provide any lift."""
from typing import Any, List
import copy
import logging

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ClientException
from .abstract_sweeper import AbstractSweeper
from ..data_transformation import _compute_sample_weight


logger = logging.getLogger(__name__)


class WeightSweeper(AbstractSweeper):
    """Sweeper that sweeps and returns whether or not to apply class weights to provide any lift."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a weight sweeper."""
        super(WeightSweeper, self).__init__(*args, **kwargs)

    def sweep(self, *args: Any, **kwargs: Any) -> bool:
        """Sweeper method."""
        if self._use_cross_validation:
            raise NotImplementedError()

        class_name = type(self).__name__
        logger.info("Begin weight sweeping")

        is_experiment_better = False
        try:
            if self._data_provider is not None:
                X_train, X_valid, y_train, y_valid = self._data_provider.get_train_validation_sets()
            else:
                raise ClientException("data_provider is not set.", has_pii=False)
            # Train
            baseline_estimator = copy.deepcopy(self._estimator)
            experiment_estimator = self._estimator
            sample_weight = _compute_sample_weight(y_train)

            if baseline_estimator is not None:
                baseline_estimator.fit(X_train, y_train)
            else:
                raise ClientException("baseline_estimator is not set.", has_pii=False)
            if experiment_estimator is not None:
                experiment_estimator.fit(X_train, y_train, sample_weight)
            else:
                raise ClientException("experiment_estimator is not set.", has_pii=False)

            if self._scorer is not None:
                # Validate
                baseline_score = self._scorer.score(
                    estimator=baseline_estimator,
                    valid_features=X_valid,
                    y_actual=y_valid
                )

                experiment_score = self._scorer.score(
                    estimator=experiment_estimator,
                    valid_features=X_valid,
                    y_actual=y_valid
                )

                is_experiment_better = self._scorer.is_experiment_better_than_baseline(
                    baseline_score=baseline_score,
                    experiment_score=experiment_score,
                    epsilon=self._epsilon)

                logger.info(
                    "{name} {sweeper}: Baseline score={bscore}, "
                    "Experiment score={escore}, "
                    "IsExperimentBetter="
                    "{is_experiment_better}".format(
                        name=class_name,
                        sweeper=self,
                        bscore=baseline_score,
                        escore=experiment_score,
                        is_experiment_better=is_experiment_better))

        except Exception as ex:
            logger.warning("Failed due to exception.")
            logging_utilities.log_traceback(ex, logger, is_critical=False)
        finally:
            logger.info("Finished sweeping.")
            return is_experiment_better
