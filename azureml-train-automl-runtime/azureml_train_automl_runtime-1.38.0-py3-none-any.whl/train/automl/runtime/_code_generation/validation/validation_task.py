# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from azureml.automl.runtime.shared.score.scoring import score_classification, score_regression

from ..constants import FunctionNames
from ..function import Function
from .data_splitting_strategy import AbstractDataSplittingStrategy
from .validation_strategy import AbstractValidationStrategy


class AbstractTask(ABC):
    TASK_TYPE = "unknown"

    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy,
        data_splitting_strategy: AbstractDataSplittingStrategy,
    ):
        self.metric_name = metric_name
        self.validation_strategy = validation_strategy
        self.data_splitting_strategy = data_splitting_strategy

    @abstractmethod
    def get_scoring_function(self) -> Function:
        raise NotImplementedError

    @property
    def task_type(self) -> str:
        return self.TASK_TYPE

    def get_cv_split_code(self, split_ratio: Optional[float], n_cross_validations: Optional[int]) -> List[str]:
        return [
            f"cv_splits = _CVSplits(X, y, frac_valid={split_ratio}, CV={n_cross_validations}, is_time_series=False"
            f", task='{self.task_type}')",
        ]


class ClassificationTask(AbstractTask):
    TASK_TYPE = "classification"

    def get_scoring_function(self) -> Function:
        function = Function(
            FunctionNames.CALCULATE_METRICS_NAME, "model", "X", "y", "sample_weights", "X_test", "y_test"
        )
        function.add_imports(score_classification)
        function.add_lines(
            "y_pred_probs = model.predict_proba(X_test)",
            "class_labels = np.unique(y)",
            "train_labels = model.classes_",
            "metrics = score_classification(",
            f"    y_test, y_pred_probs, ['{self.metric_name}'], class_labels, train_labels, use_binary=True)",
            "return metrics",
        )
        return function


class RegressionTask(AbstractTask):
    TASK_TYPE = "regression"

    def __init__(
        self,
        metric_name: str,
        validation_strategy: AbstractValidationStrategy,
        data_splitting_strategy: AbstractDataSplittingStrategy,
        y_min: Optional[float],
        y_max: Optional[float],
    ):
        self.y_min = y_min
        self.y_max = y_max
        super().__init__(metric_name, validation_strategy, data_splitting_strategy)

    def get_scoring_function(self) -> Function:
        bin_creation_imports, bin_creation_code = self.validation_strategy.get_bin_creation_code()
        function = Function(
            FunctionNames.CALCULATE_METRICS_NAME, "model", "X", "y", "sample_weights", "X_test", "y_test"
        )
        function.add_imports(score_regression)
        function.add_import_tuples(bin_creation_imports)
        function += [
            "y_pred = model.predict(X_test)",
            f"y_min = {self.y_min if self.y_min is not None else 'np.min(y)'}",
            f"y_max = {self.y_max if self.y_max is not None else 'np.max(y)'}",
            "y_std = np.std(y)",
            "",
        ]
        function += bin_creation_code
        function += [
            "metrics = score_regression(",
            f"    y_test, y_pred, ['{self.metric_name}'], y_max, y_min, y_std, sample_weights, bin_info)",
            "return metrics",
        ]
        return function
