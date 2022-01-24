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

from datarobot import (
    enums,
    FeatureImpactJob,
    Job,
    Project,
    TrainingPredictions,
    TrainingPredictionsJob,
)
from datarobot.errors import AsyncProcessUnsuccessfulError, AsyncTimeoutError

mock_job_data = {
    "status": "inprogress",
    "url": "https://host_name.com/projects/p-id/modelJobs/1/",
    "id": "1",
    "jobType": "model",
    "isBlocked": False,
    "modelId": "5d518cd3962d741512605e2b",
    "projectId": "p-id",
}

mock_model_job_data = {
    "status": enums.QUEUE_STATUS.INPROGRESS,
    "processes": [
        "One-Hot Encoding",
        "Bernoulli Naive Bayes classifier (scikit-learn)",
        "Missing Values Imputed",
        "Gaussian Naive Bayes classifier (scikit-learn)",
        "Naive Bayes combiner classifier",
        "Calibrate predictions",
    ],
    "projectId": "p-id",
    "samplePct": 28.349,
    "modelType": "Naive Bayes combiner classifier",
    "featurelistId": "56d8620bccf94e26f37af0a3",
    "modelCategory": "model",
    "blueprintId": "2a1b9ae97fe61880332e196c770c1f9f",
    "id": "1",
}

SAMPLE_BINARY_PREDICTION_RETURN = json.dumps(
    {
        u"positiveClass": 1.0,
        u"task": u"Binary",
        u"predictions": [
            {
                u"positiveProbability": 0.9,
                u"prediction": 1.0,
                u"rowId": 0,
                u"predictionValues": [
                    {u"value": 0.9, u"label": u"1.0"},
                    {u"value": 0.1, u"label": u"0.0"},
                ],
            },
            {
                u"positiveProbability": 0.1,
                u"prediction": 0.0,
                u"rowId": 1,
                u"predictionValues": [
                    {u"value": 0.9, u"label": u"1.0"},
                    {u"value": 0.1, u"label": u"0.0"},
                ],
            },
            {
                u"positiveProbability": 0.8,
                u"prediction": 1.0,
                u"rowId": 2,
                u"predictionValues": [
                    {u"value": 0.8, u"label": u"1.0"},
                    {u"value": 0.2, u"label": u"0.0"},
                ],
            },
        ],
    }
)


def assert_job_attributes(job):
    assert job.id == 1
    assert job.project == Project("p-id")
    assert job.status == "inprogress"
    assert job.job_type == "model"
    assert job.model_id == "5d518cd3962d741512605e2b"
    # ensure the instantiated object has the model ID as well
    assert job.model.id == "5d518cd3962d741512605e2b"
    assert not job.is_blocked
    assert job._job_details_path == "projects/p-id/modelJobs/1/"


def test_instantiate():
    new_job = Job(mock_job_data)
    assert_job_attributes(new_job)


def test_future_proof():
    Job(dict(mock_job_data, future="new"))


@responses.activate
@pytest.mark.parametrize("job_class", (Job, FeatureImpactJob))
def test_get_completed(client, job_class):
    resource_url = "https://host_name.com/resource-location/"
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(dict(mock_job_data, status="COMPLETED")),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )
    job = job_class.get("p-id", "1")
    assert job.status == "COMPLETED"
    assert job._completed_resource_url == resource_url


@responses.activate
def test_get_completed_feature_impact(client, feature_impact_server_data):
    job_result_url = "https://host_name.com/resource-location/"
    pid = "p-id"

    # Get project.
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(pid),
        status=200,
        body=json.dumps({"id": pid}),
        content_type="application/json",
    )
    project = Project.get(pid)

    # Get not finished jobs.
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/".format(pid),
        status=200,
        body=json.dumps({"jobs": [mock_job_data]}),
        content_type="application/json",
    )
    job = project.get_all_jobs()[0]

    # Mark job as finished.
    job_data = deepcopy(mock_job_data)
    job_data["status"] = "COMPLETED"
    job_data["jobType"] = "featureImpact"

    # Get that finished job and its results.
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/jobs/1/".format(pid),
        status=303,
        body=json.dumps(job_data),
        content_type="application/json",
        adding_headers={"Location": job_result_url},
    )
    responses.add(
        responses.GET,
        job_result_url,
        status=200,
        body=json.dumps(feature_impact_server_data),
        content_type="application/json",
    )
    assert job.get_result() == feature_impact_server_data["featureImpacts"]


@responses.activate
@pytest.mark.parametrize("job_class", (Job, FeatureImpactJob))
def test_get_no_model_id(client, job_class):
    resource_url = "https://host_name.com/resource-location/"
    job_data = mock_job_data.copy()
    del job_data["modelId"]
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(job_data),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )
    job = job_class.get("p-id", "1")
    assert job.model_id is None
    assert job.model is None


@responses.activate
def test_get_completed_pred(client):
    get_predictions_url = "https://host_name.com/projects/p-id/predictions/1/"

    mock_generic_job_data = {
        "status": "COMPLETED",
        "url": "https://host_name.com/projects/p-id/predictJobs/1/",
        "id": "1",
        "jobType": "predict",
        "isBlocked": False,
        "projectId": "p-id",
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(dict(mock_generic_job_data, status="COMPLETED")),
        content_type="application/json",
        adding_headers={"Location": get_predictions_url},
    )
    responses.add(
        responses.GET,
        get_predictions_url,
        status=200,
        body=SAMPLE_BINARY_PREDICTION_RETURN,
        content_type="application/json",
    )

    job = Job.get("p-id", "1")

    data = job.get_result()
    assert job.status == "COMPLETED"

    # inspect the data
    expected_columns = ["positive_probability", "prediction", "row_id", "class_0.0", "class_1.0"]
    assert sorted(data.columns.values) == sorted(expected_columns)


@responses.activate
def test_wait_for_completion_never_finishes(client, mock_async_time):
    resource_url = "https://host_name.com/resource-location/"
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(mock_job_data),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )
    job = Job(mock_job_data)
    mock_async_time.time.side_effect = (0, 2)
    with pytest.raises(AsyncTimeoutError):
        job.wait_for_completion(max_wait=1)


@responses.activate
@pytest.mark.parametrize("job_class", (Job, FeatureImpactJob))
def test_wait_for_completion_finishes(client, mock_async_time, job_class):
    resource_url = "https://host_name.com/resource-location/"
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(dict(mock_job_data, status="COMPLETED")),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )
    mock_async_time.time.side_effect = (0, 2)
    job = job_class(mock_job_data)
    job.wait_for_completion(max_wait=3)
    assert job.status == "COMPLETED"


@responses.activate
def test_get_result_errored(project_id, project_url):
    job_url = "{}jobs/1/".format(project_url)
    mock_job = {
        "status": enums.QUEUE_STATUS.ERROR,
        "url": "{}modelJobs/1/".format(project_url),
        "id": "1",
        "jobType": "model",
        "isBlocked": False,
        "projectId": project_id,
    }
    responses.add(
        responses.GET, job_url, status=200, json=mock_job, content_type="application/json"
    )
    job = Job.get(project_id, "1")
    with pytest.raises(AsyncProcessUnsuccessfulError):
        job.get_result()


@responses.activate
@pytest.mark.parametrize("job_class", (Job, FeatureImpactJob))
def test_get(client, job_class):
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(mock_job_data),
        content_type="application/json",
    )
    job = job_class.get("p-id", "1")
    assert_job_attributes(job)
    assert job._completed_resource_url is None


@responses.activate
def test_refresh(client):
    job = Job(mock_job_data)
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.COMPLETED)
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(refresh_job_data),
        content_type="application/json",
    )
    job.refresh()
    assert job.status == enums.QUEUE_STATUS.COMPLETED


@responses.activate
def test_cancel_job(client):
    responses.add(
        responses.DELETE,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=204,
        body="",
        content_type="application/json",
    )
    generic_job = Job(mock_job_data)
    generic_job.cancel()


@responses.activate
def test_training_predictions_job__refresh__ok():
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.ERROR)
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(refresh_job_data),
        content_type="application/json",
    )

    job = TrainingPredictionsJob(mock_job_data, model_id="model-id", data_subset="all")
    job.refresh()

    assert job.status == enums.QUEUE_STATUS.ERROR


@responses.activate
def test_training_predictions_job__get__ok():
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=200,
        body=json.dumps(mock_job_data),
        content_type="application/json",
    )

    job = TrainingPredictionsJob.get("p-id", "1", model_id="model-id", data_subset="all")

    assert job.status == enums.QUEUE_STATUS.INPROGRESS


@responses.activate
def test_training_predictions_job__wait_for_completion__ok():
    resource_url = "https://host_name.com/resource-location/"
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.COMPLETED)
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(refresh_job_data),
        content_type="application/json",
        adding_headers={"Location": resource_url},
    )

    job = TrainingPredictionsJob(mock_job_data, model_id="model-id", data_subset="all")
    job.wait_for_completion(max_wait=3)

    assert job.status == enums.QUEUE_STATUS.COMPLETED


@responses.activate
def test_regression_test_get_completed_pred_with_training_predictions_job(client):

    project_id = "p-id"
    prediction_id = "1"
    data_path = "projects/{project_id}/trainingPredictions/{prediction_id}".format(
        project_id=project_id, prediction_id=prediction_id
    )
    get_predictions_url = "https://host_name.com/{data_path}/".format(data_path=data_path)
    mock_generic_job_data = {
        "status": enums.QUEUE_STATUS.COMPLETED,
        "url": "https://host_name.com/projects/p-id/predictJobs/1/",
        "id": prediction_id,
        "jobType": "a job",
        "isBlocked": False,
        "projectId": project_id,
    }

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/jobs/1/",
        status=303,
        body=json.dumps(dict(mock_generic_job_data)),
        content_type="application/json",
        adding_headers={"Location": get_predictions_url},
    )

    job = TrainingPredictionsJob.get(project_id, prediction_id)

    data = job.get_result()
    assert job.status == "COMPLETED"

    assert isinstance(data, TrainingPredictions)
    assert data.project_id == project_id
    assert data.prediction_id == prediction_id
    assert data.path == data_path + "/"
