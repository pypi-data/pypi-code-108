# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all samplers."""
from typing import Any, Dict, List, Optional, Tuple, Union

from abc import ABC, abstractmethod

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentMismatch
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from . import SplittingConfig


class AbstractSampler(ABC):
    """Base class for all samplers."""

    @abstractmethod
    def __init__(self,
                 seed: int,
                 max_rows: int = 10000,
                 is_constraint_driven: bool = True,
                 task: str = constants.Tasks.CLASSIFICATION,
                 train_frac: Optional[float] = None,
                 *args: Any, **kwargs: Any) -> None:
        """
        Abstract initialization method for sweeping samplers. Cannot be called directly.

        :param seed: Random seed to use to sample.
        :param max_rows: Maximum rows to output during sampling.
        :param is_constraint_driven: Is the sweeping process constraint driven or not.
        :param task: The task type corresponding to this sweeping experiment.
        :param train_frac: Fraction of data to be considered for constrainted training.
        """
        self._task = task
        self._max_rows = max_rows
        self._seed = seed
        self._is_constraint_driven = is_constraint_driven
        self._train_frac = train_frac

    @abstractmethod
    def sample(self, X: DataInputType, y: DataSingleColumnInputType,
               cols: Optional[Union[str, List[str]]] = None) \
            -> Tuple[DataInputType, DataSingleColumnInputType, SplittingConfig]:
        """All sub classes should implement this."""
        raise NotImplementedError()

    def _get_train_test_frac(self,
                             n_train: int,
                             n_rows: int) -> Tuple[float, float]:
        """
        Calculate the train and test fractions of the dataset to be used during feature sweeping.

        :param n_train: The number of rows desired, not guaranteed, in the sample.
        :param n_rows: The number of rows in the input dataset from which we sample.
        :return: Tuple of (train, test) fractions of the dataset.
        """
        constraint_train_frac = n_train / float(n_rows)
        if self._is_constraint_driven:
            train_frac = constraint_train_frac
        else:
            if self._train_frac is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentMismatch, target="is_constraint_driven",
                        argument_names=', '.join(['is_constraint_driven', 'train_frac']),
                        value_list=', '.join([str(self._is_constraint_driven), str(None)])
                    )
                )
            train_frac = self._train_frac

        # in case it's a really small dataset; train_frac could be > 0.8 or even 1.
        train_frac = min(train_frac, 0.8)  # 0.8 guarantees 80-20 split

        # When sampling we want to use the same percentage for validation as well for more accurate scoring
        # but, for small datasets (where train > 50%) we need to make sure train & test don't overlap
        # hence the test_fraction would be 1 - train_frac.
        test_frac = train_frac if train_frac < 0.5 else 1 - train_frac

        return train_frac, test_frac

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
