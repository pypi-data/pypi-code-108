# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common constants for model analysis."""

import os

DEFAULT_MAXIMUM_ROWS_FOR_TEST_DATASET = 5000
SUBSAMPLE_SIZE = DEFAULT_MAXIMUM_ROWS_FOR_TEST_DATASET


class AzureMLTypes:
    """Strings for AzureML types (Runs and Assets)."""

    MODEL_ANALYSIS = 'azureml.modelanalysis'


class AnalysisTypes:
    """Strings to identify explanations, causal etc."""

    MODEL_ANALYSIS_TYPE = 'ModelAnalysis'

    CAUSAL_TYPE = 'Causal'
    COUNTERFACTUAL_TYPE = 'Counterfactual'
    ERROR_ANALYSIS_TYPE = 'ErrorAnalysis'
    EXPLANATION_TYPE = 'Explanation'


class ModelTypes:
    """The types of models that can be analysed."""
    BINARY_CLASSIFICATION = "binary_classification"


class PropertyKeys:
    """Keys for properties."""
    _PROPERTY_PREFIX = "_azureml."
    ANALYSIS_ID = _PROPERTY_PREFIX + 'ModelAnalysisId'
    ANALYSIS_TYPE = _PROPERTY_PREFIX + 'ModelAnalysisType'
    MODEL_ID = _PROPERTY_PREFIX + 'ModelId'
    MODEL_TYPE = _PROPERTY_PREFIX + 'ModelType'
    TRAIN_DATASET_ID = _PROPERTY_PREFIX + "TrainDatasetId"
    TEST_DATASET_ID = _PROPERTY_PREFIX + "TestDatasetId"
    VERSION = _PROPERTY_PREFIX + 'ModelAnalysisVersion'

    CAUSAL_POINTER_FORMAT = _PROPERTY_PREFIX + 'causal_{0}'
    COUNTERFACTUAL_POINTER_FORMAT = _PROPERTY_PREFIX + 'counterfactual_{0}'
    ERROR_ANALYSIS_POINTER_FORMAT = _PROPERTY_PREFIX + 'erroranalysis_{0}'
    EXPLANATION_POINTER_FORMAT = _PROPERTY_PREFIX + 'explanation_{0}'


class CausalVersion:
    """Supported versions on the causal Assets.

    This goes with the VERSION = 'ModelAnalysisVersion' key
    """
    V_0 = 0


class ExplanationVersion:
    """Supported versions on the explanation Assets.

    This goes with the VERSION = 'ModelAnalysisVersion' key
    """
    V_0 = 0


class CounterfactualVersion:
    """Supported versions on the counterfactual Assets.

    This goes with the VERSION = 'ModelAnalysisVersion' key
    """
    V_0 = 0


class ErrorAnalysisVersion:
    """Supported versions on the error analysis Assets.

    This goes with the VERSION = 'ModelAnalysisVersion' key
    """
    V_0 = 0


class ModelAnalysisFileNames:
    """Constants for data files in model analysis runs."""
    DATA_PREFIX = "data"
    TRAIN_DATA = os.path.join(DATA_PREFIX, "train_data.parquet")
    TRAIN_Y_PRED = os.path.join(DATA_PREFIX, "train_y_pred.parquet")
    TRAIN_Y_PROBA = os.path.join(DATA_PREFIX, "train_y_proba.parquet")
    TEST_DATA = os.path.join(DATA_PREFIX, "test_data.parquet")
    TEST_Y_PRED = os.path.join(DATA_PREFIX, "test_y_pred.parquet")
    TEST_Y_PROBA = os.path.join(DATA_PREFIX, "test_y_proba.parquet")

    TRAIN_DATA_JSON = os.path.join(DATA_PREFIX, "train_data.json")
    TRAIN_Y_PRED_JSON = os.path.join(DATA_PREFIX, "train_y_pred.json")
    TRAIN_Y_PROBA_JSON = os.path.join(DATA_PREFIX, "train_y_proba.json")
    TEST_DATA_JSON = os.path.join(DATA_PREFIX, "test_data.json")
    TEST_Y_PRED_JSON = os.path.join(DATA_PREFIX, "test_y_pred.json")
    TEST_Y_PROBA_JSON = os.path.join(DATA_PREFIX, "test_y_proba.json")

    SETTINGS = "settings.pkl"
    DATA_TYPES = "datatypes.pkl"
    CATEGORICAL_FEATURES = "categorical_features.json"
    TASK_TYPE = "task_type.json"

    OSS_EXPLANATION_JSON = 'oss_explanation.json'
