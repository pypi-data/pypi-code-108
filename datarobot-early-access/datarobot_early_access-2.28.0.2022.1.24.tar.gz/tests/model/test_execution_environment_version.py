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

from datarobot import ExecutionEnvironmentVersion
from datarobot.enums import EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS
from datarobot.errors import AsyncTimeoutError
from tests.model.utils import assert_version


@pytest.fixture
def mocked_versions(mocked_execution_environment_versions):
    return mocked_execution_environment_versions


@pytest.fixture
def mocked_version(mocked_execution_environment_version):
    return mocked_execution_environment_version


@pytest.fixture
def make_versions_url(unittest_endpoint):
    def _make_versions_url(environment_id, version_id=None):
        base_url = "{}/executionEnvironments/{}/versions/".format(unittest_endpoint, environment_id)
        if version_id is not None:
            return "{}{}/".format(base_url, version_id)
        return base_url

    return _make_versions_url


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def test_from_server_data(mocked_version):
    version = ExecutionEnvironmentVersion.from_server_data(mocked_version)
    assert_version(version, mocked_version)


@responses.activate
def test_create_non_blocking(mocked_version, make_versions_url, tmpdir):
    responses.add(
        responses.POST,
        make_versions_url(mocked_version["environmentId"]),
        status=200,
        content_type="application/json",
        body=json.dumps({"id": mocked_version["id"]}),
    )
    responses.add(
        responses.GET,
        make_versions_url(mocked_version["environmentId"], mocked_version["id"]),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_version),
    )
    docker_context_file = tmpdir.mkdir("sub").join("docker_context")
    docker_context_file.write(b"docker_context archive content")
    docker_context_file_path = str(docker_context_file)

    version = ExecutionEnvironmentVersion.create(
        mocked_version["environmentId"],
        docker_context_file_path,
        mocked_version["label"],
        mocked_version["description"],
        max_wait=None,
    )
    assert_version(version, mocked_version)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_versions_url(mocked_version["environmentId"])
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_versions_url(
        mocked_version["environmentId"], mocked_version["id"]
    )


@responses.activate
def test_create_timeout(mocked_version, make_versions_url, tmpdir):
    responses.add(
        responses.POST,
        make_versions_url(mocked_version["environmentId"]),
        status=200,
        content_type="application/json",
        body=json.dumps({"id": mocked_version["id"]}),
    )

    mocked_version["buildStatus"] = "processing"
    mock_get_response(
        make_versions_url(mocked_version["environmentId"], mocked_version["id"]), mocked_version,
    )

    docker_context_file = tmpdir.mkdir("sub").join("docker_context")
    docker_context_file.write(b"docker_context archive content")
    docker_context_file_path = str(docker_context_file)

    with pytest.raises(AsyncTimeoutError):
        ExecutionEnvironmentVersion.create(
            mocked_version["environmentId"],
            docker_context_file_path,
            mocked_version["label"],
            mocked_version["description"],
            max_wait=0,
        )

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_versions_url(mocked_version["environmentId"])
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_versions_url(
        mocked_version["environmentId"], mocked_version["id"]
    )


@responses.activate
@pytest.mark.parametrize("final_status", EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS.FINAL_STATUSES)
def test_create_blocking(mocked_version, make_versions_url, final_status, tmpdir):
    mocked_version1 = deepcopy(mocked_version)
    mocked_version2 = deepcopy(mocked_version)

    mocked_version1["buildStatus"] = "processing"
    mocked_version2["buildStatus"] = final_status

    responses.add(
        responses.POST,
        make_versions_url(mocked_version["environmentId"]),
        status=200,
        content_type="application/json",
        body=json.dumps({"id": mocked_version["id"]}),
    )

    get_url = make_versions_url(mocked_version["environmentId"], mocked_version["id"])
    mock_get_response(get_url, mocked_version1)
    mock_get_response(get_url, mocked_version2)

    docker_context_file = tmpdir.mkdir("sub").join("docker_context")
    docker_context_file.write(b"docker_context archive content")
    docker_context_file_path = str(docker_context_file)

    version = ExecutionEnvironmentVersion.create(
        mocked_version["environmentId"],
        docker_context_file_path,
        mocked_version["label"],
        mocked_version["description"],
    )
    assert_version(version, mocked_version2)

    assert len(responses.calls) == 3

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_versions_url(mocked_version["environmentId"])
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == get_url
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == get_url


@responses.activate
def test_get_version(mocked_version, make_versions_url):
    url = make_versions_url(mocked_version["environmentId"], mocked_version["id"])
    mock_get_response(url, mocked_version)

    version = ExecutionEnvironmentVersion.get(mocked_version["environmentId"], mocked_version["id"])
    assert_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_versions(mocked_versions, make_versions_url):
    environment_id = mocked_versions["data"][0]["environmentId"]
    url = make_versions_url(environment_id)
    mock_get_response(url, mocked_versions)

    versions = ExecutionEnvironmentVersion.list(environment_id)

    assert len(versions) == len(mocked_versions["data"])
    for version, mocked_version in zip(versions, mocked_versions["data"]):
        assert_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_versions_multiple_pages(mocked_versions, make_versions_url):
    environment_id = mocked_versions["data"][0]["environmentId"]

    url1 = make_versions_url(environment_id)
    url2 = make_versions_url(environment_id) + "2"

    mocked_versions_2nd = deepcopy(mocked_versions)
    mocked_versions["next"] = url2

    mock_get_response(url1, mocked_versions)
    mock_get_response(url2, mocked_versions_2nd)

    versions = ExecutionEnvironmentVersion.list(environment_id)
    assert len(versions) == len(mocked_versions["data"]) + len(mocked_versions_2nd["data"])
    for version, mocked_version in zip(
        versions, mocked_versions["data"] + mocked_versions_2nd["data"]
    ):
        assert_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_list_filter_build_status(mocked_version, make_versions_url):
    environment_id = mocked_version["environmentId"]
    url = make_versions_url(environment_id) + "?buildStatus={}".format(
        mocked_version["buildStatus"]
    )
    mock_get_response(url, {"count": 1, "next": None, "previous": None, "data": [mocked_version]})

    versions = ExecutionEnvironmentVersion.list(
        environment_id, EXECUTION_ENVIRONMENT_VERSION_BUILD_STATUS.SUCCESS
    )

    assert len(versions) == 1
    assert_version(versions[0], mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
@pytest.mark.parametrize("expected_log", ["", "some log"])
@pytest.mark.parametrize("expected_err", ["", "some error"])
def test_get_build_log(mocked_version, make_versions_url, expected_log, expected_err):
    url = make_versions_url(mocked_version["environmentId"], mocked_version["id"])
    log_url = url + "buildLog/"

    mock_get_response(url, mocked_version)
    mock_get_response(log_url, {"log": expected_log, "error": expected_err})

    environment = ExecutionEnvironmentVersion.get(
        mocked_version["environmentId"], mocked_version["id"]
    )
    log, err = environment.get_build_log()

    assert log == expected_log
    assert err == (None if expected_err == "" else expected_err)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == log_url


@responses.activate
def test_refresh(mocked_version, make_versions_url):
    url = make_versions_url(mocked_version["environmentId"], mocked_version["id"])

    mock_get_response(url, mocked_version)

    mocked_version.update({"buildStatus": "failed", "label": "l"})

    mock_get_response(url, mocked_version)

    version = ExecutionEnvironmentVersion.get(mocked_version["environmentId"], mocked_version["id"])
    version.refresh()
    assert_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url
