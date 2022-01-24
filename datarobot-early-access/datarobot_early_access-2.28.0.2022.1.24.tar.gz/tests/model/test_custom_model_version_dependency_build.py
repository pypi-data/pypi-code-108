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
import json

import mock
import pytest
import responses

from datarobot import CustomModelVersionDependencyBuild
from tests.model.utils import assert_custom_model_version_dependency_build


def mock_response(url, method, response, content_type="application/json"):
    if content_type == "application/json":
        body = json.dumps(response)
    else:
        body = response
    responses.add(
        method, url, status=200, content_type=content_type, body=body,
    )


@pytest.fixture
def make_dependency_build_url(unittest_endpoint):
    def _make_versions_url(custom_model_id, custom_model_version_id, is_log_route=False):
        base_url = "{}/customModels/{}/versions/{}/dependencyBuild{}/".format(
            unittest_endpoint,
            custom_model_id,
            custom_model_version_id,
            "Log" if is_log_route else "",
        )
        return base_url

    return _make_versions_url


@pytest.fixture
def custom_model_ids():
    return "5f2095d1e9790c51a09e6f69", "5f2095d1e9790c51a09e6f69"


@responses.activate
@pytest.mark.parametrize(
    "data",
    [
        "mock_custom_model_dependency_build_submitted",
        "mock_custom_model_dependency_build_processing",
        "mock_custom_model_dependency_build_failed",
        "mock_custom_model_dependency_build_success",
    ],
)
def test_get_info(request, data, custom_model_ids, make_dependency_build_url):
    # arrange
    model_id, version_id = custom_model_ids
    data = request.getfixturevalue(data)
    url = make_dependency_build_url(model_id, version_id)
    mock_response(url, responses.GET, data)

    # act
    build_info = CustomModelVersionDependencyBuild.get_build_info(model_id, version_id)

    # assert
    assert_custom_model_version_dependency_build(build_info, data, model_id, version_id)
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_build_non_blocking(
    mock_custom_model_dependency_build_submitted, custom_model_ids, make_dependency_build_url
):
    # arrange
    model_id, version_id = custom_model_ids
    url = make_dependency_build_url(model_id, version_id)
    mock_response(url, responses.POST, mock_custom_model_dependency_build_submitted)

    # act
    build_info = CustomModelVersionDependencyBuild.start_build(model_id, version_id, max_wait=None)

    # assert
    assert_custom_model_version_dependency_build(
        build_info, mock_custom_model_dependency_build_submitted, model_id, version_id
    )
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == url


@responses.activate
@pytest.mark.parametrize(
    "final_data",
    ["mock_custom_model_dependency_build_success", "mock_custom_model_dependency_build_failed"],
)
def test_build_blocking(
    request,
    final_data,
    mock_custom_model_dependency_build_submitted,
    mock_custom_model_dependency_build_processing,
    custom_model_ids,
    make_dependency_build_url,
):
    # arrange
    model_id, version_id = custom_model_ids
    final_data = request.getfixturevalue(final_data)
    url = make_dependency_build_url(model_id, version_id)
    mock_response(url, responses.POST, mock_custom_model_dependency_build_submitted)
    mock_response(url, responses.GET, mock_custom_model_dependency_build_processing)
    mock_response(url, responses.GET, final_data)

    # act
    with mock.patch("time.sleep"):
        build_info = CustomModelVersionDependencyBuild.start_build(model_id, version_id)

    # assert
    assert_custom_model_version_dependency_build(build_info, final_data, model_id, version_id)
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == url


@responses.activate
def test_get_log(
    mock_custom_model_dependency_build_success, custom_model_ids, make_dependency_build_url
):
    # arrange
    model_id, version_id = custom_model_ids
    url = make_dependency_build_url(model_id, version_id)
    log_url = make_dependency_build_url(model_id, version_id, is_log_route=True)
    expected_log = "this is fine. everything is fine."
    mock_response(url, responses.GET, mock_custom_model_dependency_build_success)
    mock_response(log_url, responses.GET, expected_log, content_type="text/plain")

    # act
    build_info = CustomModelVersionDependencyBuild.get_build_info(model_id, version_id)
    log = build_info.get_log()

    # assert
    assert log == expected_log
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == log_url


@responses.activate
def test_cancel(
    mock_custom_model_dependency_build_success, custom_model_ids, make_dependency_build_url
):
    # arrange
    model_id, version_id = custom_model_ids
    url = make_dependency_build_url(model_id, version_id)
    mock_response(url, responses.GET, mock_custom_model_dependency_build_success)
    mock_response(url, responses.DELETE, None)

    # act
    build_info = CustomModelVersionDependencyBuild.get_build_info(model_id, version_id)
    build_info.cancel()

    # assert
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "DELETE"
    assert responses.calls[1].request.url == url


@responses.activate
def test_refresh(
    mock_custom_model_dependency_build_processing,
    mock_custom_model_dependency_build_success,
    custom_model_ids,
    make_dependency_build_url,
):
    # arrange
    model_id, version_id = custom_model_ids
    url = make_dependency_build_url(model_id, version_id)
    mock_response(url, responses.GET, mock_custom_model_dependency_build_processing)
    mock_response(url, responses.GET, mock_custom_model_dependency_build_success)

    # act
    build_info = CustomModelVersionDependencyBuild.get_build_info(model_id, version_id)
    build_info.refresh()

    # assert
    assert_custom_model_version_dependency_build(
        build_info, mock_custom_model_dependency_build_success, model_id, version_id
    )

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url
