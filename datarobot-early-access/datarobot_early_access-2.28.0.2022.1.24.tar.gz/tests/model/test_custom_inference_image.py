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

from datarobot import CustomInferenceImage
from datarobot.utils import camelize


@pytest.fixture
def mocked_test():
    return {
        "id": "5cf4d3f5f930e26daac18alt",
        "status": "succeeded",
        "completedAt": "2019-09-28T15:19:26.587583Z",
    }


@pytest.fixture
def mocked_images(mocked_test):
    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "previous": None,
        "data": [
            {
                "id": "5cf4d3f5f930e26daac18a1a",
                "customModel": {"id": "5cf4d3f5f930e26daac18acc", "name": "cm"},
                "customModelVersion": {"id": "5cf4d3f5f930e26daac18acv", "label": "cmv"},
                "executionEnvironment": {"id": "5cf4d3f5f930e26daac18aee", "name": "ee"},
                "executionEnvironmentVersion": {"id": "5cf4d3f5f930e26daac18aev", "label": "eev"},
                "latestTest": mocked_test,
            },
            {
                "id": "5cf4d3f5f930e26daac18a2b",
                "customModel": {"id": "5cf4d3f5f930e26daac18bcc", "name": "cm n2"},
                "customModelVersion": {"id": "5cf4d3f5f930e26daac18bcv", "label": "cmv n2"},
                "executionEnvironment": {"id": "5cf4d3f5f930e26daac18bee", "name": "ee n2"},
                "executionEnvironmentVersion": {
                    "id": "5cf4d3f5f930e26daac18bev",
                    "label": "eev n2",
                },
                "latestTest": None,
            },
        ],
    }


@pytest.fixture
def mocked_image(mocked_images):
    return mocked_images["data"][0]


@pytest.fixture
def make_images_url(unittest_endpoint):
    def _make_images_url(image_id=None):
        base_url = "{}/customInferenceImages/".format(unittest_endpoint)
        if image_id is not None:
            return "{}{}/".format(base_url, image_id)
        return base_url

    return _make_images_url


def assert_image(image, image_json):
    assert image.id == image_json["id"]
    assert image.custom_model["id"] == image_json["customModel"]["id"]
    assert image.custom_model["name"] == image_json["customModel"]["name"]
    assert image.custom_model_version["id"] == image_json["customModelVersion"]["id"]
    assert image.custom_model_version["label"] == image_json["customModelVersion"]["label"]
    assert image.execution_environment["id"] == image_json["executionEnvironment"]["id"]
    assert image.execution_environment["name"] == image_json["executionEnvironment"]["name"]

    exec_env_ver = image_json["executionEnvironmentVersion"]
    assert image.execution_environment_version["id"] == exec_env_ver["id"]
    assert image.execution_environment_version["label"] == exec_env_ver["label"]
    if image.latest_test is None:
        assert image_json["latestTest"] is None
    else:
        assert image.latest_test["id"] == image_json["latestTest"]["id"]
        assert image.latest_test["status"] == image_json["latestTest"]["status"]
        assert image.latest_test["completed_at"] == image_json["latestTest"]["completedAt"]


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def test_from_server_data(mocked_image):
    image = CustomInferenceImage.from_server_data(mocked_image)
    assert_image(image, mocked_image)


@responses.activate
def test_create_image(mocked_image, make_images_url, tmpdir):
    responses.add(
        responses.POST,
        make_images_url(),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_image),
    )

    image = CustomInferenceImage.create(
        mocked_image["customModel"]["id"],
        mocked_image["customModelVersion"]["id"],
        mocked_image["executionEnvironment"]["id"],
        mocked_image["executionEnvironmentVersion"]["id"],
    )
    assert_image(image, mocked_image)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_images_url()


@responses.activate
def test_get_image(mocked_image, make_images_url):
    url = make_images_url(mocked_image["id"])
    mock_get_response(url, mocked_image)

    image = CustomInferenceImage.get(mocked_image["id"])
    assert_image(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_images(mocked_images, make_images_url):
    url = make_images_url()
    mock_get_response(url, mocked_images)

    images = CustomInferenceImage.list()

    assert len(images) == len(mocked_images["data"])
    for image, mocked_image in zip(images, mocked_images["data"]):
        assert_image(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_images_multiple_pages(mocked_images, make_images_url):
    url1 = make_images_url()
    url2 = make_images_url() + "2"

    mocked_images_2nd = deepcopy(mocked_images)
    mocked_images["next"] = url2

    mock_get_response(url1, mocked_images)
    mock_get_response(url2, mocked_images_2nd)

    images = CustomInferenceImage.list()
    assert len(images) == len(mocked_images["data"]) + len(mocked_images_2nd["data"])
    for image, mocked_image in zip(images, mocked_images["data"] + mocked_images_2nd["data"]):
        assert_image(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
@pytest.mark.parametrize(
    "filter, property_key",
    [
        ("testing_status", "latestTest.status"),
        ("custom_model_id", "customModel.id"),
        ("custom_model_version_id", "customModelVersion.id"),
        ("environment_id", "executionEnvironment.id"),
        ("environment_version_id", "executionEnvironmentVersion.id"),
    ],
)
def test_list_filter_build_status(mocked_image, make_images_url, filter, property_key):
    prop = mocked_image
    for key in property_key.split("."):
        prop = prop[key]

    url = make_images_url() + "?{}={}".format(camelize(filter), prop)
    mock_get_response(url, {"count": 1, "next": None, "previous": None, "data": [mocked_image]})

    images = CustomInferenceImage.list(**{filter: prop})

    assert len(images) == 1
    assert_image(images[0], mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_refresh(mocked_image, make_images_url, mocked_test):
    # arrange
    url = make_images_url(mocked_image["id"])

    mocked_image.update({"latestTest": None})
    mock_get_response(url, mocked_image)

    mocked_image.update({"latestTest": mocked_test})
    mock_get_response(url, mocked_image)

    # act
    image = CustomInferenceImage.get(mocked_image["id"])
    image.refresh()

    # assert
    assert_image(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url


@responses.activate
def test_get_feature_impact(mocked_image, make_images_url, feature_impact_server_data):
    # arrange
    url = make_images_url(mocked_image["id"])
    mock_get_response(url, mocked_image)
    responses.add(
        responses.GET,
        url + "featureImpact/",
        status=200,
        content_type="application/json",
        body=json.dumps(feature_impact_server_data),
    )

    # act
    image = CustomInferenceImage.get(mocked_image["id"])
    feature_impacts = image.get_feature_impact()

    # assert
    assert feature_impacts == feature_impact_server_data["featureImpacts"]

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url + "featureImpact/"


@responses.activate
def test_get_feature_impact_with_metadata(
    mocked_image, make_images_url, feature_impact_server_data, feature_impact_server_data_filtered
):
    # arrange
    url = make_images_url(mocked_image["id"])
    mock_get_response(url, mocked_image)
    responses.add(
        responses.GET,
        url + "featureImpact/",
        status=200,
        content_type="application/json",
        body=json.dumps(feature_impact_server_data),
    )

    # act
    image = CustomInferenceImage.get(mocked_image["id"])
    feature_impacts = image.get_feature_impact(with_metadata=True)

    # assert
    assert feature_impacts == feature_impact_server_data_filtered

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url + "featureImpact/"


@responses.activate
def test_calculate_feature_impact(unittest_endpoint, mocked_image, make_images_url):
    # arrange
    status_url = "{}/status_url".format(unittest_endpoint)
    url = make_images_url(mocked_image["id"])
    impact_url = url + "featureImpact/"
    mock_get_response(url, mocked_image)

    responses.add(
        responses.POST,
        impact_url,
        status=200,
        content_type="application/json",
        headers={"Location": status_url},
        # this ID is ignored, we only use headers and we dont' have a real ID from the backend.
        body=json.dumps({"status_id": "5cf4d3f5f930e26daac18a1a"}),
    )

    responses.add(
        responses.GET, status_url, headers={"Location": url}, status=303,
    )

    # act
    image = CustomInferenceImage.get(mocked_image["id"])
    image.calculate_feature_impact()

    # assert

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "POST"
    assert responses.calls[1].request.url == impact_url
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == status_url
