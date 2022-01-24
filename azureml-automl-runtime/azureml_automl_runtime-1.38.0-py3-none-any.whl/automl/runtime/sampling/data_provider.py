# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Default data splitter."""
from typing import Dict, List, Optional, Tuple, Union

import pickle
from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.runtime.shared.types import CoreDataInputType, CoreDataSingleColumnInputType
from . import IndexSplittingConfig, SplittingConfig


class DataProvider(ABC):
    """An abstract provider of dataset for doing sampling."""

    @abstractmethod
    def get_train_validation_sets(self, column: Optional[str] = None) \
            -> Tuple[CoreDataInputType, CoreDataInputType,
                     CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]:
        """Return a Tuple(X_train, X_valid, y_train, y_valid) from the input dataset."""
        raise NotImplementedError()

    @abstractmethod
    def get_cross_validation_sets(self, column: Optional[str] = None) \
            -> List[Tuple[CoreDataInputType, CoreDataInputType,
                          CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, X_valid, y_train, y_valid)."""
        raise NotImplementedError()


class InMemoryDataProvider(DataProvider):
    """Default data provider using in-memory representation of training data."""

    def __init__(self,
                 data: Union[Tuple[CoreDataInputType, CoreDataSingleColumnInputType, SplittingConfig],
                             Dict[str, Tuple[CoreDataInputType, CoreDataSingleColumnInputType, SplittingConfig]]],
                 seed: int = constants.hashing_seed_value) -> None:
        """
        Initializer for in-memory-based data provider. Meant for serving column-wise or overall samples.

        :param data: Either mapping between column names and columnwise (X, y, SplittingConfig) samples, or
        (X, y, SplittingConfig) sample taken from the input data over all columns.
        :param seed: Seed for randomization libraries.
        """
        self._columnwise_samples = \
            {}  # type: Dict[str, Tuple[CoreDataInputType, CoreDataSingleColumnInputType, SplittingConfig]]
        self._overall_sample = \
            None  # type: Optional[Tuple[CoreDataInputType, CoreDataSingleColumnInputType, SplittingConfig]]

        if isinstance(data, dict):
            self._columnwise_samples = data
        else:
            self._overall_sample = data
        self._random_seed = seed

    def get_train_validation_sets(self, column: Optional[str] = None) \
            -> Tuple[CoreDataInputType, CoreDataInputType,
                     CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]:
        """
        Get stored train and validation sets.

        :param column: Optionally, the column over which we want to sample.
        :return: Tuple(X_train, X_valid, y_train, y_valid) from the input dataset.
        """
        if column is not None and column in self._columnwise_samples:
            X_sample, y_sample, splitting_config = self._columnwise_samples[column]
        elif self._overall_sample is not None:
            X_sample, y_sample, splitting_config = self._overall_sample
        else:
            # Undefined: received neither a valid column or an overall sample
            raise ClientException("data_provider incorrectly set", has_pii=False)

        if isinstance(splitting_config, IndexSplittingConfig):
            # Preserve the train/test split already created by an advanced sampler.
            X_train_sample = X_sample.iloc[splitting_config.train_idxs]
            X_valid_sample = X_sample.iloc[splitting_config.test_idxs]
            y_train_sample = y_sample[splitting_config.train_idxs]
            y_valid_sample = y_sample[splitting_config.test_idxs]
        else:
            stratify = y_sample if splitting_config.task == constants.Tasks.CLASSIFICATION else None

            try:
                X_train_sample, X_valid_sample, y_train_sample, y_valid_sample = train_test_split(
                    X_sample, y_sample, train_size=splitting_config.train_size,
                    test_size=splitting_config.test_size, stratify=stratify, random_state=self._random_seed)
            except ValueError:
                # in case stratification fails, fall back to non-stratify train/test split
                X_train_sample, X_valid_sample, y_train_sample, y_valid_sample = train_test_split(
                    X_sample, y_sample, train_size=splitting_config.train_size,
                    test_size=splitting_config.test_size, stratify=None, random_state=self._random_seed)

        return X_train_sample, X_valid_sample, y_train_sample, y_valid_sample

    def get_cross_validation_sets(self, column: Optional[str] = None) \
            -> List[Tuple[CoreDataInputType, CoreDataInputType,
                          CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, y_train, X_valid, y_valid)."""
        raise NotImplementedError()


class DiskBasedDataProvider(DataProvider):
    """Data provider which uses files on disk to lazily load into memory the training set."""

    def __init__(self, pickled_data_file: str,
                 seed: int = constants.hashing_seed_value) -> None:
        """Initialize an instance of this class.

        :param pickled_data_file: the file where to read the input dataset from.
        :param seed: seed for randomization libraries.
        """
        self._pickled_dataset_file = pickled_data_file
        self._random_seed = seed
        self._decoratedProvider = None  # type: Optional[DataProvider]

    def get_train_validation_sets(self, column: Optional[str] = None) \
            -> Tuple[CoreDataInputType, CoreDataInputType,
                     CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]:
        """Return a Tuple(X_train, X_valid, y_train, y_valid) from the input dataset."""
        if self._decoratedProvider is None:
            self._decoratedProvider = self._lazy_create_provider()
        return self._decoratedProvider.get_train_validation_sets(column=column)

    def get_cross_validation_sets(self, column: Optional[str] = None) \
            -> List[Tuple[CoreDataInputType, CoreDataInputType,
                          CoreDataSingleColumnInputType, CoreDataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, X_valid, y_train, y_valid)."""
        if self._decoratedProvider is None:
            self._decoratedProvider = self._lazy_create_provider()
        return self._decoratedProvider.get_cross_validation_sets()

    def _lazy_create_provider(self) -> DataProvider:
        """Create lazily an InMemoryDataProvider from the input file holding the pickled dataset."""
        with open(self._pickled_dataset_file, "rb") as f:
            data = pickle.load(f)
            return InMemoryDataProvider(data, seed=self._random_seed)
