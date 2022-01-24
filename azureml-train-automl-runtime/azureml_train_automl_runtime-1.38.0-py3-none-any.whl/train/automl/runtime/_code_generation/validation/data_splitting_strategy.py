# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractDataSplittingStrategy(ABC):
    TASK_TYPE = "unknown"

    @staticmethod
    @abstractmethod
    def get_test_data_split_code(split_ratio: Optional[float]) -> List[str]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_valid_data_split_code(split_ratio: Optional[float]) -> List[str]:
        raise NotImplementedError


class ClassificationDataSplittingStrategy(AbstractDataSplittingStrategy):
    TASK_TYPE = "classification"

    @staticmethod
    def get_test_data_split_code(split_ratio: Optional[float]) -> List[str]:
        return [
            f"split_ratio = {split_ratio}",
            "try:",
            "    (X, y, sample_weights), _ = split_dataset("
            "X, y, sample_weights, split_ratio, should_stratify=True)",
            "except Exception:",
            "    (X, y, sample_weights), _ = split_dataset("
            "X, y, sample_weights, split_ratio, should_stratify=False)",
        ]

    @staticmethod
    def get_valid_data_split_code(split_ratio: Optional[float]) -> List[str]:
        return [
            f"split_ratio = {split_ratio}",
            "try:",
            "    (X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset("
            "X, y, sample_weights, split_ratio, should_stratify=True)",
            "except Exception:",
            "    (X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset("
            "X, y, sample_weights, split_ratio, should_stratify=False)",
        ]


class RegressionDataSplittingStrategy(AbstractDataSplittingStrategy):
    TASK_TYPE = "regression"

    @staticmethod
    def get_test_data_split_code(split_ratio: Optional[float]) -> List[str]:
        return [
            f"split_ratio = {split_ratio}",
            "(X, y, sample_weights), _ = split_dataset(X, y, sample_weights, split_ratio, should_stratify=False)"
        ]

    @staticmethod
    def get_valid_data_split_code(split_ratio: Optional[float]) -> List[str]:
        return [
            f"split_ratio = {split_ratio}",
            "(X_train, y_train, sample_weights_train), (X_valid, y_valid, sample_weights_valid) = split_dataset("
            "X, y, sample_weights, split_ratio, should_stratify=False)"
        ]
