# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The module handles the upload and download of the causal insights to run history."""
import json
import uuid

from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from azureml.core.run import Run

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._restclient.assets_client import AssetsClient

from azureml.responsibleai.common._constants import AssetProperties, RAITool
from azureml.responsibleai.common._search_assets import (
    list_rai_tool, search_rai_assets, get_asset_name_rai_tool,
    get_asset_type_rai_tool)
from azureml.responsibleai.common.rai_artifact_client import RAIArtifactClient
from azureml.responsibleai.common.rai_validations import (
    _check_serialization_size, _check_against_json_schema)
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track


_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class _CausalInsightsKeys:
    GLOBAL_EFFECTS = 'global_effects'
    LOCAL_EFFECTS = 'local_effects'
    POLICIES = 'policies'

    ALL = [
        GLOBAL_EFFECTS,
        LOCAL_EFFECTS,
        POLICIES,
    ]


def _check_schema(causal_insights):
    """
    Validate the dictionary version of the causal insights.

    :param causal_insights: Serialized version of the causal insights.
    :type causal_insights: Dict
    """
    # TODO: Remove this validation once causal analysis
    # in the open source supports schema validation
    schema_path = Path(__file__).parent / 'causal_output_v2.0.json'
    with open(schema_path, 'r') as schema_file:
        schema_json = json.load(schema_file)

    _check_against_json_schema(schema_json, causal_insights)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Causal'}, activity_type=LogCons.PUBLIC_API)
def upload_causal_insights(
    run: Run,
    causal_insights: Dict,
    comment: Optional[str] = None,
    datastore_name: Optional[str] = None,
) -> str:
    """Upload causal insights to the run.

    :param run: A Run object into which the causal insights need to be uploaded.
    :type run: azureml.core.Run
    :param model_analysis_id: The ID for the top-level model analysis.
    :type model_analysis_id: str
    :param causal_insights: The dictionary containing the causal insights.
    :type causal_insights: Dict
    :param datastore_name: The datastore to which the causal_insights should be uploaded
    :type datastore_name: str
    :param comment: An optional string to identify the causal insights.
                    The string is displayed when listing causal insights,
                    which allows identification of uploaded causal insights.
    :type comment: str
    :return: The id of the created Asset.
    :rtype: str
    """
    def no_updates(props: Dict[str, str]) -> None:
        pass

    asset_type = get_asset_type_rai_tool(RAITool.CAUSAL)
    return _upload_causal_insights_internal(run, causal_insights, asset_type,
                                            no_updates, comment, datastore_name)


def _upload_causal_insights_internal(
    run: Run,
    causal_insights: Dict,
    asset_type: str,
    update_properties: Callable[[Dict[str, str]], None],
    comment: Optional[str] = None,
    datastore_name: Optional[str] = None
) -> str:
    """Upload the causal insights to the run.

    :param run: A Run object into which the causal insights need to be uploaded.
    :type run: azureml.core.Run
    :param causal_insights: The dictionary containing the causal insights.
    :type causal_insights: Dict
    :param asset_type: Specifies the 'type' field of the created Asset
    :type asset_type: str
    :param update_properties: Callable which can modify the properties of the created Asset
    :type update_properties: Callable
    :param comment: An optional string to identify the causal insights.
                    The string is displayed when listing causal insights,
                    which allows identification of uploaded causal insights.
    :type comment: str
    :param datastore_name: The datastore to which the causal_insights should be uploaded
    :type datastore_name: str
    :return: The id of the created Asset.
    :rtype: str
    """
    _check_serialization_size(json.dumps(causal_insights))
    _check_schema(causal_insights)
    upload_id = str(uuid.uuid4())

    asset_artifact_list = []
    artifact_client = RAIArtifactClient(run, datastore_name)
    for artifact_name in _CausalInsightsKeys.ALL:
        artifact_data = causal_insights[artifact_name]
        area_path = get_asset_name_rai_tool(RAITool.CAUSAL)
        artifact_upload_return_code = artifact_client.upload_single_object(
            target=artifact_data,
            artifact_area_path=area_path,
            upload_id=upload_id,
            artifact_type=artifact_name)
        asset_artifact_list.append(artifact_upload_return_code)

    asset_properties = {}
    asset_properties[AssetProperties.UPLOAD_ID] = upload_id
    if comment is not None:
        asset_properties[AssetProperties.COMMENT] = comment
    update_properties(asset_properties)

    assets_client = AssetsClient(run.experiment.workspace.service_context)
    asset = assets_client.create_asset(
        model_name=get_asset_name_rai_tool(RAITool.CAUSAL),
        artifact_values=asset_artifact_list,
        metadata_dict={},
        run_id=run.id,
        properties=asset_properties,
        asset_type=asset_type)
    return asset.id


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Causal'}, activity_type=LogCons.PUBLIC_API)
def download_causal_insights(
    run: Run,
    upload_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    comment: Optional[str] = None
) -> Dict:
    """Download the causal insights that were previously uploaded in the run.

    :param run: A Run object from which the causal insights need to be downloaded.
    :type run: azureml.core.Run
    :param upload_id: If specified, tries to download the causal insights
                      from the run with the given causal insights ID.
                      If unspecified, returns the most recently uploaded
                      causal insights.
    :type upload_id: str
    :param asset_type: Type of asset to download.
    :type asset_type: str
    :param comment: A string used to download the causal insights based on the comment
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: The dictionary containing all the causal insights.
    :rtype: Dict
    """
    upload_id = search_rai_assets(run=run,
                                  rai_tool=RAITool.CAUSAL,
                                  asset_type=asset_type,
                                  query_upload_id=upload_id,
                                  query_comment=comment)

    # When downloading, the datastore_name is not used
    downloaded_insights = {}
    rai_causal_artifact_client = RAIArtifactClient(run)
    for causal_insights_key in _CausalInsightsKeys.ALL:
        downloaded_insights[causal_insights_key] = rai_causal_artifact_client.download_single_object(
            artifact_area_path=get_asset_name_rai_tool(RAITool.CAUSAL),
            upload_id=upload_id,
            artifact_type=causal_insights_key)

    _check_schema(downloaded_insights)

    return downloaded_insights


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Causal'}, activity_type=LogCons.PUBLIC_API)
def list_causal_insights(
    run: Run,
    comment: Optional[str] = None
) -> List[Dict[Any, Any]]:
    """Get the list of upload_ids of the causal insights available to a given Run.

    :param run: A Run object from which the causal insights need to be queried.
    :type run: azureml.core.Run
    :param comment: A string used to filter causal insights based on the strings
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: A list of dictionaries with upload GUIDs, comment and upload time of the uploaded
             causal insights.
    :rtype: list[Dict]
    """
    return list_rai_tool(run=run, rai_tool=RAITool.CAUSAL, comment=comment)
