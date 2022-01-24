# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for calculating the subsample percentage of dataset."""
from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn import model_selection

from azureml.automl.core.shared import constants
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.types import CoreDataInputType


def subsample_train_valid_set(
    subsample_percent: Union[int, float], random_state: Optional[int] = None
) -> Tuple[CoreDataInputType, CoreDataInputType, Optional[CoreDataInputType]]:
    """
    Get subsampled dataset using train/valid data from experiment store.

    :param subsample_percent: The percentage of training data to use for training. Ranges from (0, 100]
        with decimal or integer values.
    :param random_state: int, RandomState instance or None, optional
        (default=None) If int, random_state is the seed used by the
        random number generator; If RandomState instance, random_state
        is the random number generator; If None, the random number
        generator is the RandomState instance used by `np.random`.
    :return: X, y, sample_weight all subsampled by subsample_percent. If sample_weight will be None if
        the Experiment Store does not contain a sample weight.
    """
    assert subsample_percent > 0 and subsample_percent < 100
    subsample_frac = float(subsample_percent) / 100.0

    expr_store = ExperimentStore.get_instance()
    X, y, sample_weight = expr_store.data.materialized.get_train()
    if expr_store.metadata.task_type != constants.Tasks.CLASSIFICATION:
        train_y = None
    else:
        train_y = y

    n = X.shape[0]

    new_train_indices, _ = _train_test_split(
        data=np.arange(n), train_size=subsample_frac, stratify=train_y, random_state=random_state
    )

    if isinstance(X, pd.DataFrame):
        X = X.values

    X_new = X[new_train_indices]
    y_new = y[new_train_indices]
    sw_new = sample_weight[new_train_indices] if sample_weight else None

    return X_new, y_new, sw_new


def _train_test_split(
    data: CoreDataInputType,
    train_size: float,
    stratify: Optional[Iterable[Any]],
    random_state: Optional[Union[int, np.random.RandomState]],
) -> Tuple[CoreDataInputType, CoreDataInputType]:
    """
    Wrapper on `sklearn.model_selection.train_test_split` to gracefully fallback to random sampling in case
    stratified sampling fails.

    :param dataset: See ``arrays`` parameter of ``sklearn.model_selection.train_test_split`` method.
    :param train_size: See ``train_size`` parameter of ``sklearn.model_selection.train_test_split`` method.
    :param stratify: See ``stratify`` parameter of ``sklearn.model_selection.train_test_split`` method.
    :param random_state: See ``random_state`` parameter of ``sklearn.model_selection.train_test_split`` method.
    :return: Tuple of train indices and test indices.
    """
    try:
        train_size = float(train_size)
        train_indices, test_indices = model_selection.train_test_split(
            data, train_size=train_size, stratify=stratify, random_state=random_state
        )
    except ValueError:
        # Fall back to non-stratified sampling when stratification fails.
        train_indices, test_indices = model_selection.train_test_split(
            data, train_size=train_size, stratify=None, random_state=random_state
        )

    return train_indices, test_indices
