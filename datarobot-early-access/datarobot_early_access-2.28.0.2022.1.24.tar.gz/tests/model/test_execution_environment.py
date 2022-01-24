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

from datarobot import ExecutionEnvironment
from datarobot.models.execution_environment import RequiredMetadataKey
from datarobot.utils import camelize, underscorize
from tests.model.utils import assert_version


@pytest.fixture
def mocked_environments(mocked_execution_environments):
    return mocked_execution_environments


@pytest.fixture
def mocked_environment(mocked_execution_environment):
    return mocked_execution_environment


@pytest.fixture
def make_environments_url(unittest_endpoint):
    def _make_environments_url(environment_id=None):
        base_url = "{}/executionEnvironments/".format(unittest_endpoint)
        if environment_id is not None:
            return "{}{}/".format(base_url, environment_id)
        return base_url

    return _make_environments_url


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def assert_environment(environment, environment_json):
    assert environment.id == environment_json["id"]
    assert environment.name == environment_json["name"]
    assert environment.description == environment_json["description"]
    assert environment.programming_language == environment_json["programmingLanguage"]
    assert environment.is_public == environment_json["isPublic"]
    assert environment.created_at == environment_json["created"]
    if environment.latest_version is None:
        assert environment_json["latestVersion"] is None
    else:
        assert_version(environment.latest_version, environment_json["latestVersion"])

    if environment_json.get("requiredMetadataKeys"):
        assert all(
            key.field_name == key_json["fieldName"] and key.display_name == key_json["displayName"]
            for key, key_json in zip(
                environment.required_metadata_keys, environment_json["requiredMetadataKeys"]
            )
        )


def test_from_server_data(mocked_environment):
    environment = ExecutionEnvironment.from_server_data(mocked_environment)
    assert_environment(environment, mocked_environment)


@responses.activate
@pytest.mark.parametrize(
    "mock_environment",
    ["mocked_environment", "mocked_execution_environment_with_required_metadata_keys"],
)
def test_create_environment(request, make_environments_url, tmpdir, mock_environment):
    mock_environment = request.getfixturevalue(mock_environment)
    responses.add(
        responses.POST,
        make_environments_url(),
        status=200,
        content_type="application/json",
        body=json.dumps({"id": mock_environment["id"]}),
    )
    responses.add(
        responses.GET,
        make_environments_url(mock_environment["id"]),
        status=200,
        content_type="application/json",
        body=json.dumps(mock_environment),
    )

    keys = [
        RequiredMetadataKey.from_data({underscorize(k): v for k, v in key.items()})
        for key in mock_environment.get("requiredMetadataKeys", {})
    ]
    keys = keys or None

    environment = ExecutionEnvironment.create(
        mock_environment["name"], mock_environment["description"], required_metadata_keys=keys
    )
    assert_environment(environment, mock_environment)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_environments_url()
    if mock_environment.get("requiredMetadataKeys"):
        assert json.loads(responses.calls[0].request.body)[
            "requiredMetadataKeys"
        ] == mock_environment.get("requiredMetadataKeys")
    else:
        assert "requiredMetadataKeys" not in json.loads(responses.calls[0].request.body)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_environments_url(mock_environment["id"])


@responses.activate
@pytest.mark.parametrize(
    "mock_environment",
    ["mocked_environment", "mocked_execution_environment_with_required_metadata_keys"],
)
def test_get_environment(request, mock_environment, make_environments_url):
    mock_environment = request.getfixturevalue(mock_environment)
    url = make_environments_url(mock_environment["id"])
    mock_get_response(url, mock_environment)

    environment = ExecutionEnvironment.get(mock_environment["id"])
    assert_environment(environment, mock_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_environments(mocked_environments, make_environments_url):
    url = make_environments_url()
    mock_get_response(url, mocked_environments)

    environments = ExecutionEnvironment.list()

    assert len(environments) == len(mocked_environments["data"])
    for environment, mocked_environment in zip(environments, mocked_environments["data"]):
        assert_environment(environment, mocked_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_environments_multiple_pages(mocked_environments, make_environments_url):
    url1 = make_environments_url()
    url2 = make_environments_url() + "2"

    mocked_environments_2nd = deepcopy(mocked_environments)
    mocked_environments["next"] = url2

    mock_get_response(url1, mocked_environments)
    mock_get_response(url2, mocked_environments_2nd)

    environments = ExecutionEnvironment.list()
    assert len(environments) == len(mocked_environments["data"]) + len(
        mocked_environments_2nd["data"]
    )
    for environment, mocked_environment in zip(
        environments, mocked_environments["data"] + mocked_environments_2nd["data"]
    ):
        assert_environment(environment, mocked_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_list_filter_search_for(mocked_environment, make_environments_url):
    url = make_environments_url() + "?searchFor=xyz"
    mock_get_response(
        url, {"count": 1, "next": None, "previous": None, "data": [mocked_environment]}
    )

    environments = ExecutionEnvironment.list(search_for="xyz")

    assert len(environments) == 1
    assert_environment(environments[0], mocked_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_delete(mocked_environment, make_environments_url):
    url = make_environments_url(mocked_environment["id"])

    mock_get_response(url, mocked_environment)
    responses.add(
        responses.DELETE, url, status=204, content_type="application/json",
    )

    execution_environment = ExecutionEnvironment.get(mocked_environment["id"])
    execution_environment.delete()

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "DELETE"
    assert responses.calls[1].request.url == url


@responses.activate
@pytest.mark.parametrize(
    "attrs",
    [
        {"name": "nx"},
        {"description": "dx"},
        {"name": "nx", "description": "dx"},
        {
            "requiredMetadataKeys": [
                RequiredMetadataKey(
                    field_name="FIELD_{}".format(i), display_name="field {}".format(i)
                )
                for i in range(3)
            ]
        },
    ],
)
def test_update(mocked_environment, make_environments_url, attrs):
    envrironment_id = mocked_environment["id"]
    url = make_environments_url(envrironment_id)

    mock_get_response(url, mocked_environment)

    mock_update_fields = attrs.copy()
    if "requiredMetadataKeys" in mock_update_fields:
        mock_update_fields["requiredMetadataKeys"] = [
            {camelize(k): v for k, v in key.to_dict().items()}
            for key in mock_update_fields["requiredMetadataKeys"]
        ]

    mocked_environment.update(**mock_update_fields)

    responses.add(
        responses.PATCH,
        url,
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_environment),
    )

    environment = ExecutionEnvironment.get(envrironment_id)
    environment.update(**{underscorize(k): v for k, v in attrs.items()})
    assert_environment(environment, mocked_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "PATCH"
    assert responses.calls[1].request.url == url
    assert json.loads(responses.calls[1].request.body) == mock_update_fields


@responses.activate
def test_refresh(mocked_environment, make_environments_url):
    envrironment_id = mocked_environment["id"]
    url = make_environments_url(envrironment_id)

    mock_get_response(url, mocked_environment)

    mocked_environment.update({"programmingLanguage": "r", "name": "xx"})

    mock_get_response(url, mocked_environment)

    environment = ExecutionEnvironment.get(envrironment_id)
    environment.refresh()
    assert_environment(environment, mocked_environment)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url
