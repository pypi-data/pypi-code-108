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
from mock import patch
import pytest
import responses

from datarobot import ExternalScores
from datarobot.errors import ClientError


class TestExternalScores(object):
    @pytest.fixture()
    def scores_data(self, project_id, model_id):
        data = {
            "projectId": project_id,
            "modelId": model_id,
            "scores": [
                {"label": "AUC", "value": 1.0},
                {"label": "RMSE", "value": 0.0606},
                {"label": "Kolmogorov-Smirnov", "value": 1.0},
                {"label": "LogLoss", "value": 0.01383},
                {"label": "FVE Binomial", "value": -13845778590722.23},
                {"label": "Max MCC", "value": 1.0},
            ],
        }

        return data

    @staticmethod
    def create_response_data(count, scores, model_id=None, actual_value_column=None):
        data = []
        for i in range(count):
            item = dict(
                scores, datasetId="dataset_id_{}".format(i), actualValueColumn=actual_value_column
            )
            if model_id:
                item["modelId"] = model_id
            data.append(item)
        return data

    @pytest.fixture
    def url(self, project_id):
        return "https://host_name.com/projects/{}/externalScores/".format(project_id)

    def test_instantiation(self, scores_data):
        scores = self.create_response_data(1, scores_data, actual_value_column="label")[0]
        scores_obj = ExternalScores.from_server_data(scores)

        assert scores_obj.dataset_id == "dataset_id_0"
        assert scores_obj.project_id == scores_data["projectId"]
        assert scores_obj.model_id == scores_data["modelId"]
        assert scores_obj.actual_value_column == "label"
        assert scores_obj.scores == scores_data["scores"]

    def test_future_proof(self, scores_data):
        scores = self.create_response_data(1, scores_data)[0]
        data_with_future_keys = dict(scores, new_key="some future lift data")
        ExternalScores.from_server_data(data_with_future_keys)

    @responses.activate
    def test_scores_insights_create(self, project_id, project_url, base_job_server_data):
        scores_base_url = "{}externalScores/".format(project_url)
        job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])

        responses.add(
            responses.POST,
            scores_base_url,
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": job_url},
        )
        responses.add(
            responses.GET,
            job_url,
            json=base_job_server_data,
            status=303,
            adding_headers={"Location": job_url},
        )
        insights_job = ExternalScores.create(
            project_id=project_id,
            model_id="578e59a41ced2e5a9eb18960",
            dataset_id="581c6256100d2b60586980d9",
        )
        assert str(insights_job.id) == base_job_server_data["id"]

    @responses.activate
    def test_scores_insights_create_empty_target_unsupervised(
        self, project_id, project_url, base_job_server_data
    ):
        scores_base_url = "{}externalScores/".format(project_url)
        job_url = "{}jobs/{}/".format(project_url, base_job_server_data["id"])

        responses.add(
            responses.POST,
            scores_base_url,
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": job_url},
        )
        exception_text = (
            "Cannot compute scores and insights on this dataset because target column is missing"
        )
        responses.add(
            responses.GET,
            job_url,
            json={"message": exception_text},
            status=422,
            adding_headers={"Location": job_url},
        )
        with pytest.raises(ClientError) as e:
            ExternalScores.create(
                project_id=project_id,
                model_id="578e59a41ced2e5a9eb18960",
                dataset_id="581c6256100d2b60586980d9",
            )
        assert exception_text in str(e.value)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_scores.DEFAULT_BATCH_SIZE", 10
    )
    def test_external_scores_all_results(self, scores_data, url, project_id, model_id):
        url_page1 = url + "?modelId={}&limit=10&offset=0".format(model_id)
        url_page2 = url + "?modelId={}&limit=10&offset=10".format(model_id)
        all_data = self.create_response_data(11, scores_data)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        scores_list = ExternalScores.list(project_id, model_id, limit=0)
        assert len(scores_list) == 11
        for i, scores in enumerate(scores_list):
            assert isinstance(scores, ExternalScores)
            assert scores.project_id == project_id
            assert scores.model_id == model_id
            assert scores.scores == scores_data["scores"]

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_scores.DEFAULT_BATCH_SIZE", 1
    )
    def test_external_scores_all_results_with_offset(self, scores_data, url, project_id):
        url_page1 = url + "?datasetId={}&limit=1&offset=1".format("dataset_id_0")
        url_page2 = url + "?datasetId={}&limit=1&offset=2".format("dataset_id_0")
        all_data = self.create_response_data(1, scores_data, model_id="model_id_0")
        all_data.extend(self.create_response_data(1, scores_data, model_id="model_id_1"))
        all_data.extend(self.create_response_data(1, scores_data, model_id="model_id_2"))
        resp_data_1 = dict(count=1, previous=None, next=url_page2, data=[all_data[1]])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=[all_data[2]])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        scores_list = ExternalScores.list(project_id, dataset_id="dataset_id_0", limit=0, offset=1)
        assert len(scores_list) == 2
        assert scores_list[0].dataset_id == "dataset_id_0"
        assert scores_list[0].model_id == "model_id_1"
        assert scores_list[1].dataset_id == "dataset_id_0"
        assert scores_list[1].model_id == "model_id_2"

    @responses.activate
    def test_external_scores_limited(self, scores_data, url, project_id, model_id):
        url_page = url + "?limit=3&offset=2"
        all_data = self.create_response_data(5, scores_data)
        resp_data = dict(count=3, previous=None, next=None, data=all_data[2:5])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        scores_list = ExternalScores.list(project_id, limit=3, offset=2)
        assert len(scores_list) == 3
        for i, scores in enumerate(scores_list):
            assert isinstance(scores, ExternalScores)
            assert scores.dataset_id == "dataset_id_{}".format(i + 2)

    @responses.activate
    def test_get_scores_success(self, scores_data, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?modelId={}&datasetId={}&limit=100&offset=0".format(model_id, dataset_id)
        all_data = self.create_response_data(2, scores_data, model_id=model_id)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        scores = ExternalScores.get(project_id, model_id, dataset_id)
        assert isinstance(scores, ExternalScores)
        assert scores.dataset_id == dataset_id
        assert scores.model_id == model_id

    @responses.activate
    def test_get_scores_failure(self, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?modelId={}&datasetId={}&limit=100&offset=0".format(model_id, dataset_id)
        resp_data = dict(count=0, previous=None, next=None, data=[])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        with pytest.raises(ValueError, match="dataset_id must be specified"):
            ExternalScores.get(project_id, model_id, None)
        with pytest.raises(ValueError, match="model_id must be specified"):
            ExternalScores.get(project_id, None, None)
        with pytest.raises(ClientError, match="Requested scores do not exist."):
            ExternalScores.get(project_id, model_id, dataset_id)
