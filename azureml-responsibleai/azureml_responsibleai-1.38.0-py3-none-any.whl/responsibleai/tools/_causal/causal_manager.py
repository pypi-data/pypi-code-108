# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from responsibleai import ModelAnalysis
# TODO: The CausalResult class needs to be made public
from responsibleai._tools.causal.causal_result import CausalResult
from typing import List, Optional

from azureml.core import Run
from azureml.interpret.common.constants import History

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.tools._causal.causal_client import (
    _upload_causal_insights_internal, download_causal_insights)
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes, AzureMLTypes, CausalVersion, PropertyKeys)
from azureml.responsibleai.tools._common.base_manager import BaseManager
from azureml.responsibleai.tools.model_analysis._requests.causal_request import CausalRequest

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CausalManager(BaseManager):
    """Manager for causal analysis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(self) -> List[CausalResult]:
        """List the computed causal analyses."""
        assets = self._get_assets(AnalysisTypes.CAUSAL_TYPE, str(CausalVersion.V_0))
        summaries = []
        for asset in assets:
            summary = {
                History.ID: asset.properties.get(AssetProperties.UPLOAD_ID, None),
                History.COMMENT: asset.properties.get(History.COMMENT, None),
            }
            summaries.append(summary)
        return summaries

    def download_by_id(self, id: str):
        """Download causal result by ID."""
        asset = self._get_asset(id, AnalysisTypes.CAUSAL_TYPE, str(CausalVersion.V_0))
        run = Run(self._experiment, run_id=asset.runid)
        upload_id = asset.properties[AssetProperties.UPLOAD_ID]
        return download_causal_insights(run, upload_id=upload_id, asset_type=AzureMLTypes.MODEL_ANALYSIS)

    def _compute_and_upload(
        self,
        requests: List[CausalRequest],
        model_analysis: ModelAnalysis,
        run: Run,
    ):
        _logger.info(f"Computing and uploading {len(requests)} causal results")

        for request in requests:
            result = model_analysis.causal.add(
                treatment_features=request.treatment_features,
                heterogeneity_features=request.heterogeneity_features,
                nuisance_model=request.nuisance_model,
                heterogeneity_model=request.heterogeneity_model,
                alpha=request.alpha,
                upper_bound_on_cat_expansion=request.upper_bound_on_cat_expansion,
                treatment_cost=request.treatment_cost,
                min_tree_leaf_samples=request.min_tree_leaf_samples,
                max_tree_depth=request.max_tree_depth,
                skip_cat_limit_checks=request.skip_cat_limit_checks,
                n_jobs=request.n_jobs,
                categories=request.categories,
                verbose=request.verbose,
                random_state=request.random_state,
            )

            self._upload(result, run, comment=request.comment)

        _logger.info("Causal results computed and uploaded")

    def _upload(
        self,
        result: CausalResult,
        run: Run,
        comment: Optional[str] = None,
    ):
        def _update_properties(props):
            _logger.info("Modifying properties for causal")
            props[PropertyKeys.ANALYSIS_TYPE] = AnalysisTypes.CAUSAL_TYPE
            props[PropertyKeys.ANALYSIS_ID] = self._model_analysis_run.settings.analysis_id
            props[PropertyKeys.VERSION] = str(CausalVersion.V_0)

        asset_id = _upload_causal_insights_internal(
            run,
            # TODO: Start using result.save() instead once the model analysis client supports data on disk
            result._get_dashboard_data(),
            asset_type=AzureMLTypes.MODEL_ANALYSIS,
            update_properties=_update_properties,
            comment=comment,
            datastore_name=self._model_analysis_run.settings.confidential_datastore_name)

        props = {PropertyKeys.CAUSAL_POINTER_FORMAT.format(result.id): asset_id}
        self._model_analysis_run.add_properties(props)
