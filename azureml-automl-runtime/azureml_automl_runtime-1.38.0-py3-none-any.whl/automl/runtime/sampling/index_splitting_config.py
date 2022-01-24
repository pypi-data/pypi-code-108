# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration for sampling."""
import numpy as np

from azureml.automl.core.shared import constants
from . import SplittingConfig


class IndexSplittingConfig(SplittingConfig):
    """
    Config for how to split a sampled dataset for feature sweeping
    using explicit indices instead of train/test fractions.
    """

    def __init__(self,
                 train_idxs: np.ndarray,
                 test_idxs: np.ndarray,
                 task: str = constants.Tasks.CLASSIFICATION) -> None:
        """Initialize index-based splitting config.

        param train_idxs: Indices of rows to be used in train sample.
        param test_idxs: Indices of rows to be used in test sample.
        param task: ML task
        """
        super(IndexSplittingConfig, self).__init__(task=task)
        self.train_idxs = train_idxs
        self.test_idxs = test_idxs
