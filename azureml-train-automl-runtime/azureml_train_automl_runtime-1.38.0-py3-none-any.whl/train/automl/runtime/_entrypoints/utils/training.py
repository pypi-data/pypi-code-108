# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from typing import Any, Dict, Optional

from azureml._tracing import get_tracer
from azureml.automl.core.shared.constants import TelemetryConstants
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases import PhaseUtil
from azureml.train.automl.runtime._entrypoints import entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def load_onnx_converter(
    automl_settings: AzureAutoMLSettings,
    cache_store: CacheStore,
    parent_run_id: str
) -> Optional[OnnxConverter]:
    """called only from training entrypoints"""
    if not automl_settings.enable_onnx_compatible_models:
        return None

    with tracer.start_as_current_span(
            TelemetryConstants.SPAN_FORMATTING.format(
                TelemetryConstants.COMPONENT_NAME, TelemetryConstants.LOAD_ONNX_CONVERTER
            ),
            user_facing_name=TelemetryConstants.LOAD_ONNX_CONVERTER_USER_FACING
    ):
        onnx_cvt = PhaseUtil.build_onnx_converter(automl_settings.enable_split_onnx_featurizer_estimator_models)
        if onnx_cvt is None:
            return None
        logger.info('Get ONNX converter metadata from cache')
        cached_data_dict = cache_store.get([entrypoint_util.CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA])
        if cached_data_dict:
            onnx_cvt_init_metadata_dict = cached_data_dict.get(
                entrypoint_util.CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA, None)  # type: Optional[Dict[str, Any]]
            if onnx_cvt_init_metadata_dict is not None:
                logger.info('Initialize ONNX converter with cached metadata')
                onnx_cvt.initialize_with_metadata(metadata_dict=onnx_cvt_init_metadata_dict,
                                                  model_name=PhaseUtil.get_onnx_model_name(parent_run_id),
                                                  model_desc=PhaseUtil.get_onnx_model_desc(parent_run_id))
        if onnx_cvt.is_initialized():
            logger.info('Successfully initialized ONNX converter')
        else:
            logger.info('Failed to initialize ONNX converter')
        return onnx_cvt
