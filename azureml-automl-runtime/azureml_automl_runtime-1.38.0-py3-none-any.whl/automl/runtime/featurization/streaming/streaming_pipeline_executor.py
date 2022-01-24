# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pickle
from typing import List

from azureml.automl.runtime.featurization.streaming import StreamingEstimatorBase
from azureml.dataprep import Dataflow


class StreamingPipelineExecutor:

    @staticmethod
    def execute_pipeline(estimators: List[StreamingEstimatorBase], dataflow: Dataflow) -> Dataflow:
        # todo should group by different estimators later on
        assert len(estimators) == 1, "Expecting only NimbusML estimators for now"
        estimators[0].fit(dataflow)
        return dataflow.map_partition(lambda df, index: estimators[0].transform(df))
