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

from datarobot import ExternalRocCurve
from datarobot.errors import ClientError
from datarobot.utils import from_api


class TestExternalRocCurve(object):
    @staticmethod
    def create_response_data(roc_curve_data, count):
        return [dict(roc_curve_data, datasetId="dataset_id_{}".format(i)) for i in range(count)]

    @pytest.fixture
    def url(self, project_id, model_id):
        return "https://host_name.com/projects/{}/models/{}/datasetRocCurves/".format(
            project_id, model_id
        )

    def test_instantiation(self, roc_curve_data):
        one_roc_chart = self.create_response_data(roc_curve_data, 1)[0]
        roc = ExternalRocCurve.from_server_data(one_roc_chart)

        assert roc.dataset_id == one_roc_chart["datasetId"]
        assert roc.negative_class_predictions == roc_curve_data["negativeClassPredictions"]
        assert roc.positive_class_predictions == roc_curve_data["positiveClassPredictions"]
        assert roc.roc_points == from_api(roc_curve_data["rocPoints"])

    def test_future_proof(self, roc_curve_data):
        one_roc_chart = self.create_response_data(roc_curve_data, 1)[0]
        data_with_future_keys = dict(one_roc_chart, new_key="some future lift data")
        data_with_future_keys["rocPoints"][0]["new_key"] = "some future bin data"
        ExternalRocCurve.from_server_data(data_with_future_keys)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_roc_curve."
        "DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_roc_all_results(self, roc_curve_data, url, project_id, model_id):
        url_page1 = url + "?limit=10&offset=0"
        url_page2 = url + "?limit=10&offset=10"
        all_data = self.create_response_data(roc_curve_data, 11)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        roc_charts = ExternalRocCurve.list(project_id, model_id, limit=0)
        assert len(roc_charts) == 11
        for i, chart in enumerate(roc_charts):
            assert isinstance(chart, ExternalRocCurve)
            assert chart.dataset_id == "dataset_id_{}".format(i)
            assert chart.negative_class_predictions == roc_curve_data["negativeClassPredictions"]
            assert chart.positive_class_predictions == roc_curve_data["positiveClassPredictions"]
            assert chart.roc_points == from_api(roc_curve_data["rocPoints"])

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_roc_curve."
        "DEFAULT_BATCH_SIZE",
        10,
    )
    def test_roc_charts_all_results_with_offset(self, roc_curve_data, url, project_id, model_id):
        url_page1 = url + "?limit=10&offset=3"
        url_page2 = url + "?limit=10&offset=13"
        all_data = self.create_response_data(roc_curve_data, 15)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[3:13])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[13:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        roc_charts = ExternalRocCurve.list(project_id, model_id, limit=0, offset=3)
        assert len(roc_charts) == 12
        assert roc_charts[0].dataset_id == "dataset_id_3"

    @responses.activate
    def test_list_roc_chart_limited(self, roc_curve_data, url, project_id, model_id):
        url_page = url + "?limit=3&offset=2"
        all_data = self.create_response_data(roc_curve_data, 5)
        resp_data = dict(count=3, previous=None, next=None, data=all_data[2:5])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        roc_charts = ExternalRocCurve.list(project_id, model_id, limit=3, offset=2)
        assert len(roc_charts) == 3
        for i, chart in enumerate(roc_charts):
            assert chart.dataset_id == "dataset_id_{}".format(i + 2)
            assert chart.negative_class_predictions == roc_curve_data["negativeClassPredictions"]
            assert chart.positive_class_predictions == roc_curve_data["positiveClassPredictions"]
            assert chart.roc_points == from_api(roc_curve_data["rocPoints"])

    @responses.activate
    def test_get_roc_chart_success(self, roc_curve_data, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        all_data = self.create_response_data(roc_curve_data, 2)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        chart = ExternalRocCurve.get(project_id, model_id, dataset_id)
        assert isinstance(chart, ExternalRocCurve)
        assert chart.dataset_id == "dataset_id_0"
        assert chart.negative_class_predictions == roc_curve_data["negativeClassPredictions"]
        assert chart.positive_class_predictions == roc_curve_data["positiveClassPredictions"]
        assert chart.roc_points == from_api(roc_curve_data["rocPoints"])

    @responses.activate
    def test_get_roc_chart_failure(self, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        resp_data = dict(count=0, previous=None, next=None, data=[])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        with pytest.raises(ClientError, match="Requested roc curve does not exist."):
            ExternalRocCurve.get(project_id, model_id, dataset_id)

    def test_get_best_f1_threshold(self, roc_curve_data):
        one_roc_chart = self.create_response_data(roc_curve_data, 1)[0]
        roc = ExternalRocCurve.from_server_data(one_roc_chart)
        best_threshold = roc.get_best_f1_threshold()
        best_f1 = roc.estimate_threshold(best_threshold)["f1_score"]
        assert all(best_f1 >= roc_point["f1_score"] for roc_point in roc.roc_points)

    def test_estimate_threshold_equal(self, roc_curve_data):
        one_roc_chart = self.create_response_data(roc_curve_data, 1)[0]
        roc = ExternalRocCurve.from_server_data(one_roc_chart)
        threshold = roc_curve_data["rocPoints"][1]["threshold"]
        assert roc.estimate_threshold(threshold)["threshold"] == threshold

        threshold = roc_curve_data["rocPoints"][1]["threshold"] + 0.1
        assert roc.estimate_threshold(threshold)["threshold"] > threshold
