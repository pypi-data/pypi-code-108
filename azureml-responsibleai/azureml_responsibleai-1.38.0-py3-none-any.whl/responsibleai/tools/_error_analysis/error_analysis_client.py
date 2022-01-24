# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The module handles the upload and download of the error analysis report to run history."""
import json
import os
from typing import Callable, Dict, List, Optional, Any

from erroranalysis._internal.error_report import ErrorReport

from azureml.core.run import Run
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._restclient.assets_client import AssetsClient
from azureml.exceptions import UserErrorException

from azureml.responsibleai.common._constants import AssetProperties, RAITool
from azureml.responsibleai.common._errors.error_definitions import ArgumentInvalidTypeError
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


class _ErrorAnalysisConstants:
    TreeKey = 'tree'
    MatrixKey = 'matrix'
    TreeFeaturesKey = 'tree_features'
    MatrixFeaturesKey = 'matrix_features'
    MetadataKey = 'metadata'
    Importances = 'importances'
    IDKey = 'id'

    ALL = [TreeKey,
           MatrixKey,
           TreeFeaturesKey,
           MatrixFeaturesKey,
           MetadataKey,
           Importances,
           IDKey]


_ERROR_ANALYSIS_UPLOAD_BYTES_LIMIT = 20 * 1024 * 1024


def _check_error_analysis_output_against_json_schema(error_analysis_dict):
    """
    Validate the error analysis report.

    :param error_analysis_dict: Serialized version of the error analysis report.
    :type error_analysis_dict: dict
    """
    schema_path = os.path.join(os.path.dirname(__file__),
                               'error_analysis_output_v0.0.json')
    with open(schema_path, 'r') as schema_file:
        schema_json = json.load(schema_file)

    _check_against_json_schema(schema_json, error_analysis_dict)


def _validate_error_analysis_dict(error_analysis_json_str: str) -> None:
    """
    Validate the serialized version of the error analysis ErrorReport.

    :param error_analysis_json_str: Serialized version of error analysis report.
    :type error_analysis_json_str: ErrorReport
    """
    _check_serialization_size(json.dumps(error_analysis_json_str),
                              _ERROR_ANALYSIS_UPLOAD_BYTES_LIMIT)

    error_analysis_dict = json.loads(error_analysis_json_str)

    if not isinstance(error_analysis_dict, dict):
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArgumentInvalidTypeError,
                arg_name='error_analysis_dict',
                type=type(error_analysis_dict),
                type_list=['dict'],
            )
        )

    # Verify the outputs against json schema
    _check_error_analysis_output_against_json_schema(error_analysis_dict)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'ErrorAnalysis'}, activity_type=LogCons.PUBLIC_API)
def upload_error_analysis(run: Run,
                          error_analysis_report: ErrorReport,
                          comment: Optional[str] = None,
                          datastore_name: Optional[str] = None) -> None:
    """Upload the error analysis to the run.

    :param run: A Run object into which the error analysis needs to be uploaded.
    :type run: azureml.core.Run
    :param error_analysis_report: The error analysis ErrorReport.
    :type error_analysis_report: ErrorReport
    :param datastore_name: The datastore to which the error_analysis_report should be uploaded
    :type datastore_name: str
    :param comment: An optional string to identify the error analysis report.
                    The string is displayed when listing error analysis,
                    which allows identification of uploaded error analysis reports.
    :type comment: str
    """
    def no_updates(props: Dict[str, str]) -> None:
        pass

    _upload_error_analysis_internal(run,
                                    error_analysis_report,
                                    get_asset_type_rai_tool(RAITool.ERRORANALYSIS),
                                    no_updates,
                                    comment,
                                    datastore_name)


def _upload_error_analysis_internal(run: Run,
                                    error_analysis_report: ErrorReport,
                                    asset_type: str,
                                    update_properties: Callable[[Dict[str, str]], None],
                                    comment: Optional[str] = None,
                                    datastore_name: Optional[str] = None) -> str:
    """Upload the error analysis report to the run.

    :param run: A Run object into which the error analysis report needs to be uploaded.
    :type run: azureml.core.Run
    :param error_analysis_report: The dictionary containing the error analysis report.
    :type error_analysis_report: Dict
    :param asset_type: Specifies the 'type' field of the created Asset
    :type asset_type: str
    :param update_properties: Callable which can modify the properties of the created Asset
    :type update_properties: Callable
    :param comment: An optional string to identify the error analysis report.
                    The string is displayed when listing error analysis,
                    which allows identification of uploaded error analysis reports.
    :type comment: str
    :param datastore_name: The datastore to which the error_analysis_report should be uploaded
    :type datastore_name: str
    :return: The id of the created Asset.
    :rtype: str
    """
    if not isinstance(error_analysis_report, ErrorReport):
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArgumentInvalidTypeError,
                arg_name='error_analysis_report',
                type=type(error_analysis_report),
                type_list=['ErrorReport'],
            )
        )
    error_analysis_json_str = error_analysis_report.to_json()
    _validate_error_analysis_dict(error_analysis_json_str)
    upload_id = error_analysis_report.id

    assets_client = AssetsClient(run.experiment.workspace.service_context)
    asset_artifact_list = []
    asset_properties = {}
    asset_properties[AssetProperties.UPLOAD_ID] = upload_id
    if comment is not None:
        asset_properties[AssetProperties.COMMENT] = comment

    # Call the supplied function to modify the properties if required
    update_properties(asset_properties)

    error_analysis_dict = json.loads(error_analysis_json_str)
    if _ErrorAnalysisConstants.Importances not in error_analysis_dict:
        error_analysis_dict[_ErrorAnalysisConstants.Importances] = None

    rai_error_analysis_artifact_client = RAIArtifactClient(run, datastore_name)
    for error_analysis_key in _ErrorAnalysisConstants.ALL:
        artifact_upload_return_code = rai_error_analysis_artifact_client.upload_single_object(
            target=error_analysis_dict[error_analysis_key],
            artifact_area_path=get_asset_name_rai_tool(RAITool.ERRORANALYSIS),
            upload_id=upload_id,
            artifact_type=error_analysis_key)
        asset_artifact_list.append(artifact_upload_return_code)

    asset = assets_client.create_asset(
        model_name=get_asset_name_rai_tool(RAITool.ERRORANALYSIS),
        artifact_values=asset_artifact_list,
        metadata_dict={},
        run_id=run.id,
        properties=asset_properties,
        asset_type=asset_type)
    return asset.id


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Counterfactual'}, activity_type=LogCons.PUBLIC_API)
def download_error_analysis(run: Run, error_analysis_upload_id: Optional[str] = None,
                            asset_type: Optional[str] = None,
                            comment: Optional[str] = None) -> ErrorReport:
    """Download the error analysis reports that were previously uploaded in the run.

    :param run: A Run object from which the error analysis reports need to be downloaded.
    :type run: azureml.core.Run
    :param error_analysis_upload_id: If specified, tries to download the error analysis
                                     from the run with the given error analysis ID.
                                     If unspecified, returns the most recently uploaded
                                     error analysis report.
    :type error_analysis_upload_id: str
    :param asset_type: Specifies the 'type' field of the created Asset
    :type asset_type: str
    :param comment: A string used to download the error analysis report based on the comment
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: The error analysis report.
    :rtype: ErrorReport
    """
    upload_id = search_rai_assets(run=run, rai_tool=RAITool.ERRORANALYSIS,
                                  asset_type=asset_type,
                                  query_upload_id=error_analysis_upload_id,
                                  query_comment=comment)
    downloaded_error_analysis = {}

    # When downloading, the datastore_name is not used
    rai_error_analysis_artifact_client = RAIArtifactClient(run)
    for error_analysis_key in _ErrorAnalysisConstants.ALL:
        downloaded_error_analysis[error_analysis_key] = \
            rai_error_analysis_artifact_client.download_single_object(
                artifact_area_path=get_asset_name_rai_tool(RAITool.ERRORANALYSIS),
                upload_id=upload_id,
                artifact_type=error_analysis_key)

    _check_error_analysis_output_against_json_schema(downloaded_error_analysis)
    error_analysis_json_str = json.dumps(downloaded_error_analysis)

    return ErrorReport.from_json(error_analysis_json_str)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Counterfactual'}, activity_type=LogCons.PUBLIC_API)
def list_error_analysis(run: Run, comment: Optional[str] = None) -> List[Dict[Any, Any]]:
    """Get the list of upload_ids of the error analysis reports available to a given Run.

    :param run: A Run object from which the error analysis reports need to be queried.
    :type run: azureml.core.Run
    :param comment: A string used to filter error analysis reports based on the strings
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: A list of dictionaries with upload GUIDs, comment and upload time of the uploaded
             error analysis reports.
    :rtype: list[Dict]
    """
    return list_rai_tool(run=run, rai_tool=RAITool.ERRORANALYSIS, comment=comment)
