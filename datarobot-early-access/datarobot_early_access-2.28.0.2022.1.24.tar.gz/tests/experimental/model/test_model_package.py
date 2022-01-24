#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import copy
import json

import responses

from datarobot._experimental.models.model_package import ModelPackage
from tests.utils import add_response

_base_url = "https://host_name.com"
_project_id = "60feb853eadeed4617dd5de8"
_model_id = "60feb9286c9dfb8b69b93c80"
_model_package_id = "60feb9b5eadeed4617dd5e29"

_create_url = "{}/modelPackages/fromLearningModel/".format(_base_url)
_build_url = "{}/modelPackages/{}/modelPackageFileBuilds/".format(_base_url, _model_package_id)
_download_url = "{}/modelPackages/{}/modelPackageFile/".format(_base_url, _model_package_id)
_get_url = "{}/modelPackages/{}/".format(_base_url, _model_package_id)
_list_url = "{}/modelPackages/".format(_base_url)

_model_package_json = {
    "id": _model_package_id,
    "name": "model package name",
    "modelId": _model_id,
    "modelExecutionType": "dedicated",
    "activeDeploymentCount": 0,
    "isArchived": False,
    "permissions": ["CAN_VIEW", "CAN_EDIT", "CAN_SHARE", "CAN_ARCHIVE", "CAN_SHARE_OWNERSHIP"],
    "importMeta": {
        "creatorId": "60f82edf3cf8c8184476ee46",
        "creatorUsername": "admin@datarobot.com",
        "dateCreated": "2021-07-26T13:33:41.483782Z",
        "originalFileName": None,
    },
    "modelKind": {
        "isTimeSeries": True,
        "isMultiseries": True,
        "isUnsupervisedLearning": True,
        "isAnomalyDetectionModel": False,
        "isFeatureDiscovery": False,
    },
    "target": {
        "name": "DR_FAKE_TARGET (actual)",
        "type": "Multiclass",
        "classNames": ["Cluster 2", "Cluster 1"],
        "classCount": 2,
        "predictionThreshold": None,
        "predictionProbabilitiesColumn": None,
    },
    "modelDescription": {
        "modelName": "model name",
        "description": "",
        "location": "",
        "buildEnvironmentType": "DataRobot",
    },
    "datasets": {
        "datasetName": "dataset.csv",
        "trainingDataCatalogId": None,
        "baselineSegmentedBy": None,
        "holdoutDataCatalogId": None,
        "holdoutDatasetName": None,
    },
    "sourceMeta": {
        "projectId": _project_id,
        "projectName": "project name",
        "environmentUrl": "https://host_name.com",
        "scoringCode": {"location": None, "dataRobotPredictionVersion": "2.1.11"},
    },
    "timeseries": {
        "datetimeColumnName": "Date (actual)",
        "datetimeColumnFormat": "%Y-%m-%d",
        "forecastDistances": [0],
        "forecastDistancesTimeUnit": "DAY",
        "forecastDistanceColumnName": "Forecast Distance",
        "forecastPointColumnName": "dr_forecast_point",
        "seriesColumnName": "Series",
        "featureDerivationWindowStart": -35,
        "featureDerivationWindowEnd": 0,
        "effectiveFeatureDerivationWindowStart": -35,
        "effectiveFeatureDerivationWindowEnd": 0,
        "isTraditionalTimeSeries": False,
        "isCrossSeries": False,
        "isNewSeriesSupport": False,
    },
}


@responses.activate
def test_model_package_create():
    responses.add(
        responses.POST, _create_url, body=json.dumps(_model_package_json), status=200,
    )

    model_package = ModelPackage.create(_model_package_id)
    assert model_package.id == _model_package_id


@responses.activate
def test_model_package_get():
    add_response(url=_get_url, body=_model_package_json)

    model_package = ModelPackage.get(_model_package_id)
    assert model_package.id == _model_package_id


@responses.activate
def test_model_package_list():
    dummy_model_package_json = copy.deepcopy(_model_package_json)
    dummy_model_package_json["id"] = "60feb9b5eadeed4617dd5e33"

    add_response(
        url=_list_url,
        body={
            "count": 1,
            "next": None,
            "previous": None,
            "data": [_model_package_json, dummy_model_package_json],
        },
    )

    model_package_list = ModelPackage.list()
    assert len(model_package_list) == 2
    first_model_package = model_package_list[0]
    assert first_model_package.id == _model_package_id
    second_model_package = model_package_list[1]
    assert second_model_package.id == "60feb9b5eadeed4617dd5e33"
