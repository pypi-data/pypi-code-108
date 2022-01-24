# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Upload specific Artifacts of the dashboard

Our integration works by splitting dashboards into several
individual Artifacts. This module contains the individual
uploaders for these.
"""

import logging

from ._constants import FairnessDashboardArtifactTypes
from ._constants import FairlearnDashboardKeys
from azureml.responsibleai.common._constants import IOConstants

from ._fairness_artifact_client import FairnessArtifactClient


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def upload_y_true(run, datastore_name, dashboard_dict, upload_id):
    """Upload the `y_true` values to an Artifact.

    Retrieves the `y_true` values from the given dashboard,
    and uploads to the service.

    :param run: The target run
    :type run: :class:`azureml.core.run.Run`
    :param datastore_name: The datastore for the uploads
    :type datastore_name: str
    :param dashboard_dict: The dashboard dictionary
    :type dashboard_dict: dict
    :param upload_id: The id of the current upload (a GUID)
    :type upload_id: str
    :returns: The upload dictionary of the uploaded Artifact
    :rtype: dict(str,str)
    """
    y_true_data = dashboard_dict[FairlearnDashboardKeys.Y_TRUE]
    artifact_type = FairnessDashboardArtifactTypes.Y_TRUE

    artifact_client = FairnessArtifactClient(run)
    artifact_list = artifact_client.upload_single_object(datastore_name,
                                                         y_true_data,
                                                         upload_id,
                                                         artifact_type)
    assert len(artifact_list) == 1
    assert IOConstants.ARTIFACT_PREFIX in artifact_list[0]

    prefix_path = artifact_list[0][IOConstants.ARTIFACT_PREFIX]
    _logger.info("Uploaded y_true to prefix {0}".format(prefix_path))

    return artifact_list[0]


def upload_y_preds(run, datastore_name, dashboard_dict, upload_id):
    """Uploads all predictions to Artifacts.

    :param run: The target run
    :type run: :class:`azureml.core.run.Run`
    :param datastore_name: The datastore for the uploads
    :type datastore_name: str
    :param dashboard_dict: The dashboard dictionary
    :type dashboard_dict: dict
    :param upload_id: The id of the current upload (a GUID)
    :type upload_id: str
    :returns: The list of uploaded Artifact dictionaries
    :rtype: list(dict(str,str))
    """
    artifact_type = FairnessDashboardArtifactTypes.Y_PRED

    artifact_client = FairnessArtifactClient(run)

    result = []
    for y_p in dashboard_dict[FairlearnDashboardKeys.Y_PRED]:
        artifact_list = artifact_client.upload_single_object(datastore_name,
                                                             y_p,
                                                             upload_id,
                                                             artifact_type)
        assert len(artifact_list) == 1
        assert IOConstants.ARTIFACT_PREFIX in artifact_list[0]

        prefix_path = artifact_list[0][IOConstants.ARTIFACT_PREFIX]
        _logger.info("Uploaded prediction to prefix {0}".format(prefix_path))
        result.append(artifact_list[0])

    _logger.info("Uploaded {0} predictions".format(len(result)))
    return result


def upload_sensitive_features(run, datastore_name, dashboard_dict, upload_id):
    """Upload the sensitive features to Artifacts

    Extracts the sensitive features from the dashboard dictionary
    and uploads them to Artifacts. Returns a list of the
    artifact dictionaries (each with a single entry of 'prefix').

    :param run: The target run
    :type run: :class:`azureml.core.run.Run`
    :param datastore_name: The datastore for the uploads
    :type datastore_name: str
    :param dashboard_dict: The dashboard dictionary
    :type dashboard_dict: dict
    :param upload_id: The id of the current upload (a GUID)
    :type upload_id: str
    :returns: The list of uploaded Artifact dictionaries
    :rtype: list(dict(str,str))
    """
    artifact_type = FairnessDashboardArtifactTypes.SENSITIVE_FEATURES_COLUMN

    artifact_client = FairnessArtifactClient(run)

    result = []
    for s_f in dashboard_dict[FairlearnDashboardKeys.SENSITIVE_FEATURES]:
        artifact_list = artifact_client.upload_single_object(datastore_name,
                                                             s_f,
                                                             upload_id,
                                                             artifact_type)
        assert len(artifact_list) == 1
        assert IOConstants.ARTIFACT_PREFIX in artifact_list[0]

        prefix = artifact_list[0][IOConstants.ARTIFACT_PREFIX]
        _logger.info(
            "Uploaded sensitive feature column to prefix {0}".format(prefix))
        result.append(artifact_list[0])

    _logger.info("Uploaded {0} sensitive features".format(len(result)))
    return result


def upload_single_metric_set(run,
                             datastore_name,
                             dashboard_dict,
                             sensitive_feature_index,
                             y_pred_index,
                             upload_id):
    """Upload a single set of metrics to an Artifact.

    In the current dashboard schema, the metrics are stored
    as a 2D array of dictionaries, indexed by prediction and
    sensitive feature. This routine uploads a single one of those
    dictionaries.

    :param run: The target run
    :type run: :class:`azureml.core.run.Run`
    :param datastore_name: The datastore for the uploads
    :type datastore_name: str
    :param dashboard_dict: The dashboard dictionary
    :type dashboard_dict: dict
    :param sensitive_feature_index: The first index in the array of metrics dictionaries
    :type sensitive_feature_index: int
    :param y_pred_index: The second index in the array of metrics dictionaries
    :type y_pred_index: int
    :param upload_id: The id of the current upload (a GUID)
    :type upload_id: str
    :returns: The upload dictionary of the uploaded Artifact
    :rtype: dict(str,str)
    """
    artifact_type = FairnessDashboardArtifactTypes.METRICS_SET

    # Get the data we want
    metrics_array = dashboard_dict[FairlearnDashboardKeys.METRICS]
    metrics_data = metrics_array[sensitive_feature_index][y_pred_index]

    artifact_client = FairnessArtifactClient(run)
    artifact_list = artifact_client.upload_single_object(datastore_name,
                                                         metrics_data,
                                                         upload_id,
                                                         artifact_type)
    assert len(artifact_list) == 1
    assert IOConstants.ARTIFACT_PREFIX in artifact_list[0]

    fmt_string = "Uploaded metrics data for prediction {0} and sensitive_feature {1}"
    _logger.info(fmt_string.format(y_pred_index,
                                   sensitive_feature_index))

    return artifact_list[0]
