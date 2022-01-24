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
from copy import deepcopy
import json

import mock
import pytest
import responses

from datarobot import CustomModelTest


@pytest.fixture
def custom_model_id():
    return "5cf4d3f5f930e26daac18acc"


@pytest.fixture
def mocked_tests():
    return {
        "count": 1,
        "totalCount": 1,
        "next": None,
        "previous": None,
        "data": [
            {
                "id": "5cf4d3f5f930e26daac18acc",
                "datasetId": "5e60d80b6eb24502c8814ed2",
                "datasetVersionId": "5d31ffd2417a06005178268b",
                "customModelImageId": "5e9ec6503129820040debd8c",
                "imageType": "customModelVersion",
                "overallStatus": "in_progress",
                "testingStatus": {
                    "error_check": {"status": "in_progress", "message": "msg"},
                    "null_value_imputation": {"status": "in_progress", "message": "msg"},
                    "long_running_service": {"status": "in_progress", "message": "msg"},
                    "side_effects": {"status": "in_progress", "message": "msg"},
                },
                "completedAt": "2019-09-28T15:19:26.587583Z",
                "createdBy": "5e60d80b6eb24502c8814ed2",
                "created": "2019-09-28T15:19:26.587583Z",
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
            # unstructured models without dataset fields.
            {
                "id": "5cf4d3f5f930e26daac18acc",
                "customModelImageId": "5e9ec6503129820040debd8c",
                "imageType": "customModelVersion",
                "overallStatus": "in_progress",
                "testingStatus": {
                    "error_check": {"status": "in_progress", "message": "msg"},
                    "null_value_imputation": {"status": "in_progress", "message": "msg"},
                    "long_running_service": {"status": "in_progress", "message": "msg"},
                    "side_effects": {"status": "in_progress", "message": "msg"},
                },
                "completedAt": "2019-09-28T15:19:26.587583Z",
                "createdBy": "5e60d80b6eb24502c8814ed2",
                "created": "2019-09-28T15:19:26.587583Z",
                "networkEgressPolicy": None,
                "maximumMemory": None,
                "replicas": None,
            },
        ],
    }


@pytest.fixture
def mocked_tests_with_resources(mocked_tests):
    tests = copy.deepcopy(mocked_tests)
    tests["data"][0].update(
        {"networkEgressPolicy": "PUBLIC", "maximumMemory": 1024 * 1024 * 1024, "replicas": 3}
    )
    return tests


@pytest.fixture
def mocked_test(mocked_tests):
    return mocked_tests["data"][0]


@pytest.fixture
def mocked_test_future_test(mocked_tests):
    test = copy.deepcopy(mocked_tests["data"][0])
    test["testingStatus"]["future_test"] = {"status": "in_progress", "message": "msg"}
    return test


@pytest.fixture
def mocked_test_future_field_in_status(mocked_tests):
    test = copy.deepcopy(mocked_tests["data"][0])
    test["testingStatus"]["error_check"]["future_field"] = "chrome"
    return test


@pytest.fixture
def make_tests_url(unittest_endpoint):
    def _make_tests_url(test_id=None, custom_model_id=None):
        url = "{}/customModelTests/".format(unittest_endpoint)
        if test_id is not None:
            url = "{}{}/".format(url, test_id)
        if custom_model_id is not None:
            url += "?customModelId={}".format(custom_model_id)
        return url

    return _make_tests_url


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def assert_test(test, test_json):
    assert test.id == test_json["id"]
    assert test.custom_model_image_id == test_json["customModelImageId"]
    assert test.image_type == test_json["imageType"]
    assert test.overall_status == test_json["overallStatus"]
    assert test.detailed_status == test_json["testingStatus"]
    assert test.created_by == test_json["createdBy"]
    assert test.completed_at == test_json["completedAt"]
    assert test.created_at == test_json["created"]

    if "datasetId" in test_json:
        assert test.dataset_id == test_json["datasetId"]
    else:
        assert test.dataset_id is None

    if "datasetVersionId" in test_json:
        assert test.dataset_version_id == test_json["datasetVersionId"]
    else:
        assert test.dataset_version_id is None


def test_from_server_data(mocked_test):
    test = CustomModelTest.from_server_data(mocked_test)
    assert_test(test, mocked_test)


@responses.activate
@pytest.mark.parametrize("include_env", [True, False])
@pytest.mark.parametrize("mocked_fixture_name", ["mocked_tests", "mocked_tests_with_resources"])
def test_create_non_blocking(
    request,
    unittest_endpoint,
    mocked_fixture_name,
    make_tests_url,
    custom_model_id,
    tmpdir,
    include_env,
):
    mocked_tests = request.getfixturevalue(mocked_fixture_name)
    status_url = "{}/status_url".format(unittest_endpoint)

    responses.add(
        responses.POST,
        make_tests_url(),
        status=202,
        content_type="application/json",
        headers={"Location": status_url},
    )
    responses.add(
        responses.GET,
        make_tests_url(custom_model_id=custom_model_id),
        status=200,
        content_type="application/json",
        headers={"Location": status_url},
        body=json.dumps(mocked_tests),
    )

    args = [
        custom_model_id,
        "custom model version id",
    ]

    data = mocked_tests["data"][0]
    kwargs = dict(
        dataset_id="dataset id",
        max_wait=None,
        network_egress_policy=data["networkEgressPolicy"],
        maximum_memory=data["maximumMemory"],
        replicas=data["replicas"],
    )

    if include_env:
        kwargs.update(
            {"environment_id": "environment id", "environment_version_id": "environment version id"}
        )

    test = CustomModelTest.create(*args, **kwargs)
    assert_test(test, mocked_tests["data"][0])

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_tests_url()
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_tests_url(custom_model_id=custom_model_id)

    request_body = json.loads(responses.calls[0].request.body)
    if include_env:
        assert all(field in request_body for field in ["environmentId", "environmentVersionId"])
    else:
        assert not any(field in request_body for field in ["environmentId", "environmentVersionId"])


@responses.activate
def test_create_blocking(unittest_endpoint, mocked_tests, make_tests_url, custom_model_id, tmpdir):
    status_url = "{}/status_url".format(unittest_endpoint)

    test = mocked_tests["data"][0]
    test_url = make_tests_url(test["id"])

    responses.add(
        responses.POST,
        make_tests_url(),
        status=202,
        content_type="application/json",
        headers={"Location": status_url},
    )
    responses.add(
        responses.GET,
        make_tests_url(custom_model_id=custom_model_id),
        status=200,
        content_type="application/json",
        headers={"Location": status_url},
        body=json.dumps(mocked_tests),
    )
    responses.add(
        responses.GET,
        status_url,
        status=303,
        content_type="application/json",
        headers={"Location": test_url},
    )
    responses.add(
        responses.GET, test_url, status=200, content_type="application/json", body=json.dumps(test),
    )

    test_created = CustomModelTest.create(
        custom_model_id,
        "custom model version id",
        dataset_id="dataset id",
        environment_id="environment id",
        environment_version_id="environment version id",
    )

    assert_test(test_created, test)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_tests_url()
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_tests_url(custom_model_id=custom_model_id)
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == status_url
    assert responses.calls[3].request.method == "GET"
    assert responses.calls[3].request.url == test_url


@responses.activate
@mock.patch("time.sleep", return_value=None)
def test_create_blocking_error(
    sleep_mock, unittest_endpoint, mocked_tests, make_tests_url, custom_model_id, tmpdir
):
    status_url = "{}/status_url".format(unittest_endpoint)

    test = mocked_tests["data"][0]
    test_url = make_tests_url(test["id"])

    responses.add(
        responses.POST,
        make_tests_url(),
        status=202,
        content_type="application/json",
        headers={"Location": status_url},
    )
    responses.add(
        responses.GET,
        make_tests_url(custom_model_id=custom_model_id),
        status=200,
        content_type="application/json",
        headers={"Location": status_url},
        body=json.dumps(mocked_tests),
    )
    responses.add(
        responses.GET,
        status_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"status": "abort"}),
    )
    test["overallStatus"] = "in_progress"
    responses.add(
        responses.GET, test_url, status=200, content_type="application/json", body=json.dumps(test),
    )
    test["overallStatus"] = "failed"
    responses.add(
        responses.GET, test_url, status=200, content_type="application/json", body=json.dumps(test),
    )

    test_created = CustomModelTest.create(
        custom_model_id,
        "custom model version id",
        dataset_id="dataset id",
        environment_id="environment id",
        environment_version_id="environment version id",
    )

    assert_test(test_created, test)

    sleep_mock.call_count == 1
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_tests_url()
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == make_tests_url(custom_model_id=custom_model_id)
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == status_url
    assert responses.calls[3].request.method == "GET"
    assert responses.calls[3].request.url == test_url
    assert json.loads(responses.calls[3].response.content)["overallStatus"] == "in_progress"
    assert responses.calls[4].request.url == test_url
    assert json.loads(responses.calls[4].response.content)["overallStatus"] == "failed"


@responses.activate
@pytest.mark.parametrize(
    "test_json", ["mocked_test", "mocked_test_future_test", "mocked_test_future_field_in_status"],
)
def test_get_test(request, test_json, make_tests_url):
    mocked_test = request.getfixturevalue(test_json)
    url = make_tests_url(mocked_test["id"])
    mock_get_response(url, mocked_test)

    test = CustomModelTest.get(mocked_test["id"])
    assert_test(test, mocked_test)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_tests(mocked_tests, make_tests_url, custom_model_id):
    url = make_tests_url(custom_model_id=custom_model_id)
    mock_get_response(url, mocked_tests)

    tests = CustomModelTest.list(custom_model_id)

    assert len(tests) == len(mocked_tests["data"])
    for test, mocked_test in zip(tests, mocked_tests["data"]):
        assert_test(test, mocked_test)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_tests_multiple_pages(mocked_tests, make_tests_url, custom_model_id):
    url1 = make_tests_url(custom_model_id=custom_model_id)
    url2 = make_tests_url(custom_model_id=custom_model_id) + "2"

    mocked_tests_2nd = deepcopy(mocked_tests)
    mocked_tests["next"] = url2

    mock_get_response(url1, mocked_tests)
    mock_get_response(url2, mocked_tests_2nd)

    tests = CustomModelTest.list(custom_model_id)
    assert len(tests) == len(mocked_tests["data"]) + len(mocked_tests_2nd["data"])
    for test, mocked_test in zip(tests, mocked_tests["data"] + mocked_tests_2nd["data"]):
        assert_test(test, mocked_test)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_get_log(mocked_test, make_tests_url):
    url = make_tests_url(mocked_test["id"])
    log_url = url + "log/"

    mock_get_response(url, mocked_test)
    responses.add(responses.GET, log_url, status=200, content_type="text/plain", body="log content")

    test = CustomModelTest.get(mocked_test["id"])
    log = test.get_log()

    assert log == "log content"

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == log_url


@responses.activate
def test_get_log_tail(mocked_test, make_tests_url):
    url = make_tests_url(mocked_test["id"])
    log_url = url + "tail/"

    mock_get_response(url, mocked_test)
    responses.add(responses.GET, log_url, status=200, content_type="text/plain", body="log content")

    test = CustomModelTest.get(mocked_test["id"])
    log = test.get_log_tail()

    assert log == "log content"

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == log_url


@responses.activate
def test_cancel(mocked_test, make_tests_url):
    url = make_tests_url(mocked_test["id"])

    mock_get_response(url, mocked_test)
    responses.add(
        responses.DELETE, url, status=200,
    )

    test = CustomModelTest.get(mocked_test["id"])
    test.cancel()

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "DELETE"
    assert responses.calls[1].request.url == url


@responses.activate
def test_refresh(mocked_test, make_tests_url):
    url = make_tests_url(mocked_test["id"])

    mock_get_response(url, mocked_test)

    mocked_test.update({"overallStatus": "failed"})

    mock_get_response(url, mocked_test)

    test = CustomModelTest.get(mocked_test["id"])
    test.refresh()
    assert_test(test, mocked_test)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url
