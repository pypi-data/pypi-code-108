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

import pytest
import responses

from datarobot import errors


@pytest.fixture
def cv_scores_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/crossValidationScores/".format(
        project_id, model_id
    )


@pytest.fixture
def cv_scores():
    return {
        "metric1": {"1.0": "val", "2.0": "val2"},
        "metric2": {"1.0": "val3", "2.0": "val4"},
    }


@pytest.fixture
def cv_scores_get_response(cv_scores_url, cv_scores):
    responses.add(
        responses.GET,
        cv_scores_url,
        status=200,
        content_type="applicaiton/json",
        body=json.dumps(cv_scores),
    )


@pytest.fixture
def cv_scores_get_response_404(cv_scores_url, cv_scores):
    responses.add(
        responses.GET,
        cv_scores_url,
        status=404,
        content_type="applicaiton/json",
        body="object does not contain cross validation scores",
    )


@pytest.fixture
def cv_scores_get_response_filter_by_metric(cv_scores_url, cv_scores):
    url = cv_scores_url + "?metric=metric1"
    responses.add(
        responses.GET, url, status=200, content_type="applicaiton/json", body=json.dumps(cv_scores)
    )


@pytest.fixture
def cv_scores_get_response_filter_by_partition(cv_scores_url, cv_scores):
    url = cv_scores_url + "?partition=2"
    responses.add(
        responses.GET, url, status=200, content_type="applicaiton/json", body=json.dumps(cv_scores)
    )


@pytest.fixture
def cv_scores_get_response_filter_by_partition_and_metric(cv_scores_url, cv_scores):
    url = cv_scores_url + "?partition=2&metric=metric1"
    responses.add(
        responses.GET, url, status=200, content_type="applicaiton/json", body=json.dumps(cv_scores)
    )


@responses.activate
@pytest.mark.usefixtures("cv_scores_get_response")
def test_get_cross_validation_scores(one_model, cv_scores):
    cv_scores_retrieved = one_model.get_cross_validation_scores()
    assert cv_scores_retrieved == cv_scores


@responses.activate
@pytest.mark.usefixtures("cv_scores_get_response_filter_by_metric")
def test_get_cross_validation_scores_filtered_by_metric(one_model, cv_scores):
    cv_scores_retrieved = one_model.get_cross_validation_scores(metric="metric1")
    assert cv_scores_retrieved == cv_scores


@responses.activate
@pytest.mark.usefixtures("cv_scores_get_response_filter_by_partition")
def test_get_cross_validation_scores_filtered_by_partition(one_model, cv_scores):
    cv_scores_retrieved = one_model.get_cross_validation_scores(partition=2)
    assert cv_scores_retrieved == cv_scores


@responses.activate
@pytest.mark.usefixtures("cv_scores_get_response_filter_by_partition_and_metric")
def test_get_cross_validation_scores_filtered_by_partition_and_metric(one_model, cv_scores):
    cv_scores_retrieved = one_model.get_cross_validation_scores(partition=2, metric="metric1")
    assert cv_scores_retrieved == cv_scores


@responses.activate
@pytest.mark.usefixtures("cv_scores_get_response_404")
def test_get_cross_validation_scores_404(one_model):
    with pytest.raises(errors.ClientError):
        one_model.get_cross_validation_scores()
