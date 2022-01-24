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

from datarobot.errors import ClientError
from datarobot.models import ExternalConfusionChart
from datarobot.utils import from_api


class TestExternalConfusionChart(object):
    @pytest.fixture
    def confusion_chart_classes(self):
        return

    @staticmethod
    def create_response_data(confusion_chart_data, count):
        confusion_chart_data["classes"] = ["1", "2", "3"]
        return [
            {"data": confusion_chart_data, "datasetId": "dataset_id_{}".format(i)}
            for i in range(count)
        ]

    @pytest.fixture
    def url(self, project_id, model_id):
        return "https://host_name.com/projects/{}/models/{}/datasetConfusionCharts/".format(
            project_id, model_id
        )

    @pytest.fixture
    def metadata_url(self, project_id, model_id, dataset_id):
        return (
            "https://host_name.com/projects/{}/models/{}/datasetConfusionCharts/{}/metadata"
        ).format(project_id, model_id, dataset_id)

    @staticmethod
    def assert_equal_confusion_chart(confusion_chart_obj, api_chart_dict):
        one_chart_data = from_api(api_chart_dict["data"])
        assert confusion_chart_obj.dataset_id == api_chart_dict["datasetId"]
        assert confusion_chart_obj.class_metrics == one_chart_data["class_metrics"]
        assert confusion_chart_obj.confusion_matrix == one_chart_data["confusion_matrix"]
        assert confusion_chart_obj.classes == one_chart_data["classes"]

    def test_instantiation(self, confusion_chart_data):
        response_chart = self.create_response_data(confusion_chart_data, 1)[0]
        chart_obj = ExternalConfusionChart.from_server_data(response_chart)
        self.assert_equal_confusion_chart(chart_obj, response_chart)

    def test_future_proof(self, confusion_chart_data):
        response_chart = self.create_response_data(confusion_chart_data, 1)[0]
        data_with_future_keys = dict(response_chart, new_key="some future lift data")
        data_with_future_keys["data"]["new_key"] = {"new_key": "future class metrics"}
        ExternalConfusionChart.from_server_data(data_with_future_keys)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights."
        "external_confusion_chart.DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_confusion_chart_all_results(
        self, confusion_chart_data, url, project_id, model_id
    ):
        url_page1 = url + "?limit=10&offset=0"
        url_page2 = url + "?limit=10&offset=10"
        all_data = self.create_response_data(confusion_chart_data, 11)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        confusion_charts = ExternalConfusionChart.list(project_id, model_id, limit=0)
        assert len(confusion_charts) == 11
        for i, chart in enumerate(confusion_charts):
            assert isinstance(chart, ExternalConfusionChart)
            self.assert_equal_confusion_chart(chart, all_data[i])

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights."
        "external_confusion_chart.DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_confusion_chart_all_results_with_offset(
        self, confusion_chart_data, url, project_id, model_id
    ):
        url_page1 = url + "?limit=10&offset=2"
        url_page2 = url + "?limit=10&offset=12"
        all_data = self.create_response_data(confusion_chart_data, 15)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[2:12])
        resp_data_2 = dict(count=3, previous=url_page1, next=None, data=all_data[12:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        confusion_charts = ExternalConfusionChart.list(project_id, model_id, limit=0, offset=2)
        assert len(confusion_charts) == 13
        assert confusion_charts[0].dataset_id == "dataset_id_2"

    @responses.activate
    def test_list_confusion_chart_limited(self, confusion_chart_data, url, project_id, model_id):
        url_page = url + "?limit=3&offset=2"
        all_data = self.create_response_data(confusion_chart_data, 5)
        resp_data = dict(count=3, previous=None, next=None, data=all_data[2:5])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        confusion_charts = ExternalConfusionChart.list(project_id, model_id, limit=3, offset=2)
        assert len(confusion_charts) == 3
        for i, chart in enumerate(confusion_charts):
            assert isinstance(chart, ExternalConfusionChart)
            self.assert_equal_confusion_chart(chart, all_data[i + 2])

    @responses.activate
    def test_get_confusion_chart_success(self, confusion_chart_data, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        new_classes = ["4", "5", "6"]
        url_page = url + "{}/".format(dataset_id)
        metadata_url = url_page + "metadata/"
        all_data = self.create_response_data(confusion_chart_data, 2)
        metadata_response = {"classNames": new_classes}

        responses.add(responses.GET, metadata_url, json=metadata_response, status=200)
        responses.add(responses.GET, url_page, json=all_data[1], status=200, match_querystring=True)

        chart = ExternalConfusionChart.get(project_id, model_id, dataset_id)
        expected_chart_dict = all_data[1]
        expected_chart_dict["data"]["classes"] = ["4", "5", "6"]
        assert isinstance(chart, ExternalConfusionChart)
        self.assert_equal_confusion_chart(chart, expected_chart_dict)

    @responses.activate
    def test_get_confusion_chart_failure(self, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "{}/".format(dataset_id)

        exception_text = "No confusion chart for dataset {}".format(dataset_id)

        responses.add(responses.GET, url_page, json={"message": exception_text}, status=404)
        with pytest.raises(ClientError, match=exception_text):
            ExternalConfusionChart.get(project_id, model_id, dataset_id)
