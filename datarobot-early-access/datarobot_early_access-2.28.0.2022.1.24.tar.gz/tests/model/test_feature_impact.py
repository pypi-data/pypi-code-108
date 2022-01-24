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


@responses.activate
@pytest.mark.usefixtures("feature_impact_job_creation_response", "feature_impact_running_response")
def test_get_feature_impact_job_result_not_finished(one_model):
    feature_impact_job = one_model.request_feature_impact()
    with pytest.raises(errors.JobNotFinished):
        feature_impact_job.get_result()


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_job_creation_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_get_feature_impact_job_result_finished(feature_impact_server_data, one_model):
    feature_impact_job = one_model.request_feature_impact(
        row_count=feature_impact_server_data["rowCount"]
    )
    feature_impact = feature_impact_job.get_result()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_job_creation_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_get_feature_impact_job_result_finished_with_metadata(
    feature_impact_server_data, feature_impact_server_data_filtered, one_model
):
    feature_impact_job = one_model.request_feature_impact(
        row_count=feature_impact_server_data["rowCount"], with_metadata=True
    )
    feature_impact = feature_impact_job.get_result()
    # Note: we are not exposing the rowCount via an existing method yet and this is just to ensure
    # it does not break with an extended response format.
    assert feature_impact == feature_impact_server_data_filtered


@responses.activate
@pytest.mark.usefixtures("feature_impact_job_creation_response", "feature_impact_running_response")
def test_wait_for_feature_impact_never_finished(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    feature_impact_job = one_model.request_feature_impact()
    with pytest.raises(errors.AsyncTimeoutError):
        feature_impact_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_previously_ran_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_get_or_request_feature_impact_previously_requested(one_model, feature_impact_server_data):
    feature_impact = one_model.get_or_request_feature_impact()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_previously_ran_response__no_job_id", "feature_impact_response",
)
def test_get_or_request_feature_impact_previously_requested_but_no_job_id(
    one_model, feature_impact_server_data
):
    feature_impact = one_model.get_or_request_feature_impact()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_previously_ran_response", "feature_impact_running_response",
)
def test_get_or_request_feature_impact_currently_running_waits(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    with pytest.raises(errors.AsyncTimeoutError):
        one_model.get_or_request_feature_impact(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_job_creation_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_get_or_request_feature_impact(one_model, feature_impact_server_data):
    feature_impact = one_model.get_or_request_feature_impact()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures(
    "feature_impact_job_creation_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_get_or_request_feature_impact_with_metadata(
    one_model, feature_impact_server_data_filtered
):
    feature_impact = one_model.get_or_request_feature_impact(with_metadata=True)
    assert feature_impact == feature_impact_server_data_filtered


@responses.activate
@pytest.mark.usefixtures(
    "client",
    "feature_impact_job_creation_response",
    "feature_impact_completed_response",
    "feature_impact_response",
)
def test_wait_for_feature_impact_finished(one_model, feature_impact_server_data):
    # Would like to include a mock response for not done yet, but that didn't work.
    # Looks like `responses` might do that when `assert_all_requests_are_fired` is true.
    feature_impact_job = one_model.request_feature_impact()
    feature_impact = feature_impact_job.get_result_when_complete(max_wait=0.5)
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures("feature_impact_response")
def test_get_feature_impact_assumed_complete(one_model, feature_impact_server_data):
    feature_impact = one_model.get_feature_impact()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures("feature_impact_response")
def test_get_feature_impact_assumed_complete_with_metadata(
    one_model, feature_impact_server_data_filtered
):
    feature_impact = one_model.get_feature_impact(with_metadata=True)
    assert feature_impact == feature_impact_server_data_filtered


@responses.activate
@pytest.mark.usefixtures("known_warning")
def test_get_feature_impact_no_redundancy(
    one_model, feature_impact_server_data, feature_impact_url
):
    feature_impact_server_data["ranRedundancyDetection"] = False
    responses.add(
        responses.GET,
        feature_impact_url,
        status=200,
        content_type="application/json",
        json=feature_impact_server_data,
    )
    feature_impact = one_model.get_feature_impact()
    assert feature_impact == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.usefixtures("multiclass_feature_impact_response")
def test_get_multiclass_feature_impact(one_model, multiclass_feature_impact_server_data):
    feature_impact = one_model.get_multiclass_feature_impact()
    assert feature_impact == multiclass_feature_impact_server_data["classFeatureImpacts"]
