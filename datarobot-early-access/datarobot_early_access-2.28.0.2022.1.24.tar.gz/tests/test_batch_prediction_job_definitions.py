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
import pytest
import responses

from datarobot import BatchPredictionJobDefinition
from datarobot.utils import from_api


@pytest.fixture
def endpoint(client):
    return "{}/batchPredictionJobDefinitions/".format(client.endpoint)


@pytest.fixture
def batch_prediction_job_initializing_json():
    resp = {
        "id": "5ce1204b962d741661907ea0",
        "status": "INITIALIZING",
        "percentageCompleted": 0,
        "elapsedTimeSec": 7747,
        "links": {
            "self": "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
            "csvUpload": (
                "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/csvUpload/"
            ),
        },
        "jobSpec": {
            "numConcurrent": 1,
            "chunkSize": "auto",
            "thresholdHigh": None,
            "thresholdLow": None,
            "filename": "",
            "deploymentId": "5ce1138c962d7415e076d8c6",
            "passthroughColumns": [],
            "passthroughColumnsSet": None,
            "maxExplanations": None,
        },
        "statusDetails": "Job submitted at 2019-05-19 09:22:19.779000",
    }

    return resp


@pytest.fixture
def server_response_single():
    resp = {
        "updated": "2021-05-04T11:20:41.691000Z",
        "nextScheduledRunTime": "2021-05-10T16:00:00.000000Z",
        "lastStartedJobTime": None,
        "schedule": {
            "dayOfWeek": [1],
            "month": ["*"],
            "hour": [16],
            "minute": [0],
            "dayOfMonth": [1],
        },
        "created": "2021-05-04T11:20:41.691000Z",
        "enabled": False,
        "lastSuccessfulRunTime": "1900-01-01T00:00:00.000000Z",
        "lastStartedJobStatus": None,
        "createdBy": {
            "username": "admin@datarobot.com",
            "fullName": None,
            "userId": "6065cbcaaf795f38b8cfb4ee",
        },
        "updatedBy": {
            "username": "admin@datarobot.com",
            "fullName": None,
            "userId": "6065cbcaaf795f38b8cfb4ee",
        },
        "lastFailedRunTime": "1900-01-01T00:00:00.000000Z",
        "lastScheduledRunTime": "2021-05-03T16:00:00.000000Z",
        "id": "60912e09fd1f04e832a575c1",
        "batchPredictionJob": {
            "includeProbabilitiesClasses": [],
            "predictionWarningEnabled": None,
            "chunkSize": "auto",
            "numConcurrent": 6,
            "csvSettings": {"quotechar": '"', "delimiter": ",", "encoding": "utf-8"},
            "abortOnError": True,
            "outputSettings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
            "includeProbabilities": True,
            "columnNamesRemapping": None,
            "deploymentId": "foobar",
            "intakeSettings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
            "includePredictionStatus": True,
            "skipDriftTracking": False,
            "maxExplanations": 0,
            "disableRowLevelErrorHandling": False,
        },
        "name": "supportive_paramatta_frogmouth",
    }
    return resp


@pytest.fixture
def server_response_single_patched(server_response_single):
    patched = server_response_single.copy()

    patched.update(
        {
            "enabled": True,
            "scheduled": {
                "day_of_week": ["*"],
                "month": ["*"],
                "hour": [16, 45, 59],
                "minute": [1, 5, 30],
                "day_of_month": [1],
            },
            "num_concurrent": 6,
            "deployment_id": "foobar_new",
            "name": "updated_definition_name",
        }
    )

    return patched


@pytest.fixture
def server_response_list(server_response_single):
    count = 10

    resp = {
        "count": count,
        "totalCount": 10,
        "next": None,
        "previous": None,
    }

    data = []

    for i in range(count):
        modified_response = server_response_single.copy()
        modified_response["name"] = "random_definition_{i}".format(i=i)

        data.append(modified_response)

    resp["data"] = data

    return resp


@responses.activate
def test_list(endpoint, server_response_list):
    responses.add(responses.GET, endpoint, json=server_response_list)

    definitions = BatchPredictionJobDefinition.list()

    assert len(definitions) == 10


@responses.activate
def test_get(endpoint, server_response_single):
    id = server_response_single["id"]

    responses.add(responses.GET, "{}{}/".format(endpoint, id), json=server_response_single)

    definition = BatchPredictionJobDefinition.get(id)

    assert definition.name == server_response_single["name"]
    assert definition.last_successful_run_time == server_response_single["lastSuccessfulRunTime"]


@responses.activate
def test_create(endpoint, server_response_single):
    responses.add(responses.POST, endpoint, json=server_response_single)

    job_spec = {
        "num_concurrent": 4,
        "deployment_id": "foobar",
        "intake_settings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
        "output_settings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
        "timeseries_settings": {
            "type": "forecast",
            "predictions_start_date": "2020-05-16T17:42:12+00:00",
        },
    }

    schedule = {
        "day_of_week": [1],
        "month": ["*"],
        "hour": [16],
        "minute": [0],
        "day_of_month": [1],
    }

    definition = BatchPredictionJobDefinition.create(
        enabled=False,
        schedule=schedule,
        batch_prediction_job=job_spec,
        name="supportive_paramatta_frogmouth",
    )

    assert definition.name == server_response_single["name"]
    assert definition.enabled == server_response_single["enabled"]
    assert definition.schedule == from_api(server_response_single["schedule"])
    assert definition.batch_prediction_job == from_api(server_response_single["batchPredictionJob"])


@responses.activate
def test_update(endpoint, server_response_single, server_response_single_patched):
    id = server_response_single["id"]

    responses.add(responses.GET, "{}{}/".format(endpoint, id), json=server_response_single)

    responses.add(responses.PATCH, "{}{}".format(endpoint, id), json=server_response_single_patched)

    job_spec = {
        "num_concurrent": 6,
        "deployment_id": "foobar_new",
        "intake_settings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
        "output_settings": {"url": "s3://foobar/123", "type": "s3", "format": "csv"},
    }

    schedule = {
        "day_of_week": ["*"],
        "month": ["*"],
        "hour": [16, 45, 59],
        "minute": [1, 5, 30],
        "day_of_month": [1],
    }

    definition = BatchPredictionJobDefinition.get(id)

    definition = definition.update(
        enabled=True,
        schedule=schedule,
        batch_prediction_job=job_spec,
        name="updated_definition_name",
    )

    assert definition.name == server_response_single_patched["name"]
    assert definition.enabled == server_response_single_patched["enabled"]
    assert definition.schedule == from_api(server_response_single_patched["schedule"])
    assert definition.batch_prediction_job == from_api(
        server_response_single_patched["batchPredictionJob"]
    )


@responses.activate
def test_run_once(endpoint, server_response_single, batch_prediction_job_initializing_json):
    id = server_response_single["id"]

    responses.add(responses.GET, "{}{}/".format(endpoint, id), json=server_response_single)

    responses.add(
        responses.POST,
        "https://host_name.com/batchPredictions/fromJobDefinition/",
        json=batch_prediction_job_initializing_json,
    )

    responses.add(
        responses.GET,
        "https://host_name.com/batchPredictions/5ce1204b962d741661907ea0/",
        json=batch_prediction_job_initializing_json,
    )

    definition = BatchPredictionJobDefinition.get(id)

    resp = definition.run_once()
    assert resp.status == "INITIALIZING"


@responses.activate
def test_run_on_schedule(endpoint, server_response_single, server_response_single_patched):
    id = server_response_single["id"]

    responses.add(responses.GET, "{}{}/".format(endpoint, id), json=server_response_single)

    responses.add(responses.PATCH, "{}{}".format(endpoint, id), json=server_response_single_patched)

    definition = BatchPredictionJobDefinition.get(id)

    schedule = {
        "day_of_week": ["*"],
        "month": ["*"],
        "hour": [16, 45, 59],
        "minute": [1, 5, 30],
        "day_of_month": [1],
    }

    resp = definition.run_on_schedule(schedule)
    assert resp.enabled is True
