# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from responsibleai import ModelAnalysis
from typing import Any, Dict, List, Optional

from azureml.core import Run

from azureml.interpret.common.constants import History

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.tools._error_analysis.error_analysis_client import (
    _upload_error_analysis_internal, download_error_analysis)
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes, AzureMLTypes, PropertyKeys, ErrorAnalysisVersion)
from azureml.responsibleai.tools.model_analysis._requests.error_analysis_request import ErrorAnalysisRequest

from azureml.responsibleai.tools._common.base_manager import BaseManager


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ErrorAnalysisManager(BaseManager):
    """Manager for error analysis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(self) -> List[Dict[str, str]]:
        """List the computed error analysis results."""
        assets = self._get_assets(AnalysisTypes.ERROR_ANALYSIS_TYPE, str(ErrorAnalysisVersion.V_0))
        summaries = []
        for asset in assets:
            summary = {
                History.ID: asset.properties.get(AssetProperties.UPLOAD_ID, None),
                History.COMMENT: asset.properties.get(History.COMMENT, None),
                History.UPLOAD_TIME: asset.created_time
            }
            summaries.append(summary)
        return summaries

    def download_by_id(self, id: str):
        """Download error analysis result by ID."""
        asset = self._get_asset(id, AnalysisTypes.ERROR_ANALYSIS_TYPE, str(ErrorAnalysisVersion.V_0))
        run = Run(self._experiment, run_id=asset.runid)
        upload_id = asset.properties[AssetProperties.UPLOAD_ID]
        return download_error_analysis(run, upload_id, asset_type=AzureMLTypes.MODEL_ANALYSIS)

    def _compute_and_upload(
        self,
        requests: List[ErrorAnalysisRequest],
        model_analysis: ModelAnalysis,
        run: Run,
    ):
        _logger.info(f"Computing and uploading {len(requests)} error analysis results")

        for request in requests:
            model_analysis.error_analysis.add(
                max_depth=request.max_depth,
                num_leaves=request.num_leaves,
                filter_features=request.filter_features,
            )

        # TODO: Remove when deferred compute is removed
        model_analysis.compute()
        for result in model_analysis.error_analysis.get():
            self._upload(result, run, comment=request.comment)

        _logger.info("Error analysis results computed and uploaded")

    def _upload(
        self,
        result: Any,
        run: Run,
        comment: Optional[str] = None,
    ):
        def _update_properties(prop_dict: Dict):
            _logger.info("Modifying properties for error analysis")
            prop_dict[PropertyKeys.ANALYSIS_TYPE] = AnalysisTypes.ERROR_ANALYSIS_TYPE
            prop_dict[PropertyKeys.ANALYSIS_ID] = self._model_analysis_run.settings.analysis_id
            prop_dict[PropertyKeys.VERSION] = str(ErrorAnalysisVersion.V_0)

        asset_id = _upload_error_analysis_internal(
            run,
            result,
            AzureMLTypes.MODEL_ANALYSIS,
            _update_properties,
            comment=comment,
            datastore_name=self._model_analysis_run.settings.confidential_datastore_name
        )

        props = {
            PropertyKeys.ERROR_ANALYSIS_POINTER_FORMAT.format(result.id): asset_id
        }
        self._model_analysis_run.add_properties(props)
