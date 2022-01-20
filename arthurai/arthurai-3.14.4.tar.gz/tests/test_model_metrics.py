import pytest

from arthurai.core.models import ArthurModel
from arthurai.core.alerts import Metric, MetricType
from arthurai.client.http.requests import HTTPClient
from arthurai.common.exceptions import ArthurUserError
from tests import MockResponse

metric_id = "4e18df3d-307d-4b3f-aba4-a434ca893c8a"

metric_dict = {
    "name": "Custom Metric A",
    "endpoint": "/api/v3/models/4e18df3d-307d-4b3f-aba4-a434ca893c8a/inferences/query",
    "query": {
        "select": [
            {
                "function": "rate",
                "parameters": {
                    "property": "class_a",
                    "comparater": "gte",
                    "value": 0.5
                }
            }
        ],
        "filter": [
            {
                "property": "city",
                "comparator": "eq",
                "value": "Boston"
            }
        ]
    },
    "type": "model_performance_metric"
}


def patch_metric_post_request(*args, **kwargs):
    metric_to_create = kwargs['json']
    assert "name" in metric_to_create
    assert "query" in metric_to_create
    assert "endpoint" in metric_to_create
    assert "https://test.ai" not in metric_to_create["endpoint"]
    assert "/inferences/query" in metric_to_create["endpoint"]
    assert metric_to_create["name"] == "Custom Metric A"
    metric_dict["name"] = metric_to_create["name"]
    metric_dict["query"] = metric_to_create["query"]
    metric_dict["endpoint"] = metric_to_create["endpoint"]
    metric_dict["id"] = metric_id
    return MockResponse(metric_dict, 201)


def patch_metric_get_request(*args, **kwargs):
    assert args[1] == f'/models/4a57c553-e787-4307-88f1-3747ec9130f5/metrics'
    assert kwargs["params"]["page"] == str(TestMetrics.current_page_num)
    metric_list = {
        "metrics": [
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "name": "rate that city is Boston and predicted class_a",
                "query": {
                    "select": [
                        {
                            "function": "rate",
                            "parameters": {
                                "property": "class_a",
                                "comparater": "gte",
                                "value": 0.5
                            }
                        }
                    ],
                    "filter": [
                        {
                            "property": "city",
                            "comparator": "eq",
                            "value": "Boston"
                        }
                    ]
                },
                "endpoint": "/api/v3/models/00000000-0000-0000-0000-000000000000/inferences/query",
                "is_default": False
            },
            {
                "id": "10000000-0000-0000-0000-000000000000",
                "name": "Inference Count",
                "query": {
                    "select": [
                        {
                            "function": "count"
                        }
                    ]
                },
                "endpoint": "/api/v3/models/10000000-0000-0000-0000-000000000000/inferences/query",
                "type": "model_output_metric",
                "is_default": True
            }
        ],
        "page": TestMetrics.current_page_num,
        "page_size": 2,
        "total_pages": 2,
        "total_count": 4
    }

    TestMetrics.current_page_num += 1

    return MockResponse(metric_list, 200)


def patch_metric_get_request_no_metrics_resp(*args, **kwargs):
    assert args[1] == f'/models/4a57c553-e787-4307-88f1-3747ec9130f5/metrics'
    metrics = {"metrics": [], "page": 1, "page_size": 20}
    return MockResponse(metrics, 200)


def patch_metric_get_by_id_request(*args, **kwargs):
    assert args[1] == f'/models/4a57c553-e787-4307-88f1-3747ec9130f5/metrics/{metric_id}'
    metric = {
        "id": metric_id,
        "name": "rate that city is Boston and predicted class_a",
        "query": {
            "select": [
                {
                    "function": "rate",
                    "parameters": {
                        "property": "class_a",
                        "comparater": "gte",
                        "value": 0.5
                    }
                }
            ],
            "filter": [
                {
                    "property": "city",
                    "comparator": "eq",
                    "value": "Boston"
                }
            ]
        },
        "endpoint": "/api/v3/models/00000000-0000-0000-0000-000000000000/inferences/query",
        "is_default": False
    }

    return MockResponse(metric, 200)


class TestMetrics:
    current_page_num = 1

    def test_create_metric(self, monkeypatch, mock_cred_env_vars, binary_classification_model: ArthurModel):
        query = {
            "select": [
                {
                    "function": "rate",
                    "parameters": {
                        "property": "class_a",
                        "comparater": "gte",
                        "value": 0.5
                    }
                }
            ],
            "filter": [
                {
                    "property": "city",
                    "comparator": "eq",
                    "value": "Boston"
                }
            ]
        }
        monkeypatch.setattr(HTTPClient, "post", patch_metric_post_request)
        res = binary_classification_model.create_metric("Custom Metric A", query=query)
        assert res == metric_id

    def test_get_metrics_pagination(self, monkeypatch, mock_cred_env_vars, binary_classification_model: ArthurModel):
        monkeypatch.setattr(HTTPClient, "get", patch_metric_get_request)
        res = binary_classification_model.get_metrics()
        assert len(res) == 4
        assert TestMetrics.current_page_num == 3

    def test_get_metrics_no_resp(self, monkeypatch, mock_cred_env_vars, binary_classification_model: ArthurModel):
        monkeypatch.setattr(HTTPClient, "get", patch_metric_get_request_no_metrics_resp)
        res = binary_classification_model.get_metrics()
        assert len(res) == 0

    def test_get_metrics_error(self, monkeypatch, mock_cred_env_vars,
                               binary_classification_model: ArthurModel):
        monkeypatch.setattr(HTTPClient, "get", patch_metric_get_request)
        with pytest.raises(ArthurUserError) as e:
            res = binary_classification_model.get_metrics(metric_type="invalid metric type")
        assert str(MetricType.list()) in str(e.value)

    def test_get_metric_by_id(self, monkeypatch, mock_cred_env_vars, binary_classification_model: ArthurModel):
        monkeypatch.setattr(HTTPClient, "get", patch_metric_get_by_id_request)
        res = binary_classification_model.get_metrics(metric_id=metric_id)
        assert len(res) == 1
        assert res[0].id == metric_id
