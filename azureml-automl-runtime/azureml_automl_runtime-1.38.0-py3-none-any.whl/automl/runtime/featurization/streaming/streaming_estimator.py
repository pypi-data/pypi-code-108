# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class for input backed by streaming supported transformers."""
from abc import ABC, abstractmethod
from typing import Any, List

from azureml.automl.runtime.shared.nimbus_wrappers import _process_bridgeerror_for_dataerror
from azureml.dataprep import Dataflow
from nimbusml import DprepDataStream
from nimbusml import Pipeline
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem
from nimbusml.internal.utils.entrypoints import BridgeRuntimeError
from azureml.automl.core.shared.exceptions import FitException, TransformException
from pandas import DataFrame


class StreamingEstimatorBase(ABC):
    """
    Base class for all estimators that can adhere to the streaming paradigm

    All sub-classes are required to override:
    1. A fit() method, that can accept and understand an AzureML Dataflow object.
    2. A transform() method that reads in a pandas.DataFrame object and produces a transformed pandas.DataFrame object

    The underlying framework should handle the batched transformation of StreamingInputType, depending on the memory
    pressures.
    """

    @abstractmethod
    def get_output_columns(self) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def fit(self, dataflow: Dataflow) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def transform(self, dataframe: DataFrame) -> DataFrame:
        raise NotImplementedError()


class NimbusMLStreamingEstimator(StreamingEstimatorBase):
    """
    Estimator class for NimbusML based estimators.
    """

    def __init__(self, steps: List[BasePipelineItem]):
        self._pipeline = Pipeline(steps=steps)

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline

    def get_output_columns(self) -> Any:
        try:
            return self._pipeline.get_output_columns()
        except BridgeRuntimeError as bre:
            _process_bridgeerror_for_dataerror(bre)
            raise FitException.from_exception(bre, has_pii=True, target="NimbusML").with_generic_msg(
                "nimbus ml failed at get_output_columns during featurization at {0}".format(bre.callstack))

    def fit(self, dataflow: Dataflow) -> Any:
        try:
            datastream_X = DprepDataStream(dataflow)
            self._pipeline.fit(datastream_X)
        except BridgeRuntimeError as bre:
            _process_bridgeerror_for_dataerror(bre)
            raise FitException.from_exception(bre, has_pii=True, target="NimbusML").with_generic_msg(
                "nimbus ml failed to fit during featurization at {0}".format(bre.callstack))

    def transform(self, dataframe: DataFrame) -> DataFrame:
        try:
            return self._pipeline.transform(dataframe)
        except BridgeRuntimeError as bre:
            _process_bridgeerror_for_dataerror(bre)
            raise TransformException.from_exception(bre, has_pii=True, target="NimbusML").with_generic_msg(
                "nimbus ml failed to transform at {0}".format(bre.callstack))
