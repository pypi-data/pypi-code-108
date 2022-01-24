# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import io
import json
import logging
import os

from typing import Dict, List

from responsibleai.serialization_utilities import serialize_json_safe
from responsibleai import ModelAnalysis

from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.constants import RUN_ORIGIN

from azureml.interpret import ExplanationClient
from azureml.interpret.common.constants import History

from azureml.responsibleai.common._constants import IOConstants
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes,
    AzureMLTypes,
    PropertyKeys,
    ExplanationVersion,
    ModelAnalysisFileNames
)

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


class ModelAnalysisExplanationClient(ExplanationClient):
    def __init__(self,
                 *,
                 service_context,
                 experiment_name,
                 run_id,
                 _run=None,
                 datastore_name=None,
                 model_analysis: ModelAnalysis,
                 analysis_id: str):
        super(ModelAnalysisExplanationClient,
              self).__init__(service_context,
                             experiment_name,
                             run_id,
                             _run,
                             datastore_name)
        self._analysis_id = analysis_id
        self._assets_client = AssetsClient(service_context)
        self._model_analysis = model_analysis

    @property
    def analysis_id(self) -> str:
        return self._analysis_id

    def _get_asset_type(self) -> str:
        """Return the type of Asset to be created."""
        _logger.info("Overriding default asset type for explanation")
        return AzureMLTypes.MODEL_ANALYSIS

    def _update_asset_properties(self, prop_dict: Dict):
        """Modify the properties of the about-to-be-created Asset."""
        _logger.info("Modifying properties for explanation")
        prop_dict[PropertyKeys.ANALYSIS_TYPE] = AnalysisTypes.EXPLANATION_TYPE
        prop_dict[PropertyKeys.ANALYSIS_ID] = self.analysis_id
        prop_dict[PropertyKeys.VERSION] = str(ExplanationVersion.V_0)

    def _extra_artifact_uploads(
            self,
            explanation,
            max_num_blocks,
            block_size,
            top_k,
            comment,
            init_dataset_id,
            eval_dataset_id,
            ys_pred_dataset_id,
            ys_pred_proba_dataset_id,
            upload_datasets,
            model_id,
            true_ys,
            visualization_points) -> List[Dict[str, str]]:
        """Upload extra artifacts

        Upload the extra JSON in format which Model Analysis
        Dashbaord expects.
        """
        _logger.info("Uploading extra explanation artifact")

        # Get and serialise the data
        extracted_data = self._model_analysis.explainer._get_interpret(
            explanation)
        json_string = json.dumps(
            extracted_data,
            default=serialize_json_safe
        )
        stream = io.BytesIO(json_string.encode(IOConstants.UTF8))

        upload_dir = './explanation/{}/'.format(
            explanation.id[:History.ID_PATH_2004])
        upload_path = "{0}/{1}".format(upload_dir,
                                       ModelAnalysisFileNames.OSS_EXPLANATION_JSON)
        _logger.info("Upload dir: {0}".format(upload_path))

        self.run.upload_file(upload_path,
                             stream,
                             datastore_name=self._datastore_name)

        item = {History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(
            RUN_ORIGIN,
            self.run.id,
            upload_dir,
            ModelAnalysisFileNames.OSS_EXPLANATION_JSON))}
        _logger.info("Uploaded to : {0}".format(item[History.PREFIX]))

        return [item]
