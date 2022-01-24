# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Sweeper that sweeps and returns whether or not to include the featurizer(s) provide any lift."""
from typing import Any, List, Optional, Union
import copy
import logging

from sklearn.pipeline import make_union
import numpy as np
import scipy

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared import logging_utilities
from .abstract_sweeper import AbstractSweeper


logger = logging.getLogger(__name__)


class BinarySweeper(AbstractSweeper):
    """Sweeper that sweeps and returns whether or not to include the featurizer(s) provide any lift."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a Binary sweeper."""
        super(BinarySweeper, self).__init__(*args, **kwargs)

    def sweep(self,
              column: Optional[str] = None,
              featurize_separately: bool = False,
              *args: Any, **kwargs: Any) -> bool:
        """
        Execute a sweeping experiment.

        :param column: Which column to sweep over. If None, sweeps over entire sample stored in the DataProvider.
        :param featurize_separately: Whether to featurize the columns of the sample separately before scoring or not.
        :return: Boolean for whether or not the experimental featurizer provides any lift.
        """
        if self._use_cross_validation:
            raise NotImplementedError()

        class_name = type(self).__name__
        logger.info("{} {}: Begin sweeping".format(class_name, self))

        is_experiment_better = False
        try:
            if self._data_provider is not None:
                X_train_sample, X_valid_sample, y_train_sample, y_valid_sample = \
                    self._data_provider.get_train_validation_sets(column=column)
            else:
                raise ClientException("data_provider is not set.", has_pii=False)

            # Featurizer
            baseline_featurizer = self._baseline
            experiment_featurizer = self._experiment
            if self._include_baseline_features_in_experiment:
                experiment_featurizer = make_union(self._baseline, self._experiment)

            baseline_features, experiment_features, baseline_valid_features, experiment_valid_features \
                = self._featurize(X_train_sample, y_train_sample, X_valid_sample, y_valid_sample,
                                  baseline_featurizer, experiment_featurizer, featurize_separately)

            # Train
            baseline_estimator = copy.deepcopy(self._estimator)
            experiment_estimator = self._estimator

            if baseline_estimator is not None:
                baseline_estimator.fit(baseline_features, y_train_sample)
            else:
                raise ClientException("baseline_estimator is not set.", has_pii=False)
            if experiment_estimator is not None:
                experiment_estimator.fit(experiment_features, y_train_sample)
            else:
                raise ClientException("experiment_estimator is not set.", has_pii=False)

            if self._scorer is not None:
                # Validate
                baseline_score = self._scorer.score(
                    estimator=baseline_estimator,
                    valid_features=baseline_valid_features,
                    y_actual=y_valid_sample
                )

                experiment_score = self._scorer.score(
                    estimator=experiment_estimator,
                    valid_features=experiment_valid_features,
                    y_actual=y_valid_sample
                )

                is_experiment_better = self._scorer.is_experiment_better_than_baseline(
                    baseline_score=baseline_score,
                    experiment_score=experiment_score,
                    epsilon=self._epsilon,
                    scale_epsilon=self._scale_epsilon)

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

        except Exception as e:
            logger.warning("{} {sweeper}: Failed due to exception.".format(class_name, sweeper=self))
            logging_utilities.log_traceback(e, logger, is_critical=False)
        finally:
            logger.info("{} {}: Finished sweeping.".format(class_name, self))
            return is_experiment_better

    def _featurize(self, X, y, X_valid, y_valid, baseline_featurizer,
                   experiment_featurizer, featurize_seperately):
        if featurize_seperately:
            baseline_features_list = []
            experiment_features_list = []
            baseline_features_valid_list = []
            experiment_features_valid_list = []
            for col in X:
                baseline_features_list.append(baseline_featurizer.fit_transform(X[col], y))
                experiment_features_list.append(experiment_featurizer.fit_transform(X[col], y))
                baseline_features_valid_list.append(baseline_featurizer.transform(X_valid[col]))
                experiment_features_valid_list.append(experiment_featurizer.transform(X_valid[col]))
            if scipy.sparse.issparse(baseline_features_list[0]):
                baseline_features = scipy.sparse.hstack(baseline_features_list)
                baseline_features_valid = scipy.sparse.hstack(baseline_features_valid_list)
            else:
                baseline_features = np.hstack(baseline_features_list)
                baseline_features_valid = np.hstack(baseline_features_valid_list)

            if scipy.sparse.issparse(experiment_features_list[0]):
                experiment_features = scipy.sparse.hstack(experiment_features_list)
                experiment_features_valid = scipy.sparse.hstack(experiment_features_valid_list)
            else:
                experiment_features = np.hstack(experiment_features_list)
                experiment_features_valid = np.hstack(experiment_features_valid_list)
        else:
            baseline_features = baseline_featurizer.fit_transform(X, y)
            experiment_features = experiment_featurizer.fit_transform(X, y)
            baseline_features_valid = baseline_featurizer.transform(X_valid)
            experiment_features_valid = experiment_featurizer.transform(X_valid)
        return baseline_features, experiment_features, baseline_features_valid, experiment_features_valid
