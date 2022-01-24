# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for handling the search and listing of assets for RAI tools."""
from typing import Optional, List, Dict

from azureml._common._error_definition import AzureMLError
from azureml._restclient.assets_client import AssetsClient
from azureml.core.run import Run
from azureml.exceptions import UserErrorException
from azureml.responsibleai.common._constants import AssetProperties, RAITool
from azureml.responsibleai.common._errors.error_definitions import AssetNotFoundError, InvalidRAIToolError


class RAIToolAssetName:
    CAUSAL = 'causal'
    COUNTERFACTUAL = 'counterfactual'
    ERRORANALYSIS = 'erroranalysis'


RAIToolAssetNameMapping = {
    RAITool.CAUSAL: RAIToolAssetName.CAUSAL,
    RAITool.COUNTERFACTUAL: RAIToolAssetName.COUNTERFACTUAL,
    RAITool.ERRORANALYSIS: RAIToolAssetName.ERRORANALYSIS
}


class RAIToolAssetType:
    CAUSAL = 'azureml.causal'
    COUNTERFACTUAL = 'azureml.counterfactual'
    ERRORANALYSIS = 'azureml.erroranalysis'


RAIToolAssetTypeMapping = {
    RAITool.CAUSAL: RAIToolAssetType.CAUSAL,
    RAITool.COUNTERFACTUAL: RAIToolAssetType.COUNTERFACTUAL,
    RAITool.ERRORANALYSIS: RAIToolAssetType.ERRORANALYSIS
}


def get_asset_name_rai_tool(rai_tool: RAITool) -> str:
    """Return the asset name for a RAI tool.

    :param rai_tool: Identifier for RAI tool.
    :type rai_tool: RAITool
    :return: The asset name used for the RAI tool.
    :rtype: str
    """
    rai_asset_name = RAIToolAssetNameMapping.get(rai_tool)
    if rai_asset_name is not None:
        return rai_asset_name
    else:
        raise UserErrorException._with_error(
            AzureMLError.create(
                InvalidRAIToolError,
                tool_name=rai_tool,
                target='rai_tool',
            )
        )


def get_asset_type_rai_tool(rai_tool: RAITool) -> str:
    """Return the asset type for a RAI tool.

    :param rai_tool: Identifier for RAI tool.
    :type rai_tool: RAITool
    :return: The asset type used for the RAI tool.
    :rtype: str
    """
    rai_asset_type = RAIToolAssetTypeMapping.get(rai_tool)
    if rai_asset_type is None:
        raise UserErrorException._with_error(
            AzureMLError.create(
                InvalidRAIToolError,
                tool_name=rai_tool,
                target='rai_tool',
            )
        )
    return rai_asset_type


def search_rai_assets(run: Run,
                      rai_tool: RAITool,
                      asset_type: Optional[str] = None,
                      query_upload_id: Optional[str] = None,
                      query_comment: Optional[str] = None) -> str:
    """Search for the upload-id of the previously uploaded RAI tool insight in the run.

    :param run: A Run object from which the RAI insights need to be searched.
    :type run: azureml.core.Run
    :param rai_tool: Identifier for RAI tool.
    :type rai_tool: RAITool
    :param asset_type: Type of asset to search.
    :type asset_type: str
    :param query_upload_id: If specified, tries to search the asset from the run with the
                            given upload ID. If unspecified, returns the most recently
                            uploaded RAI insight.
    :type query_upload_id: str
    :param query_comment: A string used to search the assets with. Requires an exact match.
    :type query_comment: str
    :return: The upload ID of the RAI insight.
    :rtype: str
    """
    if asset_type is None:
        asset_type = get_asset_type_rai_tool(rai_tool)
    asset_name = get_asset_name_rai_tool(rai_tool)

    assets_client = AssetsClient(run.experiment.workspace.service_context)
    query_props = {}
    if query_upload_id is not None:
        query_props[AssetProperties.UPLOAD_ID] = query_upload_id
    if query_comment is not None:
        query_props[AssetProperties.COMMENT] = query_comment

    all_rai_tool_assets = list(assets_client.list_assets_with_query(
        run_id=run.id,
        properties=query_props,
        asset_type=asset_type))

    upload_id = None
    for asset in all_rai_tool_assets:
        asset_upload_id = asset.properties.get(AssetProperties.UPLOAD_ID)
        asset_comment = asset.properties.get(AssetProperties.COMMENT)
        if query_upload_id is not None and query_upload_id == asset_upload_id:
            upload_id = asset_upload_id
            break
        if query_comment is not None and query_comment == asset_comment:
            upload_id = asset.properties[AssetProperties.UPLOAD_ID]
            break

    if upload_id is None:
        attributes = {}
        if query_upload_id is not None:
            attributes['upload_id'] = query_upload_id
        if query_comment is not None:
            attributes['comment'] = query_comment

        if query_upload_id is not None or query_comment is not None:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    AssetNotFoundError,
                    asset_type=asset_name,
                    attributes=attributes,
                )
            )

        all_rai_tools_assets = list(assets_client.list_assets_with_query(
            run_id=run.id,
            asset_type=asset_type))

        all_time_sorted_assets = sorted(all_rai_tools_assets, key=lambda asset: asset.created_time)

        if len(all_time_sorted_assets) > 0:
            upload_id = all_time_sorted_assets[-1].properties[AssetProperties.UPLOAD_ID]

    if upload_id is None:
        attributes = {}
        attributes['run_id'] = run.id
        raise UserErrorException._with_error(
            AzureMLError.create(
                AssetNotFoundError,
                asset_type=asset_name,
                attributes=attributes,
            )
        )

    return upload_id


def list_rai_tool(run: Run,
                  rai_tool: RAITool,
                  comment: Optional[str] = None) -> List[Dict]:
    """Get the list of upload_ids of RAI insights available to a given Run.

    :param run: A Run object from which the RAI insight need to be queried.
    :type run: azureml.core.Run
    :param rai_tool: Identifier for RAI tool.
    :type rai_tool: RAITool
    :param comment: A string used to filter RAI insights based on the strings
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: A list of dictionaries with upload GUIDs, comment and upload time of the uploaded
             RAI insights.
    :rtype: list[Dict]
    """
    assets_client = AssetsClient(run.experiment.workspace.service_context)
    asset_type = get_asset_type_rai_tool(rai_tool)

    asset_properties = {}
    if comment is not None:
        asset_properties[AssetProperties.COMMENT] = comment

    all_rai_assets = list(assets_client.list_assets_with_query(
        run_id=run.id,
        properties=asset_properties,
        asset_type=asset_type))

    available_rai_insights = []
    for asset in all_rai_assets:
        meta_dict = asset.properties
        meta_dict[
            AssetProperties.UPLOAD_TIME] = asset.created_time
        available_rai_insights.append(meta_dict)
    return available_rai_insights
