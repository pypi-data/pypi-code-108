# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and methods for MLEngine."""

from .ml_engine import convert_to_onnx, featurize, validate, run_ensemble_selection
from .training import train
from .classification_ml_engine import evaluate_classifier
from .featurizer_suggestion import suggest_featurizers, suggest_featurizers_timeseries
from .regression_ml_engine import evaluate_regressor
from .timeseries_ml_engine import evaluate_timeseries, validate_timeseries

__all__ = [
    "validate",
    "featurize",
    "convert_to_onnx",
    "train",
    "suggest_featurizers",
    "suggest_featurizers_timeseries",
    "evaluate_classifier",
    "evaluate_regressor",
    "evaluate_timeseries",
    "validate_timeseries",
    "run_ensemble_selection"
]
