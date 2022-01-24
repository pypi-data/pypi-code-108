# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Default sampler."""
from typing import cast, Any, List, Optional, Tuple, Union
import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared.types import CoreDataInputType, CoreDataSingleColumnInputType
from . import AbstractSampler, SplittingConfig


logger = logging.getLogger(__name__)


class CountSampler(AbstractSampler):
    """Default sampler."""

    def __init__(self,
                 seed: int,
                 min_examples_per_class: int = 2000,
                 max_rows: int = 10000,
                 is_constraint_driven: bool = True,
                 task: str = constants.Tasks.CLASSIFICATION,
                 train_frac: Optional[float] = None,
                 *args: Any, **kwargs: Any) -> None:
        """
        Create default sampler.

        :param seed: Random seed to use to sample.
        :param min_examples_per_class: Minimum examples per class to sample.
        :param max_rows: Maximum rows to output.
        :param is_constraint_driven: Is constraint driven or not.
        :param task: The task type corresponding to this sweeping experiment.
        :param train_frac: Fraction of data to be considered for constrained training.
        """
        super(CountSampler, self).__init__(seed=seed,
                                           task=task,
                                           max_rows=max_rows,
                                           is_constraint_driven=is_constraint_driven,
                                           train_frac=train_frac)
        self._min_examples_per_class = min_examples_per_class

    def sample(self, X: CoreDataInputType,
               y: CoreDataSingleColumnInputType,
               cols: Optional[Union[str, List[str]]] = None) \
            -> Tuple[CoreDataInputType, CoreDataSingleColumnInputType, SplittingConfig]:
        """
        Sample the give input data.

        :param X: Input data.
        :param y: Output label.
        :param cols: Optionally, the specific input column(s) over which to sample.
        :return: Sampled data.
        """
        if cols is not None:
            # Column argument only passed in from feature sweeping codepath, where X must be a DataFrame.
            Contract.assert_type(X, "X", expected_types=pd.DataFrame)
            X = cast(pd.DataFrame, X)[cols]

        n_rows = np.shape(X)[0]

        # For regression we want to use up to _max_rows from input
        n_train = self._max_rows

        # For classification, follow min max logic.
        # Aside from overall max_rows for exp, also have class-based max = n_classes * min_examples_per_class
        # Get minimum possible sample.
        if self._task == constants.Tasks.CLASSIFICATION:
            class_labels = np.unique(y)
            n_train_by_min_class_examples = len(class_labels) * self._min_examples_per_class
            n_train = min(n_train_by_min_class_examples, self._max_rows)

        train_frac, test_frac = self._get_train_test_frac(n_train=n_train, n_rows=n_rows)

        # Here we just scale down the dataset, the splitter will handle it further to do TrainValidation or CV split.
        sample_fraction = train_frac + test_frac
        stratify = y if self._task == constants.Tasks.CLASSIFICATION else None

        if sample_fraction < 1:
            try:
                X_sampled, _, y_sampled, _ = train_test_split(
                    X, y, train_size=sample_fraction, random_state=self._seed, stratify=stratify)
            except ValueError:
                # in case stratification fails, fall back to non-stratify train/test split
                X_sampled, _, y_sampled, _ = train_test_split(
                    X, y, train_size=sample_fraction, random_state=self._seed, stratify=None)

        else:
            X_sampled, y_sampled = X, y

        logger.debug("Feature sweeping sampling: train_frac = {}, test_frac={}".format(
            train_frac, test_frac))
        split_config = SplittingConfig(task=self._task,
                                       test_size=test_frac / (train_frac + test_frac),
                                       train_size=None)

        return X_sampled, y_sampled, split_config
