# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from azureml.automl.core import _codegen_utilities
from azureml.automl.core._codegen_utilities import ImportInfoType
from azureml.automl.runtime.shared._cv_splits import _CVSplits
from azureml.automl.runtime.shared._dataset_binning import get_dataset_bins, make_dataset_bins
from azureml.automl.runtime.shared.score.scoring import aggregate_scores

from ..constants import FunctionNames
from .data_splitting_strategy import AbstractDataSplittingStrategy


class AbstractValidationStrategy(ABC):
    @abstractmethod
    def get_bin_creation_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        raise NotImplementedError

    @abstractmethod
    def get_scoring_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        raise NotImplementedError


class CrossValidationStrategy(AbstractValidationStrategy, ABC):
    def __init__(
        self, task_type: str, metric_name: str, validation_size: Optional[float], n_cross_validations: Optional[int]
    ):
        self.metric_name = metric_name
        self.task_type = task_type
        self.validation_size = validation_size
        self.n_cross_validations = n_cross_validations

    def get_bin_creation_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        import_info = [_codegen_utilities.get_import(get_dataset_bins)]
        code = [f"bin_info = {get_dataset_bins.__name__}(cv_splits, X, y)"]
        return import_info, code

    def get_scoring_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        import_info = [_codegen_utilities.get_import(_CVSplits), _codegen_utilities.get_import(aggregate_scores)]
        code = [
            f"cv_splits = {_CVSplits.__name__}(X, y, frac_valid={self.validation_size}, CV={self.n_cross_validations}"
            f", is_time_series=False, task='{self.task_type}')",
            "scores = []",
            "for X_train, y_train, sample_weights_train, X_valid, y_valid, sample_weights_valid in "
            "cv_splits.apply_CV_splits(X, y, sample_weights):",
            f"    partially_fitted_model = {FunctionNames.TRAIN_MODEL_FUNC_NAME}(X_train, y_train"
            f", sample_weights_train)",
            f"    metrics = {FunctionNames.CALCULATE_METRICS_NAME}("
            f"partially_fitted_model, X, y, sample_weights, X_test=X_valid, y_test=y_valid)",
            "    scores.append(metrics)",
            "    print(metrics)",
            f"model = {FunctionNames.TRAIN_MODEL_FUNC_NAME}(X_train, y_train, sample_weights_train)",
            "",
            f"aggregated_metrics = {aggregate_scores.__name__}(scores, ['{self.metric_name}'])",
            "print(aggregated_metrics)",
        ]
        return import_info, code


class SplitTrainingDataStrategy(AbstractValidationStrategy, ABC):
    def __init__(self, data_splitting_strategy: AbstractDataSplittingStrategy, split_ratio: Optional[float]):
        self.data_splitting_strategy = data_splitting_strategy

        # Set a sensible default
        if split_ratio is None or split_ratio == 0.0:
            split_ratio = 0.25

        self.split_ratio = split_ratio

    def get_bin_creation_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        import_info = [_codegen_utilities.get_import(make_dataset_bins)]
        code = [f"bin_info = {make_dataset_bins.__name__}(X_test.shape[0], y_test)"]
        return import_info, code

    def get_scoring_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        code = [
            *self.data_splitting_strategy.get_valid_data_split_code(self.split_ratio),
            f"model = {FunctionNames.TRAIN_MODEL_FUNC_NAME}(X_train, y_train, sample_weights_train)",
            "",
            f"metrics = {FunctionNames.CALCULATE_METRICS_NAME}("
            f"model, X, y, sample_weights, X_test=X_valid, y_test=y_valid)",
            "print(metrics)",
        ]
        return [], code


class SeparateValidationDataStrategy(AbstractValidationStrategy, ABC):
    """Separate validation dataset exists"""

    def get_bin_creation_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        import_info = [_codegen_utilities.get_import(make_dataset_bins)]
        code = [f"bin_info = {make_dataset_bins.__name__}(X_test.shape[0], y_test)"]
        return import_info, code

    def get_scoring_code(self) -> Tuple[List[ImportInfoType], List[str]]:
        code = [
            f"model = {FunctionNames.TRAIN_MODEL_FUNC_NAME}(X, y, sample_weights)",
            "",
            f"valid_df = {FunctionNames.GET_VALID_DATASET_FUNC_NAME}(validation_dataset_id)",
            f"X_valid, y_valid, sample_weights_valid = {FunctionNames.PREPARE_DATA_FUNC_NAME}(valid_df)",
            "",
            f"metrics = {FunctionNames.CALCULATE_METRICS_NAME}("
            f"model, X, y, sample_weights, X_test=X_valid, y_test=y_valid)",
            "print(metrics)",
        ]
        return [], code
