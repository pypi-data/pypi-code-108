# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for uploading and downloading fairness Assets.

Currently, we only support one type of fairness Asset, the dashboard dictionary.

On upload, we split the dictionary into several Artifacts:
* One Artifact for `y_true`
* One Artifact for each of the predictions
* One Artifact for each of the sensitive features
* One metrics Artifact for each _combination_ of the predictions and sensitive features

These Artifacts are bound into Composability Unit for Fairness (CUF) Assets,
which each point to four Artifacts, one from each of the groups listed
above.

One thing to note about the 'type' is that we have two
layers of identification:
* That the Asset belongs to 'azureml.fairness'
* That the Asset is has a fairness type of 'dashboard.metrics'

The first of these is currently stored in the name of the Asset, but
will be moved to the type field once that is available. The second
is stored in the `fairness_asset_type` property.

There is a check on the maximum size of the upload, which is imposed on
the size of the entire dictionary (when converted to JSON). Although
the dictionary is broken up for upload, limiting the overall size is
the simplest approach to keeping the sizes reasonable.
"""

import base64
import copy
import logging
import uuid

from typing import List

from azureml.exceptions import UserErrorException
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._common._error_definition.system_error import SystemError
from azureml._common._error_definition import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml._restclient.assets_client import AssetsClient

from ._azureml_validation import validate_models_exist
from ._common_properties import extract_common_properties
from ._constants import (
    AssetPropertyKeys,
    PredictionTypeConvertors,
    FairnessAssetTypes,
    FairnessDashboardArtifactTypes,
    FairlearnDashboardKeys,
    _AZUREML_FAIRNESS_NAME,
    _DASHBOARD_SCHEMA_TYPE
)
from ._dashboard_validation import validate_dashboard_dictionary
from azureml.responsibleai.common._errors.error_definitions import (
    DashboardDownloadError,
    MissingDatastoreError
)
from ._fairness_artifact_client import FairnessArtifactClient
from ._specific_uploaders import upload_y_true
from ._specific_uploaders import upload_y_preds
from ._specific_uploaders import upload_sensitive_features
from ._specific_uploaders import upload_single_metric_set
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


DEFAULT_UPLOAD_BYTES_LIMIT = 20 * 1024 * 1024

_EXPECTED_ARTIFACT_COUNT = 4

_DOWNLOAD_MISSING_ASSETS = "DashboardDownload: Problem encountered " +\
    "with download. Got {0} sets of metrics but expected {1}"


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Fairness'}, activity_type=LogCons.PUBLIC_API)
def upload_dashboard_dictionary(run,
                                datastore_name,
                                dashboard_dict,
                                dashboard_name,
                                dataset_name=None,
                                dataset_id=None,
                                upload_bytes_limit=DEFAULT_UPLOAD_BYTES_LIMIT,
                                validate_model_ids=True):
    """Uploads the given dashboard dictionary to Azure Machine Learning Studio.

    The supplied dictionary should follow the schema required
    by the dashboard. There is a method in Fairlearn to generate
    the required dictionary.

    Since the uploaded dashboard includes some of the input data (specifically
    the sensitive features specified, along with the true and predicted values),
    there is a mandatory `datastore_name` argument to specify the destination
    for the upload. Controls on this datastore may prevent the dashboard from
    rendering in Azure Machine Learning Studio. If there are no confidentiality
    concerns, then `run.experiment.workspace.get_default_datastore().name` may
    be supplied.

    The size of the `dashboard_dict` object after conversion to JSON is limited
    by `upload_bytes_limit` (with a default of 20MB). An exception is
    raised if this is exceeded. There is also an optional check
    (performed by default) which ensures that the names of the models
    listed in the dictionary are the ids (i.e. `name:version` format)
    of models registered in the current workspace.

    :param run: The Run to which the upload should be attached.
    :type run: azureml.core.run.Run
    :param datastore_name: The datastore for the uploads
    :type datastore_name: str
    :param dashboard_dict: Dashboard data.
    :type dashboard_dict: dict
    :param dashboard_name: To be shown in the Run view.
    :type dashboard_name: str
    :param dataset_name: Name of dataset used for y_true etc. (optional).
    :type dataset_name: str
    :param dataset_id: AzureML dataset id used for y_true etc. (optional).
    :type dataset_id: str
    :param upload_bytes_limit: Maximum size of the dashboard after conversion to JSON.
    :type upload_bytes_limit: int
    :param validate_model_ids: Check whether model strings in the dashboard correspond to registered model ids.
    :type validate_model_ids: bool
    :return: A GUID identifying the upload.
    :rtype: str
    """
    # Require a datastore
    if datastore_name is None:
        raise UserErrorException._with_error(
            AzureMLError.create(
                MissingDatastoreError,
                arg_name='datastore'
            )
        )

    # This makes sure that all array lengths agree and spares us later checks
    validate_dashboard_dictionary(dashboard_dict, upload_bytes_limit)

    # Verify that all model 'names' in the dashboard are actually registered
    # models
    if validate_model_ids:
        validate_models_exist(run.experiment.workspace,
                              dashboard_dict[FairlearnDashboardKeys.MODEL_NAMES])

    common_props = extract_common_properties(dashboard_dict,
                                             dashboard_name,
                                             str(run.experiment.id),
                                             dataset_name,
                                             dataset_id)

    upload_id = common_props[AssetPropertyKeys.UPLOAD_ID]

    # Upload y_true
    _logger.info("Uploading y_true")
    y_true_artifact = upload_y_true(run,
                                    datastore_name,
                                    dashboard_dict,
                                    upload_id)

    # Upload y_preds
    num_y_preds = len(dashboard_dict[FairlearnDashboardKeys.Y_PRED])
    _logger.info("Found {0} predictions".format(num_y_preds))
    y_pred_artifacts = upload_y_preds(run,
                                      datastore_name,
                                      dashboard_dict,
                                      upload_id)

    # Upload sensitive features
    num_sf = len(dashboard_dict[FairlearnDashboardKeys.SENSITIVE_FEATURES])
    _logger.info("Found {0} sensitive features")
    sf_artifacts = upload_sensitive_features(run,
                                             datastore_name,
                                             dashboard_dict,
                                             upload_id)

    # Upload metrics
    _logger.info("Uploading metrics")
    metrics_artifacts = []
    for i_sf in range(num_sf):
        metrics_for_sf = []
        for i_pred in range(num_y_preds):
            metric_artifact = upload_single_metric_set(run,
                                                       datastore_name,
                                                       dashboard_dict,
                                                       i_sf,
                                                       i_pred,
                                                       upload_id)
            metrics_for_sf.append(metric_artifact)
        metrics_artifacts.append(metrics_for_sf)

    # Create the assets
    _logger.info("Creating CUF Assets")
    assets_client = AssetsClient(run.experiment.workspace.service_context)
    for i_sf in range(num_sf):
        for i_pred in range(num_y_preds):
            # Create the artifact list
            artifact_list = []
            artifact_list.append(y_true_artifact)
            artifact_list.append(y_pred_artifacts[i_pred])
            artifact_list.append(sf_artifacts[i_sf])
            artifact_list.append(metrics_artifacts[i_sf][i_pred])

            # Extract model and sensitive feature information
            model_id = dashboard_dict[FairlearnDashboardKeys.MODEL_NAMES][i_pred]
            sf_data = dashboard_dict[FairlearnDashboardKeys.SENSITIVE_FEATURES][i_sf]
            sf_name = sf_data[FairlearnDashboardKeys.SENSITIVE_FEATURE_NAME]

            # Set up the properties
            props = copy.deepcopy(common_props)
            props[AssetPropertyKeys.MODEL_ID] = model_id
            props[AssetPropertyKeys.SENSITIVE_FEATURES_COLUMN_NAME] = sf_name

            # Compute the name we want for the Asset
            # This is going to be the upload_id, but the
            # name field is restricted to 30 alphanumeric characters
            upload_id_uuid = uuid.UUID(upload_id)
            upload_id_b32 = base64.b32encode(upload_id_uuid.bytes)
            name = upload_id_b32.decode().replace('=', '')
            assert len(name) < 30

            # TODO: Remove once UX supports using 'type' field on Assets
            name = _AZUREML_FAIRNESS_NAME

            # Create the Asset
            asset = assets_client.create_asset(
                model_name=name,
                artifact_values=artifact_list,
                metadata_dict={},
                run_id=run.id,
                properties=props,
                asset_type=FairnessAssetTypes.FAIRNESS_ASSET)
            _logger.info("Asset uploaded with id {0}".format(asset.id))

    # Return the upload id which binds everything together
    return common_props[AssetPropertyKeys.UPLOAD_ID]


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Fairness'}, activity_type=LogCons.PUBLIC_API)
def list_available_upload_ids(run):
    """Get the list of upload_ids of dashboards attached to a given Run.

    :param run: The Run which should be checked for dashboard uploads.
    :type run: azureml.core.run.Run
    :return: A list of upload GUIDs (as strings).
    :rtype: list[str]
    """
    assets_client = AssetsClient(run.experiment.workspace.service_context)

    all_fairness_assets = assets_client.list_assets_with_query(run_id=run.id,
                                                               asset_type=FairnessAssetTypes.FAIRNESS_ASSET)
    upload_ids = set()
    for a in all_fairness_assets:
        upload_id = a.properties[AssetPropertyKeys.UPLOAD_ID]
        upload_ids.add(upload_id)
    return list(upload_ids)


def _list_assets_for_upload_id(run, upload_id):
    """Get the Assets (but not Artifacts) corresponding to the given upload_id.
    A given dashboard can be assembled from these.

    :param run: The Run which should be checked.
    :type run: azureml.core.run.Run
    :param upload_id: The desired upload id.
    :type upload_id: str
    :returns: List of Assets corresponding to the given upload id.
    :rtype: list[azureml.core._restclient.models.asset.Asset]
    """
    assets_client = AssetsClient(run.experiment.workspace.service_context)

    # TODO: Improve once Assets have Type and improved querying
    properties = dict()
    properties[AssetPropertyKeys.UPLOAD_ID] = upload_id
    candidates = assets_client.list_assets_with_query(run_id=run.id,
                                                      asset_type=FairnessAssetTypes.FAIRNESS_ASSET,
                                                      properties=properties)

    result = [x for x in candidates
              if x.properties[AssetPropertyKeys.UPLOAD_ID] == upload_id]

    return result


def _assert_identical_property(asset_list, property_name, expected=None):
    """Sanity check a list of Assets

    Ensures that the named property is the same for every Asset in the
    list. Optionally checks that the property value is equal to an
    expected value.

    :param asset_list: List of Assets.
    :type asset_list: list[azureml.core._restclient.models.asset.Asset]
    :param property_name: The property which should be identical for all.
    :type property_name: str
    :param expected: The (optional) expected value of the property.
    :type expected: str
    :returns: Nothing.
    """
    first_value = asset_list[0].properties[property_name]
    if expected is not None:
        assert first_value == expected

    for a in asset_list:
        assert a.properties[property_name] == first_value


def _get_single_artifact_prefix(asset, artifact_type):
    """Extracts the Artifact prefix which contains the given type.

    An Asset has a list of Artifacts, each with an attribute called
    `prefix`. This routine returns the prefix which contains the
    given `artifact_type` as a substring. It ensures that only a
    single prefix matches the given `artifact_type`.

    :param asset: The Asset to be examined.
    :type asset: azureml.core._restclient.models.asset.Asset
    :param artifact_type: The type string which should appear in the `prefix`.
    :type artifact_type: str
    """
    prefixes = [a.prefix for a in asset.artifacts
                if artifact_type in a.prefix]
    assert len(prefixes) == 1
    return prefixes[0]


def _extract_artifact_prefixes(asset):
    """Extracts artifact prefixes from the Assets as new attributes

    This exploits the highly dynamic nature of Python. Each Asset
    has an artifacts list. Each entry in the list is an Artifact,
    which has a single attribute of 'prefix'. There should be
    four Artifacts on an Asset, for y_true, y_pred, sensitive_feature
    and the metrics. This extracts the prefix for each from there
    and turns them into an attribute on the Asset.

    :param asset: The Asset to have its prefixes extracted and regrafted.
    :type asset: azureml.core._restclient.models.asset.Asset
    """
    assert len(asset.artifacts) == _EXPECTED_ARTIFACT_COUNT

    # Dynamically add the attributes to the Asset
    asset.y_true_prefix = _get_single_artifact_prefix(asset,
                                                      FairnessDashboardArtifactTypes.Y_TRUE)
    asset.y_pred_prefix = _get_single_artifact_prefix(asset,
                                                      FairnessDashboardArtifactTypes.Y_PRED)
    asset.sensitive_feature_prefix = \
        _get_single_artifact_prefix(asset,
                                    FairnessDashboardArtifactTypes.SENSITIVE_FEATURES_COLUMN)
    asset.metric_prefix = _get_single_artifact_prefix(asset,
                                                      FairnessDashboardArtifactTypes.METRICS_SET)


def _check_asset_count(all_assets: List, sensitive_features: List, predictions: List):
    num_sf = len(sensitive_features)
    num_pred = len(predictions)
    num_assets = len(all_assets)
    if num_assets != num_sf * num_pred:
        msg = _DOWNLOAD_MISSING_ASSETS.format(
            num_assets, num_sf * num_pred)
        raise AzureMLException._with_error(
            AzureMLError.create(
                DashboardDownloadError,
                full_message=msg)
        )


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Fairness'}, activity_type=LogCons.PUBLIC_API)
def download_dashboard_by_upload_id(run, upload_id):
    """Reassemble all the pieces of a dashboard from a single upload.

    This reverses `upload_dashboard_dict()`, retrieving the individual
    components from Azure Machine Learning Studio and stitching them
    back together.

    The logical contents of the downloaded dashboard will be identical
    to the original. However, the models and sensitive features will
    be sorted into alphabetical order, which may result in changes
    to the physical layout.

    :param run: The Run to which the uploaded dashboard is attached.
    :type run: azureml.core.run.Run
    :param upload_id: The GUID identifying the desired dashboard.
    :type upload_id: str
    :return: The dashboard dictionary from the upload.
    :rtype: dict
    """
    result = {}

    _logger.info("Fetching asset list")
    all_assets = _list_assets_for_upload_id(run, upload_id)
    _assert_identical_property(all_assets, AssetPropertyKeys.DASHBOARD_NAME)
    _assert_identical_property(all_assets, AssetPropertyKeys.VERSION)
    _assert_identical_property(all_assets,
                               AssetPropertyKeys.FAIRNESS_ASSET_TYPE,
                               FairnessAssetTypes.DASHBOARD_METRICS)
    _assert_identical_property(all_assets,
                               AssetPropertyKeys.PREDICTION_TYPE)

    result[FairlearnDashboardKeys.SCHEMA_TYPE] = _DASHBOARD_SCHEMA_TYPE
    result[FairlearnDashboardKeys.SCHEMA_VERSION] = \
        int(all_assets[0].properties[AssetPropertyKeys.VERSION])
    result[FairlearnDashboardKeys.PREDICTION_TYPE] = \
        PredictionTypeConvertors.ASSET_TO_DASHBOARD[
            all_assets[0].properties[AssetPropertyKeys.PREDICTION_TYPE]]

    # Validate the Artifact list for each Asset, and extract the prefixes as attributes
    [_extract_artifact_prefixes(a) for a in all_assets]

    # Next, cross validate the artifacts between assets
    y_true_prefixes = set()
    y_pred_prefixes = dict()
    sf_prefixes = dict()
    for a in all_assets:
        model_id = a.properties[AssetPropertyKeys.MODEL_ID]
        if model_id in y_pred_prefixes:
            assert a.y_pred_prefix == y_pred_prefixes[model_id]
        else:
            y_pred_prefixes[model_id] = a.y_pred_prefix
        sf_name = a.properties[AssetPropertyKeys.SENSITIVE_FEATURES_COLUMN_NAME]
        if sf_name in sf_prefixes:
            assert a.sensitive_feature_prefix == sf_prefixes[sf_name]
        else:
            sf_prefixes[sf_name] = a.sensitive_feature_prefix
        y_true_prefixes.add(a.y_true_prefix)
    assert len(y_true_prefixes) == 1
    _check_asset_count(
        all_assets, sensitive_features=sf_prefixes, predictions=y_pred_prefixes)

    # We need to go through the dictionaries in sorted order
    pred_names_sorted = sorted(y_pred_prefixes.keys())
    sf_names_sorted = sorted(sf_prefixes.keys())

    # Start assembling the result dictionary
    fac = FairnessArtifactClient(run)

    # Populate y_true
    _logger.info("Populating y_true")
    y_true_prefix = y_true_prefixes.pop()
    result[FairlearnDashboardKeys.Y_TRUE] = \
        fac.download_single_object(y_true_prefix)

    # Populate y_pred
    _logger.info("Populating y_pred")
    y_preds = []
    model_names = []
    for name in pred_names_sorted:
        prefix = y_pred_prefixes[name]
        y_preds.append(fac.download_single_object(prefix))
        model_names.append(name)
    result[FairlearnDashboardKeys.Y_PRED] = y_preds
    result[FairlearnDashboardKeys.MODEL_NAMES] = model_names

    # Populate sensitive features
    _logger.info("Populating sensitive features")
    sf_list = []
    for name in sf_names_sorted:
        prefix = sf_prefixes[name]
        sf = fac.download_single_object(prefix)
        assert name == sf[FairlearnDashboardKeys.SENSITIVE_FEATURE_NAME]
        sf_list.append(sf)
    result[FairlearnDashboardKeys.SENSITIVE_FEATURES] = sf_list

    # Populate the metrics
    _logger.info("Populating metrics")
    metrics = []
    for sf_name in sf_names_sorted:
        curr = []
        for pred_name in pred_names_sorted:
            metric_list = [x for x in all_assets
                           if x.properties[AssetPropertyKeys.SENSITIVE_FEATURES_COLUMN_NAME] == sf_name
                           and x.properties[AssetPropertyKeys.MODEL_ID] == pred_name]
            assert len(metric_list) == 1
            metric = metric_list[0]
            metric_data = fac.download_single_object(metric.metric_prefix)
            curr.append(metric_data)
        metrics.append(curr)
    result[FairlearnDashboardKeys.METRICS] = metrics

    return result
