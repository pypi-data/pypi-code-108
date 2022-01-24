# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper for the final pipeline in the streaming scenario."""
from copy import deepcopy, copy
from typing import Any, Dict, Optional

from azureml.automl.core.shared.constants import Transformers
from azureml.automl.runtime.shared.model_wrappers import _AbstractModelWrapper
from azureml.automl.runtime.shared.nimbus_wrappers import NimbusMlPipelineWrapper
from azureml.automl.runtime.featurization.streaming import StreamingFeaturizationTransformer


class StreamingPipelineWrapper(_AbstractModelWrapper):
    """
    Wrapper for the final pipeline in the streaming scenario.

    Goals this wrapper aims to achieve:

        (1) Expose a FeaturizationInfoProvider as pipeline.steps[0] of the run's final pipeline.
            This API expectation is documented publicly in the non-streaming scenario, and we
            include it for parity.

        (2) Enable pipeline.fit() & pipeline.transform() for the final pipeline object.
            The FeaturizationInfoProvider cannot itself directly be a component of the Nimbus
            pipeline (we run into various Nimbus-specific errors). Instead, we internally compose
            a Nimbus pipeline (self._pipeline) & operate using that.
    """
    def __init__(
            self,
            streaming_featurization_transformer: Optional[StreamingFeaturizationTransformer],
            fitted_pipeline: NimbusMlPipelineWrapper) -> None:
        """Initialize this StreamingPipelineWrapper."""
        self._pipeline = deepcopy(fitted_pipeline)

        if len(self._pipeline.steps) == 1 or streaming_featurization_transformer is None:
            self._displayed_steps = self._pipeline.steps
            return

        self._displayed_steps = copy(self._pipeline.steps)
        self._displayed_steps[0] = (Transformers.X_TRANSFORMER, streaming_featurization_transformer)
        self._pipeline.steps = streaming_featurization_transformer.pipeline.steps + self._pipeline.steps[1:]

    @property
    def steps(self):
        return self._displayed_steps

    @property
    def named_steps(self) -> Dict[str, Any]:
        return {name: transformer for (name, transformer) in self._displayed_steps}

    @property
    def classes_(self):
        return getattr(self._pipeline, 'classes_', None)

    def fit(self, training_data, **kwargs):
        self._pipeline.fit(training_data, None, **kwargs)
        return self

    def fit_transform(self, training_data):
        self._pipeline.fit(training_data, None)
        return self._pipeline.transform(training_data)

    def get_model(self):
        return self._pipeline.model

    def predict(self, X, *args, **kwargs):
        return self._pipeline.predict(X, *args, **kwargs)

    def predict_proba(self, X, verbose=0, **kwargs):
        """Apply transforms to the data and predict class probabilities using the final estimator."""
        return self._pipeline.predict_proba(X, verbose, **kwargs)

    def transform(self, X, **kwargs):
        return self._pipeline.transform(X, **kwargs)

    def __str__(self) -> str:
        return "{}(steps={})".format(
            self.__class__.__name__,
            str(self._displayed_steps)
        )
