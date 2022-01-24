# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


_AZUREML_FAIRNESS_NAME = "AzureMLFairness"

_DASHBOARD_SCHEMA_TYPE = "dashboardDictionary"


class FairlearnDashboardKeys:
    """Contains keys as they appear in the dashboard dictionary."""
    PREDICTION_TYPE = "predictionType"
    Y_TRUE = "trueY"
    Y_PRED = "predictedY"
    METRICS = "precomputedMetrics"
    SENSITIVE_FEATURES = "precomputedFeatureBins"
    SENSITIVE_FEATURE_NAME = "featureBinName"
    SENSITIVE_FEATURE_CLASSES = "binLabels"
    SENSITIVE_FEATURE_VALUES = "binVector"
    MODEL_NAMES = "modelNames"
    SCHEMA_TYPE = "schemaType"
    SCHEMA_VERSION = "schemaVersion"


class FairlearnDashboardPredictionTypes:
    """Contains the prediction types as they appear in the dashboard dictionary."""
    BINARY_CLASSIFICATION = "binaryClassification"
    REGRESSION = "regression"
    PROBABILITY = "probability"

    VALID_TYPES = {BINARY_CLASSIFICATION, REGRESSION, PROBABILITY}


class AssetPropertyKeys:
    """Contains the keys which we will store in the Properties of the Assets."""
    DASHBOARD_NAME = "dashboard_name"
    DATASET_ID = "dataset_id"
    DATASET_NAME = "dataset_name"
    EXPERIMENT_ID = "experiment_id"
    FAIRNESS_ASSET_TYPE = "fairness_asset_type"
    MODEL_ID = "model_id"
    PREDICTION_TYPE = "prediction_type"
    SENSITIVE_FEATURES_COLUMN_NAME = "sensitive_features_column_name"
    UPLOAD_ID = "upload_id"
    VERSION = "version"


class AssetPredictionTypes:
    """Contains the prediction types as stored in Asset properties."""
    BINARY_CLASSIFICATION = "binary_classification"
    REGRESSION = "regression"
    PROBABILITY = "probability"


class FairnessAssetTypes:
    """Defines the types of Asset we store."""
    FAIRNESS_ASSET = "azureml.fairness"

    DASHBOARD_METRICS = "dashboard.metrics"


class FairnessDashboardArtifactTypes:
    """The different Artifact types which are in an uploaded dashboard."""
    METRICS_SET = "metrics_set"
    SENSITIVE_FEATURES_COLUMN = "sensitive_features_column"
    Y_PRED = "y_pred"
    Y_TRUE = "y_true"

    VALID_ARTIFACT_TYPES = {
        METRICS_SET,
        SENSITIVE_FEATURES_COLUMN,
        Y_PRED,
        Y_TRUE
    }


class PredictionTypeConvertors:
    """Contains dictionaries for converting prediction types.

    Converts between those stored in the Asset and those
    in the dictionary.
    """
    ASSET_TO_DASHBOARD = {
        # Binary classification
        AssetPredictionTypes.BINARY_CLASSIFICATION:
        FairlearnDashboardPredictionTypes.BINARY_CLASSIFICATION,
        # Regression
        AssetPredictionTypes.REGRESSION:
        FairlearnDashboardPredictionTypes.REGRESSION,
        # Probability
        AssetPredictionTypes.PROBABILITY:
        FairlearnDashboardPredictionTypes.PROBABILITY
    }

    DASHBOARD_TO_ASSET = {
        # Binary classification
        FairlearnDashboardPredictionTypes.BINARY_CLASSIFICATION:
        AssetPredictionTypes.BINARY_CLASSIFICATION,
        # Regression
        FairlearnDashboardPredictionTypes.REGRESSION:
        AssetPredictionTypes.REGRESSION,
        # Probability
        FairlearnDashboardPredictionTypes.PROBABILITY:
        AssetPredictionTypes.PROBABILITY
    }


class IOConstants:
    """Contains IO related constants."""
    JSON = 'json'
    UTF8 = 'utf-8'
    ARTIFACT_PREFIX = 'prefix'
