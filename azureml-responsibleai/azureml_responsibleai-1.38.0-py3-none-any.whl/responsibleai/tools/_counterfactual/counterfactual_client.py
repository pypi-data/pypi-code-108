# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The module handles the upload and download of the counterfactual examples to run history."""
import json
import uuid

from pathlib import Path
from typing import Callable, Dict, List, Optional

from dice_ml.counterfactual_explanations import CounterfactualExplanations

from azureml.core.run import Run
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition import AzureMLError
from azureml._restclient.assets_client import AssetsClient
from azureml.exceptions import UserErrorException

from azureml.responsibleai.common.rai_artifact_client import RAIArtifactClient
from azureml.responsibleai.common.rai_validations import _check_serialization_size, _check_against_json_schema
from azureml.responsibleai.common._constants import AssetProperties, RAITool
from azureml.responsibleai.common._errors.error_definitions import (
    ArgumentInvalidTypeError, ArtifactMissingFieldError,
    SchemaVersionNotSupportedError)
from azureml.responsibleai.common._search_assets import (
    list_rai_tool, search_rai_assets, get_asset_name_rai_tool,
    get_asset_type_rai_tool)
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class _CommonSchemaConstants:
    LOCAL_IMPORTANCE = 'local_importance'
    METADATA = 'metadata'
    SUMMARY_IMPORTANCE = 'summary_importance'
    VERSION = 'version'


class _V1SchemaConstants:
    CF_EXAMPLES_LIST = 'cf_examples_list'
    LOCAL_IMPORTANCE = _CommonSchemaConstants.LOCAL_IMPORTANCE
    METADATA = _CommonSchemaConstants.METADATA
    SUMMARY_IMPORTANCE = _CommonSchemaConstants.SUMMARY_IMPORTANCE

    ALL = [CF_EXAMPLES_LIST, LOCAL_IMPORTANCE, METADATA, SUMMARY_IMPORTANCE]


class _V2SchemaConstants:
    CFS_LIST = 'cfs_list'
    DATA_INTERFACE = 'data_interface'
    DESIRED_CLASS = 'desired_class'
    DESIRED_RANGE = 'desired_range'
    FEATURE_NAMES = 'feature_names'
    FEATURE_NAMES_INCLUDING_TARGET = 'feature_names_including_target'
    LOCAL_IMPORTANCE = _CommonSchemaConstants.LOCAL_IMPORTANCE
    METADATA = _CommonSchemaConstants.METADATA
    MODEL_TYPE = 'model_type'
    SUMMARY_IMPORTANCE = _CommonSchemaConstants.SUMMARY_IMPORTANCE
    TEST_DATA = 'test_data'

    ALL = [CFS_LIST, DATA_INTERFACE, DESIRED_CLASS, DESIRED_RANGE,
           FEATURE_NAMES, FEATURE_NAMES_INCLUDING_TARGET,
           LOCAL_IMPORTANCE, METADATA, MODEL_TYPE,
           SUMMARY_IMPORTANCE, TEST_DATA]


class _SchemaVersions:
    V1 = '1.0'
    V2 = '2.0'

    ALL_VERSIONS = [V1, V2]


_COUNTERFACTUALS_SIZE_LIMIT_BYTES = 20 * 1024 * 1024  # 20MB


def _get_schema_version(counterfactuals_dict: Dict) -> str:
    """
    Get the version from the serialized version of the counterfactual examples.

    :param counterfactuals_dict: Serialized version of the counterfactual example.
    :type counterfactuals_dict: Dict
    """
    if _CommonSchemaConstants.METADATA not in counterfactuals_dict:
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArtifactMissingFieldError,
                artifact='counterfactuals_dict',
                field='metadata',
            )
        )

    metadata = counterfactuals_dict[_CommonSchemaConstants.METADATA]
    if _CommonSchemaConstants.VERSION not in metadata:
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArtifactMissingFieldError,
                artifact='counterfactuals_dict',
                field='metadata.version',
            )
        )

    version = metadata[_CommonSchemaConstants.VERSION]
    if version not in _SchemaVersions.ALL_VERSIONS:
        raise UserErrorException._with_error(
            AzureMLError.create(
                SchemaVersionNotSupportedError,
                version=version,
                artifact='counterfactuals_dict',
            )
        )

    return version


def _validate_counterfactuals_with_schema(counterfactuals_dict: Dict) -> None:
    """
    Validate the dictionary version of the counterfactual examples.

    :param counterfactuals_dict: Serialized version of the counterfactual example.
    :type counterfactuals_dict: Dict
    """
    version = _get_schema_version(counterfactuals_dict)
    schema_file_name = 'counterfactual_examples_output_v{}.json'.format(version)
    schema_path = Path(__file__).parent / schema_file_name
    with open(schema_path, 'r') as schema_file:
        schema_json = json.load(schema_file)

    _check_against_json_schema(schema_json, counterfactuals_dict)


def _validate_counterfactuals_dict(counterfactuals_json_str: str) -> None:
    """
    Validate the serialized version of the counterfactual examples.

    :param counterfactuals_json_str: Serialized version of the counterfactual example.
    :type counterfactuals_json_str: str
    """
    _check_serialization_size(counterfactuals_json_str, _COUNTERFACTUALS_SIZE_LIMIT_BYTES)

    counterfactuals_dict = json.loads(counterfactuals_json_str)

    if not isinstance(counterfactuals_dict, dict):
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArgumentInvalidTypeError,
                arg_name='counterfactuals_dict',
                type=type(counterfactuals_dict),
                type_list=['dict'],
            )
        )

    _validate_counterfactuals_with_schema(counterfactuals_dict)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Counterfactual'}, activity_type=LogCons.PUBLIC_API)
def upload_counterfactual_examples(run: Run,
                                   counterfactual_examples: CounterfactualExplanations,
                                   comment: Optional[str] = None,
                                   datastore_name: Optional[str] = None) -> None:
    """Upload the counterfactual examples to the run.

    :param run: A Run object into which the counterfactual examples need to be uploaded.
    :type run: azureml.core.Run
    :param counterfactual_examples: The counterfactual example object.
    :type counterfactual_examples: dice_ml.counterfactual_explanations.CounterfactualExplanations
    :param comment: An optional string to identify the counterfactual examples.
                    The string is displayed when listing counterfactual examples,
                    which allows identification of uploaded counterfactual examples.
    :type comment: str
    :param datastore_name: The datastore to which the counterfactual_examples should be uploaded
    :type datastore_name: str
    """
    def no_updates(props: Dict[str, str]) -> None:
        pass

    _upload_counterfactual_examples_internal(run,
                                             counterfactual_examples,
                                             get_asset_type_rai_tool(RAITool.COUNTERFACTUAL),
                                             no_updates,
                                             comment,
                                             datastore_name)


def _upload_counterfactual_examples_internal(run: Run,
                                             counterfactual_examples: CounterfactualExplanations,
                                             asset_type: str,
                                             update_properties: Callable[[Dict[str, str]], None],
                                             comment: Optional[str] = None,
                                             datastore_name: Optional[str] = None) -> str:
    """Upload the counterfactual examples to the run.

    :param run: A Run object into which the counterfactual examples need to be uploaded.
    :type run: azureml.core.Run
    :param counterfactual_examples: The counterfactual example object.
    :type counterfactual_examples: dice_ml.counterfactual_explanations.CounterfactualExplanations
    :param comment: An optional string to identify the counterfactual examples.
                    The string is displayed when listing counterfactual examples,
                    which allows identification of uploaded counterfactual examples.
    :type comment: str
    :param asset_type: Specifies the 'type' field of the created Asset
    :type asset_type: str
    :param update_properties: Callable which can modify the properties of the created Asset
    :type update_properties: Callable
    :param datastore_name: The datastore to which the counterfactual_examples should be uploaded
    :type datastore_name: str
    :return: The id of the created Asset.
    :rtype: str
    """
    if not isinstance(counterfactual_examples, CounterfactualExplanations):
        raise UserErrorException._with_error(
            AzureMLError.create(
                ArgumentInvalidTypeError,
                arg_name='counterfactual_examples',
                type=type(counterfactual_examples),
                type_list=['CounterfactualExplanations'],
            )
        )

    counterfactuals_json_str = counterfactual_examples.to_json()
    _validate_counterfactuals_dict(counterfactuals_json_str)

    upload_id = str(uuid.uuid4())

    assets_client = AssetsClient(run.experiment.workspace.service_context)
    asset_artifact_list = []
    asset_properties = {}
    asset_properties[AssetProperties.UPLOAD_ID] = upload_id
    if comment is not None:
        asset_properties[AssetProperties.COMMENT] = comment

    # Update the properties (if needed)
    update_properties(asset_properties)

    counterfactuals_dict = json.loads(counterfactuals_json_str)
    rai_artifact_client = RAIArtifactClient(run, datastore_name)

    version = _get_schema_version(counterfactuals_dict)

    if version == _SchemaVersions.V1:
        cf_schema_keys = _V1SchemaConstants.ALL
    else:
        cf_schema_keys = _V2SchemaConstants.ALL

    for counterfactual_examples_key in cf_schema_keys:
        artifact_upload_return_code = rai_artifact_client.upload_single_object(
            target=counterfactuals_dict[counterfactual_examples_key],
            artifact_area_path=get_asset_name_rai_tool(RAITool.COUNTERFACTUAL),
            upload_id=upload_id,
            artifact_type=counterfactual_examples_key)
        asset_artifact_list.append(artifact_upload_return_code)

    asset = assets_client.create_asset(
        model_name=get_asset_name_rai_tool(RAITool.COUNTERFACTUAL),
        artifact_values=asset_artifact_list,
        metadata_dict={},
        run_id=run.id,
        properties=asset_properties,
        asset_type=asset_type)
    return asset.id


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Counterfactual'}, activity_type=LogCons.PUBLIC_API)
def download_counterfactual_examples(run: Run, counterfactual_examples_upload_id: Optional[str] = None,
                                     asset_type: Optional[str] = None,
                                     comment: Optional[str] = None) -> CounterfactualExplanations:
    """Download the counterfactual examples previously uploaded in the run.

    :param run: A Run object from which the counterfactual examples need to be downloaded.
    :type run: azureml.core.Run
    :param counterfactual_examples_upload_id: If specified, tries to download the counterfactual example
                                              from the run with the given counterfactual example ID.
                                              If unspecified, returns the most recently uploaded
                                              counterfactual examples.
    :type counterfactual_examples_upload_id: str
    :param comment: A string used to download the counterfactual examples based on the strings
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: The counterfactual example object.
    :rtype: dice_ml.counterfactual_explanations.CounterfactualExplanations
    """
    upload_id = search_rai_assets(run=run, rai_tool=RAITool.COUNTERFACTUAL,
                                  asset_type=asset_type,
                                  query_upload_id=counterfactual_examples_upload_id,
                                  query_comment=comment)
    downloaded_counterfactual_examples = {}

    # When downloading, datastore_name is not relevant
    rai_artifact_client = RAIArtifactClient(run)

    version = rai_artifact_client.download_single_object(
        artifact_area_path=get_asset_name_rai_tool(RAITool.COUNTERFACTUAL),
        upload_id=upload_id,
        artifact_type=_CommonSchemaConstants.METADATA)['version']
    if version == _SchemaVersions.V1:
        cf_schema_keys = _V1SchemaConstants.ALL
    else:
        cf_schema_keys = _V2SchemaConstants.ALL

    for counterfactual_examples_key in cf_schema_keys:
        downloaded_counterfactual_examples[counterfactual_examples_key] = \
            rai_artifact_client.download_single_object(
                artifact_area_path=get_asset_name_rai_tool(RAITool.COUNTERFACTUAL),
                upload_id=upload_id,
                artifact_type=counterfactual_examples_key)

    _validate_counterfactuals_with_schema(downloaded_counterfactual_examples)

    counterfactuals_json_str = json.dumps(downloaded_counterfactual_examples)
    return CounterfactualExplanations.from_json(counterfactuals_json_str)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Counterfactual'}, activity_type=LogCons.PUBLIC_API)
def list_counterfactual_examples(run: Run, comment: Optional[str] = None) -> List[Dict]:
    """Get the list of upload_ids of counterfactual examples available to a given Run.

    :param run: A Run object from which the counterfactual examples need to be queried.
    :type run: azureml.core.Run
    :param comment: A string used to filter counterfactual examples based on the strings
                    they were uploaded with. Requires an exact match.
    :type comment: str
    :return: A list of dictionaries with upload GUIDs, comment and upload time of the uploaded
             counterfactual examples.
    :rtype: list[Dict]
    """
    return list_rai_tool(run=run, rai_tool=RAITool.COUNTERFACTUAL, comment=comment)
