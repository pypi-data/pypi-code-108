# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File contains globally known feature Ids for automl features and static methods to generate input objects."""
from azureml._restclient.models.feature_config_request import FeatureConfigRequest

FEATURE_SWEEPING_ID = "feature_sweeping"
FEATURE_SWEEPING_VERSION = "1.7"
STREAMING_ID = "automatedml_sdk_largedatasupport"
STREAMING_VERSION = "1.0"


class CaclulatedExperimentInfo:
    """Caclulated experimentInfo class."""

    def __init__(
            self,
            num_rows: float,
            num_numerical_columns: int,
            num_categorical_columns: int,
            num_text_columns: int,
            machine_memory: float
    ) -> None:
        self.num_rows = num_rows
        self.num_numerical_columns = num_numerical_columns
        self.num_categorical_columns = num_categorical_columns
        self.num_text_columns = num_text_columns
        self.machine_memory = machine_memory


def _get_feature_sweeping_config_request(task_type: str, is_gpu: bool) -> FeatureConfigRequest:
    return FeatureConfigRequest(feature_version=FEATURE_SWEEPING_VERSION,
                                feature_id=FEATURE_SWEEPING_ID,
                                feature_metadata_map={
                                    'task': task_type,
                                    'is_gpu': is_gpu
                                })


def _get_streaming_config_request(caclulated_experiment_info: CaclulatedExperimentInfo) -> FeatureConfigRequest:
    return FeatureConfigRequest(
        feature_version=STREAMING_VERSION,
        feature_id=STREAMING_ID,
        feature_metadata_map={
            'experiment_info': {
                'num_rows': caclulated_experiment_info.num_rows,
                'num_numerical_columns': caclulated_experiment_info.num_numerical_columns,
                'num_categorical_columns': caclulated_experiment_info.num_categorical_columns,
                'num_text_columns': caclulated_experiment_info.num_text_columns,
                'machine_memory': caclulated_experiment_info.machine_memory
            }
        })
