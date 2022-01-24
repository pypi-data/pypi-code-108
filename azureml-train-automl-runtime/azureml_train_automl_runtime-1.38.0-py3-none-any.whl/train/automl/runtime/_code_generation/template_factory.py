# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Optional

from sklearn.pipeline import Pipeline

from .data_featurizer_template import DataFeaturizerTemplate
from .featurizer_template import AbstractFeaturizerTemplate, NoFeaturizerTemplate
from .preprocessor_template import (
    AbstractPreprocessorTemplate,
    NamedPreprocessorTemplate,
    NoPreprocessorTemplate,
    PreprocessorTemplate,
)
from .timeseries_featurizer_template import TimeSeriesFeaturizerTemplate
from .validation.data_splitting_strategy import (
    AbstractDataSplittingStrategy,
    ClassificationDataSplittingStrategy,
    RegressionDataSplittingStrategy,
)
from .validation.validation_strategy import (
    AbstractValidationStrategy,
    CrossValidationStrategy,
    SeparateValidationDataStrategy,
    SplitTrainingDataStrategy,
)
from .validation.validation_task import AbstractTask, ClassificationTask, RegressionTask


class FeaturizerTemplateFactory:
    def select_template(self, pipeline: Pipeline, task_type: str) -> AbstractFeaturizerTemplate:
        if DataFeaturizerTemplate.can_handle(pipeline):
            return DataFeaturizerTemplate(pipeline, task_type)
        elif TimeSeriesFeaturizerTemplate.can_handle(pipeline):
            return TimeSeriesFeaturizerTemplate(pipeline)
        elif NoFeaturizerTemplate.can_handle(pipeline):
            return NoFeaturizerTemplate()
        raise NotImplementedError


class PreprocessorTemplateFactory:
    def select_template(self, pipeline: Pipeline, name: Optional[Any] = None) -> AbstractPreprocessorTemplate:
        if name is not None:
            if NamedPreprocessorTemplate.can_handle(pipeline):
                return NamedPreprocessorTemplate(pipeline, name)
        elif PreprocessorTemplate.can_handle(pipeline):
            return PreprocessorTemplate(pipeline)
        if NoPreprocessorTemplate.can_handle(pipeline):
            return NoPreprocessorTemplate()
        raise NotImplementedError


class ValidationTemplateFactory:
    def select_template(
        self,
        task_type: str,
        metric_name: str,
        has_valid_dataset: bool,
        validation_size: Optional[float],
        n_cross_validations: Optional[int],
        y_min: Optional[float],
        y_max: Optional[float],
    ) -> AbstractTask:
        if task_type == ClassificationDataSplittingStrategy.TASK_TYPE:
            data_splitting_strategy = ClassificationDataSplittingStrategy()  # type: AbstractDataSplittingStrategy
        elif task_type == RegressionDataSplittingStrategy.TASK_TYPE:
            data_splitting_strategy = RegressionDataSplittingStrategy()
        else:
            raise NotImplementedError(f"No validation strategy for task '{task_type}'")

        if has_valid_dataset:
            validation_strategy = SeparateValidationDataStrategy()  # type: AbstractValidationStrategy
        elif n_cross_validations:
            validation_strategy = CrossValidationStrategy(task_type, metric_name, validation_size, n_cross_validations)
        else:
            validation_strategy = SplitTrainingDataStrategy(data_splitting_strategy, validation_size)

        if task_type == ClassificationTask.TASK_TYPE:
            return ClassificationTask(metric_name, validation_strategy, data_splitting_strategy)
        elif task_type == RegressionTask.TASK_TYPE:
            return RegressionTask(metric_name, validation_strategy, data_splitting_strategy, y_min, y_max)

        raise NotImplementedError(f"No task template for task '{task_type}'")


featurizer_template_factory = FeaturizerTemplateFactory()
preprocessor_template_factory = PreprocessorTemplateFactory()
validation_template_factory = ValidationTemplateFactory()
