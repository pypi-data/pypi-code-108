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
from copy import deepcopy
import json

import pytest
import responses
from six.moves.urllib.parse import urljoin

from datarobot import enums
from datarobot.enums import CUSTOM_MODEL_TARGET_TYPE
from tests.model.utils import change_response_value


@pytest.fixture
def model_url(project_url, model_id):
    return urljoin(project_url, "models/{}/".format(model_id))


@pytest.fixture
def feature_impact_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/featureImpact/".format(project_id, model_id)


@pytest.fixture
def multiclass_feature_impact_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/multiclassFeatureImpact/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_impact_job_creation_response(feature_impact_url, job_url):
    responses.add(
        responses.POST,
        feature_impact_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def multiclass_feature_impact_server_data():
    return {
        "ranRedundancyDetection": False,
        "classFeatureImpacts": [
            {
                "featureImpacts": [
                    {
                        "featureName": "Petal Width",
                        "redundantWith": None,
                        "impactUnnormalized": 0.157,
                        "impactNormalized": 0.701,
                    },
                    {
                        "featureName": "Petal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.121,
                        "impactNormalized": 0.539,
                    },
                    {
                        "featureName": "Sepal Width",
                        "redundantWith": None,
                        "impactUnnormalized": 0.225,
                        "impactNormalized": 1.0,
                    },
                    {
                        "featureName": "Sepal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.057,
                        "impactNormalized": 0.257,
                    },
                ],
                "class": "setosa",
            },
            {
                "featureImpacts": [
                    {
                        "featureName": "Petal Width",
                        "redundantWith": None,
                        "impactUnnormalized": 0.302,
                        "impactNormalized": 1.0,
                    },
                    {
                        "featureName": "Petal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.229,
                        "impactNormalized": 0.758,
                    },
                    {
                        "featureName": "Sepal Width",
                        "redundantWith": None,
                        "impactUnnormalized": 0.221,
                        "impactNormalized": 0.730,
                    },
                    {
                        "featureName": "Sepal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.073,
                        "impactNormalized": 0.241,
                    },
                ],
                "class": "versicolor",
            },
            {
                "featureImpacts": [
                    {
                        "featureName": "Petal Width",
                        "redundantWith": None,
                        "impactUnnormalized": 0.273,
                        "impactNormalized": 1.0,
                    },
                    {
                        "featureName": "Petal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.174,
                        "impactNormalized": 0.640,
                    },
                    {
                        "featureName": "Sepal Width",
                        "redundantWith": None,
                        "impactUnnormalized": -0.001,
                        "impactNormalized": -0.006,
                    },
                    {
                        "featureName": "Sepal Length",
                        "redundantWith": None,
                        "impactUnnormalized": 0.018,
                        "impactNormalized": 0.067,
                    },
                ],
                "class": "virginica",
            },
        ],
    }


@pytest.fixture
def feature_impact_response(feature_impact_server_data, feature_impact_url):
    body = json.dumps(feature_impact_server_data)
    responses.add(
        responses.GET, feature_impact_url, status=200, content_type="application/json", body=body
    )


@pytest.fixture
def multiclass_feature_impact_response(
    multiclass_feature_impact_server_data, multiclass_feature_impact_url
):
    body = json.dumps(multiclass_feature_impact_server_data)
    responses.add(
        responses.GET,
        multiclass_feature_impact_url,
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def feature_impact_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType="featureImpact")


@pytest.fixture
def feature_impact_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType="featureImpact")


@pytest.fixture
def approximate_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_RULESETS)


@pytest.fixture
def approximate_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_RULESETS)


@pytest.fixture
def prime_validation_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_VALIDATION)


@pytest.fixture
def prime_validation_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_VALIDATION)


@pytest.fixture
def feature_impact_completed_response(
    feature_impact_job_finished_server_data, job_url, feature_impact_url
):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_impact_job_finished_server_data),
        status=303,
        adding_headers={"Location": feature_impact_url},
        content_type="application/json",
    )


@pytest.fixture
def feature_impact_previously_ran_response(project_url, model_id, job_id):
    return _feature_impact_previously_ran_response(project_url, model_id, job_id)


@pytest.fixture
def feature_impact_previously_ran_response__no_job_id(project_url, model_id):
    return _feature_impact_previously_ran_response(
        project_url,
        model_id,
        message="Feature Impact has been computed for this model.",
        job_id=None,
    )


def _feature_impact_previously_ran_response(project_url, model_id, job_id, message=None):
    """
    Loads a response that the given model has already ran its feature impact
     """
    body = {
        "message": message or "Feature Impact is in progress for this model.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        "{}models/{}/featureImpact/".format(project_url, model_id),
        body=json.dumps(body),
        status=422,
        content_type="application/json",
    )


@pytest.fixture
def feature_impact_running_response(feature_impact_job_running_server_data, job_url):
    """
    Loads a response that the given job is a featureImpact job, and is running
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_impact_job_running_server_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def approximate_job_creation_response(project_url, model_id, job_url):
    responses.add(
        responses.POST,
        "{}models/{}/primeRulesets/".format(project_url, model_id),
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def approximate_completed_response(
    approximate_job_finished_server_data,
    job_url,
    project_url,
    model_id,
    ruleset_without_model_server_data,
    ruleset_with_model_server_data,
):
    rulesets_url = "{}models/{}/primeRulesets/".format(project_url, model_id)
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(approximate_job_finished_server_data),
        status=303,
        adding_headers={"Location": rulesets_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        rulesets_url,
        body=json.dumps([ruleset_with_model_server_data, ruleset_without_model_server_data]),
        content_type="application/json",
    )


@pytest.fixture
def prime_validation_job_creation_response(project_url, job_url):
    responses.add(
        responses.POST,
        "{}primeFiles/".format(project_url),
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def prime_validation_job_completed_response(
    prime_validation_job_finished_server_data, job_url, project_url, prime_file_server_data
):
    file_url = "{}primeFiles/{}/".format(project_url, prime_file_server_data["id"])
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(prime_validation_job_finished_server_data),
        status=303,
        adding_headers={"Location": file_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        file_url,
        body=json.dumps(prime_file_server_data),
        content_type="application/json",
    )


@pytest.fixture
def mocked_execution_environment_versions():
    return {
        "count": 5,
        "totalCount": 5,
        "next": None,
        "previous": None,
        "data": [
            {
                "id": "5cf4d3f5f930e26daac18a1a",
                "environmentId": "5cf4d3f5f930e26daac18a1xx",
                "label": "Version 1",
                "description": "",
                "buildStatus": "success",
                "created": "2019-09-28T15:19:26.587583Z",
            },
            {
                "id": "5cf4d3f5f930e26daac18a2a",
                "environmentId": "5cf4d3f5f930e26daac18a1xx",
                "label": "Version 1",
                "description": "",
                "buildStatus": "processing",
                "created": "2019-09-28T15:19:26.587583Z",
            },
            {
                "id": "5cf4d3f5f930e26daac18a3a",
                "environmentId": "5cf4d3f5f930e26daac18a1xx",
                "label": "Version 1",
                "description": "some description",
                "buildStatus": "failed",
                "created": "2019-09-28T15:19:26.587583Z",
            },
            {
                "id": "5cf4d3f5f930e26daac18a3a",
                "environmentId": "5cf4d3f5f930e26daac18a1xx",
                "label": "Version 1",
                "description": "some description",
                "buildStatus": "failed",
                "created": "2019-09-28T15:19:26.587583Z",
                "dockerContextSize": 1024,
                "dockerImageSize": 2048,
            },
            {
                "id": "5cf4d3f5f930e26daac18a3a",
                "environmentId": "5cf4d3f5f930e26daac18a1xx",
                "label": "Version 1",
                "description": "some description",
                "buildStatus": "failed",
                "created": "2019-09-28T15:19:26.587583Z",
                "dockerContextSize": None,
                "dockerImageSize": None,
            },
        ],
    }


@pytest.fixture
def mocked_execution_environment_version(mocked_execution_environment_versions):
    return mocked_execution_environment_versions["data"][0]


@pytest.fixture
def mocked_execution_environments(mocked_execution_environment_version):
    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "previous": None,
        "data": [
            {
                "id": "5cf4d3f5f930e26daac18a1a",
                "name": "env1",
                "description": "some description",
                "programmingLanguage": "python",
                "isPublic": True,
                "created": "2019-09-28T15:19:26.587583Z",
                "latestVersion": mocked_execution_environment_version,
            },
            {
                "id": "5cf4d3f5f930e26daac18a1a",
                "name": "env2",
                "description": "",
                "programmingLanguage": "other",
                "isPublic": False,
                "created": "2019-09-28T15:19:26.587583Z",
                "latestVersion": None,
            },
            {
                "id": "5cf4d3f5f930e26daac18a1a",
                "name": "env2",
                "description": "",
                "programmingLanguage": "other",
                "isPublic": False,
                "created": "2019-09-28T15:19:26.587583Z",
                "latestVersion": None,
                "requiredMetadataKeys": [
                    {"fieldName": "FIELD_{}".format(i), "displayName": "field {}".format(i)}
                    for i in range(3)
                ],
            },
        ],
    }


@pytest.fixture
def mocked_execution_environment(mocked_execution_environments):
    return mocked_execution_environments["data"][0]


@pytest.fixture
def mocked_execution_environment_with_required_metadata_keys(mocked_execution_environments):
    return next(
        env for env in mocked_execution_environments["data"] if env.get("requiredMetadataKeys")
    )


@pytest.fixture
def mocked_custom_model_version_with_required_metadata(mocked_versions):
    return next(version for version in mocked_versions["data"] if version.get("requiredMetadata"))


@pytest.fixture
def shap_impact_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/shapImpact/".format(project_id, model_id)


@pytest.fixture
def shap_impact_job_creation_response(shap_impact_url, job_url):
    responses.add(
        responses.POST, shap_impact_url, body="", status=202, adding_headers={"Location": job_url}
    )


@pytest.fixture
def shap_impact_response(shap_impact_server_data, shap_impact_url):
    body = json.dumps(shap_impact_server_data)
    responses.add(
        responses.GET, shap_impact_url, status=200, content_type="application/json", body=body
    )


@pytest.fixture
def shap_impact_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType="shapImpact")


@pytest.fixture
def shap_impact_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType="shapImpact")


@pytest.fixture
def shap_impact_running_response(shap_impact_job_running_server_data, job_url):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(shap_impact_job_running_server_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def shap_impact_completed_response(shap_impact_job_finished_server_data, job_url, shap_impact_url):
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(shap_impact_job_finished_server_data),
        status=303,
        adding_headers={"Location": shap_impact_url},
        content_type="application/json",
    )


@pytest.fixture
def shap_impact_previously_ran_response(project_url, model_id, job_id, job_url):
    body = {
        "message": "SHAP impact already exists.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        "{}models/{}/shapImpact/".format(project_url, model_id),
        body=json.dumps(body),
        status=202,
        content_type="application/json",
        adding_headers={"Location": job_url},
    )


# CustomTask and CustomTaskVersion


@pytest.fixture
def custom_task_id():
    return "60dcbf0e8cd36258f9f5fff7"


@pytest.fixture
def custom_task_version_id():
    return "60dcbf2b8cd36258f9f5fff8"


@pytest.fixture
def custom_task_version(custom_task_version_id, custom_task_id):
    return {
        "id": custom_task_version_id,
        "customTaskId": custom_task_id,
        "created": "abc",
        "description": "this task is the coolest",
        "items": [],
        "isFrozen": True,
        "versionMajor": 1,
        "versionMinor": 2,
        "label": "1.2",
        "trainingHistory": [],
    }


@pytest.fixture
def workspace_items():
    return [
        {
            "fileSource": "local",
            "workspaceId": "60abd24fc3d97e6f5f732575",
            "filePath": "custom.py",
            "storagePath": "workspace/60abd24fc3/custom.py",
            "repositoryLocation": None,
            "repositoryName": None,
            "repositoryFilePath": None,
            "ref": None,
            "commitSha": None,
            "id": "60abd2abb66ce93dc37324d2",
            "created": "2021-05-24T16:22:03.423629Z",
            "fileName": "custom.py",
        },
        {
            "fileSource": "local",
            "workspaceId": "60abd24fc3d97e6f5f732575",
            "filePath": "createPipeline.py",
            "storagePath": "workspace/60abd24fc3/createPipeline.py",
            "repositoryLocation": "some location",
            "repositoryName": "erics-awesome-repo",
            "repositoryFilePath": "x/y.py",
            "ref": "no idea",
            "commitSha": "123abc",
            "id": "60abd2abb66ce93dc37324d3",
            "created": "2021-05-24T16:22:03.423995Z",
            "fileName": "createPipeline.py",
        },
    ]


@pytest.fixture
def training_history():
    return [
        {"projectId": "def", "modelId": "abc"},
        {"projectId": "ghi", "modelId": "jkl"},
    ]


@pytest.fixture
def custom_task_version_arguments():
    return [
        {
            "key": "user_param___param_float",
            "argument": {
                "name": "param_float",
                "type": "float",
                "default": 0.5,
                "values": [0.0, 1.0],
            },
        },
        {
            "key": "user_param___param_floatgrid",
            "argument": {
                "name": "param_floatgrid",
                "type": "floatgrid",
                "default": 0.5,
                "values": [0.0, 1.0],
            },
        },
        {
            "key": "user_param___param_int",
            "argument": {"name": "param_int", "type": "int", "default": 1, "values": [0, 1]},
        },
        {
            "key": "user_param___param_intgrid",
            "argument": {
                "name": "param_intgrid",
                "type": "intgrid",
                "default": 1,
                "values": [0, 1],
            },
        },
        {
            "key": "user_param___param_multi",
            "argument": {
                "name": "param_multi",
                "type": "multi",
                "default": 1,
                "values": {
                    "int": [0, 1],
                    "float": [0.0, 1.0],
                    "select": {"values": ["a", "b", "c"]},
                },
            },
        },
        {
            "key": "user_param___param_sel",
            "argument": {
                "name": "param_sel",
                "type": "select",
                "default": "b",
                "values": ["a", "b", "c"],
            },
        },
        {
            "key": "user_param___param_selgrid",
            "argument": {
                "name": "param_selgrid",
                "type": "selectgrid",
                "default": "b",
                "values": ["a", "b", "c"],
            },
        },
        {
            "key": "user_param___param_string",
            "argument": {
                "name": "param_string",
                "type": "unicode",
                "default": "default string",
                "values": [],
            },
        },
    ]


@pytest.fixture
def custom_task_version_with_optional_values(
    custom_task_version, workspace_items, training_history, custom_task_version_arguments,
):
    new_task_version = deepcopy(custom_task_version)
    new_task_version.update(
        {
            "baseEnvironmentVersionId": "mno",
            "baseEnvironmentId": "pqr",
            "dependencies": [
                {
                    "packageName": "pandas",
                    "constraints": [{"constraintType": ">=", "version": "1.0"}],
                    "line": "pandas >= 1.0",
                    "lineNumber": 1,
                }
            ],
            "items": workspace_items,
            "trainingHistory": training_history,
            "requiredMetadata": {"hello": "world"},
            "requiredMetadataValues": [{"fieldName": "hello", "value": "world"}],
            "arguments": custom_task_version_arguments,
        }
    )
    return new_task_version


@pytest.fixture
def custom_task_version_response_json(custom_task_version_with_optional_values):
    return deepcopy(custom_task_version_with_optional_values)


@pytest.fixture
def custom_task_version_list_response(custom_task_version_response_json):
    second_version = {
        k: change_response_value(v) for k, v in custom_task_version_response_json.items()
    }

    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "data": [custom_task_version_response_json, second_version],
    }


@pytest.fixture
def custom_task(custom_task_id):
    return {
        "created": "10-10-2020",
        "createdBy": "a froody dude",
        "deploymentsCount": 1,
        "description": "there's some stuff",
        "id": custom_task_id,
        "language": "python",
        "name": "the coolest model",
        "targetType": CUSTOM_MODEL_TARGET_TYPE.BINARY,
        "updated": "12-12-3030",
        "latestVersion": None,
        "customModelType": "training",
    }


@pytest.fixture
def custom_task_with_optional_values(custom_task, custom_task_version_with_optional_values):
    full_task = deepcopy(custom_task)
    full_task["latestVersion"] = deepcopy(custom_task_version_with_optional_values)
    full_task["calibratePredictions"] = False
    return full_task


@pytest.fixture
def custom_task_response_json(custom_task_with_optional_values):
    return deepcopy(custom_task_with_optional_values)


@pytest.fixture
def custom_task_list_response(custom_task_response_json):
    second = {k: change_response_value(v) for k, v in custom_task_response_json.items()}
    second["latestVersion"] = None

    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "data": [custom_task_response_json, second],
    }


@pytest.fixture
def custom_task_version_dependency_build_server_data(custom_task_id, custom_task_version_id):
    return {
        "customTaskId": custom_task_id,
        "customTaskVersionId": custom_task_version_id,
        "buildStart": "2018-11-19T14:18:01.468272Z",
        "buildEnd": "2018-11-19T15:18:01.468272Z",
        "buildStatus": "success",
        "buildLogLocation": "https://127.0.0.1/logs/",
    }
