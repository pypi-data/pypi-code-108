# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic transformer for NimbusML based classifier models."""
from typing import Any, Optional
import logging

import numpy as np

from azureml.automl.core import _codegen_utilities
from azureml.automl.runtime.column_purpose_detection.columnpurpose_detector import StatsAndColumnPurposeType
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.runtime.shared.types import DataSingleColumnInputType, DataInputType
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.core.shared.exceptions import AutoMLException, FitException, TransformException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.transformer_runtime_exceptions import (
    NimbusMlTextTargetEncoderFeaturizerInvalidTypeException, NimbusMlTextTargetEncoderLearnerInvalidTypeException)
from ..automltransformer import AutoMLTransformer


_logger = logging.getLogger(__name__)


class NimbusMLTextTargetEncoder(AutoMLTransformer):
    """Generic class for NimbusML based classifier pipelines."""

    def __init__(self, featurizer: Any,
                 learner: Any) -> None:
        """
        Construct NimbusML based text target encoder.

        :param featurizer: Featurizer to be used.
        :type Any: Ideally should be of type nimbusml.internal.core.base_pipeline_item.BasePipelineItem
        :param learner: Learner to be used for training.
        :type Any: Ideally should be of type nimbusml.internal.core.base_pipeline_item.BasePipelineItem
        """
        from nimbusml import Pipeline as NimbusMLPipeline
        from nimbusml.multiclass import OneVsRestClassifier
        from nimbusml.preprocessing.schema import ColumnDropper
        from nimbusml.internal.core.base_pipeline_item import BasePipelineItem

        if not isinstance(featurizer, BasePipelineItem):
            raise NimbusMlTextTargetEncoderFeaturizerInvalidTypeException(
                "featurizer: Expecting type nimbusml.internal.core.base_pipeline_item.BasePipelineItem.",
                reference_code=ReferenceCodes._NIMBUS_INIT_WRONG_FEATURIZER_TYPE,
                has_pii=False)

        if not isinstance(learner, BasePipelineItem):
            raise NimbusMlTextTargetEncoderLearnerInvalidTypeException(
                "learner: Expecting type nimbusml.internal.core.base_pipeline_item.BasePipelineItem.",
                reference_code=ReferenceCodes._NIMBUS_INIT_WRONG_LEANER_TYPE,
                has_pii=False)

        super().__init__()
        self._featurizer = featurizer
        self._learner = learner
        self.pipeline = NimbusMLPipeline(
            [self._featurizer, OneVsRestClassifier(self._learner, use_probabilities=True)])
        self._pipeline_details = "{} Featurizer-'{}' Learner- {}".format(__name__,
                                                                         type(
                                                                             self._featurizer).__name__,
                                                                         type(self._learner).__name__)
        _logger.info(self._pipeline_details)
        self.column_dropper = ColumnDropper(columns=['PredictedLabel'])
        self._model = None

    def __repr__(self):
        params = {
            "featurizer": self._featurizer,
            "learner": self._learner
        }
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def _get_imports(self):
        return [
            (self._featurizer.__module__, self._featurizer.__class__.__name__, self._featurizer.__class__),
            (self._learner.__module__, self._learner.__class__.__name__, self._learner.__class__),
        ]

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(NimbusMLTextTargetEncoder, self)._to_dict()
        dct['id'] = "averaged_perceptron_text_target_encoder"
        dct['type'] = 'text'

        return dct

    @function_debug_log_wrapped()
    def fit(self, X: DataInputType, y: DataSingleColumnInputType = None) -> "NimbusMLTextTargetEncoder":
        """
        Nimbusml based classifier transform to learn conditional probablities for textual data.

        :param X: The data to transform.
        :type X: azureml.automl.runtime.shared.types.DataInputType
        :param y: Target values.
        :type y: azureml.automl.runtime.shared.types.DataSingleColumnInputType
        :return: The instance object: self.
        """
        try:
            self._model = self.pipeline.fit(X, y)
            return self
        except Exception as e:
            _logger.error("Failed during fit call.")
            raise FitException.from_exception(
                e,
                target="NimbusMLTextTargetEncoder",
                reference_code=ReferenceCodes._NIMBUS_FIT
            ).with_generic_msg("Exception while performing fit on NimbusMLTextTargetEncoder pipeline")

    @function_debug_log_wrapped()
    def transform(self, X: DataInputType) -> DataInputType:
        """
        Transform data x.

        :param X: The data to transform.
        :type X: azureml.automl.runtime.shared.types.DataInputType
        :return: Prediction probability values from NimbusML based classifier model.
        """
        try:
            return self.predict_proba(X)
        except AutoMLException:
            raise
        except Exception as e:
            _logger.error("Failed during transform call.")
            raise TransformException.from_exception(
                e,
                target="NimbusMLTextTargetEncoder",
                reference_code=ReferenceCodes._NIMBUS_TRANSFORM
            ).with_generic_msg("Exception while transforming data using NimbusMLTextTargetEncoder")

    @function_debug_log_wrapped()
    def predict_proba(self, X: DataInputType) -> DataInputType:
        """
        Predict probability for the input text data.

        :param X: The data to predict.
        :type X: azureml.automl.runtime.shared.types.DataInputType
        """
        if self._model is None:
            _logger.error("No model found for NimbusMLTextTargetEncoder.")
            raise TransformException(
                "No model found. Call 'fit' method first.",
                target="NimbusMLTextTargetEncoder",
                reference_code=ReferenceCodes._NIMBUS_PREDICT_PROBA,
                has_pii=False
            )
        try:
            scores = self._model.predict(X)
            # drop column
            output = self.column_dropper.fit_transform(scores)
            return output
        except Exception:
            _logger.error("Failed during predict_proba call.")
            raise

    @function_debug_log_wrapped()
    def predict(self, X: DataInputType) -> DataInputType:
        """
        Predict probability for the input text data.

        :param X: The data to predict.
        :type X: azureml.automl.runtime.shared.types.DataInputType
        """
        return self.predict_proba(X)

    def get_model(self) -> Any:
        """
        Return inner NimbusML Pipeline.

        :return: NimbusML pipeline.
        """
        return self._model

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint estimate for this transformer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken.
        """
        num_rows = len(X)
        n_classes = len(np.unique(y))
        f_size = memory_utilities.get_data_memory_size(float)
        return num_rows * n_classes * f_size
