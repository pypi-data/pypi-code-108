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
from datarobot.models import ExternalResidualsChart


class TestExternalResiduals(object):
    @pytest.fixture
    def url(self, project_id, model_id):
        return "https://host_name.com/projects/{}/models/{}/datasetResidualsCharts/".format(
            project_id, model_id
        )

    @pytest.fixture
    def residuals_response(self):
        return [
            {
                "datasetId": "datasetId{}".format(i),
                "residualMean": 1.234567,
                "coefficientOfDetermination": 0.65,
                "standardDeviation": 0.1,
                "data": [[1, 2.5, 1.5, 16], [3, 4.6, 1.6, None]],
                "histogram": [
                    {"intervalStart": 2, "intervalEnd": 4, "occurrences": 1},
                    {"intervalStart": 4, "intervalEnd": 6, "occurrences": 1},
                ],
            }
            for i in range(20)
        ]

    def test_external_residuals_parsing(self, residuals_response):
        residuals = ExternalResidualsChart.from_server_data(residuals_response[0])
        assert residuals.dataset_id == residuals_response[0]["datasetId"]
        assert residuals.residual_mean == residuals_response[0]["residualMean"]
        cod = residuals_response[0]["coefficientOfDetermination"]
        assert residuals.coefficient_of_determination == cod
        assert residuals.standard_deviation == residuals_response[0]["standardDeviation"]
        assert residuals.data == [tuple(x) for x in residuals_response[0]["data"]]

    @responses.activate
    def test_get_residuals_ok(self, url, project_id, model_id, residuals_response):
        dataset_id = "datasetId0"
        url_page = url + "?offset=0&limit=1&datasetId={}".format(dataset_id)
        resp_data = dict(count=1, previous=None, next=None, data=[residuals_response[0]])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        chart = ExternalResidualsChart.get(project_id, model_id, dataset_id)
        assert chart.dataset_id == residuals_response[0]["datasetId"]
        assert chart.residual_mean == residuals_response[0]["residualMean"]
        cod = residuals_response[0]["coefficientOfDetermination"]
        assert chart.coefficient_of_determination == cod
        assert chart.standard_deviation == residuals_response[0]["standardDeviation"]
        assert chart.data == [tuple(x) for x in residuals_response[0]["data"]]

    @responses.activate
    def test_get_residuals_failure(self, url, project_id, model_id):
        dataset_id = "dataset_id_0"
        url_page = url + "?offset=0&limit=1&datasetId={}".format(dataset_id)
        resp_data = dict(count=0, previous=None, next=None, data=[])
        responses.add(responses.GET, url_page, json=resp_data, status=200, match_querystring=True)
        with pytest.raises(ClientError, match="Requested residual chart does not exist."):
            ExternalResidualsChart.get(project_id, model_id, dataset_id)

    @responses.activate
    @patch(
        "datarobot.models.external_dataset_scores_insights."
        "external_dataset_residuals.DEFAULT_BATCH_SIZE",
        10,
    )
    def test_residuals_all_results(self, url, residuals_response, project_id, model_id):
        url_page1 = url + "?limit=10&offset=0"
        url_page2 = url + "?limit=10&offset=10"
        resp_data_1 = dict(count=10, previous=None, next=url_page2, data=residuals_response[:10])
        resp_data_2 = dict(count=1, previous=url_page1, next=None, data=residuals_response[10:])
        responses.add(
            responses.GET, url_page1, json=resp_data_1, status=200, match_querystring=True
        )
        responses.add(
            responses.GET, url_page2, json=resp_data_2, status=200, match_querystring=True
        )

        residuals = ExternalResidualsChart.list(project_id, model_id, limit=0)
        assert len(residuals) == 20
        for i, chart in enumerate(residuals):
            assert isinstance(chart, ExternalResidualsChart)
            assert chart.dataset_id == "datasetId{}".format(i)
            assert chart.data == [tuple(x) for x in residuals_response[0]["data"]]
