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

from datarobot import errors
from datarobot.enums import DATE_EXTRACTION, VARIABLE_TYPE_TRANSFORM
from tests.utils import request_body_to_json


@pytest.fixture
def type_transform_create_url(unittest_endpoint, project_id):
    return "{}/projects/{}/typeTransformFeatures/".format(unittest_endpoint, project_id)


@pytest.fixture
def feature_categorical_url(type_transform_create_url):
    return type_transform_create_url + "FeatureCategorical/"


@pytest.fixture
def feature_categorical_json():
    return """
    {
      "featureType": "Categorical",
      "lowInformation": true,
      "name": "FeatureCategorical",
      "uniqueCount": 44,
      "importance": -0.09249820420850052,
      "id": 8,
      "naCount": 0,
      "dateFormat": null,
      "projectId": "556cdfbb100d2b0e88585195",
      "min": null,
      "max": null,
      "mean": null,
      "median": null,
      "stdDev": null,
      "timeSeriesEligible": false,
      "timeSeriesEligibilityReason": "notADate",
      "timeStep": null,
      "timeUnit": null
    }
"""


@pytest.fixture
def type_transform_create_responses(
    type_transform_create_url, async_url, feature_categorical_url, feature_categorical_json
):
    responses.add(
        responses.POST,
        type_transform_create_url,
        status=202,
        body="",
        adding_headers={"Location": async_url},
    )
    responses.add(
        responses.GET,
        async_url,
        status=303,
        body="",
        adding_headers={"Location": feature_categorical_url},
    )
    responses.add(responses.GET, feature_categorical_url, status=200, body=feature_categorical_json)


@responses.activate
@pytest.mark.usefixtures("known_warning")
@pytest.mark.usefixtures("type_transform_create_responses")
def test_create_feature(project):

    new_feat = project.create_type_transform_feature(
        name="FeatureCategorical",
        parent_name="Feature",
        variable_type=VARIABLE_TYPE_TRANSFORM.CATEGORICAL,
    )

    assert new_feat.name == "FeatureCategorical"
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["name"] == "FeatureCategorical"
    assert payload["parentName"] == "Feature"
    assert payload["variableType"] == "categorical"


@responses.activate
@pytest.mark.usefixtures("known_warning")
@pytest.mark.usefixtures("type_transform_create_responses")
def test_create_with_replacement(project):

    new_feat = project.create_type_transform_feature(
        name="FeatureCategorical",
        parent_name="Feature",
        variable_type=VARIABLE_TYPE_TRANSFORM.CATEGORICAL,
        replacement="Missing",
        date_extraction=DATE_EXTRACTION.YEAR_DAY,
    )

    assert new_feat.name == "FeatureCategorical"
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["replacement"] == "Missing"


@responses.activate
@pytest.mark.usefixtures("known_warning")
@pytest.mark.usefixtures("type_transform_create_responses")
def test_create_with_date_extraction(project):
    new_feat = project.create_type_transform_feature(
        name="Date (yearDay)",
        parent_name="Date",
        variable_type=VARIABLE_TYPE_TRANSFORM.CATEGORICAL,
        date_extraction=DATE_EXTRACTION.YEAR_DAY,
    )

    assert new_feat.name == "FeatureCategorical"
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["dateExtraction"] == "yearDay"


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_create_respects_timeout_arg(
    project, async_url, type_transform_create_url, async_running_json, mock_async_time
):
    """
    Want to make sure that create_type_transform_feature respects the max_wait arg.

    We do this by having the async route always return RUNNING and make the call to time
    return 0 (the start) and then 2 - 2 being greater than the max_wait used in this test,
    which is 1 - so an AsyncTimeoutError should be raised


    Parameters
    ----------
    project
    async_url
    type_transform_create_url
    async_running_json
    mock_async_time

    Returns
    -------

    """
    responses.add(
        responses.POST,
        type_transform_create_url,
        status=202,
        body="",
        adding_headers={"Location": async_url},
    )
    responses.add(responses.GET, async_url, status=200, body=async_running_json)

    mock_async_time.time.side_effect = (0, 2)

    with pytest.raises(errors.AsyncTimeoutError):
        project.create_type_transform_feature(
            name="Date (yearDay)",
            parent_name="Date",
            variable_type=VARIABLE_TYPE_TRANSFORM.CATEGORICAL,
            date_extraction=DATE_EXTRACTION.YEAR_DAY,
            max_wait=1,
        )


@responses.activate
@pytest.mark.usefixtures("type_transform_create_responses")
def test_create_feature_categorical_int(project):

    new_feat = project.create_type_transform_feature(
        name="FeatureCategorical",
        parent_name="Feature",
        variable_type=VARIABLE_TYPE_TRANSFORM.CATEGORICAL_INT,
    )

    assert new_feat.name == "FeatureCategorical"
    assert new_feat.feature_type == "Categorical"
    payload = request_body_to_json(responses.calls[0].request)
    assert payload["name"] == "FeatureCategorical"
    assert payload["parentName"] == "Feature"
    assert payload["variableType"] == "categoricalInt"
