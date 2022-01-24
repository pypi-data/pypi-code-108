# encoding: utf-8
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

from mock import Mock, patch
import pytest
import responses

from datarobot.errors import ClientError
from datarobot.models.project import Project
from datarobot.models.restore_discarded_features import DiscardedFeaturesInfo


@pytest.fixture
def async_url():
    return "https://host_name.com/status/status-id/"


@pytest.fixture
def discarded_features_url(unittest_endpoint, project_id):
    return "{}/projects/{}/discardedFeatures/".format(unittest_endpoint, project_id)


@pytest.fixture
def restore_discarded_features_url(unittest_endpoint, project_id):
    return "{}/projects/{}/modelingFeatures/fromDiscardedFeatures/".format(
        unittest_endpoint, project_id
    )


@pytest.fixture
def discarded_features_server_data():
    return {
        "totalRestoreLimit": 5,
        "remainingRestoreLimit": 3,
        "count": 3,
        "features": [
            "input4 (days from timestamp) (7 day mean)",
            "input4 (days from timestamp) (7 day min)",
            "input4 (days from timestamp) (7 day std)",
        ],
    }


@pytest.fixture
def discarded_features_response(discarded_features_url, discarded_features_server_data):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=200,
        content_type="application/json",
        body=json.dumps(discarded_features_server_data),
    )


@pytest.fixture
def restore_discarded_features_response(restore_discarded_features_url, async_url):
    responses.add(
        responses.POST,
        restore_discarded_features_url,
        status=202,
        content_type="application/json",
        adding_headers={"Location": async_url},
        body=json.dumps(
            {
                "featuresToRestore": [
                    "input4 (days from timestamp) (7 day mean)",
                    "input4 (days from timestamp) (7 day min)",
                ],
                "warnings": ['"ololo" does not exist'],
            }
        ),
    )


@pytest.fixture
def discarded_features_not_found_response(discarded_features_url):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=404,
        content_type="application/json",
        body=json.dumps({"message": "no discarded features info"}),
    )


@pytest.fixture
def discarded_features_not_allowed_response(discarded_features_url):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=422,
        content_type="application/json",
        body=json.dumps({"message": "Segmented project is not allowed"}),
    )


@responses.activate
@pytest.mark.usefixtures("discarded_features_response")
def test_retrieve_discarded_features(project_id):
    project = Project(project_id)
    discarded_feature_info = project.get_discarded_features()
    assert discarded_feature_info.features == [
        "input4 (days from timestamp) (7 day mean)",
        "input4 (days from timestamp) (7 day min)",
        "input4 (days from timestamp) (7 day std)",
    ]
    assert discarded_feature_info.count == len(discarded_feature_info.features)
    assert discarded_feature_info.remaining_restore_limit == 3
    assert discarded_feature_info.total_restore_limit == 5


@responses.activate
@pytest.mark.usefixtures("discarded_features_not_found_response")
def test_retrieve_no_discarded_features(project_id):
    with pytest.raises(ClientError):
        DiscardedFeaturesInfo.retrieve(project_id)


@responses.activate
@pytest.mark.usefixtures("discarded_features_not_allowed_response")
def test_retrieve_segmented_project_not_allowed(project_id):
    with pytest.raises(ClientError):
        DiscardedFeaturesInfo.retrieve(project_id)


@responses.activate
@pytest.mark.usefixtures("restore_discarded_features_response")
@patch("datarobot.models.restore_discarded_features.wait_for_async_resolution", Mock())
def test_restore_discarded_features(project_id):
    project = Project(project_id)
    restored_info = project.restore_discarded_features(
        ["input4 (days from timestamp) (7 day mean)", "input4 (days from timestamp) (7 day min)"]
    )
    assert restored_info.warnings == ['"ololo" does not exist']
    assert restored_info.restored_features == [
        "input4 (days from timestamp) (7 day mean)",
        "input4 (days from timestamp) (7 day min)",
    ]
