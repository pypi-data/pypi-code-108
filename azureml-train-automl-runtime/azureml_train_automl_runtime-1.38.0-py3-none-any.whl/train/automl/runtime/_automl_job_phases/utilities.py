# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Dict, Optional, Tuple, Union

from azureml.automl.runtime._data_definition import RawExperimentData

from azureml.automl.core.onnx_convert import OnnxConvertConstants
from azureml.automl.runtime.data_context import RawDataContext, DataContextParams
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.utilities import _get_package_version

logger = logging.getLogger(__name__)


class PhaseUtil:
    """Utils leveraged by AutoML job phases."""

    @staticmethod
    def build_onnx_converter(
        enable_split_onnx_featurizer_estimator_models: bool
    ) -> Optional[OnnxConverter]:
        """Build the ONNX converter for the run."""
        pkg_ver = _get_package_version()
        return OnnxConverter(
            version=pkg_ver,
            is_onnx_compatible=True,
            enable_split_onnx_featurizer_estimator_models=enable_split_onnx_featurizer_estimator_models)

    @staticmethod
    def build_raw_data_context(
        raw_experiment_data: RawExperimentData,
        data_context_params: DataContextParams
    ) -> RawDataContext:
        return RawDataContext(
            data_context_params=data_context_params,
            X=raw_experiment_data.X,
            y=raw_experiment_data.y,
            X_valid=raw_experiment_data.X_valid,
            y_valid=raw_experiment_data.y_valid,
            sample_weight=raw_experiment_data.weights,
            sample_weight_valid=raw_experiment_data.weights_valid,
            x_raw_column_names=raw_experiment_data.feature_column_names,
            cv_splits_indices=raw_experiment_data.cv_splits_indices,
            training_data=raw_experiment_data.training_data,
            validation_data=raw_experiment_data.validation_data,
            data_snapshot_str=raw_experiment_data.data_snapshot_str)

    @staticmethod
    def get_onnx_model_desc(parent_run_id: str) -> Dict[str, str]:
        """Get the description for the ONNX model."""
        return {'ParentRunId': parent_run_id}

    @staticmethod
    def get_onnx_model_name(parent_run_id: str) -> str:
        """Get the name for the ONNX model."""
        return '{}[{}]'.format(OnnxConvertConstants.OnnxModelNamePrefix, parent_run_id)

    @staticmethod
    def log_with_memory(info: str) -> None:
        logger.info(info)
        avail_memory = memory_utilities.get_available_physical_memory() / (1024 * 1024 * 1024)
        all_memory = memory_utilities.get_all_ram() / (1024 * 1024 * 1024)
        percentage_available = avail_memory * 100 / all_memory
        logger.info("Memory usage info:  "
                    "   RAM = {}GB  "
                    "   Available RAM = {}GB    "
                    "   Percentage RAM Available = {}".format(all_memory, avail_memory, percentage_available))
