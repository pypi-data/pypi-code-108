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

from datarobot import ExternalLiftChart
from datarobot.errors import ClientError
from datarobot.utils import from_api


class TestExternalLiftChart(object):
    @staticmethod
    def create_response_data(lift_chart_bins_data, count):
        return [
            {"bins": lift_chart_bins_data, "datasetId": "dataset_id_{}".format(i)}
            for i in range(count)
        ]

    @pytest.fixture
    def url(self, project_id, model_id):
        return "https://host_name.com/projects/{}/models/{}/datasetLiftCharts/".format(
            project_id, model_id
        )

    def test_instantiation(self, lift_chart_bins_data):
        one_lift_chart = self.create_response_data(lift_chart_bins_data, 1)[0]
        lc = ExternalLiftChart.from_server_data(one_lift_chart)

        assert lc.dataset_id == one_lift_chart["datasetId"]
        assert lc.bins == from_api(lift_chart_bins_data)

    def test_future_proof(self, lift_chart_bins_data):
        one_lift_chart = self.create_response_data(lift_chart_bins_data, 1)[0]
        data_with_future_keys = dict(one_lift_chart, new_key="some future lift data")
        data_with_future_keys["bins"][0]["new_key"] = "some future bin data"
        ExternalLiftChart.from_server_data(data_with_future_keys)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_lift_chart."
        "DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_lift_chart_all_results(self, lift_chart_bins_data, url, project_id, model_id):
        url_page1 = url + "?limit=10&offset=0"
        url_page2 = url + "?limit=10&offset=10"
        all_data = self.create_response_data(lift_chart_bins_data, 11)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        lift_charts = ExternalLiftChart.list(project_id, model_id, limit=0)
        assert len(lift_charts) == 11
        for i, chart in enumerate(lift_charts):
            assert isinstance(chart, ExternalLiftChart)
            assert chart.dataset_id == "dataset_id_{}".format(i)
            assert chart.bins == from_api(lift_chart_bins_data)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_lift_chart."
        "DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_lift_chart_all_results_with_offset(
        self, lift_chart_bins_data, url, project_id, model_id
    ):
        url_page1 = url + "?limit=10&offset=2"
        url_page2 = url + "?limit=10&offset=12"
        all_data = self.create_response_data(lift_chart_bins_data, 15)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[2:12])
        resp_data_2 = dict(count=3, previous=url_page1, next=None, data=all_data[12:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        lift_charts = ExternalLiftChart.list(project_id, model_id, limit=0, offset=2)
        assert len(lift_charts) == 13
        assert lift_charts[0].dataset_id == "dataset_id_2"

    @responses.activate
    def test_list_lift_chart_limited(self, lift_chart_bins_data, url, project_id, model_id):
        url_page = url + "?limit=3&offset=2"
        all_data = self.create_response_data(lift_chart_bins_data, 5)
        resp_data = dict(count=3, previous=None, next=None, data=all_data[2:5])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        lift_charts = ExternalLiftChart.list(project_id, model_id, limit=3, offset=2)
        assert len(lift_charts) == 3
        for i, chart in enumerate(lift_charts):
            assert isinstance(chart, ExternalLiftChart)
            assert chart.dataset_id == "dataset_id_{}".format(i + 2)
            assert chart.bins == from_api(lift_chart_bins_data)

    @responses.activate
    def test_get_lift_chart_success(self, lift_chart_bins_data, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        all_data = self.create_response_data(lift_chart_bins_data, 2)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        chart = ExternalLiftChart.get(project_id, model_id, dataset_id)
        assert isinstance(chart, ExternalLiftChart)
        assert chart.dataset_id == "dataset_id_0"
        assert chart.bins == from_api(lift_chart_bins_data)

    @responses.activate
    def test_get_lift_chart_failure(self, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        resp_data = dict(count=0, previous=None, next=None, data=[])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        with pytest.raises(ClientError, match="Requested lift chart does not exist."):
            ExternalLiftChart.get(project_id, model_id, dataset_id)
