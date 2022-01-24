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

from datarobot import errors, ShapImpact


@responses.activate
@pytest.mark.usefixtures("shap_impact_job_creation_response", "shap_impact_running_response")
def test_get_shap_impact_job_result_not_finished(project_id, model_id):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    with pytest.raises(errors.JobNotFinished):
        shap_impact_job.get_result()


@responses.activate
@pytest.mark.usefixtures("shap_impact_job_creation_response", "shap_impact_running_response")
def test_wait_for_shap_impact_never_finished(project_id, model_id, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    shap_impact_job = ShapImpact.create(project_id, model_id)
    with pytest.raises(errors.AsyncTimeoutError):
        shap_impact_job.get_result_when_complete(max_wait=1)


def assert_shap_impact_result(shap_impact, shap_impact_server_data):
    assert shap_impact is not None
    assert shap_impact.count is not None
    assert shap_impact.shap_impacts is not None
    assert shap_impact.row_count == 10
    assert shap_impact.count == len(shap_impact.shap_impacts)
    assert shap_impact.count == shap_impact_server_data["count"]
    assert len(shap_impact.shap_impacts) == len(shap_impact_server_data["shapImpacts"])
    for actual, expected in zip(shap_impact.shap_impacts, shap_impact_server_data["shapImpacts"]):
        assert actual["feature_name"] == expected["featureName"]
        assert actual["impact_normalized"] == expected["impactNormalized"]
        assert actual["impact_unnormalized"] == expected["impactUnnormalized"]


@responses.activate
@pytest.mark.usefixtures(
    "shap_impact_job_creation_response", "shap_impact_completed_response", "shap_impact_response"
)
def test_get_shap_impact_job_result_finished(project_id, model_id, shap_impact_server_data):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    shap_impact = shap_impact_job.get_result()
    assert_shap_impact_result(shap_impact, shap_impact_server_data)


@responses.activate
@pytest.mark.usefixtures(
    "shap_impact_previously_ran_response", "shap_impact_completed_response", "shap_impact_response"
)
def test_get_or_request_shap_impact_previously_requested(
    project_id, model_id, shap_impact_server_data
):
    shap_impact_job = ShapImpact.create(project_id, model_id)
    assert shap_impact_job.job_type == "shapImpact"
    assert shap_impact_job.status == "COMPLETED"
    shap_impact = shap_impact_job.get_result()
    assert_shap_impact_result(shap_impact, shap_impact_server_data)


@responses.activate
@pytest.mark.usefixtures("shap_impact_response")
def test_shap_impact_get(project_id, model_id, shap_impact_server_data):
    shap_impact = ShapImpact.get(project_id, model_id)
    assert_shap_impact_result(shap_impact, shap_impact_server_data)
