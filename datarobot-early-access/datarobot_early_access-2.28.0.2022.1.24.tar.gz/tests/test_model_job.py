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

from datarobot import Blueprint, errors, Job, ModelJob, Project
from datarobot.models.modeljob import wait_for_async_model_creation
from tests.utils import assert_raised_regex, SDKTestcase


class TestWaitForAsyncModelCreation(SDKTestcase):
    mock_model_job_data = {
        "status": "inprogress",
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
        "isBlocked": False,
        "id": "1",
    }

    def setUp(self):
        super(TestWaitForAsyncModelCreation, self).setUp()
        self.pid = "p-id"
        self.model_job_id = "5"
        self.get_job_url = "https://host_name.com/projects/{}/modelJobs/{}/".format(
            self.pid, self.model_job_id,
        )

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.mock_model_job_data),
            content_type="application/json",
        )
        with pytest.raises(errors.AsyncTimeoutError) as exc_info:
            wait_for_async_model_creation(self.pid, self.model_job_id, max_wait=1)
        assert_raised_regex(exc_info, "Model creation timed out in")

    @responses.activate
    @mock.patch("datarobot.models.modeljob.ModelJob.get_model")
    def test_success(self, get_model):
        responses.add(
            responses.GET, self.get_job_url, status=303, body="", content_type="application/json"
        )
        wait_for_async_model_creation(self.pid, self.model_job_id)
        self.assertEqual(get_model.call_count, 1)

    @responses.activate
    @mock.patch("datarobot.models.modeljob.ModelJob.get_model")
    def test_error(self, get_model):
        data = dict(self.mock_model_job_data, status="error")
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(data),
            content_type="application/json",
        )

        with pytest.raises(errors.AsyncModelCreationError) as exc_info:
            wait_for_async_model_creation(self.pid, self.model_job_id)
        assert_raised_regex(exc_info, "Model creation unsuccessful")


class TestJobModel(SDKTestcase):
    fully_trained_model = """
            {
        "featurelistId": "556cdfbd100d2b10048c7941",
        "processes": ["One", "Two", "Three"],
        "featurelistName": "Informative Features",
        "projectId": "p-id",
        "samplePct": 64,
        "modelType": "AVG Blender",
        "metrics": {
            "AUC": {
                "holdout": 0.76603,
                "validation": 0.64141,
                "crossValidation": 0.7625240000000001
            },
            "Rate@Top5%": {
                "holdout": 1,
                "validation": 0.5,
                "crossValidation": 0.9
            },
            "Rate@TopTenth%": {
                "holdout": 1,
                "validation": 1,
                "crossValidation": 1
            },
            "RMSE": {
                "holdout": 0.42054,
                "validation": 0.44396,
                "crossValidation": 0.40162000000000003
            },
            "LogLoss": {
                "holdout": 0.53707,
                "validation": 0.58051,
                "crossValidation": 0.5054160000000001
            },
            "FVE Binomial": {
                "holdout": 0.17154,
                "validation": 0.03641,
                "crossValidation": 0.17637399999999998
            },
            "Gini Norm": {
                "holdout": 0.53206,
                "validation": 0.28282,
                "crossValidation": 0.525048
            },
            "Rate@Top10%": {
                "holdout": 1,
                "validation": 0.25,
                "crossValidation": 0.7
            }
        },
        "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
        "id": "5223deadbeefdeadbeef1234"
    }
    """

    final_model_location = (
        "https://host_name.com/projects/55666eb9100d2b109b59e267/"
        "models/5223deadbeefdeadbeef1234/"
    )

    mock_generic_job_data_inprogress = {
        "status": "inprogress",
        "url": "https://host_name.com/projects/p-id/modelJobs/1/",
        "id": "1",
        "jobType": "model",
        "isBlocked": False,
        "projectId": "p-id",
    }

    mock_generic_job_data_completed = dict(mock_generic_job_data_inprogress, status="COMPLETED")

    mock_model_job_data = {
        "status": "inprogress",
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
        "isBlocked": False,
        "id": "1",
    }

    mock_predict_job_data = {
        "status": "error",
        "url": "https://host_name.com/projects/p-id/predictJobs/64/",
        "id": "64",
        "jobType": "predict",
        "isBlocked": False,
        "projectId": "p-id",
    }

    def test_instantiate_job(self):
        data = {
            "status": "queue",
            "processes": ["One-Hot Encoding", "Missing Values Imputed", "RuleFit Classifier"],
            "projectId": "556902e8100d2b3728d47551",
            "samplePct": 64,
            "modelType": "RuleFit Classifier",
            "featurelistId": "556902eb100d2b37d1130771",
            "blueprintId": "a8959bc1d46f07fb3dc14db7c1e3fc99",
            "isBlocked": False,
            "id": 11,
            "modelId": "556902ef100d2b37da13077d",
        }
        job = ModelJob(data)
        self.assertEqual(job.status, "queue")
        self.assertEqual(job.job_type, "model")
        self.assertEqual(job.processes, data["processes"])
        self.assertEqual(job.sample_pct, 64)
        self.assertEqual(job.model_type, "RuleFit Classifier")
        assert job.featurelist_id == data["featurelistId"]
        self.assertIsInstance(job.project, Project)
        self.assertEqual(job.project.id, "556902e8100d2b3728d47551")
        self.assertIsInstance(job.blueprint, Blueprint)
        self.assertEqual(job.blueprint.id, "a8959bc1d46f07fb3dc14db7c1e3fc99")

        repr(job)

        with self.assertRaises(ValueError):
            ModelJob("qid")

    def test_future_proof(self):
        ModelJob(dict(self.mock_model_job_data, future="new"))

    @responses.activate
    def test_from_job(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/modelJobs/1/",
            status=200,
            body=json.dumps(self.mock_model_job_data),
            content_type="application/json",
        )
        generic_job = Job(self.mock_generic_job_data_inprogress)
        model_job = ModelJob.from_job(generic_job)

        self.assertEqual(model_job.status, "inprogress")
        self.assertEqual(model_job.job_type, "model")
        self.assertEqual(model_job.project, Project("p-id"))
        self.assertEqual(model_job.processes, self.mock_model_job_data["processes"])

    def test_from_job_wrong_type(self):
        generic_job = Job(self.mock_predict_job_data)
        with self.assertRaises(ValueError):
            ModelJob.from_job(generic_job)

    @responses.activate
    def test_cancel(self):
        data = {
            "status": "inprogress",
            "samplepct": 64.0,
            "processes": [
                "One-Hot Encoding",
                "Missing Values Imputed",
                "Standardize",
                "Linear Regression",
            ],
            "modelType": "Linear Regression",
            "featurelistId": "55666d05100d2b01a1104dae",
            "blueprintId": "3bb4665320be633b30a9601b3e73284d",
            "projectId": "55666eb9100d2b109b59e267",
            "isBlocked": False,
            "id": 5,
            "modelId": "55666d0d100d2b01b1104db4",
        }
        job = ModelJob(data)
        responses.add(
            responses.DELETE,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=204,
            body="",
            content_type="application/json",
        )
        job.cancel()
        self.assertEqual(responses.calls[0].request.method, "DELETE")

    @responses.activate
    def test_get_success(self):
        data = {
            "status": "inprogress",
            "samplepct": 64.0,
            "processes": [
                "One-Hot Encoding",
                "Missing Values Imputed",
                "Standardize",
                "Linear Regression",
            ],
            "modelType": "Linear Regression",
            "featurelistId": "55666d05100d2b01a1104dae",
            "blueprintId": "3bb4665320be633b30a9601b3e73284d",
            "projectId": "55666eb9100d2b109b59e267",
            "isBlocked": False,
            "id": 5,
            "modelId": "55666d0d100d2b01b1104db4",
        }
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=200,
            body=json.dumps(data),
            content_type="application/json",
        )
        job = ModelJob.get("55666eb9100d2b109b59e267", 5)
        self.assertEqual(responses.calls[0].request.method, "GET")
        self.assertEqual(job.status, "inprogress")

    @responses.activate
    def test_get_redirect(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            content_type="application/json",
            status=303,
            body="",
            adding_headers={"Location": "http://pam/api/v2/projects/p-id/models/id/"},
        )
        with self.assertRaises(errors.PendingJobFinished):
            ModelJob.get("55666eb9100d2b109b59e267", 5)

    @responses.activate
    def test_get_exceptional(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=404,
            body="",
        )
        with self.assertRaises(errors.AppPlatformError):
            ModelJob.get("55666eb9100d2b109b59e267", 5)

    @responses.activate
    def test_get_unexpected_status_code(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=202,
            body="",
        )
        with pytest.raises(errors.AsyncFailureError) as exc_info:
            ModelJob.get("55666eb9100d2b109b59e267", 5)
        assert_raised_regex(exc_info, "Server unexpectedly returned status code")

    @responses.activate
    def test_get_model_success(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=303,
            body="",
            adding_headers={"Location": self.final_model_location},
        )
        responses.add(
            responses.GET, self.final_model_location, status=200, body=self.fully_trained_model
        )
        ModelJob.get_model("55666eb9100d2b109b59e267", 5)

    @responses.activate
    def test_get_model_from_job_success(self):
        generic_job = Job(self.mock_generic_job_data_inprogress)
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/jobs/1/",
            status=303,
            body=json.dumps(self.mock_generic_job_data_completed),
            adding_headers={"Location": self.final_model_location},
        )
        responses.add(
            responses.GET, self.final_model_location, status=200, body=self.fully_trained_model
        )
        generic_job.get_result()

    @responses.activate
    def test_get_model_from_job_not_finished(self):
        generic_job = Job(self.mock_generic_job_data_inprogress)
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/jobs/1/",
            status=200,
            body=json.dumps(self.mock_generic_job_data_inprogress),
            adding_headers={"Location": self.final_model_location},
        )
        with self.assertRaises(errors.JobNotFinished):
            generic_job.get_result()

    @responses.activate
    def test_get_model_not_finished(self):
        model_job_data = {
            "status": "queue",
            "processes": ["One-Hot Encoding", "Missing Values Imputed", "RuleFit Classifier"],
            "projectId": "556902e8100d2b3728d47551",
            "samplePct": 64,
            "modelType": "RuleFit Classifier",
            "featurelistId": "556902eb100d2b37d1130771",
            "blueprintId": "a8959bc1d46f07fb3dc14db7c1e3fc99",
            "isBlocked": False,
            "id": 5,
            "modelId": "556902ef100d2b37da13077d",
        }

        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=200,
            body=json.dumps(model_job_data),
        )
        with self.assertRaises(errors.JobNotFinished):
            ModelJob.get_model("55666eb9100d2b109b59e267", 5)

    @responses.activate
    def test_get_model_exceptional(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=404,
            body="",
        )
        with self.assertRaises(errors.AppPlatformError):
            ModelJob.get_model("55666eb9100d2b109b59e267", 5)

    @responses.activate
    def test_get_model_unexpected_status_code(self):
        final_model_location = (
            "https://host_name.com/projects/55666eb9100d2b109b59e267/"
            "models/5223deadbeefdeadbeef1234/"
        )

        responses.add(
            responses.GET,
            "https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/",
            status=202,
            body="",
            adding_headers={"Location": final_model_location},
        )

        with pytest.raises(errors.AsyncFailureError) as exc_info:
            ModelJob.get_model("55666eb9100d2b109b59e267", 5)
        assert_raised_regex(exc_info, "Server unexpectedly returned status code")
