# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for dataset categoricals."""
import logging

from typing import Any, List, Optional, Tuple

from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.shared.constants import LearnerColumns
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.model_wrappers import DropColumnsTransformer
from azureml.automl.runtime.shared.pipeline_spec import PipelineSpec
from azureml.automl.runtime.shared.problem_info import ProblemInfo


logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def get_column_transformer_pipeline(pipeline_spec: PipelineSpec, data_type: str = "X")\
        -> Optional[Tuple[str, DropColumnsTransformer]]:
    exp_store = ExperimentStore.get_instance()
    learner_mapping = None
    if pipeline_spec.accepts_categoricals():
        learner_mapping = exp_store.metadata.learner_columns_mapping.get(LearnerColumns.CatIndicatorLearners)
    elif not pipeline_spec.is_ensemble_pipeline():
        learner_mapping = exp_store.metadata.learner_columns_mapping.get(LearnerColumns.DefaultLearners)

    if learner_mapping and learner_mapping.get(data_type):
        indices_to_keep = learner_mapping[data_type]
        logger.info("Pipeline {} number of columns to consider {}".format(
                    pipeline_spec.pipeline_name, len(indices_to_keep)))
        return exp_store.transformers.get_column_transformer_pipeline_step(indices_to_keep)

    return None


def get_dataset_categoricals(data_type: str) -> List[int]:
    exp_store = ExperimentStore.get_instance()
    dataset_categoricals = exp_store.metadata.dataset_categoricals_dict.get(data_type, [])
    if dataset_categoricals:
        cat_learner_column_mapping = exp_store.metadata.learner_columns_mapping.get(
            LearnerColumns.CatIndicatorLearners)
        if cat_learner_column_mapping:
            indices_to_keep = cat_learner_column_mapping.get(data_type, [])
            if indices_to_keep:
                return [dataset_categoricals[i] for i in indices_to_keep]

    return []


def update_problem_info_preprocess_pipelines(pipeline_spec: PipelineSpec, problem_info: ProblemInfo,
                                             preprocess_pipelines: List[Tuple[str, Any]],
                                             data_type: str = "X") -> Tuple[ProblemInfo, List[Tuple[str, Any]]]:
    exp_store = ExperimentStore.get_instance()

    if exp_store.metadata.dataset_categoricals_dict:
        if pipeline_spec.accepts_categoricals() or pipeline_spec.is_ensemble_pipeline():
            # Get the right dataset_categoricals for the appropriate data, X, CV etc
            problem_info.dataset_categoricals = get_dataset_categoricals(data_type)

        # Get the column transformer pipeline
        column_transformer_pipeline = get_column_transformer_pipeline(pipeline_spec,
                                                                      data_type)
        if column_transformer_pipeline:
            preprocess_pipelines.append(column_transformer_pipeline)

    return problem_info, preprocess_pipelines
