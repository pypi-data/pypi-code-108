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

from datarobot import ExternalMulticlassLiftChart
from datarobot.errors import ClientError
from datarobot.utils import from_api


class TestExternalMulticlassLiftChart(object):
    @pytest.fixture()
    def multiclass_liftchart_classbins_data(self, lift_chart_bins_data):
        return [
            {"targetClass": "classA", "bins": lift_chart_bins_data},
            {"targetClass": "classB", "bins": lift_chart_bins_data},
            {"targetClass": "classC", "bins": lift_chart_bins_data},
        ]

    @pytest.fixture()
    def one_class_liftchart(self, lift_chart_bins_data):
        return {
            "targetClass": "classA",
            "bins": lift_chart_bins_data,
            "datasetId": "dataset_id_1",
        }

    @staticmethod
    def create_response_data(multiclass_liftchart_classbins_data, count):
        return [
            {
                "classBins": multiclass_liftchart_classbins_data,
                "datasetId": "dataset_id_{}".format(i),
            }
            for i in range(count)
        ]

    @pytest.fixture
    def url(self, project_id, model_id):
        return "https://host_name.com/projects/{}/models/{}/datasetMulticlassLiftCharts/".format(
            project_id, model_id
        )

    def test_instantiation(self, one_class_liftchart):
        lc = ExternalMulticlassLiftChart.from_server_data(one_class_liftchart)
        assert lc.dataset_id == one_class_liftchart["datasetId"]
        assert lc.bins == from_api(one_class_liftchart["bins"])
        assert lc.target_class == from_api(one_class_liftchart["targetClass"])

    def test_future_proof(self, one_class_liftchart):
        data_with_future_keys = dict(one_class_liftchart, new_key="some future lift data")
        data_with_future_keys["bins"][0]["new_key"] = "some future bin data"
        ExternalMulticlassLiftChart.from_server_data(data_with_future_keys)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights.external_multiclass_lift_chart."
        "DEFAULT_BATCH_SIZE",
        10,
    )
    def test_list_lift_chart_all_results(
        self, multiclass_liftchart_classbins_data, url, project_id, model_id
    ):
        url_page1 = url + "?limit=10&offset=0"
        url_page2 = url + "?limit=10&offset=10"
        all_data = self.create_response_data(multiclass_liftchart_classbins_data, 11)
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=all_data[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=all_data[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True,
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True,
        )

        lift_charts = ExternalMulticlassLiftChart.list(project_id, model_id, limit=0)
        n_classes = len(multiclass_liftchart_classbins_data)
        assert len(lift_charts) == 11 * n_classes
        for j in range(11):
            for k, class_bin in enumerate(multiclass_liftchart_classbins_data):
                i = j * n_classes + k
                assert isinstance(lift_charts[i], ExternalMulticlassLiftChart)
                assert lift_charts[i].dataset_id == "dataset_id_{}".format(j)
                assert lift_charts[i].bins == from_api(class_bin["bins"])
                assert lift_charts[i].target_class == class_bin["targetClass"]

    @responses.activate
    def test_list_lift_chart_limited(
        self, multiclass_liftchart_classbins_data, lift_chart_bins_data, url, project_id, model_id,
    ):
        url_page = url + "?limit=3&offset=2"
        all_data = self.create_response_data(multiclass_liftchart_classbins_data, 5)
        resp_data = dict(count=3, previous=None, next=None, data=all_data[2:5])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        lift_charts = ExternalMulticlassLiftChart.list(project_id, model_id, limit=3, offset=2)
        n_classes = len(multiclass_liftchart_classbins_data)
        assert len(lift_charts) == 3 * n_classes
        for j in range(3):
            for k, class_bin in enumerate(multiclass_liftchart_classbins_data):
                i = j * n_classes + k
                assert isinstance(lift_charts[i], ExternalMulticlassLiftChart)
                assert lift_charts[i].dataset_id == "dataset_id_{}".format(j + 2)
                assert lift_charts[i].bins == from_api(class_bin["bins"])
                assert lift_charts[i].target_class == class_bin["targetClass"]

    @responses.activate
    def test_get_lift_chart_by_dataset(
        self, multiclass_liftchart_classbins_data, lift_chart_bins_data, url, project_id, model_id,
    ):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        all_data = self.create_response_data(multiclass_liftchart_classbins_data, 1)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        # chart for each class
        lift_charts = ExternalMulticlassLiftChart.list(project_id, model_id, dataset_id)
        assert len(lift_charts) == len(multiclass_liftchart_classbins_data)
        for chart in lift_charts:
            assert isinstance(chart, ExternalMulticlassLiftChart)
            assert chart.dataset_id == dataset_id
            assert chart.bins == from_api(lift_chart_bins_data)

    @responses.activate
    def test_get_lift_chart_by_target_class(
        self, multiclass_liftchart_classbins_data, lift_chart_bins_data, url, project_id, model_id,
    ):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        all_data = self.create_response_data(multiclass_liftchart_classbins_data, 1)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)

        lift_chart = ExternalMulticlassLiftChart.get(
            project_id, model_id, dataset_id, target_class="classB"
        )
        assert isinstance(lift_chart, ExternalMulticlassLiftChart)
        assert lift_chart.dataset_id == dataset_id
        assert lift_chart.bins == from_api(lift_chart_bins_data)
        assert lift_chart.target_class == "classB"

    @responses.activate
    def test_get_lift_chart_by_target_class_failure(
        self, multiclass_liftchart_classbins_data, lift_chart_bins_data, url, project_id, model_id,
    ):
        dataset_id = "dataset_id_0"
        url_page = url + "?datasetId={}&limit=100&offset=0".format(dataset_id)
        all_data = self.create_response_data(multiclass_liftchart_classbins_data, 1)
        resp_data = dict(count=1, previous=None, next=None, data=[all_data[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        with pytest.raises(ClientError, match="Requested multiclass lift chart does not exist."):
            ExternalMulticlassLiftChart.get(
                project_id, model_id, dataset_id, target_class="wrong_class"
            )
