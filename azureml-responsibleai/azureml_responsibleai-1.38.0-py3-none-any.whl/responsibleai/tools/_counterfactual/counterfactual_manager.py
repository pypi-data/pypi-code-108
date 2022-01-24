# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import uuid

from responsibleai import ModelAnalysis
from typing import Any, Dict, List, Optional

from azureml.core import Run
from azureml.interpret.common.constants import History

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes, AzureMLTypes, CounterfactualVersion, PropertyKeys)
from azureml.responsibleai.tools._counterfactual.counterfactual_client import (
    _upload_counterfactual_examples_internal, download_counterfactual_examples)
from azureml.responsibleai.tools._common.base_manager import BaseManager
from azureml.responsibleai.tools.model_analysis._requests.counterfactual_request import CounterfactualRequest


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CounterfactualManager(BaseManager):
    """Manager for diverse counterfactual analysis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(self) -> List[Dict[str, str]]:
        """List the computed counterfactual results."""
        assets = self._get_assets(AnalysisTypes.COUNTERFACTUAL_TYPE, str(CounterfactualVersion.V_0))
        summaries = []
        for asset in assets:
            summary = {
                History.ID: asset.properties.get(AssetProperties.UPLOAD_ID, None),
                History.COMMENT: asset.properties.get(History.COMMENT, None),
            }
            summaries.append(summary)
        return summaries

    def download_by_id(self, id: str):
        """Download counterfactual result by ID."""
        asset = self._get_asset(id, AnalysisTypes.COUNTERFACTUAL_TYPE, str(CounterfactualVersion.V_0))
        run = Run(self._experiment, run_id=asset.runid)
        upload_id = asset.properties[AssetProperties.UPLOAD_ID]
        return download_counterfactual_examples(run=run,
                                                counterfactual_examples_upload_id=upload_id,
                                                asset_type=AzureMLTypes.MODEL_ANALYSIS)

    def _compute_and_upload(
        self,
        requests: List[CounterfactualRequest],
        model_analysis: ModelAnalysis,
        run: Run,
    ):
        _logger.info(f"Computing and uploading {len(requests)} counterfactual results")

        for request in requests:
            model_analysis.counterfactual.add(
                method=request.method,
                total_CFs=request.total_CFs,
                desired_class=request.desired_class,
                desired_range=request.desired_range,
                permitted_range=request.permitted_range,
                features_to_vary=request.features_to_vary,
                feature_importance=request.feature_importance,
            )

        # TODO: Remove when deferred compute is removed
        model_analysis.compute()
        for result in model_analysis.counterfactual.get():
            self._upload(result, run, comment=request.comment)

        _logger.info("Counterfactual results computed and uploaded")

    def _upload(
        self,
        result: Any,
        run: Run,
        comment: Optional[str] = None,
    ):
        def _update_properties(prop_dict: Dict):
            _logger.info("Modifying properties for counterfactual")
            prop_dict[PropertyKeys.ANALYSIS_TYPE] = AnalysisTypes.COUNTERFACTUAL_TYPE
            prop_dict[PropertyKeys.ANALYSIS_ID] = self._model_analysis_run.settings.analysis_id
            prop_dict[PropertyKeys.VERSION] = str(CounterfactualVersion.V_0)

        asset_id = _upload_counterfactual_examples_internal(
            run,
            result,
            AzureMLTypes.MODEL_ANALYSIS,
            _update_properties,
            comment=comment,
            datastore_name=self._model_analysis_run.settings.confidential_datastore_name
        )

        props = {
            PropertyKeys.COUNTERFACTUAL_POINTER_FORMAT.format(uuid.uuid4()): asset_id
        }
        self._model_analysis_run.add_properties(props)
