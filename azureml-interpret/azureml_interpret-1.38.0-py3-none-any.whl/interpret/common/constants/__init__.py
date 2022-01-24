# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains classes defining constants used in interpretability in Azure Machine Learning.

For more information about interpretability, see [Interpretability: model explanations in automated machine
learning](https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl).
"""
from interpret_community.common.constants import ExplanationParams, \
    ExplainType, ExplainParams, Defaults, Attributes, Dynamic, Tensorflow, SKLearn, \
    Spacy, ModelTask, LightGBMParams, ShapValuesOutput, \
    ExplainableModelType, MimicSerializationConstants, LightGBMSerializationConstants, \
    DNNFramework

__all__ = ['Attributes', 'BackCompat', 'Defaults', 'Dynamic',
           'DNNFramework', 'ExplainableModelType', 'ExplainParams',
           'ExplainType', 'ExplanationParams', 'History', 'IO',
           'LightGBMParams', 'LightGBMSerializationConstants',
           'LoggingNamespace', 'MimicSerializationConstants',
           'ModelTask', 'RunPropertiesAndTags', 'Scoring',
           'ShapValuesOutput', 'SKLearn', 'Spacy', 'Tensorflow']


class BackCompat(object):
    """Provide constants necessary for supporting old versions of our product."""

    FEATURE_NAMES = 'feature_names'
    GLOBAL_IMPORTANCE_NAMES = 'global_importance_names'
    GLOBAL_IMPORTANCE_RANK = 'global_importance_rank'
    GLOBAL_IMPORTANCE_VALUES = 'global_importance_values'
    NAME = 'name'
    OLD_NAME = 'old_name'
    OVERALL_FEATURE_ORDER = 'overall_feature_order'
    OVERALL_IMPORTANCE_ORDER = 'overall_importance_order'
    OVERALL_SUMMARY = 'overall_summary'
    PER_CLASS_FEATURE_ORDER = 'per_class_feature_order'
    PER_CLASS_IMPORTANCE_ORDER = 'per_class_importance_order'
    PER_CLASS_SUMMARY = 'per_class_summary'
    SHAP_VALUES = 'shap_values'


class IO(object):
    """Provide file input and output related constants."""

    JSON = 'json'
    PICKLE = 'pickle'
    UTF8 = 'utf-8'


class Scoring(object):
    """Provide constants for scoring time explainers."""

    EXPLAINER = 'explainer'
    SURROGATE_MODEL = 'surrogate_model'


class RunPropertiesAndTags(object):
    """Provide constants for tracking tags and properties set on the Run object."""

    MODEL_EXPLANATION_TAG = "model_explanation"


class LoggingNamespace(object):
    """Provide logging namespace related constants."""

    AZUREML = 'azureml'


class History(object):
    """Provide constants related to uploading assets to run history."""

    ASSET_TYPE = 'azureml.explanation'
    BLOCK_SIZE = 'block_size'
    CLASSES = 'classes'
    COMMENT = 'comment'
    EVAL_DATA = 'eval_data'
    EVAL_DATASET_ID = 'eval_dataset_id'
    EVAL_DATA_VIZ = 'eval_data_viz'
    TRUE_YS_VIZ = 'true_ys_viz'
    YS_PRED_VIZ = 'ys_pred_viz'
    YS_PRED_PROBA_VIZ = 'ys_pred_proba_viz'
    LOCAL_IMPORTANCE_VIZ = 'local_importance_viz'
    EVAL_DATA_VIZ_INDICES = 'eval_data_viz_indices'
    EVAL_Y_PRED = 'eval_y_predicted'
    EVAL_Y_PRED_PROBA = 'eval_y_predicted_proba'
    EXPECTED_VALUES = 'expected_values'
    EXPERIMENT_ID = 'experiment_id'
    EXPERIMENT_NAME = 'experiment_name'
    EXPLANATION = 'explanation'
    EXPLANATION_ASSET = 'explanation_asset'
    EXPLANATION_ASSET_TYPE_V2 = 'azureml.v2.model.explanation'
    EXPLANATION_ASSET_TYPE_V3 = 'azureml.v3.model.explanation'
    EXPLANATION_ASSET_TYPE_V4 = 'azureml.v4.model.explanation'
    EXPLANATION_ASSET_TYPE_V5 = 'azureml.v5.model.explanation'
    EXPLANATION_ASSET_TYPE_V6 = 'azureml.v6.model.explanation'
    EXPLANATION_ASSET_TYPE_V7 = 'azureml.v7.model.explanation'
    EXPLANATION_ASSET_TYPE_V8 = 'azureml.v8.model.explanation'
    EXPLANATION_ID = 'explanation_id'
    FEATURES = 'features'
    GLOBAL = 'global'
    GLOBAL_NAMES = 'global_names'
    GLOBAL_RANK = 'global_rank'
    GLOBAL_VALUES = 'global_values'
    ID = 'id'
    INDICES = 'indices'
    INIT_DATA = 'init_data'
    INIT_DATASET_ID = 'init_dataset_id'
    LOCAL = 'local'
    LOCAL_IMPORTANCE_RANK = 'local_importance_rank'
    LOCAL_IMPORTANCE_VALUES = 'local_importance_values'
    LOCAL_IMPORTANCE_VALUES_SPARSE = 'local_importance_values_sparse'
    MAX_NUM_BLOCKS = 'max_num_blocks'
    METADATA_ARTIFACT = 'metadata_artifact_path'
    METHOD = 'method'
    MODEL_ID = 'model_id'
    NAME = 'name'
    NUM_BLOCKS = 'num_blocks'
    NUM_CLASSES = 'num_classes'
    NUM_EXAMPLES = 'num_examples'
    NUM_FEATURES = 'num_features'
    ORDERED_LOCAL_IMPORTANCE_VALUES = 'ordered_local_importance_values'
    ID_PATH_2004 = 8
    PER_CLASS_NAMES = 'per_class_names'
    PER_CLASS_RANK = 'per_class_rank'
    PER_CLASS_VALUES = 'per_class_values'
    PREFIX = 'prefix'
    PROPERTIES = 'properties'
    RANKED_GLOBAL_NAMES = 'ranked_global_names'
    RANKED_GLOBAL_VALUES = 'ranked_global_values'
    RANKED_PER_CLASS_NAMES = 'ranked_per_class_names'
    RANKED_PER_CLASS_VALUES = 'ranked_per_class_values'
    RICH_METADATA = 'rich_metadata'
    SPARSE_DATA = 'sparse_data'
    TYPE = 'type'
    UPLOAD_TIME = 'upload_time'
    VERSION = 'version'
    VERSION_TYPE = 'version_type'
    VISUALIZATION_DICT = 'visualization_dict'
    YS_PRED = 'ys_pred'
    YS_PRED_PROBA = 'ys_pred_proba'


class Serialization(object):
    """Provide constants for serialization."""

    LOGGER = '_logger'


class VizData(object):
    """Provide constants for viz data."""

    TEST_DATA = 'testData'
    INDICES = History.INDICES
    TRUE_Y = 'trueY'
    PREDICTED_Y = 'predictedY'
    PROBABILITY_Y = 'probabilityY'
    PRECOMPUTED_LOCAL_FEATURE_IMPORTANCE_SCORES = \
        'precomputedExplanations.localFeatureImportance.scores'
    PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_SCORES = \
        'precomputedExplanations.globalFeatureImportance.scores'
    PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_NAMES = \
        'precomputedExplanations.globalFeatureImportance.featureNames'
    DATA_SUMMARY_FEATURE_NAMES = 'dataSummary.featureNames'
    DATA_SUMMARY_CLASS_NAMES = 'dataSummary.classNames'
    PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_INTERCEPT = \
        'precomputedExplanations.globalFeatureImportance.intercept'
    PRECOMPUTED_LOCAL_FEATURE_IMPORTANCE_INTERCEPT = \
        'precomputedExplanations.localFeatureImportance.intercept'
