# -*- encoding: utf-8 -*-
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
import unittest

import mock
import pandas as pd
import pytest
import responses

from datarobot import errors, Job, PredictJob, Project
from datarobot.models.predict_job import wait_for_async_predictions
from datarobot.utils import raw_prediction_response_to_dataframe
from tests.test_helpers import fixture_file_path
from tests.utils import assert_raised_regex, SDKTestcase

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


SAMPLE_BINARY_FLOAT_PREDICTION_RETURN = json.dumps(
    {
        u"positiveClass": 1.0,
        u"task": u"Binary",
        u"predictions": [
            {
                u"positiveProbability": 0.9,
                u"prediction": 1.0,
                u"rowId": 0,
                u"predictionValues": [
                    {u"value": 0.9, u"label": 1.0},
                    {u"value": 0.1, u"label": 0.0},
                ],
            },
            {
                u"positiveProbability": 0.1,
                u"prediction": 0.0,
                u"rowId": 1,
                u"predictionValues": [
                    {u"value": 0.9, u"label": 1.0},
                    {u"value": 0.1, u"label": 0.0},
                ],
            },
            {
                u"positiveProbability": 0.8,
                u"prediction": 1.0,
                u"rowId": 2,
                u"predictionValues": [
                    {u"value": 0.8, u"label": 1.0},
                    {u"value": 0.2, u"label": 0.0},
                ],
            },
        ],
    }
)


SAMPLE_MULTICLASS_PREDICTION_RETURN = json.dumps(
    {
        u"positiveClass": 1.0,
        u"task": u"Multiclass",
        u"predictions": [
            {
                u"positiveProbability": None,
                u"prediction": u"class_a",
                u"rowId": 0,
                u"predictionValues": [
                    {u"value": 0.7, u"label": u"class_a"},
                    {u"value": 0.2, u"label": u"class_b"},
                    {u"value": 0.1, u"label": u"class_c"},
                ],
            },
            {
                u"positiveProbability": None,
                u"prediction": u"class_a",
                u"rowId": 1,
                u"predictionValues": [
                    {u"value": 0.6, u"label": u"class_a"},
                    {u"value": 0.2, u"label": u"class_b"},
                    {u"value": 0.2, u"label": u"class_c"},
                ],
            },
            {
                u"positiveProbability": None,
                u"prediction": u"class_b",
                u"rowId": 2,
                u"predictionValues": [
                    {u"value": 0.1, u"label": u"class_a"},
                    {u"value": 0.8, u"label": u"class_b"},
                    {u"value": 0.1, u"label": u"class_c"},
                ],
            },
        ],
    }
)


UNICODE_SAMPLE_MULTICLASS_PREDICTION_RETURN = json.dumps(
    {
        u"positiveClass": 1.0,
        u"task": u"Multiclass",
        u"predictions": [
            {
                u"positiveProbability": None,
                u"prediction": u"class_赤木",
                u"rowId": 0,
                u"predictionValues": [
                    {u"value": 0.7, u"label": u"class_赤木"},
                    {u"value": 0.2, u"label": u"class_エピソード"},
                    {u"value": 0.1, u"label": u"class_外"},
                ],
            },
            {
                u"positiveProbability": None,
                u"prediction": u"class_赤木",
                u"rowId": 1,
                u"predictionValues": [
                    {u"value": 0.6, u"label": u"class_赤木"},
                    {u"value": 0.2, u"label": u"class_エピソード"},
                    {u"value": 0.2, u"label": u"class_外"},
                ],
            },
            {
                u"positiveProbability": None,
                u"prediction": u"class_エピソード",
                u"rowId": 2,
                u"predictionValues": [
                    {u"value": 0.1, u"label": u"class_赤木"},
                    {u"value": 0.8, u"label": u"class_エピソード"},
                    {u"value": 0.1, u"label": u"class_外"},
                ],
            },
        ],
    }
)


SAMPLE_REGRESSION_PREDICTION_RETURN = json.dumps(
    {
        u"positiveClass": None,
        u"task": u"Regression",
        u"predictions": [
            {u"positiveProbability": None, u"prediction": 32.0, u"rowId": 0},
            {u"positiveProbability": None, u"prediction": 100.0, u"rowId": 1},
            {u"positiveProbability": None, u"prediction": 212.0, u"rowId": 2},
        ],
    }
)


SAMPLE_REGRESSION_PREDICTION_WITH_SHAP_EXPL_RETURN = json.dumps(
    {
        "shapBaseValue": [31108.28125],
        "task": "Regression",
        "positiveClass": None,
        "predictions": [
            {
                "positiveProbability": None,
                "predictionExplanationMetadata": {"shapRemainingTotal": -6969.941378326501},
                "prediction": 27229.166666666668,
                "rowId": 0,
                "predictionExplanations": [
                    {
                        "featureValue": "2004",
                        "strength": 3090.8262156678165,
                        "feature": "YearMade",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "999089",
                        "strength": -2788.4580943655205,
                        "feature": "MachineID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "2006",
                        "strength": -2286.181442643504,
                        "feature": "saledate (Year)",
                        "label": "SalePrice",
                    },
                ],
            },
            {
                "positiveProbability": None,
                "predictionExplanationMetadata": {"shapRemainingTotal": 13439.981135022792},
                "prediction": 60583.333333333336,
                "rowId": 1,
                "predictionExplanations": [
                    {
                        "featureValue": "117657",
                        "strength": 16035.069717943523,
                        "feature": "MachineID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "77",
                        "strength": 10105.427194858292,
                        "feature": "ModelID",
                        "label": "SalePrice",
                    },
                    {
                        "featureValue": "Medium",
                        "strength": 3432.899846833262,
                        "feature": "ProductSize",
                        "label": "SalePrice",
                    },
                ],
            },
        ],
    }
)


class TestPredictJob(SDKTestcase):
    def setUp(self):
        super(TestPredictJob, self).setUp()
        self.project_id = "556902e8100d2b3728d47551"
        self.model_id = "556902ef100d2b37da13077d"
        self.predict_job_id = 111
        self.post_url = "https://host_name.com/projects/{}/predictions/".format(self.project_id)
        self.get_job_url = "https://host_name.com/projects/{}/predictJobs/{}/".format(
            self.project_id, self.predict_job_id
        )
        self.get_predictions_url = "https://host_name.com/projects/{}/predictions/123/".format(
            self.project_id
        )
        self.predict_job_data = {
            "status": "queue",
            "id": self.predict_job_id,
            "projectId": self.project_id,
            "modelId": self.model_id,
            "isBlocked": False,
        }

        self.predict_job_with_message = {
            "status": "error",
            "id": self.predict_job_id,
            "projectId": self.project_id,
            "modelId": self.model_id,
            "isBlocked": False,
            "message": "Clearly this is user error :)",
        }

        self.mock_generic_job_data = {
            "status": "inprogress",
            "url": "https://host_name.com/projects/{}/predictJobs/1/".format(self.project_id),
            "id": "1",
            "jobType": "predict",
            "isBlocked": False,
            "projectId": self.project_id,
        }

        self.mock_model_job_data = {
            "status": "inprogress",
            "url": "https://host_name.com/projects/{}/modelJobs/2/".format(self.project_id),
            "id": "2",
            "jobType": "model",
            "isBlocked": False,
            "projectId": self.project_id,
        }

    def test_instantiate_predict_job(self):
        job = PredictJob(self.predict_job_data)
        print(job)  # checks that method relevant to print works on this (failed in one release)
        self.assertEqual(job.id, self.predict_job_id)
        self.assertEqual(job.status, "queue")
        self.assertIsInstance(job.project, Project)
        self.assertEqual(job.project.id, "556902e8100d2b3728d47551")

        with self.assertRaises(ValueError):
            PredictJob("qid")

    def test_future_proof(self):
        PredictJob(dict(self.predict_job_data, future="new"))

    @responses.activate
    def test_from_job(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/predictJobs/1/".format(self.project_id),
            status=200,
            body=json.dumps(self.predict_job_with_message),
            content_type="application/json",
        )
        generic_job = Job(self.mock_generic_job_data)
        predict_job = PredictJob.from_job(generic_job)

        self.assertEqual(predict_job.status, "error")
        self.assertEqual(predict_job.job_type, "predict")
        self.assertEqual(predict_job.project, Project(self.project_id))
        self.assertEqual(predict_job.model.id, self.model_id)

    def test_from_job_wrong_type(self):
        generic_job = Job(self.mock_model_job_data)
        with self.assertRaises(ValueError):
            PredictJob.from_job(generic_job)

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_create_non_ascii_filename(self):
        path = fixture_file_path(u"日本/データ.csv")
        model = mock.Mock()
        model.id = self.model_id
        model.project.id = self.project_id
        responses.add(
            responses.POST,
            self.post_url,
            status=202,
            body="",
            adding_headers={"Location": "https://host_name.com" + self.get_job_url},
        )
        predict_job_id = PredictJob.create(model, sourcedata=path)
        assert predict_job_id == str(self.predict_job_id)

    @pytest.mark.usefixtures("known_warning")
    def test_create_bad_sourcedata(self):
        with pytest.raises(errors.InputNotUnderstoodError) as exc_info:
            PredictJob.create(mock.Mock(), sourcedata=123)
        assert_raised_regex(exc_info, "sourcedata parameter not understood.")

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_create_success(self):
        model = mock.Mock()
        model.id = self.model_id
        model.project.id = self.project_id
        responses.add(
            responses.POST,
            self.post_url,
            status=202,
            body="",
            adding_headers={"Location": "https://host_name.com" + self.get_job_url},
        )
        predict_job_id = PredictJob.create(model, b"one,two\n3,4")
        self.assertEqual(predict_job_id, str(self.predict_job_id))

    @responses.activate
    def test_cancel(self):
        predict_job = PredictJob(self.predict_job_data)
        responses.add(
            responses.DELETE, self.get_job_url, status=204, body="", content_type="application/json"
        )
        predict_job.cancel()
        self.assertEqual(responses.calls[0].request.method, "DELETE")

    @responses.activate
    def test_get_unfinished_predict_job_with_message(self):
        """A new attribute of PredictJob beginning in DataRobot API v2.1"""
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_with_message),
            content_type="application/json",
        )
        predict_job = PredictJob.get(self.project_id, self.predict_job_id)
        self.assertIsInstance(predict_job, PredictJob)
        self.assertEqual(predict_job.id, self.predict_job_id)
        self.assertEqual(predict_job.status, "error")
        self.assertEqual(predict_job.message, "Clearly this is user error :)")

    @responses.activate
    def test_get_unfinished_predict_job(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_data),
            content_type="application/json",
        )
        predict_job = PredictJob.get(self.project_id, self.predict_job_id)
        self.assertIsInstance(predict_job, PredictJob)
        self.assertEqual(predict_job.id, self.predict_job_id)
        self.assertEqual(predict_job.status, "queue")
        self.assertEqual(predict_job.message, "")

    @responses.activate
    def test_get_finished_predict_job(self):
        responses.add(
            responses.GET, self.get_job_url, status=303, body="",
        )
        with self.assertRaises(errors.PendingJobFinished):
            PredictJob.get(self.project_id, self.predict_job_id)

    @responses.activate
    def test_get_predict_job_async_failure(self):
        responses.add(
            responses.GET, self.get_job_url, status=202, body="",
        )
        with pytest.raises(errors.AsyncFailureError) as exc_info:
            PredictJob.get(self.project_id, self.predict_job_id)
        assert_raised_regex(exc_info, "Server unexpectedly returned status code 202")

    @responses.activate
    def test_get_unfinished_predictions(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_data),
            content_type="application/json",
        )
        with pytest.raises(errors.JobNotFinished) as exc_info:
            PredictJob.get_predictions(self.project_id, self.predict_job_id)
        assert_raised_regex(exc_info, "Pending job status is queue")

    @responses.activate
    def test_get_predictions_async_failure(self):
        responses.add(
            responses.GET, self.get_job_url, status=202, body="",
        )
        with pytest.raises(errors.AsyncFailureError) as exc_info:
            PredictJob.get_predictions(self.project_id, self.predict_job_id)
        assert_raised_regex(exc_info, "Server unexpectedly returned status code 202")

    @responses.activate
    def test_get_finished_predictions(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=303,
            body="",
            adding_headers={"Location": self.get_predictions_url},
        )
        responses.add(
            responses.GET,
            self.get_predictions_url,
            status=200,
            body=SAMPLE_BINARY_PREDICTION_RETURN,
            content_type="application/json",
        )
        predictions = PredictJob.get_predictions(self.project_id, self.predict_job_id)
        self.assertIsInstance(predictions, pd.DataFrame)
        self.assertEqual(predictions.shape, (3, 5))
        self.assertEqual(
            sorted(predictions.columns),
            sorted(["positive_probability", "prediction", "row_id", "class_0.0", "class_1.0"]),
        )


class TestWaitForAsyncPredictions(SDKTestcase):
    def setUp(self):
        super(TestWaitForAsyncPredictions, self).setUp()
        self.pid = "p-id"
        self.predict_job_id = "5"
        self.get_job_url = "https://host_name.com/projects/{}/predictJobs/{}/".format(
            self.pid, self.predict_job_id,
        )

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps({"isBlocked": False}),
            content_type="application/json",
        )
        with pytest.raises(errors.AsyncTimeoutError) as exc_info:
            wait_for_async_predictions(self.pid, self.predict_job_id, max_wait=1)
        assert_raised_regex(exc_info, "Predictions generation timed out in")

    @responses.activate
    @mock.patch("datarobot.models.predict_job.PredictJob.get_predictions")
    def test_success(self, get_predictions):
        responses.add(
            responses.GET, self.get_job_url, status=303, body="", content_type="application/json"
        )
        wait_for_async_predictions(self.pid, self.predict_job_id)
        self.assertEqual(get_predictions.call_count, 1)

    @responses.activate
    @mock.patch("datarobot.models.predict_job.PredictJob.get_predictions")
    def test_error(self, get_predictions):
        data = {"status": "error", "isBlocked": False}
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(data),
            content_type="application/json",
        )
        with pytest.raises(errors.AsyncPredictionsGenerationError) as exc_info:
            wait_for_async_predictions(self.pid, self.predict_job_id)
        assert_raised_regex(exc_info, "Predictions generation unsuccessful")


class TestRawPredictionResponseToDataframe(unittest.TestCase):
    def test_parse_regression_predictions(self):
        data = json.loads(SAMPLE_REGRESSION_PREDICTION_RETURN)

        frame = raw_prediction_response_to_dataframe(data, "")
        self.assertEqual(frame.shape, (3, 2))
        self.assertEqual(
            sorted(frame.columns), [u"prediction", u"row_id"],
        )

    def test_parse_classification_predictions(self):
        data = json.loads(SAMPLE_BINARY_PREDICTION_RETURN)
        frame = raw_prediction_response_to_dataframe(data, "")
        self.assertEqual(frame.shape, (3, 5))
        self.assertEqual(
            sorted(frame.columns),
            sorted([u"positive_probability", u"prediction", u"row_id", u"0.0", u"1.0"]),
        )

    def test_parse_classification_predictions_with_floats(self):
        data = json.loads(SAMPLE_BINARY_FLOAT_PREDICTION_RETURN)
        frame = raw_prediction_response_to_dataframe(data, "class_")
        self.assertEqual(frame.shape, (3, 5))
        self.assertEqual(
            sorted(frame.columns),
            sorted([u"positive_probability", u"prediction", u"row_id", u"class_0.0", u"class_1.0"]),
        )

    def test_parse_multiclass_classification_predictions(self):
        data = json.loads(SAMPLE_MULTICLASS_PREDICTION_RETURN)
        frame = raw_prediction_response_to_dataframe(data, "")
        self.assertEqual(frame.shape, (3, 5))
        self.assertEqual(
            sorted(frame.columns),
            sorted([u"prediction", u"row_id", u"class_a", u"class_b", u"class_c"]),
        )

    def test_parse_multiclass_classification_predictions_unicode(self):
        data = json.loads(UNICODE_SAMPLE_MULTICLASS_PREDICTION_RETURN)
        frame = raw_prediction_response_to_dataframe(data, "")
        self.assertEqual(frame.shape, (3, 5))
        self.assertEqual(
            sorted(frame.columns),
            sorted([u"prediction", u"row_id", u"class_赤木", u"class_エピソード", u"class_外"]),
        )

    def test_parse_regression_predictions_with_shap_explanations(self):
        data = json.loads(SAMPLE_REGRESSION_PREDICTION_WITH_SHAP_EXPL_RETURN)
        frame = raw_prediction_response_to_dataframe(data, class_prefix="")
        assert frame.shape == (2, 13)
        assert sorted(frame.columns) == sorted(
            [
                "prediction",
                "row_id",
                "Explanation_1_feature_name",
                "Explanation_1_feature_value",
                "Explanation_1_strength",
                "Explanation_2_feature_name",
                "Explanation_2_feature_value",
                "Explanation_2_strength",
                "Explanation_3_feature_name",
                "Explanation_3_feature_value",
                "Explanation_3_strength",
                "shap_remaining_total",
                "shap_base_value",
            ]
        )

        # assert scalar shapBaseValue doesn't cause an error
        data["shapBaseValue"] = data["shapBaseValue"][0]
        frame_2 = raw_prediction_response_to_dataframe(data, class_prefix="")
        assert frame.equals(frame_2)

        # when shapBaseValue has multiple items the first one is used and no error is raised
        data["shapBaseValue"] = [9.12, 42.1, -27.1]
        frame_3 = raw_prediction_response_to_dataframe(data, class_prefix="")
        assert frame_3["shap_base_value"].tolist() == [9.12, 9.12]
