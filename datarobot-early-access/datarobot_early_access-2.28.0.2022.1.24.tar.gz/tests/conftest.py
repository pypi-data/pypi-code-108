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
import os
import tempfile
import warnings

import mock
import pytest
import responses

from datarobot import (
    BlenderModel,
    Dataset,
    DatetimeModel,
    enums,
    FrozenModel,
    Model,
    PredictionExplanations,
    PredictionExplanationsInitialization,
    PrimeFile,
    PrimeModel,
    Project,
    RatingTable,
    RatingTableModel,
    ReasonCodes,
    ReasonCodesInitialization,
    Ruleset,
)
from datarobot.client import get_client, set_client
from datarobot.models.api_object import APIObject
from datarobot.models.prediction_explanations import PredictionExplanationsPage
from datarobot.models.reason_codes import ReasonCodesPage
from datarobot.rest import RESTClientObject
from datarobot.utils import from_api

# This filter causes the tests to fail if any uncaught warnings leak out
warnings.simplefilter("error")
# some of our dependencies trigger DeprecationWarning's on Python 3.7 (internally), which we would
# normally treat as exceptions per the rule above; ignore them instead so that tests pass on 3.7
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=r".*", module=r"(requests)|(responses)|(yaml)",
)


@pytest.yield_fixture
def no_client_version_check():
    """Mock client version check, to avoid actual HTTP requests."""
    with mock.patch("datarobot.client._is_compatible_client") as version_check:
        yield version_check


@pytest.yield_fixture
def temporary_file():
    new_file = tempfile.NamedTemporaryFile(delete=False)
    new_file.close()
    yield new_file.name
    os.remove(new_file.name)


@pytest.fixture
def temporary_dir(tmpdir):
    yield tmpdir.strpath


@pytest.yield_fixture
def mock_async_time():
    patch = mock.patch("datarobot.utils.waiters.time")
    yield patch.start()
    patch.stop()


@pytest.fixture
def unicode_string():
    return u"\u3053\u3093\u306b\u3061\u306f"


@pytest.fixture
def unittest_endpoint():
    return "https://host_name.com"


@pytest.yield_fixture(scope="function")
def known_warning():
    """
    A context that will not let any warnings out. This will allow us to
    test for known deprecations and the like while still making sure the rest of the tested
    code does not emit any warnings

    This fixture asserts that a warning was raised while it was used, so users of this
    fixture don't need to do so themselves
    """
    filters = warnings.filters[:]
    warnings.resetwarnings()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # record _all_ warnings, not just first instance
        yield w
    assert w, "Expected a warning but did not find one"
    warnings.filters = filters


@pytest.yield_fixture(scope="function", autouse=True)
def client(request):
    """A mocked client

    The DataRobot package is built around acquiring the GlobalClient, which this sets
    to point to `https://host_name.com`.

    This is set automatically via autouse for all tests.  If you specifically need it _not_
    to be set, you can use the "no_client" marker.

    Most often you only need the effect, not the client. In this case you can use
    the pytest.mark.usefixtures decorator to make sure this patch takes place
    for your test
    """
    if request.node.get_closest_marker("no_client"):
        set_client(None)
        yield None
    else:
        c = RESTClientObject(auth="t-token", endpoint="https://host_name.com")
        set_client(c)
        yield get_client()
    set_client(None)


@pytest.fixture
def project_id():
    """
    A project id that matches the objects in the fixtures

    Returns
    -------
    project_id : str
        The id of the project used across the fixtures
    """
    return "556cdfbb100d2b0e88585195"


@pytest.fixture
def project_collection_url():
    return "https://host_name.com/projects/"


@pytest.fixture
def project_url(project_id):
    return "https://host_name.com/projects/{}/".format(project_id)


@pytest.fixture
def project_aim_url(project_url):
    return "{}{}/".format(project_url, "aim")


@pytest.fixture
def project_endpoint(client):
    return "{}/projects/".format(client.endpoint)


@pytest.fixture
def project_without_target_json():
    """The JSON of one project

    This data in this project has been uploaded and analyzed, but the target
    has not been set
    """
    return """
    {
    "id": "556cdfbb100d2b0e88585195",
    "projectName": "A Project Name",
    "fileName": "test_data.csv",
    "stage": "aim",
    "autopilotMode": null,
    "created": "2016-07-26T02:29:58.546312Z",
    "target": null,
    "metric": null,
    "partition": {
      "datetimeCol": null,
      "cvMethod": null,
      "validationPct": null,
      "reps": null,
      "cvHoldoutLevel": null,
      "holdoutLevel": null,
      "userPartitionCol": null,
      "validationType": null,
      "trainingLevel": null,
      "partitionKeyCols": null,
      "holdoutPct": null,
      "validationLevel": null
    },
    "recommender": {
      "recommenderItemId": null,
      "isRecommender": null,
      "recommenderUserId": null
    },
    "advancedOptions": {
      "blueprintThreshold": null,
      "responseCap": null,
      "seed": null,
      "weights": null,
      "smartDownsampled": null,
      "majorityDownsamplingRate": null,
      "offset": null,
      "exposure": null
    },
    "positiveClass": null,
    "maxTrainPct": null,
    "holdoutUnlocked": false,
    "targetType": null
  }
"""


@pytest.fixture
def project_without_target_data(project_without_target_json):
    data = json.loads(project_without_target_json)
    return from_api(data)


@pytest.fixture
def project_with_target_json():
    return """{
        "id": "556cdfbb100d2b0e88585195",
        "projectName": "A Project Name",
        "fileName": "data.csv",
        "stage": "modeling",
        "autopilotMode": 0,
        "created": "2016-07-26T02:29:58.546312Z",
        "target": "target_name",
        "metric": "LogLoss",
        "partition": {
            "datetimeCol": null,
            "cvMethod": "stratified",
            "validationPct": null,
            "reps": 5,
            "cvHoldoutLevel": null,
            "holdoutLevel": null,
            "userPartitionCol": null,
            "validationType": "CV",
            "trainingLevel": null,
            "partitionKeyCols": null,
            "holdoutPct": 19.99563,
            "validationLevel": null
        },
        "recommender": {
            "recommenderItemId": null,
            "isRecommender": false,
            "recommenderUserId": null
        },
        "advancedOptions": {
            "blueprintThreshold": null,
            "responseCap": false,
            "seed": null,
            "weights": null,
            "smartDownsampled": false,
            "majorityDownsamplingRate": null,
            "offset": null,
            "exposure": null
        },
        "positiveClass": 1,
        "maxTrainPct": 64.0035,
        "holdoutUnlocked": false,
        "targetType": "Binary"
    }
"""


@pytest.fixture
def project_server_data(project_with_target_json):
    return json.loads(project_with_target_json)


@pytest.fixture
def project_with_target_data(project_with_target_json):
    data = json.loads(project_with_target_json)
    return from_api(data)


@pytest.fixture
def smart_sampled_project_server_data(project_with_target_json):
    base_data = json.loads(project_with_target_json)
    return dict(base_data, smartDownsampled=True, majorityDownsamplingRate=50.5)


@pytest.fixture
def project(project_with_target_data):
    return Project.from_data(project_with_target_data)


@pytest.fixture
def smart_sampled_project(smart_sampled_project_data):
    return Project.from_data(smart_sampled_project_data)


@pytest.fixture
def project_without_target(project_without_target_data):
    return Project.from_data(project_without_target_data)


@pytest.fixture
def async_failure_json():
    return """
    {
        "status": "ERROR",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def async_aborted_json():
    return """
    {
        "status": "ABORTED",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def async_running_json():
    return """
    {
        "status": "RUNNING",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def featurelist_server_data(project_id):
    return {
        "id": "5223deadbeefdeadbeef9999",
        "name": "Some Features",
        "features": ["One Fish", "Two Fish", "Red Fish", "Blue Fish"],
        "created": "2018-07-02T18:49:38.019000Z",
        "isUserCreated": True,
        "numModels": 5,
        "projectId": project_id,
        "description": "Some String",
    }


@pytest.fixture
def model_id():
    """
    The id of the model used in the fixtures

    Returns
    -------
    model_id : str
        The id of the model used in the fixtures
    """
    return "556ce973100d2b6e51ca9657"


@pytest.fixture
def parent_model_id():
    """
    The id of the parent model used in the fixtures
    Returns
    -------
    parent_model_id : str
        The id of the parent model used in the fixtures
    """
    return "5bc76f0cfcf4c80f4af88481"


@pytest.fixture
def model_json():
    return """
{
    "featurelistId": "57993241bc92b715ed0239ee",
    "processes": [
      "One",
      "Two",
      "Three"
    ],
    "featurelistName": "Informative Features",
    "projectId": "556cdfbb100d2b0e88585195",
    "samplePct": 64,
    "modelType": "Gradient Boosted Trees Classifier",
    "metrics": {
      "AUC": {
        "holdout": null,
        "validation": 0.73376,
        "crossValidation": null
      },
      "Rate@Top5%": {
        "holdout": null,
        "validation": 0.44218,
        "crossValidation": null
      },
      "Rate@TopTenth%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "RMSE": {
        "holdout": null,
        "validation": 0.27966,
        "crossValidation": null
      },
      "LogLoss": {
        "holdout": null,
        "validation": 0.2805,
        "crossValidation": null
      },
      "FVE Binomial": {
        "holdout": null,
        "validation": 0.12331,
        "crossValidation": null
      },
      "Gini Norm": {
        "holdout": null,
        "validation": 0.46752,
        "crossValidation": null
      },
      "Rate@Top10%": {
        "holdout": null,
        "validation": 0.34812,
        "crossValidation": null
      }
    },
    "modelCategory": "model",
    "isFrozen": false,
    "blueprintId": "de628edee06f2b23218767a245e45ae1",
    "id": "556ce973100d2b6e51ca9657",
    "supportsMonotonicConstraints": true,
    "monotonicIncreasingFeaturelistId": "5ae04c0d962d7410683073cb",
    "monotonicDecreasingFeaturelistId": "5ae04c0f962d7410683073cc",
    "isStarred": false,
    "predictionThreshold": 0.6,
    "predictionThresholdReadOnly": true,
    "model_number": 1234
  }
    """


@pytest.fixture
def model_deployment_id():
    return "5a7d96bd962d745ea62459fb"


@pytest.fixture
def model_deployment_json():
    return """
{
    "status": "active",
    "trendTimeWindow": "1d",
    "prevRequestCount": 0,
    "description": "test",
    "predictionEndpoint": "fake-5a7d9559962d745ea62459c7",
    "organizationId": "5a7d96a3962d745ea62459f1",
    "requestRates": [0, 24, 24, 24, 23, 0, 0, 0],
    "createdAt": "2018-02-09 12:40:29.730000",
    "label": "Auto-Tuned Word N-Gram Text Modeler using token occurrences - diag_1_desc",
    "project": {
        "id": "5a7d69ad962d743f559d1a97",
        "projectName": "MMM",
        "fileName":
        "10k_diabetes-200.tsv",
        "stage":
        "modeling",
        "autopilotMode": 0,
        "created": "2018-02-09T09:28:19.928403Z",
        "target": "readmitted",
        "metric": "LogLoss",
        "partition": {
            "datetimeCol": null,
            "cvHoldoutLevel": null,
            "validationPct": null,
            "reps": 5,
            "cvMethod":
            "stratified",
            "holdoutLevel": null,
            "userPartitionCol": null,
            "validationType": "CV",
            "trainingLevel": null,
            "partitionKeyCols": null,
            "holdoutPct": 20.0,
            "validationLevel": null
        },
        "recommender": {
            "recommenderItemId": null,
            "isRecommender": null,
            "recommenderUserId": null
        },
        "advancedOptions": {
            "scaleoutModelingMode": "disabled",
            "responseCap": false,
            "downsampledMinorityRows": null,
            "smartDownsampled": false,
            "blueprintThreshold": 3,
            "seed": null,
            "weights": null,
            "downsampledMajorityRows": null,
            "majorityDownsamplingRate": null
        },
        "positiveClass": 1.0,
        "maxTrainPct": 64.0,
        "maxTrainRows": 128,
        "scaleoutMaxTrainPct": 64.0,
        "scaleoutMaxTrainRows": 128,
        "holdoutUnlocked": true,
         "targetType": "Binary"
    },
    "instance": null,
    "serviceHealthMessages": [
        {"msgId": "NO_GOOD_REQUESTS",
         "message": "No successful predictions in 24 hours",
         "level": "passing"}
    ],
    "model": {
        "uid": "5a2e9f83c15fa0be8d2b2c74",
        "id": "5a7d69dd962d745e1b69535b",
        "modelType": "Auto-Tuned Word N-Gram Text Modeler using token occurrences - diag_1_desc",
        "icons": [0]
    },
    "user": {
        "username": "admin@datarobot.com",
        "lastName": "Test",
        "id": "5a2e9f83c15fa0be8d2b2c74",
        "firstName": "Test"
    },
    "relativeRequestsTrend": 5,
    "updatedAt": "2018-02-12 12:16:39.163000",
    "serviceHealth": "passing",
    "recentRequestCount": 10,
    "type": "dedicated",
    "id": "5a7d96bd962d745ea62459fb",
    "deployed": true
}
    """


@pytest.fixture
def blender_json(model_json):
    data = json.loads(model_json)
    data["modelIds"] = ["556ce973100d2b6e51ca9656", "556ce973100d2b6e51ca9655"]
    data["blenderMethod"] = "AVG"
    return json.dumps(data)


@pytest.fixture
def blenders_list_response_json(blender_json):
    data = json.loads(blender_json)
    return json.dumps({"data": [data, data]})


@pytest.fixture
def frozen_json(model_json, parent_model_id):
    data = json.loads(model_json)
    data["parentModelId"] = parent_model_id
    return json.dumps(data)


@pytest.fixture
def frozen_models_list_response(frozen_json):
    data = json.loads(frozen_json)
    return {"data": [data, data], "count": 2, "prev": None, "next": None}


@pytest.fixture
def model_data(model_json):
    return from_api(json.loads(model_json))


@pytest.fixture
def model_deployment_data(model_deployment_json):
    return from_api(json.loads(model_deployment_json))


@pytest.fixture
def datetime_model_data(model_data):
    modified_model_data = dict(model_data)
    modified_model_data.pop("sample_pct")
    modified_model_data["training_start_date"] = "2015-12-10T19:00:00.000000Z"
    modified_model_data["training_end_date"] = "2016-12-10T19:00:00.000000Z"
    modified_model_data["effective_feature_derivation_window_start"] = -120
    modified_model_data["effective_feature_derivation_window_end"] = 0
    modified_model_data["forecast_window_start"] = 10
    modified_model_data["forecast_window_end"] = 10
    modified_model_data["windows_basis_unit"] = "MINUTE"
    return modified_model_data


@pytest.fixture
def one_model(model_data):
    return Model.from_data(model_data)


@pytest.fixture
def one_datetime_model(model_id, project_id):
    return DatetimeModel(id=model_id, project_id=project_id)


@pytest.fixture
def blender_data(blender_json):
    return from_api(json.loads(blender_json))


@pytest.fixture
def one_blender(blender_data):
    return BlenderModel.from_data(blender_data)


@pytest.fixture
def frozen_data(frozen_json):
    return from_api(json.loads(frozen_json))


@pytest.fixture
def one_frozen(frozen_data):
    return FrozenModel.from_data(frozen_data)


@pytest.fixture
def prime_model_id():
    return "57aa68e1ccf94e1ce3197743"


@pytest.fixture
def prime_model_json():
    return """
    {
    "featurelistId": "57aa1c46ccf94e5bb073841b",
    "processes": [],
    "featurelistName": "Informative Features",
    "projectId": "556cdfbb100d2b0e88585195",
    "samplePct": 63.863,
    "modelType": "DataRobot Prime",
    "metrics": {
      "AUC": {
        "holdout": null,
        "validation": 0.8559,
        "crossValidation": null
      },
      "Rate@Top5%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "Rate@TopTenth%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "RMSE": {
        "holdout": null,
        "validation": 0.37973,
        "crossValidation": null
      },
      "LogLoss": {
        "holdout": null,
        "validation": 0.41848,
        "crossValidation": null
      },
      "FVE Binomial": {
        "holdout": null,
        "validation": 0.32202,
        "crossValidation": null
      },
      "Gini Norm": {
        "holdout": null,
        "validation": 0.7118,
        "crossValidation": null
      },
      "Rate@Top10%": {
        "holdout": null,
        "validation": 0.66667,
        "crossValidation": null
      }
    },
    "modelCategory": "prime",
    "blueprintId": "bcfb575932da72a92d01837a6c42a36f5cc56cbdab7d92f43b88e114179f2942",
    "id": "57aa68e1ccf94e1ce3197743",
    "rulesetId": 3,
    "score": 0.41847989771503824,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 323
    }
    """


@pytest.fixture
def prime_model_server_data(prime_model_json):
    return json.loads(prime_model_json)


@pytest.fixture
def prime_data(prime_model_server_data):
    return from_api(prime_model_server_data)


@pytest.fixture
def prime_model(prime_model_server_data):
    return PrimeModel.from_server_data(prime_model_server_data)


@pytest.fixture
def ruleset_with_model_json():
    return """
    {
    "projectId": "556cdfbb100d2b0e88585195",
    "rulesetId": 3,
    "score": 0.41847989771503824,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 323,
    "modelId": "57aa68e1ccf94e1ce3197743"
    }
    """


@pytest.fixture
def ruleset_without_model_json():
    return """
    {
    "projectId": "556cdfbb100d2b0e88585195",
    "rulesetId": 2,
    "score": 0.428702,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 161,
    "modelId": null
    }
    """


@pytest.fixture
def ruleset_with_model_server_data(ruleset_with_model_json):
    return json.loads(ruleset_with_model_json)


@pytest.fixture
def ruleset_without_model_server_data(ruleset_without_model_json):
    return json.loads(ruleset_without_model_json)


@pytest.fixture
def ruleset_with_model(ruleset_with_model_server_data):
    return Ruleset.from_server_data(ruleset_with_model_server_data)


@pytest.fixture
def ruleset_without_model(ruleset_without_model_server_data):
    return Ruleset.from_server_data(ruleset_without_model_server_data)


@pytest.fixture
def prime_file_json():
    return """
    {
    "id": "57fa1c41ccf94e59a9024e87",
    "projectId": "556cdfbb100d2b0e88585195",
    "parentModelId": "556ce973100d2b6e51ca9657",
    "modelId": "57aa68e1ccf94e1ce3197743",
    "rulesetId": 3,
    "language": "Python",
    "isValid": true
    }
    """


@pytest.fixture
def prime_file_server_data(prime_file_json):
    return json.loads(prime_file_json)


@pytest.fixture
def prime_file(prime_file_server_data):
    return PrimeFile.from_server_data(prime_file_server_data)


@pytest.fixture
def rating_table_model_server_data(model_json):
    data = json.loads(model_json)
    data["ratingTableId"] = "5984af32100d2b2d9f10fbe0"
    return data


@pytest.fixture
def rating_table_model_json(rating_table_model_server_data):
    return json.dumps(rating_table_model_server_data)


@pytest.fixture
def rating_table_model(rating_table_model_server_data):
    return RatingTableModel.from_server_data(rating_table_model_server_data)


@pytest.fixture
def rating_table_model_url(project_collection_url, rating_table_model_server_data):
    d = rating_table_model_server_data
    return "{}{}/ratingTableModels/{}/".format(project_collection_url, d["projectId"], d["id"])


@pytest.fixture
def job_id():
    return "13"


@pytest.fixture
def job_url(project_id, job_id):
    return "https://host_name.com/projects/{}/jobs/{}/".format(project_id, job_id)


@pytest.fixture
def base_job_server_data(job_id, project_id, job_url):
    return {
        "status": None,
        "url": job_url,
        "id": job_id,
        "jobType": None,
        "isBlocked": False,
        "projectId": project_id,
    }


@pytest.fixture
def base_job_running_server_data(base_job_server_data):
    return dict(base_job_server_data, status=enums.QUEUE_STATUS.INPROGRESS)


@pytest.fixture
def base_job_completed_server_data(base_job_server_data):
    return dict(base_job_server_data, status=enums.QUEUE_STATUS.COMPLETED)


@pytest.fixture
def prime_model_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_MODEL)


@pytest.fixture
def prime_model_job_completed_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_MODEL)


@pytest.fixture
def prime_model_job_creation_response(project_url, job_url):
    responses.add(
        responses.POST,
        "{}primeModels/".format(project_url),
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def prime_model_job_completed_response(
    prime_model_job_completed_server_data,
    job_url,
    project_url,
    prime_model_id,
    prime_model_server_data,
):
    prime_model_url = "{}primeModels/{}/".format(project_url, prime_model_id)
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(prime_model_job_completed_server_data),
        status=303,
        adding_headers={"Location": prime_model_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        prime_model_url,
        body=json.dumps(prime_model_server_data),
        content_type="application/json",
    )


@pytest.fixture
def frozen_model_job_completed_server_data(base_job_completed_server_data, one_model):
    return dict(
        base_job_completed_server_data,
        jobType=enums.JOB_TYPE.MODEL,
        modelType=one_model.model_type,
        processes=one_model.processes,
        blueprintId=one_model.blueprint_id,
    )


@pytest.fixture
def rci_json():
    """ ReasonCodesInitialization GET json
    """
    return """{
      "projectId": "556cdfbb100d2b0e88585195",
      "reasonCodesSample": [
        {
          "reasonCodes": [
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 115.59591064453161,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": "Wheel Loader - 250.0 to 275.0 Horsepower",
              "label": "YearMade",
              "strength": 60.62447509765593,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 54.968029785156205,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1.0,
              "label": "YearMade",
              "strength": 51.503918457031205,
              "feature": "auctioneerID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1763636,
              "label": "YearMade",
              "strength": 45.668481445312636,
              "feature": "SalesID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "-2",
              "label": "YearMade",
              "strength": 35.2052001953125,
              "feature": "fiModelSeries",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Utah",
              "label": "YearMade",
              "strength": 25.33120117187491,
              "feature": "state",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "WA450",
              "label": "YearMade",
              "strength": 21.51729736328116,
              "feature": "fiBaseModel",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": 383693,
              "label": "YearMade",
              "strength": 17.533557128906068,
              "feature": "MachineID",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 12.142431640625091,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "+"
            }
          ],
          "prediction": 2059.988037109375,
          "rowId": 7459,
          "predictionValues": [{"value": 2059.988037109375, "label": "YearMade"}]
        },
        {
          "reasonCodes": [
            {
              "featureValue": "50DZTS",
              "label": "YearMade",
              "strength": 86.08530273437486,
              "feature": "fiModelDesc",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 2063.0,
              "label": "YearMade",
              "strength": 49.44567871093727,
              "feature": "MachineHoursCurrentMeter",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Medium",
              "label": "YearMade",
              "strength": 43.51775771484381,
              "feature": "UsageBand",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Hydraulic Excavator, Track - 4.0 to 5.0 Metric Tons",
              "label": "YearMade",
              "strength": 33.40051269531273,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1250726400,
              "label": "YearMade",
              "strength": 30.625183105468295,
              "feature": "saledate",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 26.95623779296875,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 21500,
              "label": "YearMade",
              "strength": 25.61611328124968,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 22117,
              "label": "YearMade",
              "strength": 25.539965820312545,
              "feature": "ModelID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "D",
              "label": "YearMade",
              "strength": 21.061962890624955,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "50",
              "label": "YearMade",
              "strength": 20.641674804687682,
              "feature": "fiBaseModel",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 2056.3349609375,
          "rowId": 6934,
          "predictionValues": [{"value": 2056.3349609375, "label": "YearMade"}]
        }
      ],
      "modelId": "578e59a41ced2e5a9eb18965"
    }"""


@pytest.fixture
def rci_data(rci_json):
    return from_api(json.loads(rci_json))


@pytest.fixture
def one_rci(rci_data):
    return ReasonCodesInitialization.from_data(rci_data)


@pytest.fixture
def rc_list_json():
    """List of reason codes"""
    return """{
      "count": 3,
      "next": null,
      "data": [
        {
          "finishTime": 1482414443.292265,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..7/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 2,
          "id": "585bd862dd56a7482bdcb567",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482414817.200652,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..6/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 3,
          "id": "585bda05dd56a7483781c4b6",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482418494.81697,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..a/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 3,
          "id": "585be85cdd56a7482bdcb56a",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        }
      ],
      "previous": null
    }"""


@pytest.fixture
def rc_json():
    """ ReasonCodes GET json
    """
    return """{
      "finishTime": 1482424475.33823,
      "numColumns": 50,
      "reasonCodesLocation": "https://host_name.com/projects/578e...2f64/reasonCodes/585b...9e0f/",
      "thresholdHigh": 2010.0490966796874,
      "projectId": "556cdfbb100d2b0e88585195",
      "thresholdLow": 1706.8041999316963,
      "maxCodes": 3,
      "id": "585ba071dd56a72ec7109e0f",
      "datasetId": "585b9d71c522f20d38107d6e",
      "modelId": "578e59a41ced2e5a9eb18960"
    }"""


@pytest.fixture
def rc_data(rc_json):
    return from_api(json.loads(rc_json))


@pytest.fixture
def one_rc(rc_data):
    return ReasonCodes.from_data(rc_data)


@pytest.fixture
def rcp_json():
    """ ReasonCodesPage GET json
    """
    return """{
      "count": 6,
      "reasonCodesRecordLocation": "https://host_name.com/projects/5..4/reasonCodesRecords/5..7/",
      "next": null,
      "data": [
        {
          "reasonCodes": [
            {
              "featureValue": 66000,
              "label": "YearMade",
              "strength": 113.18563232421889,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 1139246,
              "label": "YearMade",
              "strength": -84.37227783203139,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1843.3448486328125,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 1843.3448486328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 121,
              "label": "YearMade",
              "strength": -140.4251185424805,
              "feature": "datasource",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 107.4373168945308,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1730.043701171875,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 1730.043701171875,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139249,
              "label": "YearMade",
              "strength": -201.79853515624995,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 10000,
              "label": "YearMade",
              "strength": -144.66733398437532,
              "feature": "SalePrice",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1751.1256103515625,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 1751.1256103515625,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139251,
              "label": "YearMade",
              "strength": -222.99357910156255,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 1305763200,
              "label": "YearMade",
              "strength": -107.39191894531268,
              "feature": "saledate",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1663.2529296875,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 1663.2529296875,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139253,
              "label": "YearMade",
              "strength": -209.14246826171893,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 11000,
              "label": "YearMade",
              "strength": -67.03535156250018,
              "feature": "SalePrice",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1724.86328125,
          "rowId": 4,
          "predictionValues": [
            {
              "value": 1724.86328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139255,
              "label": "YearMade",
              "strength": -81.31390380859398,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 26500,
              "label": "YearMade",
              "strength": 52.808850097656205,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1881.0067138671875,
          "rowId": 5,
          "predictionValues": [
            {
              "value": 1881.0067138671875,
              "label": "YearMade"
            }
          ]
        }
      ],
      "id": "585bd862dd56a7482bdcb567",
      "previous": null
    }"""


@pytest.fixture
def rcp_data(rcp_json):
    return from_api(json.loads(rcp_json))


@pytest.fixture
def rcp_data_with_adjusted_predictions(rcp_data):
    rcp_data_with_ap = rcp_data.copy()
    rcp_data_with_ap["adjustment_method"] = "exposureNormalized"
    for record in rcp_data_with_ap["data"]:
        # Trivial case, all exposure values set to 1
        record["adjusted_prediction"] = record["prediction"]
        record["adjusted_prediction_values"] = record["prediction_values"]
    return rcp_data_with_ap


@pytest.fixture
def rcp_json_classification():
    return """{
      "count": 4,
      "reasonCodesRecordLocation": "https://host_name.com/projects/5...2/reasonCodesRecords/5...c/",
      "next": null,
      "data": [
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 0.2893982637455831,
              "label": 1
            },
            {
              "value": 0.7106017362544169,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 0.29246609348399255,
              "label": 1
            },
            {
              "value": 0.7075339065160074,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 0.3840762929836601,
              "label": 1
            },
            {
              "value": 0.6159237070163399,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 3,
              "strength": -0.3712657301791762,
              "feature": "number_diagnoses",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "UN",
              "strength": -0.3112189393477769,
              "feature": "payer_code",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "41",
              "strength": -0.2607262089753333,
              "feature": "diag_2",
              "qualitativeStrength": "--",
              "label": 1
            }
          ],
          "prediction": 0,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 0.12064479565777504,
              "label": 1
            },
            {
              "value": 0.8793552043422249,
              "label": 0
            }
          ]
        }
      ],
      "id": "58d1ef9fc80891088925890c",
      "previous": null
    }"""


@pytest.fixture
def rcp_data_classification(rcp_json_classification):
    return from_api(json.loads(rcp_json_classification))


@pytest.fixture
def one_rcp(rcp_data):
    with mock.patch(
        "datarobot.models.reason_codes.t.URL.check", side_effect=(lambda url, context=None: url)
    ):
        return ReasonCodesPage.from_data(rcp_data)


@pytest.fixture
def pei_json():
    """ PredictionExplanationsInitialization GET json
    """
    return """{
      "projectId": "556cdfbb100d2b0e88585195",
      "predictionExplanationsSample": [
        {
          "predictionExplanations": [
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 115.59591064453161,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": "Wheel Loader - 250.0 to 275.0 Horsepower",
              "label": "YearMade",
              "strength": 60.62447509765593,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 54.968029785156205,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1.0,
              "label": "YearMade",
              "strength": 51.503918457031205,
              "feature": "auctioneerID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1763636,
              "label": "YearMade",
              "strength": 45.668481445312636,
              "feature": "SalesID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "-2",
              "label": "YearMade",
              "strength": 35.2052001953125,
              "feature": "fiModelSeries",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Utah",
              "label": "YearMade",
              "strength": 25.33120117187491,
              "feature": "state",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "WA450",
              "label": "YearMade",
              "strength": 21.51729736328116,
              "feature": "fiBaseModel",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": 383693,
              "label": "YearMade",
              "strength": 17.533557128906068,
              "feature": "MachineID",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 12.142431640625091,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "+"
            }
          ],
          "prediction": 2059.988037109375,
          "rowId": 7459,
          "predictionValues": [{"value": 2059.988037109375, "label": "YearMade"}]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": "50DZTS",
              "label": "YearMade",
              "strength": 86.08530273437486,
              "feature": "fiModelDesc",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 2063.0,
              "label": "YearMade",
              "strength": 49.44567871093727,
              "feature": "MachineHoursCurrentMeter",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Medium",
              "label": "YearMade",
              "strength": 43.51775771484381,
              "feature": "UsageBand",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Hydraulic Excavator, Track - 4.0 to 5.0 Metric Tons",
              "label": "YearMade",
              "strength": 33.40051269531273,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1250726400,
              "label": "YearMade",
              "strength": 30.625183105468295,
              "feature": "saledate",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 26.95623779296875,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 21500,
              "label": "YearMade",
              "strength": 25.61611328124968,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 22117,
              "label": "YearMade",
              "strength": 25.539965820312545,
              "feature": "ModelID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "D",
              "label": "YearMade",
              "strength": 21.061962890624955,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "50",
              "label": "YearMade",
              "strength": 20.641674804687682,
              "feature": "fiBaseModel",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 2056.3349609375,
          "rowId": 6934,
          "predictionValues": [{"value": 2056.3349609375, "label": "YearMade"}]
        }
      ],
      "modelId": "578e59a41ced2e5a9eb18965"
    }"""


@pytest.fixture
def pei_data(pei_json):
    return from_api(json.loads(pei_json))


@pytest.fixture
def one_pei(pei_data):
    return PredictionExplanationsInitialization.from_data(pei_data)


@pytest.fixture
def pe_list_json():
    """List of reason codes"""
    return """{
      "count": 3,
      "next": null,
      "data": [
        {
          "finishTime": 1482414443.292265,
          "numColumns": 50,
          "predictionExplanationsLocation":
            "https://host_name.com/projects/5..4/predictionExplanations/5..7/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxExplanations": 2,
          "id": "585bd862dd56a7482bdcb567",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482414817.200652,
          "numColumns": 50,
          "predictionExplanationsLocation":
            "https://host_name.com/projects/5..4/predictionExplanations/5..6/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxExplanations": 3,
          "id": "585bda05dd56a7483781c4b6",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482418494.81697,
          "numColumns": 50,
          "predictionExplanationsLocation":
            "https://host_name.com/projects/5..4/predictionExplanations/5..a/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxExplanations": 3,
          "id": "585be85cdd56a7482bdcb56a",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        }
      ],
      "previous": null
    }"""


@pytest.fixture
def pe_json():
    """ PredictionExplanations GET json
    """
    return """{
      "finishTime": 1482424475.33823,
      "numColumns": 50,
      "predictionExplanationsLocation":
        "https://host_name.com/projects/578e...2f64/predictionExplanations/585...9e0f/",
      "thresholdHigh": 2010.0490966796874,
      "projectId": "556cdfbb100d2b0e88585195",
      "thresholdLow": 1706.8041999316963,
      "maxExplanations": 3,
      "id": "585ba071dd56a72ec7109e0f",
      "datasetId": "585b9d71c522f20d38107d6e",
      "modelId": "578e59a41ced2e5a9eb18960"
    }"""


@pytest.fixture
def pe_data(pe_json):
    return from_api(json.loads(pe_json))


@pytest.fixture
def one_pe(pe_data):
    return PredictionExplanations.from_data(pe_data)


@pytest.fixture
def pep_json():
    """ PredictionExplanationsPage GET json
    """
    return """{
      "count": 6,
      "predictionExplanationsRecordLocation":
        "https://host_name.com/projects/5..4/predictionExplanationsRecords/5..7/",
      "next": null,
      "data": [
        {
          "predictionExplanations": [
            {
              "featureValue": 66000,
              "label": "YearMade",
              "strength": 113.18563232421889,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 1139246,
              "label": "YearMade",
              "strength": -84.37227783203139,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1843.3448486328125,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 1843.3448486328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 121,
              "label": "YearMade",
              "strength": -140.4251185424805,
              "feature": "datasource",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 107.4373168945308,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1730.043701171875,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 1730.043701171875,
              "label": "YearMade"
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 1139249,
              "label": "YearMade",
              "strength": -201.79853515624995,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 10000,
              "label": "YearMade",
              "strength": -144.66733398437532,
              "feature": "SalePrice",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1751.1256103515625,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 1751.1256103515625,
              "label": "YearMade"
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 1139251,
              "label": "YearMade",
              "strength": -222.99357910156255,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 1305763200,
              "label": "YearMade",
              "strength": -107.39191894531268,
              "feature": "saledate",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1663.2529296875,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 1663.2529296875,
              "label": "YearMade"
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 1139253,
              "label": "YearMade",
              "strength": -209.14246826171893,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 11000,
              "label": "YearMade",
              "strength": -67.03535156250018,
              "feature": "SalePrice",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1724.86328125,
          "rowId": 4,
          "predictionValues": [
            {
              "value": 1724.86328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 1139255,
              "label": "YearMade",
              "strength": -81.31390380859398,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 26500,
              "label": "YearMade",
              "strength": 52.808850097656205,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1881.0067138671875,
          "rowId": 5,
          "predictionValues": [
            {
              "value": 1881.0067138671875,
              "label": "YearMade"
            }
          ]
        }
      ],
      "id": "585bd862dd56a7482bdcb567",
      "previous": null
    }"""


@pytest.fixture
def pep_data(pep_json):
    return from_api(json.loads(pep_json))


@pytest.fixture
def pep_data_with_adjusted_predictions(pep_data):
    pep_data_with_ap = pep_data.copy()
    pep_data_with_ap["adjustment_method"] = "exposureNormalized"
    for record in pep_data_with_ap["data"]:
        # Trivial case, all exposure values set to 1
        record["adjusted_prediction"] = record["prediction"]
        record["adjusted_prediction_values"] = record["prediction_values"]
    return pep_data_with_ap


@pytest.fixture
def pep_json_classification():
    return """{
      "count": 4,
      "predictionExplanationsRecordLocation":
        "https://host_name.com/projects/5...2/predictionExplanationsRecords/5...c/",
      "next": null,
      "data": [
        {
          "predictionExplanations": [],
          "prediction": 0,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 0.2893982637455831,
              "label": 1
            },
            {
              "value": 0.7106017362544169,
              "label": 0
            }
          ]
        },
        {
          "predictionExplanations": [],
          "prediction": 0,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 0.29246609348399255,
              "label": 1
            },
            {
              "value": 0.7075339065160074,
              "label": 0
            }
          ]
        },
        {
          "predictionExplanations": [],
          "prediction": 0,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 0.3840762929836601,
              "label": 1
            },
            {
              "value": 0.6159237070163399,
              "label": 0
            }
          ]
        },
        {
          "predictionExplanations": [
            {
              "featureValue": 3,
              "strength": -0.3712657301791762,
              "feature": "number_diagnoses",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "UN",
              "strength": -0.3112189393477769,
              "feature": "payer_code",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "41",
              "strength": -0.2607262089753333,
              "feature": "diag_2",
              "qualitativeStrength": "--",
              "label": 1
            }
          ],
          "prediction": 0,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 0.12064479565777504,
              "label": 1
            },
            {
              "value": 0.8793552043422249,
              "label": 0
            }
          ]
        }
      ],
      "id": "58d1ef9fc80891088925890c",
      "previous": null
    }"""


@pytest.fixture
def pep_data_classification(pep_json_classification):
    return from_api(json.loads(pep_json_classification))


@pytest.fixture
def one_pep(pep_data):
    with mock.patch(
        "datarobot.models.prediction_explanations.t.URL.check",
        side_effect=(lambda url, context=None: url),
    ):
        return PredictionExplanationsPage.from_data(pep_data)


@pytest.fixture
def rating_table_backend_generated_json():
    return """
    {
        "validationJobId": null,
        "validationError": "",
        "projectId": "556cdfbb100d2b0e88585195",
        "ratingTableName": "custom_table_name1",
        "parentModelId": "5984b4d7100d2b31c1166529",
        "modelJobId": null,
        "id": "5984b4e9100d2b34e5710c9b",
        "originalFilename": "rating_table.csv",
        "modelId": "5984b4d7100d2b31c1166529"
    }"""


@pytest.fixture
def rating_table_backend_generated(rating_table_backend_generated_json):
    return RatingTable.from_server_data(json.loads(rating_table_backend_generated_json))


@pytest.fixture
def rating_table_uploaded_but_not_modeled_json():
    return """
    {
        "validationJobId": "107",
        "validationError": "",
        "projectId": "556cdfbb100d2b0e88585195",
        "ratingTableName": "custom_table_name2",
        "parentModelId": "5983643a100d2b6b89af9622",
        "modelJobId": null,
        "id": "5988b817100d2b62c224691b",
        "originalFilename": "rating_table.csv",
        "modelId": null
    }"""


@pytest.fixture
def rating_table_renamed_json(rating_table_uploaded_but_not_modeled_json):
    rating_table_dict = json.loads(rating_table_uploaded_but_not_modeled_json)
    rating_table_dict["ratingTableName"] = "renamed"
    return json.dumps(rating_table_dict)


@pytest.fixture
def rating_table_uploaded_but_not_modeled(rating_table_uploaded_but_not_modeled_json):
    return RatingTable.from_server_data(json.loads(rating_table_uploaded_but_not_modeled_json))


@pytest.fixture
def renamed_rating_table(rating_table_renamed_json):
    return RatingTable.from_server_data(json.loads(rating_table_renamed_json))


@pytest.fixture
def rating_table_uploaded_and_modeled_json():
    return """
    {
        "validationJobId": "107",
        "validationError": "",
        "projectId": "556cdfbb100d2b0e88585195",
        "ratingTableName": "custom_table_name2",
        "parentModelId": "5983643a100d2b6b89af9622",
        "modelJobId": "114",
        "id": "5988b817100d2b62c224691b",
        "originalFilename": "rating_table.csv",
        "modelId": "5983643a100d2b6b89af9624"
    }"""


@pytest.fixture
def rating_table_uploaded_and_modeled(rating_table_uploaded_and_modeled_json):
    return RatingTable.from_server_data(json.loads(rating_table_uploaded_and_modeled_json))


@pytest.fixture
def blueprint_docs():
    return [
        {
            "task": u"Approximate kernel support vector classifier.",
            "description": u"Support vector machines are a class of \u201cmaximum margin\u201d ...",
            "links": [
                {
                    "url": u"https://en.wikipedia.org/wiki/Support_vector_machine",
                    "name": u"Support vector machine wikipedia",
                },
                {
                    "url": u"http://scikit-learn.org/stable/modules/svm.html",
                    "name": u"Support vector machine scikit-learn",
                },
                {
                    "url": u"http://scikit-learn.org/stable/modules/kernel_approximation.html",
                    "name": u"Kernel Approximation scikit-learn",
                },
            ],
            "title": (
                u"Nystroem Kernel SVM Classifier Documentation - DataRobot Model Documentation"
            ),
            "references": [
                {
                    "url": None,
                    "name": u'[R21]Caputo, B., Sim, K., Furesjo, F., & Smola, A. "Appearance-based '
                    u'Object Recognition using SVMs: Which Kernel Should I Use?". In Proc '
                    u"of NIPS workshop on Statistical methods for computational experiments in "
                    u"visual processing and computer vision (2002).",
                },
                {
                    "url": u"http://bioinformatics.oxfordjournals.org/content/16/10/906.full.pdf",
                    "name": u'[R22]Suykens, Johan AK, and Joos Vandewalle. "Least squares '
                    u'support vector machine classifiers." Neural processing '
                    u"letters 9.3 (1999): 293-300. ",
                },
            ],
            "parameters": [
                {
                    "type": u'select (default="nystroem")',
                    "name": u"approx (ap)",
                    "description": (
                        u" The kernel approximation method to use. values: ['nystroem', ..."
                    ),
                },
                {
                    "type": u'intgrid (default="100")',
                    "name": u"n_components (nc)",
                    "description": u" Is the target dimensionality of the feature transform",
                },
            ],
        }
    ]


@pytest.fixture
def blueprint_chart_data():
    return {
        "nodes": [{"id": "1", "label": "Task1"}, {"id": "2", "label": "Task2"}],
        "edges": [("1", "2")],
    }


@pytest.fixture
def missing_report_data():
    return {
        "missing_values_report": [
            {
                "feature": u"WheelTypeID",
                "type": u"Numeric",
                "missing_count": 136,
                "missing_percentage": 0.0687,
                "tasks": {
                    u"2": {
                        "name": "Missing Values Imputed",
                        "descriptions": [u"Imputed value: -9999"],
                    },
                    u"5": {
                        "name": "Missing Values Imputed",
                        "descriptions": [u"Missing indicator was treated as feature"],
                    },
                },
            },
            {
                "feature": u"TopThreeAmericanName",
                "type": u"Categorical",
                "missing_count": 2,
                "missing_percentage": 0.0005,
                "tasks": {
                    u"1": {
                        "name": "Ordinal encoding of categorical variables",
                        "descriptions": [u"Imputed value: -2"],
                    },
                    u"7": {
                        "name": "One-Hot Encoding",
                        "descriptions": [u"Missing indicator was treated as feature"],
                    },
                },
            },
        ]
    }


@pytest.fixture
def invalid_rating_table_json():
    return """
    {
        "validationJobId": "107",
        "validationError": "Error lol",
        "projectId": "556cdfbb100d2b0e88585195",
        "ratingTableName": "custom_table_name2",
        "parentModelId": "5983643a100d2b6b89af9622",
        "modelJobId": "114",
        "id": "5988b817100d2b62c224691b",
        "originalFilename": "rating_table.csv",
        "modelId": "5983643a100d2b6b89af9624"
    }"""


@pytest.fixture
@pytest.mark.usefixtures("known_warning")
def invalid_rating_table(invalid_rating_table_json):
    return RatingTable.from_server_data(json.loads(invalid_rating_table_json))


@pytest.fixture
def multiseries_precomputed_properties(project_url):
    final_payload = {
        "datetimePartitionColumn": "dates",
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["other_eligible"], "timeUnit": "HOUR", "timeStep": 5},
            {"multiseriesIdColumns": ["series_id"], "timeUnit": "DAY", "timeStep": 1},
        ],
    }
    responses.add(
        responses.GET,
        "{}features/dates/multiseriesProperties/".format(project_url),
        status=200,
        json=final_payload,
        content_type="application/json",
    )
    return final_payload["detectedMultiseriesIdColumns"][1]


@pytest.yield_fixture()
def multiseries_postcomputed_properties(project_url):
    initial_payload = {"datetimePartitionColumn": "timestamp", "detectedMultiseriesIdColumns": []}
    final_payload = {
        "datetimePartitionColumn": "timestamp",
        "detectedMultiseriesIdColumns": [
            {"multiseriesIdColumns": ["other_eligible"], "timeUnit": "HOUR", "timeStep": 5},
            {"multiseriesIdColumns": ["series_id"], "timeUnit": "DAY", "timeStep": 1},
        ],
    }

    with responses.RequestsMock():
        responses.add(
            responses.GET,
            "{}features/dates/multiseriesProperties/".format(project_url),
            status=200,
            json=initial_payload,
            content_type="application/json",
        )
        responses.add(
            responses.POST,
            "{}multiseriesProperties/".format(project_url),
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": "https://host_name.com/status/status-id/"},
        )
        responses.add(
            responses.GET,
            "https://host_name.com/status/status-id/",
            status=303,
            body="",
            content_type="application/json",
            adding_headers={
                "Location": "{}features/dates/multiseriesProperties/".format(project_url),
            },
        )
        responses.add(
            responses.GET,
            "{}features/dates/multiseriesProperties/".format(project_url),
            status=200,
            json=final_payload,
            content_type="application/json",
        )
        yield final_payload["detectedMultiseriesIdColumns"][1]


@pytest.yield_fixture
def multiseries_ineligible_properties(project_url):
    final_payload = {"datetimePartitionColumn": "timestamp", "detectedMultiseriesIdColumns": []}
    with responses.RequestsMock() as req_mock:
        responses.add(
            responses.POST,
            "{}multiseriesProperties/".format(project_url),
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": "https://host_name.com/status/status-id/"},
        )
        responses.add(
            responses.GET,
            "https://host_name.com/status/status-id/",
            status=303,
            body="",
            content_type="application/json",
            adding_headers={
                "Location": "{}features/float/multiseriesProperties/".format(project_url),
            },
        )
        responses.add(
            responses.GET,
            "{}features/float/multiseriesProperties/".format(project_url),
            status=200,
            json=final_payload,
            content_type="application/json",
        )
        yield req_mock


@pytest.fixture
def driver_libraries_endpoint(client):
    return "{}/externalDataDriverFile/".format(client.endpoint)


@pytest.fixture
def drivers_endpoint(client):
    return "{}/externalDataDrivers/".format(client.endpoint)


@pytest.fixture
def connectors_endpoint(client):
    return "{}/externalConnectors/".format(client.endpoint)


@pytest.fixture
def data_stores_endpoint(client):
    return "{}/externalDataStores/".format(client.endpoint)


@pytest.fixture
def data_sources_endpoint(client):
    return "{}/externalDataSources/".format(client.endpoint)


@pytest.fixture
def credentials_endpoint(client):
    return "{}/credentials/".format(client.endpoint)


@pytest.fixture
def drivers_list_server_resp():
    return {
        "data": [
            {
                "className": "org.postgresql.Driver",
                "baseNames": ["postgresql-9.4.1208.jre6.jar"],
                "id": "5a99545fe8fc4e0001fa996d",
                "canonicalName": "PostgreSQL",
                "creator": "5a55dc230936d31663231e3b",
            },
            {
                "className": "com.mysql.jdbc.Driver",
                "baseNames": ["mysql-connector-java-5.1.44-bin.jar"],
                "id": "5ab37d55438519000121b441",
                "canonicalName": "mysql",
                "creator": "5ab37d55962d7440474020cc",
            },
            {
                "className": "com.amazon.redshift.jdbc.Driver",
                "baseNames": ["RedshiftJDBC41-no-awssdk-1.2.10.1009.jar"],
                "id": "5abcac920ca81900010c1535",
                "canonicalName": "RedShift",
                "creator": "5a55dc230936d31663231e3b",
            },
        ]
    }


@pytest.fixture
def driver_library_upload_server_resp():
    return {"localUrl": "jdbc_drivers/b6214457-b1f7-403e-8947-60c9aa5710ae.jar"}


@pytest.fixture
def postgresql_driver_server_resp(drivers_list_server_resp):
    return drivers_list_server_resp["data"][0]


@pytest.fixture
def mysql_driver_server_resp(drivers_list_server_resp):
    return drivers_list_server_resp["data"][1]


@pytest.fixture
def redshift_driver_server_resp(drivers_list_server_resp):
    return drivers_list_server_resp["data"][2]


@pytest.fixture
def connectors_list_server_resp():
    return {
        "data": [
            {
                "id": "5fe1063e1c075e0245071446",
                "creatorId": "5f99f71d6d8bbae4367bdd29",
                "configurationId": "5fe106421c075e6f782ed953",
                "baseName": "connector-s3.jar",
                "canonicalName": "S3 Connector",
            },
            {
                "id": "5fe133ce1c075e0245071449",
                "creatorId": "5f99f71d6d8bbae4367bdd29",
                "configurationId": "5fe133d11c075e1a7a2ed957",
                "baseName": "connector-adls-gen2.jar",
                "canonicalName": "ADLS Gen2 Connector",
            },
        ]
    }


@pytest.fixture
def s3_connector_server_resp(connectors_list_server_resp):
    return connectors_list_server_resp["data"][0]


@pytest.fixture
def adls_gen2_connector_server_resp(connectors_list_server_resp):
    return connectors_list_server_resp["data"][1]


@pytest.fixture
def data_stores_list_server_resp():
    redshift_host = "prtests-redshift.cjzuk728s1ja.us-east-1.redshift.amazonaws.com"
    redshift_url = "jdbc:redshift://{}:5439/test".format(redshift_host)
    return {
        "data": [
            {
                "updated": "2018-03-25T08:49:05.485000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "perftest",
                "params": {
                    "driverId": "5a99545fe8fc4e0001fa996d",
                    "jdbcUrl": "jdbc:postgresql://bos-dss-borrow1.hq.datarobot.com:5432/perftest",
                },
                "type": "jdbc",
                "id": "5a995761e8fc4e0001fa996e",
                "role": "OWNER",
            },
            {
                "updated": "2018-03-25T08:48:55.598000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "PostgreSQL Demo",
                "params": {
                    "driverId": "5a99545fe8fc4e0001fa996d",
                    "jdbcUrl": "jdbc:postgresql://bos-dss-borrow1.hq.datarobot.com:5432/demo",
                },
                "type": "jdbc",
                "id": "5ab76277bd09db0001f3be16",
                "role": "OWNER",
            },
            {
                "updated": "2018-03-29T09:38:39.107000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "RedShift Demo",
                "params": {"driverId": "5abcac920ca81900010c1535", "jdbcUrl": redshift_url},
                "type": "jdbc",
                "id": "5abcb41f0ca81900010c1536",
                "role": "OWNER",
            },
        ]
    }


@pytest.fixture
def data_stores_list_server_resp_no_jdbc_url():
    return {
        "data": [
            {
                "updated": "2018-03-25T08:49:05.485000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "perftest",
                "params": {"driverId": "5a99545fe8fc4e0001fa996d"},
                "type": "jdbc",
                "id": "5a995761e8fc4e0001fa996e",
                "role": "OWNER",
            },
            {
                "updated": "2018-03-25T08:48:55.598000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "PostgreSQL Demo",
                "params": {"driverId": "5a99545fe8fc4e0001fa996d"},
                "type": "jdbc",
                "id": "5ab76277bd09db0001f3be16",
                "role": "OWNER",
            },
            {
                "updated": "2018-03-29T09:38:39.107000",
                "creator": "5a55dc230936d31663231e3b",
                "canonicalName": "RedShift Demo",
                "params": {"driverId": "5abcac920ca81900010c1535"},
                "type": "jdbc",
                "id": "5abcb41f0ca81900010c1536",
                "role": "OWNER",
            },
        ]
    }


@pytest.fixture
def postgresql_data_store_server_resp(data_stores_list_server_resp):
    return data_stores_list_server_resp["data"][1]


@pytest.fixture
def postgresql_data_store_server_resp_no_jdbc_url(data_stores_list_server_resp_no_jdbc_url):
    return data_stores_list_server_resp_no_jdbc_url["data"][1]


@pytest.fixture
def redshift_data_store_server_resp(data_stores_list_server_resp):
    return data_stores_list_server_resp["data"][2]


@pytest.fixture
def postgresql_schemas_list_server_resp():
    return {
        "catalog": "perftest",
        "schemas": ["demo", "information_schema", "pg_catalog", "public"],
    }


@pytest.fixture
def postgresql_tables_list_server_resp():
    return [
        {"type": "TABLE", "name": "diagnosis", "schema": "demo"},
        {"type": "TABLE", "name": "kickcars", "schema": "demo"},
        {"type": "TABLE", "name": "patient", "schema": "demo"},
        {"type": "TABLE", "name": "transcript", "schema": "demo"},
    ]


@pytest.fixture
def data_sources_list_server_resp():
    return {
        "data": [
            {
                "updated": "2018-02-19T12:57:15.365000",
                "creator": "5a530498d5c1f302d6d176c8",
                "canonicalName": "query_select_all_from_demo_diagnostics",
                "params": {
                    "query": "SELECT * FROM demo.diagnostics;",
                    "dataStoreId": "5a8ac90b07a57a0001be501e",
                },
                "type": "jdbc",
                "id": "5a8ac9ab07a57a0001be501f",
                "role": "OWNER",
            },
            {
                "updated": "2018-04-10T09:29:25.091000",
                "creator": "5a530498d5c1f302d6d176c8",
                "canonicalName": "Airlines 100mb",
                "params": {
                    "table": "airlines100mb",
                    "schema": "public",
                    "dataStoreId": "5acc73e5ec8d670001ba16b2",
                },
                "type": "jdbc",
                "id": "5acc7420ec8d670001ba16b3",
                "role": "OWNER",
            },
            {
                "updated": "2018-04-10T08:22:40.886000",
                "creator": "5a530498d5c1f302d6d176c8",
                "canonicalName": "Airlines 10mb",
                "params": {
                    "table": "airlines10mb",
                    "schema": "public",
                    "dataStoreId": "5acc73e5ec8d670001ba16b2",
                },
                "type": "jdbc",
                "id": "5acc7450ec8d670001ba16b4",
                "role": "OWNER",
            },
            {
                "updated": "2018-04-10T09:30:31.831000",
                "creator": "5a530498d5c1f302d6d176c8",
                "canonicalName": "Airlines 100mb (1000 records)",
                "params": {
                    "table": "airlines100mb",
                    "fetchSize": 1000,
                    "dataStoreId": "5acc73e5ec8d670001ba16b2",
                },
                "type": "jdbc",
                "id": "5acc8437ec8d670001ba16bf",
                "role": "OWNER",
            },
        ]
    }


@pytest.fixture
def interaction_feature_server_data():
    return {
        "rows": 30,
        "source_columns": ["col1", "col2"],
        "bars": [
            {
                "column_name": "col1",
                "counts": [{"value": "a", "count": 10}, {"value": "aa", "count": 20}],
            },
            {
                "column_name": "col2",
                "counts": [{"value": "b", "count": 5}, {"value": "bb", "count": 6}],
            },
        ],
        "bubbles": [
            {
                "source_data": [
                    {"column_name": "col1", "value": "a"},
                    {"column_name": "col2", "value": "b"},
                ],
                "count": 1,
            },
            {
                "source_data": [
                    {"column_name": "col1", "value": "aa"},
                    {"column_name": "col2", "value": "bb"},
                ],
                "count": 2,
            },
            {
                "source_data": [
                    {"column_name": "col1", "value": "a"},
                    {"column_name": "col2", "value": "bb"},
                ],
                "count": 2,
            },
            {
                "source_data": [
                    {"column_name": "col1", "value": "aa"},
                    {"column_name": "col2", "value": "b"},
                ],
                "count": 1,
            },
        ],
    }


@pytest.fixture
def airlines10mb_1000_records_data_source_server_resp(data_sources_list_server_resp):
    return data_sources_list_server_resp["data"][3]


@pytest.fixture
def airlines10mb_data_source_server_resp(data_sources_list_server_resp):
    return data_sources_list_server_resp["data"][2]


@pytest.fixture
def diagnostics_data_source_server_resp(data_sources_list_server_resp):
    return data_sources_list_server_resp["data"][0]


@pytest.fixture
def dataset_id():
    return "5e177c5bf6fe7c042641f118"


@pytest.fixture
def dataset_url(unittest_endpoint, dataset_id):
    return "{}/datasets/{}/".format(unittest_endpoint, dataset_id)


@pytest.fixture()
def mock_dataset(dataset_id):
    return {
        "isLatestVersion": True,
        "categories": ["TRAINING", "PREDICTION"],
        "name": "Anomaly_credit_card.csv",
        "datasetId": dataset_id,
        "versionId": "5e177c5cf6fe7c042641f119",
        "dataPersisted": True,
        "createdBy": "Eric Shaw",
        "creationDate": "2020-01-09T19:17:48.282000Z",
        "isSnapshot": True,
        "isDataEngineEligible": True,
        "datasetSize": 10993415,
        "rowCount": 26127,
        "processingState": "COMPLETED",
        "extraFields": "W.C.",
    }


@pytest.fixture
def mock_dataset_obj(mock_dataset):
    return Dataset.from_server_data(mock_dataset)


@pytest.fixture
def lift_chart_bins_data():
    return [
        {"binWeight": 2.0, "actual": 19.0, "predicted": 18.701785714285712},
        {"binWeight": 1.0, "actual": 10.5, "predicted": 9.716000000000001},
        {"binWeight": 1.0, "actual": 7.5, "predicted": 9.73913043478261},
        {"binWeight": 2.0, "actual": 17.5, "predicted": 19.561085972850677},
        {"binWeight": 1.0, "actual": 12.1, "predicted": 10.4},
        {"binWeight": 1.0, "actual": 13.8, "predicted": 10.549999999999997},
        {"binWeight": 2.0, "actual": 28.5, "predicted": 23.451428571428572},
        {"binWeight": 1.0, "actual": 17.8, "predicted": 13.057142857142855},
        {"binWeight": 1.0, "actual": 14.4, "predicted": 13.452631578947367},
        {"binWeight": 2.0, "actual": 27.4, "predicted": 29.022926829268297},
        {"binWeight": 1.0, "actual": 23.2, "predicted": 15.760377358490558},
        {"binWeight": 1.0, "actual": 17.2, "predicted": 15.811538461538465},
        {"binWeight": 2.0, "actual": 29.799999999999997, "predicted": 31.967142857142857},
        {"binWeight": 1.0, "actual": 21.7, "predicted": 16.33478260869565},
        {"binWeight": 1.0, "actual": 13.1, "predicted": 17.022222222222226},
        {"binWeight": 2.0, "actual": 33.9, "predicted": 34.43989743589744},
        {"binWeight": 1.0, "actual": 20.5, "predicted": 17.86857142857143},
        {"binWeight": 1.0, "actual": 15.6, "predicted": 18.06},
        {"binWeight": 2.0, "actual": 37.400000000000006, "predicted": 36.72619047619048},
        {"binWeight": 1.0, "actual": 20.4, "predicted": 18.79},
        {"binWeight": 1.0, "actual": 19.6, "predicted": 19.18068181818182},
        {"binWeight": 2.0, "actual": 39.0, "predicted": 39.42089047903004},
        {"binWeight": 1.0, "actual": 21.9, "predicted": 20.055714285714277},
        {"binWeight": 1.0, "actual": 21.8, "predicted": 20.089583333333334},
        {"binWeight": 2.0, "actual": 45.7, "predicted": 40.20238095238094},
        {"binWeight": 1.0, "actual": 21.8, "predicted": 20.117894736842103},
        {"binWeight": 1.0, "actual": 16.2, "predicted": 20.24895833333333},
        {"binWeight": 2.0, "actual": 38.6, "predicted": 40.828123261764375},
        {"binWeight": 1.0, "actual": 20.0, "predicted": 20.56131386861314},
        {"binWeight": 1.0, "actual": 24.3, "predicted": 20.604385964912293},
        {"binWeight": 2.0, "actual": 41.5, "predicted": 41.352748538011696},
        {"binWeight": 1.0, "actual": 19.8, "predicted": 20.710743801652903},
        {"binWeight": 1.0, "actual": 21.1, "predicted": 20.7235294117647},
        {"binWeight": 2.0, "actual": 32.6, "predicted": 41.49125},
        {"binWeight": 1.0, "actual": 18.6, "predicted": 20.78782608695652},
        {"binWeight": 1.0, "actual": 21.0, "predicted": 20.794690265486736},
        {"binWeight": 2.0, "actual": 37.3, "predicted": 42.73298850574714},
        {"binWeight": 1.0, "actual": 22.3, "predicted": 21.538356164383554},
        {"binWeight": 1.0, "actual": 23.0, "predicted": 21.79859154929577},
        {"binWeight": 2.0, "actual": 45.5, "predicted": 44.31785714285715},
        {"binWeight": 1.0, "actual": 22.6, "predicted": 22.854999999999997},
        {"binWeight": 1.0, "actual": 22.4, "predicted": 23.418749999999996},
        {"binWeight": 2.0, "actual": 47.0, "predicted": 47.75747028862478},
        {"binWeight": 1.0, "actual": 24.7, "predicted": 24.20416666666667},
        {"binWeight": 1.0, "actual": 16.5, "predicted": 24.233333333333334},
        {"binWeight": 2.0, "actual": 44.0, "predicted": 49.43414634146342},
        {"binWeight": 1.0, "actual": 23.1, "predicted": 24.863829787234042},
        {"binWeight": 1.0, "actual": 26.5, "predicted": 25.13},
        {"binWeight": 2.0, "actual": 50.9, "predicted": 51.14829424307035},
        {"binWeight": 1.0, "actual": 30.7, "predicted": 27.419999999999998},
        {"binWeight": 1.0, "actual": 24.8, "predicted": 28.247999999999998},
        {"binWeight": 2.0, "actual": 51.900000000000006, "predicted": 58.22245989304814},
        {"binWeight": 1.0, "actual": 24.0, "predicted": 29.263636363636362},
        {"binWeight": 1.0, "actual": 33.2, "predicted": 31.84444444444444},
        {"binWeight": 2.0, "actual": 65.6, "predicted": 64.13333333333334},
        {"binWeight": 1.0, "actual": 34.9, "predicted": 33.515},
        {"binWeight": 1.0, "actual": 29.0, "predicted": 34.068749999999994},
        {"binWeight": 2.0, "actual": 68.8, "predicted": 69.67843137254901},
        {"binWeight": 1.0, "actual": 42.8, "predicted": 43.05},
        {"binWeight": 2.0, "actual": 88.7, "predicted": 95.475},
    ]


@pytest.fixture
def roc_curve_data():
    return {
        "rocPoints": [
            {
                "matthewsCorrelationCoefficient": 0.0,
                "liftNegative": 1.6580310880829014,
                "falseNegativeScore": 635,
                "threshold": 1.0,
                "positivePredictiveValue": 0.0,
                "falsePositiveScore": 0,
                "truePositiveRate": 0.0,
                "falsePositiveRate": 0.0,
                "trueNegativeScore": 965,
                "fractionPredictedAsPositive": 0.396875,
                "truePositiveScore": 0,
                "liftPositive": 0.0,
                "trueNegativeRate": 1.0,
                "fractionPredictedAsNegative": 0.603125,
                "negativePredictiveValue": 0.603125,
                "f1Score": 0.0,
                "accuracy": 0.603125,
            },
            {
                "matthewsCorrelationCoefficient": 0.2654644740095313,
                "liftNegative": 0.7027302746382453,
                "falseNegativeScore": 108,
                "threshold": 0.3192387913454449,
                "positivePredictiveValue": 0.4866112650046168,
                "falsePositiveScore": 556,
                "truePositiveRate": 0.8299212598425196,
                "falsePositiveRate": 0.5761658031088083,
                "trueNegativeScore": 409,
                "fractionPredictedAsPositive": 0.396875,
                "truePositiveScore": 527,
                "liftPositive": 2.0911401822803644,
                "trueNegativeRate": 0.42383419689119173,
                "fractionPredictedAsNegative": 0.603125,
                "negativePredictiveValue": 0.7911025145067698,
                "f1Score": 0.6135040745052387,
                "accuracy": 0.585,
            },
            {
                "matthewsCorrelationCoefficient": 0.26949035662808024,
                "liftNegative": 0.6872667722623426,
                "falseNegativeScore": 101,
                "threshold": 0.3159331104401148,
                "positivePredictiveValue": 0.4858962693357598,
                "falsePositiveScore": 565,
                "truePositiveRate": 0.8409448818897638,
                "falsePositiveRate": 0.5854922279792746,
                "trueNegativeScore": 400,
                "fractionPredictedAsPositive": 0.396875,
                "truePositiveScore": 534,
                "liftPositive": 2.118916237832476,
                "trueNegativeRate": 0.41450777202072536,
                "fractionPredictedAsNegative": 0.603125,
                "negativePredictiveValue": 0.7984031936127745,
                "f1Score": 0.615916955017301,
                "accuracy": 0.58375,
            },
            {
                "matthewsCorrelationCoefficient": 0.26539544824735506,
                "liftNegative": 0.6666487690944723,
                "falseNegativeScore": 97,
                "threshold": 0.31168680078090694,
                "positivePredictiveValue": 0.48251121076233183,
                "falsePositiveScore": 577,
                "truePositiveRate": 0.8472440944881889,
                "falsePositiveRate": 0.5979274611398964,
                "trueNegativeScore": 388,
                "fractionPredictedAsPositive": 0.396875,
                "truePositiveScore": 538,
                "liftPositive": 2.134788269576539,
                "trueNegativeRate": 0.40207253886010363,
                "fractionPredictedAsNegative": 0.603125,
                "negativePredictiveValue": 0.8,
                "f1Score": 0.6148571428571429,
                "accuracy": 0.57875,
            },
            {
                "matthewsCorrelationCoefficient": 0.0,
                "liftNegative": 0.0,
                "falseNegativeScore": 0,
                "threshold": 0.040378634122377174,
                "positivePredictiveValue": 0.396875,
                "falsePositiveScore": 965,
                "truePositiveRate": 1.0,
                "falsePositiveRate": 1.0,
                "trueNegativeScore": 0,
                "fractionPredictedAsPositive": 0.396875,
                "truePositiveScore": 635,
                "liftPositive": 2.5196850393700787,
                "trueNegativeRate": 0.0,
                "fractionPredictedAsNegative": 0.603125,
                "negativePredictiveValue": 0.0,
                "f1Score": 0.5682326621923938,
                "accuracy": 0.396875,
            },
        ],
        "negativeClassPredictions": [
            0.3089065297896129,
            0.2192436274291769,
            0.2741881940220157,
            0.45359061567051495,
            0.33373525837036394,
            0.2022848622576362,
            0.37657493994960095,
            0.3446332343090306,
        ],
        "positiveClassPredictions": [
            0.31066443626142176,
            0.3335789706639738,
            0.41265286028960974,
            0.5962910547142551,
            0.6729667252356237,
            0.4358587761356483,
            0.7175456320809883,
            0.6880904423192126,
        ],
    }


@pytest.fixture
def confusion_chart_data():
    return {
        "classMetrics": [
            {
                "actualCount": 9,
                "className": "1",
                "confusionMatrixOneVsAll": [[15, 0], [0, 9]],
                "f1": 1.0,
                "precision": 1.0,
                "predictedCount": 9,
                "recall": 1.0,
                "wasActualPercentages": [
                    {"otherClassName": "1", "percentage": 1.0},
                    {"otherClassName": "2", "percentage": 0.0},
                    {"otherClassName": "3", "percentage": 0.0},
                ],
                "wasPredictedPercentages": [
                    {"otherClassName": "1", "percentage": 1.0},
                    {"otherClassName": "2", "percentage": 0.0},
                    {"otherClassName": "3", "percentage": 0.0},
                ],
            },
            {
                "actualCount": 5,
                "className": "2",
                "confusionMatrixOneVsAll": [[18, 1], [1, 4]],
                "f1": 0.8000000000000002,
                "precision": 0.8,
                "predictedCount": 5,
                "recall": 0.8,
                "wasActualPercentages": [
                    {"otherClassName": "1", "percentage": 0.0},
                    {"otherClassName": "2", "percentage": 0.8},
                    {"otherClassName": "3", "percentage": 0.2},
                ],
                "wasPredictedPercentages": [
                    {"otherClassName": "1", "percentage": 0.0},
                    {"otherClassName": "2", "percentage": 0.8},
                    {"otherClassName": "3", "percentage": 0.2},
                ],
            },
            {
                "actualCount": 10,
                "className": "3",
                "confusionMatrixOneVsAll": [[13, 1], [1, 9]],
                "f1": 0.9,
                "precision": 0.9,
                "predictedCount": 10,
                "recall": 0.9,
                "wasActualPercentages": [
                    {"otherClassName": "1", "percentage": 0.0},
                    {"otherClassName": "2", "percentage": 0.1},
                    {"otherClassName": "3", "percentage": 0.9},
                ],
                "wasPredictedPercentages": [
                    {"otherClassName": "1", "percentage": 0.0},
                    {"otherClassName": "2", "percentage": 0.1},
                    {"otherClassName": "3", "percentage": 0.9},
                ],
            },
        ],
        "confusionMatrix": [[9, 0, 0], [0, 4, 1], [0, 1, 9]],
    }


@pytest.fixture(params=[42, None])
def feature_impact_server_data(request):
    return {
        u"count": 2,
        u"featureImpacts": [
            {
                u"featureName": u"dates",
                u"impactNormalized": 1.0,
                u"impactUnnormalized": 2.0,
                u"redundantWith": None,
            },
            {
                u"featureName": u"item_ids",
                u"impactNormalized": 0.93,
                u"impactUnnormalized": 1.87,
                u"redundantWith": None,
            },
        ],
        u"next": None,
        u"previous": None,
        u"ranRedundancyDetection": True,
        u"rowCount": request.param,
        u"shapBased": False,
    }


@pytest.fixture
def feature_impact_server_data_filtered(feature_impact_server_data):
    del feature_impact_server_data["next"]
    del feature_impact_server_data["previous"]
    return feature_impact_server_data


@pytest.fixture
def create_dataset_definitions():
    return [
        {
            "identifier": "user",
            "catalogVersionId": "5c88a37770fc42a2fcc62759",
            "catalogId": "5c88a37770fc42a2fcc62759",
            "snapshotPolicy": "latest",
        },
        {
            "identifier": "transaction",
            "catalogId": "5c88a37770fc42a2fcc62759",
            "catalogVersionId": "5c88a37770fc42a2fcc62760",
            "primaryTemporalKey": "date",
            "snapshotPolicy": "latest",
        },
    ]


@pytest.fixture
def create_jdbc_dataset_definitions():
    return [
        {
            "identifier": "user",
            "catalog_id": "60c6e4430fc6c2770b7ec634",
            "catalog_version_id": "60c6e4440fc6c2770b7ec635",
            "primary_temporal_key": None,
            "feature_list_id": "60c6e451b42e0f6c5e920f5d",
            "snapshot_policy": "dynamic",
            "data_source": {
                "data_store_name": "mssql-remote-dev",
                "data_store_id": "60c6e3f833de57c65440f571",
                "data_source_id": "60c6e3f833de57c65440f581",
                "url": "jdbc:sqlserver://10.50.225.143:1433;databaseName=safer",
                "dbtable": "safer_credit",
                "schema": "",
                "catalog": "safer",
            },
            "is_deleted": False,
            "data_sources": None,
        }
    ]


@pytest.fixture
def create_relationships():
    return [
        {
            "dataset2Identifier": "user",
            "dataset1Keys": ["user_id", "dept_id"],
            "dataset2Keys": ["user_id", "dept_id"],
        },
        {
            "dataset1Identifier": "user",
            "dataset2Identifier": "transaction",
            "dataset1Keys": ["user_id"],
            "dataset2Keys": ["user_id"],
            "featureDerivationWindowStart": -10,
            "featureDerivationWindowEnd": -1,
            "featureDerivationWindowTimeUnit": "SECOND",
            "predictionPointRounding": 5,
            "predictionPointRoundingTimeUnit": "SECOND",
        },
    ]


@pytest.fixture
def create_relationships_multiple_fdws():
    return [
        {
            "dataset2Identifier": "user",
            "dataset1Keys": ["user_id", "dept_id"],
            "dataset2Keys": ["user_id", "dept_id"],
        },
        {
            "dataset1Identifier": "user",
            "dataset2Identifier": "transaction",
            "dataset1Keys": ["user_id"],
            "dataset2Keys": ["user_id"],
            "featureDerivationWindows": [
                {"start": -10, "end": -1, "unit": "SECOND"},
                {"start": -20, "end": -10, "unit": "SECOND"},
            ],
            "predictionPointRounding": 5,
            "predictionPointRoundingTimeUnit": "SECOND",
        },
    ]


@pytest.fixture
def create_feature_discovery_settings():
    return [
        {"name": "enable_numeric_skewness", "value": True},
        {"name": "enable_numeric_kurtosis", "value": True},
    ]


@pytest.fixture
def relationships_configuration(
    create_dataset_definitions, create_relationships, create_feature_discovery_settings,
):
    return {
        "id": "5a530498d5c1f302d6d176c8",
        "datasetDefinitions": create_dataset_definitions,
        "relationships": create_relationships,
        "featureDiscoveryMode": "manual",
        "featureDiscoverySettings": create_feature_discovery_settings,
    }


@pytest.fixture
def relationships_configuration_multiple_fdws(
    create_dataset_definitions,
    create_relationships_multiple_fdws,
    create_feature_discovery_settings,
):
    return {
        "id": "5a530498d5c1f302d6d176c8",
        "datasetDefinitions": create_dataset_definitions,
        "relationships": create_relationships_multiple_fdws,
        "featureDiscoveryMode": "manual",
        "featureDiscoverySettings": create_feature_discovery_settings,
    }


@pytest.fixture
def jdbc_relationships_configuration(create_jdbc_dataset_definitions, create_relationships):
    return {
        "id": "5a530498d5c1f302d6d176c8",
        "datasetDefinitions": create_jdbc_dataset_definitions,
        "relationships": create_relationships,
    }


@pytest.fixture
def shap_impact_server_data():
    return {
        u"count": 2,
        u"rowCount": 10,
        u"shapImpacts": [
            {
                u"featureName": u"number_inpatient",
                u"impactNormalized": 1.0,
                u"impactUnnormalized": 0.07670175497683789,
            },
            {
                u"featureName": u"number_diagnoses",
                u"impactNormalized": 0.6238014237049752,
                u"impactUnnormalized": 0.047846663955221636,
            },
        ],
    }


@pytest.fixture
def make_models_url(unittest_endpoint):
    def _make_models_url(model_id=None):
        base_url = "{}/customModels/".format(unittest_endpoint)
        if model_id is not None:
            return "{}{}/".format(base_url, model_id)
        return base_url

    return _make_models_url


@pytest.fixture
def make_tasks_url(unittest_endpoint):
    def _make_tasks_url(task_id=None):
        base_url = "{}/customTasks/".format(unittest_endpoint)
        if task_id is not None:
            return "{}{}/".format(base_url, task_id)
        return base_url

    return _make_tasks_url


@pytest.fixture
def mocked_models(mocked_custom_model_version, mocked_custom_model_version2):
    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "data": [
            {
                "deploymentsCount": 0,
                "updated": "2020-04-30T09:55:38.319786Z",
                "description": "",
                "language": "python",
                "created": "2020-04-30T09:55:38.319558Z",
                "targetType": "Regression",
                "createdBy": "admin@datarobot.com",
                "latestVersion": mocked_custom_model_version,
                "customModelType": "training",
                "id": "5eaaa09a40240308176cee55",
                "name": "dddd",
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
            {
                "multiseriesIdColumns": None,
                "targetType": "Regression",
                "trainingDatasetVersionId": "5ea6bbc7402403321d4e1fae",
                "timeSteps": None,
                "latestVersion": mocked_custom_model_version2,
                "targetName": "MEDV",
                "id": "5ea6b5da402403181895cc51",
                "featureDerivationWindowEnd": None,
                "datetimePartitionColumn": None,
                "trainingDatasetId": "5ea6bbc7402403321d4e1fad",
                "trainingDataPartitionColumn": None,
                "positiveClassLabel": "1",
                "customModelType": "inference",
                "updated": "2020-04-27T10:37:14.341673Z",
                "description": "",
                "negativeClassLabel": "0",
                "createdBy": "admin@datarobot.com",
                "timeUnit": None,
                "predictionThreshold": 0.5,
                "trainingDataFileName": "boston_housing.csv",
                "forecastWindowStart": None,
                "deploymentsCount": 0,
                "name": "ee",
                "language": "",
                "created": "2020-04-27T10:37:14.340932Z",
                "forecastWindowEnd": None,
                "isTimeSeries": False,
                "trainingDataAssignmentInProgress": False,
                "featureDerivationWindowStart": None,
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
        ],
        "previous": None,
    }


@pytest.fixture
def mocked_models_with_resources(mocked_models):
    models = copy.deepcopy(mocked_models)
    models["data"][1].update(
        {"networkEgressPolicy": "PUBLIC", "maximumMemory": 1024 * 1024 * 1024, "replicas": 3}
    )
    return models


@pytest.fixture
def mocked_multiclass_models(mocked_models):
    models = copy.deepcopy(mocked_models)
    models["data"][1].update(
        {"classLabels": ["hot dog", "burrito", "hoagie", "reuben"], "targetType": "Multiclass"}
    )
    for key in ["predictionThreshold", "positiveClassLabel", "negativeClassLabel"]:
        models["data"][1].pop(key, None)

    return models


@pytest.fixture
def mocked_unstructured_models(mocked_models):
    models = copy.deepcopy(mocked_models)
    models["data"][1].update({"targetType": "Unstructured"})
    for key in ["predictionThreshold", "positiveClassLabel", "negativeClassLabel", "targetName"]:
        models["data"][1].pop(key, None)

    return models


@pytest.fixture
def mocked_anomaly_models(mocked_models):
    models = copy.deepcopy(mocked_models)
    models["data"][1].update({"targetType": "Anomaly"})
    for key in ["predictionThreshold", "positiveClassLabel", "negativeClassLabel", "targetName"]:
        models["data"][1].pop(key, None)

    return models


@pytest.fixture
def mocked_custom_model_version(mocked_versions):
    return mocked_versions["data"][0]


@pytest.fixture
def mocked_custom_model_version_with_resources(mocked_versions):
    data = copy.deepcopy(mocked_versions["data"][1])
    data.update(
        {"networkEgressPolicy": "PUBLIC", "maximumMemory": 1024 * 1024 * 1024, "replicas": 3}
    )
    return data


@pytest.fixture
def base_environment_id():
    return "5f21ca7de9790c26984e2758"


@pytest.fixture
def base_environment_version_id():
    return "5f21ca7de9790c26984e2759"


@pytest.fixture
def mocked_versions(base_environment_id, base_environment_version_id):
    versions = {
        "next": None,
        "previous": None,
        "data": [
            {
                "id": "5cf4d3f5f93ee26daac18a1a",
                "customModelId": "5cf4d3f5f930e26daac18a1xx",
                "baseEnvironmentId": base_environment_id,
                "baseEnvironmentVersionId": base_environment_version_id,
                "label": "Version 1",
                "description": "",
                "versionMinor": 0,
                "versionMajor": 1,
                "isFrozen": False,
                "items": [
                    {
                        "id": "5cf4d3f5f930e26daac18xxx",
                        "fileName": "name",
                        "filePath": "path",
                        "fileSource": "source",
                        "created": "2019-09-28T15:19:26.587583Z",
                    }
                ],
                "created": "2019-09-28T15:19:26.587583Z",
                "dependencies": [
                    {
                        "packageName": "pandas",
                        "constraints": [{"constraintType": "<=", "version": "0.23"}],
                        "line": "pandas <= 0.23",
                        "lineNumber": 1,
                    }
                ],
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
            {
                "id": "5cf4d3f5f930e26daac18aBB",
                "customModelId": "5cf4d3f5f930e26daac18a1BB",
                "baseEnvironmentId": base_environment_id,
                "baseEnvironmentVersionId": base_environment_version_id,
                "label": "Version 2",
                "description": "ss",
                "versionMinor": 2,
                "versionMajor": 3,
                "isFrozen": True,
                "items": [],
                "created": "2019-09-28T15:19:26.587583Z",
                "dependencies": [
                    {
                        "packageName": "pandas",
                        "constraints": [{"constraintType": ">=", "version": "1.0"}],
                        "line": "pandas >= 1.0",
                        "lineNumber": 1,
                    }
                ],
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
            {
                "id": "5cf4d3f5f930e26daac18FFFF",
                "customModelId": "5cf4d3f5f930e26daac18FFFF",
                "baseEnvironmentId": base_environment_id,
                "baseEnvironmentVersionId": base_environment_version_id,
                "label": "Version 2",
                "description": "ss",
                "versionMinor": 2,
                "versionMajor": 3,
                "isFrozen": True,
                "items": [],
                "created": "2019-09-28T15:19:26.587583Z",
                "networkEgressPolicy": "PUBLIC",
                "maximumMemory": 1024 * 1024 * 1024,
                "replicas": 3,
            },
            {
                "id": "5cf4d3f5f930e26daac18FFFF",
                "customModelId": "5cf4d3f5f930e26daac18FFFF",
                "baseEnvironmentId": base_environment_id,
                "baseEnvironmentVersionId": base_environment_version_id,
                "label": "Version 2",
                "description": "ss",
                "versionMinor": 2,
                "versionMajor": 3,
                "isFrozen": True,
                "items": [],
                "created": "2019-09-28T15:19:26.587583Z",
                "networkEgressPolicy": "PUBLIC",
                "maximumMemory": 1024 * 1024 * 1024,
                "replicas": 3,
                "requiredMetadata": {"REQUIRED_FIELD": "super important value"},
                "requiredMetadataValues": [
                    {"fieldName": "REQUIRED_FIELD", "value": "super important value"}
                ],
            },
        ],
    }
    versions.update({"count": len(versions["data"]), "totalCount": len(versions["data"])})
    return versions


@pytest.fixture
def mocked_custom_model_version_no_dependencies(mocked_custom_model_version):
    version = copy.deepcopy(mocked_custom_model_version)
    version.pop("dependencies")
    return version


@pytest.fixture
def mocked_custom_model_version_no_base_environment(mocked_custom_model_version):
    version = copy.deepcopy(mocked_custom_model_version)
    version.pop("baseEnvironmentId")
    return version


@pytest.fixture
def mocked_custom_model_version_future_field_in_version(mocked_custom_model_version):
    version = copy.deepcopy(mocked_custom_model_version)
    version["future_field"] = "chrome"
    return version


@pytest.fixture
def mocked_custom_model_version_future_field_in_dependency(mocked_custom_model_version):
    version = copy.deepcopy(mocked_custom_model_version)
    version["dependencies"][0]["future_field"] = "chrome"
    return version


@pytest.fixture
def mocked_custom_model_version_future_field_in_constraint(mocked_custom_model_version):
    version = copy.deepcopy(mocked_custom_model_version)
    version["dependencies"][0]["constraints"][0]["future_field"] = "chrome"
    return version


@pytest.fixture
def mock_custom_model_dependency_build_submitted():
    return {
        "buildStatus": "submitted",
        "buildStart": "2019-09-28T15:19:26.587583Z",
        "buildEnd": None,
        "buildLogLocation": None,
    }


@pytest.fixture
def mock_custom_model_dependency_build_processing():
    return {
        "buildStatus": "processing",
        "buildStart": "2019-09-28T15:19:26.587583Z",
        "buildEnd": None,
        "buildLogLocation": None,
    }


@pytest.fixture
def mock_custom_model_dependency_build_failed():
    return {
        "buildStatus": "failed",
        "buildStart": "2019-09-28T15:19:26.587583Z",
        "buildEnd": "2019-09-28T15:25:26.587583Z",
        "buildLogLocation": "http://log-location.com",
    }


@pytest.fixture
def mock_custom_model_dependency_build_success():
    return {
        "buildStatus": "success",
        "buildStart": "2019-09-28T15:19:26.587583Z",
        "buildEnd": "2019-09-28T15:25:26.587583Z",
        "buildLogLocation": "http://log-location.com",
    }


@pytest.fixture
def mocked_custom_model_version2(mocked_versions):
    return mocked_versions["data"][1]


@pytest.fixture
def feature_association_matrix_url(unittest_endpoint, project_id):
    return unittest_endpoint + "/projects/{}/featureAssociationMatrix/".format(project_id)


@pytest.fixture
def feature_association_matrix():
    return {
        "strengths": [
            {
                "feature1": "first feature",
                "feature2": "second feature",
                "statistic": 0.04064090101797498,
            },
            {
                "feature1": "second feature",
                "feature2": "third feature",
                "statistic": 0.014925019571901423,
            },
            {"feature1": "first feature", "feature2": "first feature", "statistic": 1},
            {"feature1": "second feature", "feature2": "second feature", "statistic": 1},
            {"feature1": "third feature", "feature2": "third feature", "statistic": 1},
        ],
        "features": [
            {
                "clusterSortIndex": 0,
                "clusterName": "Some cluster",
                "clusterId": 0,
                "feature": "first feature",
                "strengthSortIndex": 8,
                "alphabeticSortIndex": 0,
                "importanceSortIndex": 11,
            },
            {
                "clusterSortIndex": 1,
                "clusterName": "Some cluster",
                "clusterId": 0,
                "feature": "second feature",
                "strengthSortIndex": 12,
                "alphabeticSortIndex": 1,
                "importanceSortIndex": 5,
            },
            {
                "clusterSortIndex": 2,
                "clusterName": "Some cluster",
                "clusterId": 1,
                "feature": "third feature",
                "strengthSortIndex": 10,
                "alphabeticSortIndex": 2,
                "importanceSortIndex": 7,
            },
        ],
    }


@pytest.fixture
def feature_association_matrix_details_url(unittest_endpoint):
    fam_details_url = "/projects/{}/featureAssociationMatrixDetails/?feature1={}&feature2={}"
    return unittest_endpoint + fam_details_url


@pytest.fixture
def feature_association_matrix_details_data():
    return {
        "chart_type": "VERTICAL_BOX",
        "values": [
            ["168", "33", 0.045],
            ["1", "1", 0.329],
            ["37", "17", 0.005],
            ["207", "41", 0.014],
            ["178", "35", 0.006],
            ["34", "16", 0.032],
            ["194", "37", 0.004],
        ],
        "features": ["area1", "area2"],
        "types": ["NUMERIC", "NUMERIC"],
    }


@pytest.fixture
def feature_association_featurelists_url(unittest_endpoint, project_id):
    return unittest_endpoint + "/projects/{}/featureAssociationFeaturelists/".format(project_id)


@pytest.fixture
def feature_association_featurelists_data():
    return {
        "featurelists": [
            {
                "featurelistId": "54e510ef8bd88f5aeb02a3ed",
                "hasFam": True,
                "title": "Informative Features",
            },
            {
                "featurelistId": "6034fee009e8a6e9a2eead20",
                "hasFam": False,
                "title": "Raw Features",
            },
        ]
    }


@pytest.fixture
def project_clustering_json():
    return """
    {
        "id": "556cdfbb100d2b0e88585195",
        "projectName": "clustering project",
        "fileName": "clustering.csv",
        "stage": "modeling",
        "autopilotMode": 4,
        "created": "2021-11-02T09:37:02.691034Z",
        "target": null,
        "metric": "Silhouette Score",
        "partition": {
            "cvMethod": "random",
            "validationType": "TVH",
            "holdoutPct": 0.0,
            "validationPct": 10.0144,
            "useTimeSeries": null,
            "userPartitionCol": null,
            "trainingLevel": null,
            "validationLevel": null,
            "reps": null,
            "holdoutLevel": null,
            "cvHoldoutLevel": null,
            "partitionKeyCols": null,
            "datetimeCol": null
        },
        "recommender": {
            "isRecommender": null,
            "recommenderItemId": null,
            "recommenderUserId": null
        },
        "advancedOptions": {
            "weights": null,
            "blueprintThreshold": 3,
            "responseCap": false,
            "seed": null,
            "scaleoutModelingMode": "disabled",
            "defaultMonotonicIncreasingFeaturelistId": null,
            "defaultMonotonicDecreasingFeaturelistId": null,
            "onlyIncludeMonotonicBlueprints": false,
            "shapOnlyMode": false,
            "runLeakageRemovedFeatureList": false,
            "smartDownsampled": false,
            "majorityDownsamplingRate": null,
            "downsampledMinorityRows": null,
            "downsampledMajorityRows": null,
            "blendBestModels": true,
            "prepareModelForDeployment": true,
            "considerBlendersInRecommendation": false,
            "scoringCodeOnly": false
        },
        "positiveClass": null,
        "maxTrainPct": 89.9857,
        "maxTrainRows": 5014,
        "scaleoutMaxTrainPct": 89.9857,
        "scaleoutMaxTrainRows": 5014,
        "holdoutUnlocked": false,
        "catalogId": null,
        "catalogVersionId": null,
        "externalTimeSeriesBaselineDatasetMetadata": null,
        "segmentation": null,
        "queryGeneratorId": null,
        "targetType": null,
        "unsupervisedMode": true,
        "unsupervisedType": null,
        "useFeatureDiscovery": false,
        "quickrun": false,
        "automodelDeploymentId": null
    }
    """


@pytest.fixture
def project_clustering_data(project_clustering_json):
    data = json.loads(project_clustering_json)
    return from_api(data)


@pytest.fixture
def clustering_model_gmm_json():
    return """
    {
        "blueprintId": "36865bdc3a4a7d7227ea04df5f60b6e0",
        "featurelistId": "618106c5a52dcb9bd13cb308",
        "featurelistName": "Informative Features",
        "hasEmptyClusters": false,
        "id": "556ce973100d2b6e51ca96571",
        "isFrozen": false,
        "isNClustersDynamicallyDetermined": false,
        "isStarred": false,
        "linkFunction": null,
        "metrics": {
            "Silhouette Score": {
                "validation": 0.27480000257492065,
                "crossValidation": null,
                "holdout": null,
                "training": 0.2623400092124939,
                "backtestingScores": null,
                "backtesting": null
            }
        },
        "modelCategory": "model",
        "modelFamily": "CLUSTER",
        "modelNumber": 86,
        "modelType": "Gaussian Mixture Model",
        "monotonicDecreasingFeaturelistId": null,
        "monotonicIncreasingFeaturelistId": null,
        "nClusters": 5,
        "parentModelId": null,
        "predictionThreshold": 0.5,
        "predictionThresholdReadOnly": false,
        "processes": [
            "One-Hot Encoding",
            "Truncated Singular Value Decomposition",
            "Matrix of word-grams occurrences",
            "Standardize",
            "Gaussian Mixture Model"
        ],
        "projectId": "556cdfbb100d2b0e88585195",
        "samplePct": 89.9857,
        "supportsComposableMl": false,
        "supportsMonotonicConstraints": false,
        "trainingDuration": null,
        "trainingEndDate": null,
        "trainingRowCount": 5014,
        "trainingStartDate": null
    }
    """


@pytest.fixture
def clustering_model_kmeans_json():
    return """
    {
        "blueprintId": "f81f14a2ee21c088ea211bb96cfa44bd",
        "featurelistId": "618106c5a52dcb9bd13cb308",
        "featurelistName": "Informative Features",
        "hasEmptyClusters": false,
        "id": "556ce973100d2b6e51ca96572",
        "isFrozen": false,
        "isNClustersDynamicallyDetermined": false,
        "isStarred": false,
        "linkFunction": null,
        "metrics": {
            "Silhouette Score": {
                "validation": 0.2781899869441986,
                "crossValidation": null,
                "holdout": null,
                "training": 0.2622799873352051,
                "backtestingScores": null,
                "backtesting": null
            }
        },
        "modelCategory": "model",
        "modelFamily": "CLUSTER",
        "modelNumber": 89,
        "modelType": "K-Means Clustering",
        "monotonicDecreasingFeaturelistId": null,
        "monotonicIncreasingFeaturelistId": null,
        "nClusters": 3,
        "parentModelId": null,
        "predictionThreshold": 0.5,
        "predictionThresholdReadOnly": false,
        "processes": [
            "One-Hot Encoding",
            "Truncated Singular Value Decomposition",
            "Matrix of word-grams occurrences",
            "Standardize",
            "K-Means Clustering"
        ],
        "projectId": "556cdfbb100d2b0e88585195",
        "samplePct": 89.9857,
        "supportsComposableMl": false,
        "supportsMonotonicConstraints": false,
        "trainingDuration": null,
        "trainingEndDate": null,
        "trainingRowCount": 5014,
        "trainingStartDate": null
    }
    """


@pytest.fixture
def clustering_model_hdbscan_json():
    return """
    {
        "blueprintId": "3185ab2691b5978eb125994b4b129cc5",
        "featurelistId": "618106c5a52dcb9bd13cb308",
        "featurelistName": "Informative Features",
        "hasEmptyClusters": false,
        "id": "556ce973100d2b6e51ca96573",
        "isFrozen": false,
        "isNClustersDynamicallyDetermined": true,
        "isStarred": false,
        "linkFunction": null,
        "metrics": {
            "Silhouette Score": {
                "validation": -0.5048499703407288,
                "crossValidation": null,
                "holdout": null,
                "training": -0.3644700050354004,
                "backtestingScores": null,
                "backtesting": null
            }
        },
        "modelCategory": "model",
        "modelFamily": "CLUSTER",
        "modelNumber": 92,
        "modelType": "Hierarchical Density-Based Spatial Clustering of Applications with Noise",
        "monotonicDecreasingFeaturelistId": null,
        "monotonicIncreasingFeaturelistId": null,
        "nClusters": 91,
        "parentModelId": null,
        "predictionThreshold": 0.5,
        "predictionThresholdReadOnly": false,
        "processes": [
            "One-Hot Encoding",
            "Truncated Singular Value Decomposition",
            "Matrix of word-grams occurrences",
            "Standardize",
            "Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN)"
        ],
        "projectId": "556cdfbb100d2b0e88585195",
        "samplePct": 89.9857,
        "supportsComposableMl": false,
        "supportsMonotonicConstraints": false,
        "trainingDuration": null,
        "trainingEndDate": null,
        "trainingRowCount": 5014,
        "trainingStartDate": null
    }
    """


@pytest.fixture
def clustering_model_gmm_server_data(clustering_model_gmm_json):
    return json.loads(clustering_model_gmm_json)


@pytest.fixture
def clustering_model_kmeans_server_data(clustering_model_kmeans_json):
    return json.loads(clustering_model_kmeans_json)


@pytest.fixture
def clustering_model_hdbscan_server_data(clustering_model_hdbscan_json):
    return json.loads(clustering_model_hdbscan_json)


@pytest.fixture
def clustering_models(
    clustering_model_hdbscan_server_data,
    clustering_model_kmeans_server_data,
    clustering_model_gmm_server_data,
):
    return [
        clustering_model_hdbscan_server_data,
        clustering_model_kmeans_server_data,
        clustering_model_gmm_server_data,
    ]


@pytest.fixture
def dummy_api_object_values():
    yield {"parakeet": "parakeet", "jones": "jones", "squak_squak": "squak_squak"}


@pytest.fixture
def dummy_api_object_class():
    class DummyClass(APIObject):
        def __init__(self, parakeet, jones, squak_squak):
            self.parakeet = parakeet
            self.jones = jones
            self.squak_squak = squak_squak

        def some_function(self):
            pass

    yield DummyClass


@pytest.fixture
def dummy_nested_api_object_class(dummy_api_object_class, dummy_api_object_values):
    class NestedDummyClass(APIObject):
        def __init__(self, parakeet, jones, squak_squak):
            self.parakeet = parakeet
            self.jones = jones
            self.squak_squak = squak_squak
            self.nested = dummy_api_object_class(**dummy_api_object_values)

        def some_other_function(self):
            pass

    yield NestedDummyClass
