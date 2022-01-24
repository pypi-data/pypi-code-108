# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from responsibleai import ModelAnalysis
from typing import Any, Dict, List, Optional

from azureml.core import Run

from azureml.interpret.common.constants import ExplainType, History

from azureml.responsibleai.tools._common.base_manager import BaseManager
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes, PropertyKeys, ExplanationVersion)
from azureml.responsibleai.tools._explain.model_analysis_explanation_client import (
    ModelAnalysisExplanationClient)
from azureml.responsibleai.tools.model_analysis._requests.explain_request import ExplainRequest


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ExplanationManager(BaseManager):
    """Manager for model explanations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(self) -> List[Dict[str, str]]:
        """List the computed model explanations."""
        assets = self._get_assets(AnalysisTypes.EXPLANATION_TYPE, str(ExplanationVersion.V_0))
        summaries = []
        for asset in assets:
            summary = {
                History.ID: asset.properties.get(History.EXPLANATION_ID),
                History.COMMENT: asset.properties.get(History.COMMENT),
                ExplainType.DATA: asset.properties.get(ExplainType.DATA),
                ExplainType.EXPLAIN: asset.properties.get(ExplainType.EXPLAIN),
                ExplainType.MODEL: asset.properties.get(ExplainType.MODEL),
                ExplainType.IS_RAW: asset.properties.get(ExplainType.IS_RAW),
                ExplainType.IS_ENG: asset.properties.get(ExplainType.IS_ENG),
                History.UPLOAD_TIME: asset.created_time
            }
            summaries.append(summary)
        return summaries

    def download_by_id(self, id: str):
        """Download model explanation by ID."""
        asset = self._get_asset(id, AnalysisTypes.EXPLANATION_TYPE, str(ExplanationVersion.V_0),
                                id_property=History.EXPLANATION_ID)

        client = ModelAnalysisExplanationClient(service_context=self._service_context,
                                                experiment_name=self._experiment_name,
                                                run_id=asset.runid,
                                                analysis_id=self.analysis_id,
                                                model_analysis=None)
        explain_id = asset.properties[History.EXPLANATION_ID]
        return client.download_model_explanation(explanation_id=explain_id)

    def _compute_and_upload(
        self,
        requests: List[ExplainRequest],
        model_analysis: ModelAnalysis,
        run: Run,
    ):
        _logger.info(f"Computing and uploading {len(requests)} explanations")

        for request in requests:
            model_analysis.explainer.add()

        # TODO: Remove when deferred compute is removed
        model_analysis.compute()
        for result in model_analysis.explainer.get():
            self._upload(result, run, model_analysis, comment=request.comment)

        _logger.info("Explain results computed and uploaded")

    def _upload(
        self,
        result: Any,
        run: Run,
        model_analysis: ModelAnalysis,
        comment: Optional[str] = None,
    ):
        client = ModelAnalysisExplanationClient(
            service_context=run.experiment.workspace.service_context,
            experiment_name=run.experiment,
            run_id=run.id,
            _run=run,
            datastore_name=self._model_analysis_run.settings.confidential_datastore_name,
            # TODO: Start using result.save() instead once the model analysis client supports data on disk
            model_analysis=model_analysis,
            analysis_id=self._model_analysis_run.settings.analysis_id,
        )

        asset_id = client._upload_model_explanation_internal(result, comment=comment)
        props = {
            PropertyKeys.EXPLANATION_POINTER_FORMAT.format(result.id): asset_id
        }
        self._model_analysis_run.add_properties(props)
