# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for top level text transformation logic."""
from typing import Optional

import logging

from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared import constants
from ..featurizer.transformer.automltransformer import AutoMLTransformer

logger = logging.getLogger(__name__)


class TextTransformer(AutoMLTransformer):
    """Deprecated in favor of static_suggestions.suggest_featurizers_for_text_data."""

    def __init__(self,
                 task_type: Optional[str] = constants.Tasks.CLASSIFICATION,
                 is_onnx_compatible: bool = False,
                 featurization_config: Optional[FeaturizationConfig] = None):
        """
        Preprocessing class for Text.

        :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
        :param logger: The logger to use.
        :param is_onnx_compatible: If works in onnx compatible mode.
        :param featurization_config: Configuration used for custom featurization.
        """
        # Retaining the class for Backward compatibility.
        raise DeprecationWarning('Deprecating in favor of static_suggestions.suggest_featurizers_for_text_data')
