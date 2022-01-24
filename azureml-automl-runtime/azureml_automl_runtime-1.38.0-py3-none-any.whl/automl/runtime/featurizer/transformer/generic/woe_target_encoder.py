# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Weight of Evidence target encoder."""
import logging
from typing import Tuple, Dict, Optional, cast

import numpy as np
import pandas as pd
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.constants import Tasks
from .abstract_multiclass_target_encoder import AbstractMultiClassTargetEncoder
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal


class WoEBasedTargetEncoder(AbstractMultiClassTargetEncoder):
    """Weight of Evidence target encoder."""

    def __init__(self,
                 # TODO  Setting the regularization_param to 10 on par with the count target encoder.
                 # Need to revisit this.
                 regularization_param: float = 10,
                 task: str = Tasks.CLASSIFICATION,
                 classes: Optional[np.ndarray] = None) -> None:
        """Construct the target encoder.

        :param regularization_param : Value for avoiding division by 0
        :param task : Classification or Regression task type.
        :param classes: Different target values for classification, None for regression.
        """
        super().__init__(task, classes)
        self.regularization_param = regularization_param
        self.target_agg = {}  # type: Dict[str, Dict[str, float]]
        self._transformer_name = _SupportedTransformersInternal.WoETargetEncoder

    def get_params(self, deep=True):
        return {
            "regularization_param": self.regularization_param,
            "task": self._task,
            "classes": self._classes
        }

    def _get_imports(self):
        if self._classes is not None:
            new_imports = [
                (self._classes.__class__.__module__, "array", np.array)
            ]
        else:
            new_imports = []
        return super()._get_imports() + new_imports

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    @function_debug_log_wrapped()
    def get_map_for_target(self, X: pd.Series, y: pd.Series) -> \
            Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
        """
        Get map for data.

        :param X: Data to be transformed.
        :param y: Target data.
        :return: Computed categorical map using y as target.
        """
        prior = y.mean()

        target_agg = y.groupby(X).agg(['sum', 'count'])

        # TODO make count for novels a configurable parameter
        # Trying to remove novel categories, they can be represented by single value/bin
        target_agg = target_agg[target_agg['count'] > 1]

        target_agg['mean'] = target_agg['sum'] / target_agg['count']

        sum_agg = y.sum()
        count_agg = y.count()

        non_events = (target_agg['sum'] + self.regularization_param) / (sum_agg + 2 * self.regularization_param)
        events = ((target_agg['count'] - target_agg['sum']) + self.regularization_param) / \
                 (count_agg - sum_agg + 2 * self.regularization_param)

        woe = np.log(non_events / events)

        # Ignore unique values. This helps to prevent overfitting on id-like columns.
        woe[target_agg['count'] == 1] = 0

        target_agg['woe'] = woe

        target_agg = target_agg.to_dict(orient='index')

        return target_agg, prior

    def transform_target_class(self, X: pd.Series, curr_class_map: Dict[str, Dict[str, float]],
                               default_value: float) -> np.ndarray:
        """
        Return target encoded data for current input data.

        :param X: The data to transform.
        :param curr_class_map: map for current class
        :param default_value: default value to use when category not in map
        :return: Target encoded values from current X column and curr_class maps.
        """
        return cast(
            np.ndarray,
            X.apply(lambda x: curr_class_map.get(x, {'woe': default_value})['woe'])
        )
