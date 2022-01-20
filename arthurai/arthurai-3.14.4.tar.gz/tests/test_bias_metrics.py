import responses
import pytest

from arthurai.core.models import ArthurModel
from arthurai.core.bias.bias_metrics import BiasMetrics
from .helpers import mock_post

from .test_request_models.fixtures import model_response_json_strings
from .fixtures.mocks import BASE_URL, ACCESS_KEY, client as mock_client


bias_query_json_result = {
            "query_result": [
            {
                "bias": 1,
                "confusion_matrix": {
                "accuracy_rate": 0.9,
                "balanced_accuracy_rate": 0.8,
                "f1": 0.7,
                "false_negative_rate": 0.5,
                "false_positive_rate": 0,
                "precision": 0.9,
                "true_negative_rate": 1,
                "true_positive_rate": 0.5
                }
            },
            {
                "bias": 2,
                "confusion_matrix": {
                "accuracy_rate": 0.9,
                "balanced_accuracy_rate": 0.8,
                "f1": 0.7,
                "false_negative_rate": 0.4,
                "false_positive_rate": 0,
                "precision": 0.8,
                "true_negative_rate": 1,
                "true_positive_rate": 0.6
                }
            }
            ],
            "sampling_threshold": 1
        }


@pytest.fixture
def binary_model(mock_client):
    binary_model = ArthurModel.from_json(model_response_json_strings[4])
    binary_model._client = mock_client.client
    return binary_model


@pytest.fixture
def multiclass_model(mock_client):
    multiclass_model = ArthurModel.from_json(model_response_json_strings[5])
    multiclass_model._client = mock_client.client
    return multiclass_model


@responses.activate
def test_get_bias_cm_binary(binary_model):
    endpoint = "/api/v3/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/inferences/query"
    mock_post(endpoint, response_body=bias_query_json_result)

    bin_metric = BiasMetrics(binary_model)

    metrics = bin_metric.group_confusion_matrices("bias")
    metrics_flipped = bin_metric.group_confusion_matrices("bias", return_by_metric=False)

    assert "precision" in metrics.keys()
    assert len(metrics.keys()) == 8
    assert len(metrics['f1'].keys()) == 2
    assert len(metrics_flipped[1].keys()) == 8
    assert metrics_flipped[1]['accuracy_rate'] == 0.9


@responses.activate
def test_get_bias_cm_multiclass(multiclass_model):
    endpoint = "/api/v3/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasmulticlass/inferences/query"
    mock_post(endpoint, response_body=bias_query_json_result)

    mult_metric = BiasMetrics(multiclass_model)
    metrics = mult_metric.group_confusion_matrices("bias", "attr_2")
    metrics_flipped = mult_metric.group_confusion_matrices("bias", "attr_2", return_by_metric=False)

    assert "precision" in metrics.keys()
    assert len(metrics.keys()) == 8
    assert len(metrics['f1'].keys()) == 2
    assert len(metrics_flipped[1].keys()) == 8
    assert metrics_flipped[1]['accuracy_rate'] == 0.9


def test_get_bias_cm_multiclass_requires_predvalue(multiclass_model):
    mult_metric = BiasMetrics(multiclass_model)
    with pytest.raises(Exception):
        mult_metric.group_confusion_matrices("bias")


@responses.activate
def test_get_bias_pr_binary(binary_model):
    endpoint = "/api/v3/models/ac55c7b4-2db7-4902-8cc3-969ed67a20c8_biasbinary/inferences/query"
    expected_response = {
            "query_result": [
            {
                "bias": 1,
                "positive_rate": 0.15
            },
            {
                "bias": 2,
                "positive_rate": 0.14
            }
            ],
            "sampling_threshold": 1
        }
    mock_post(endpoint, response_body=expected_response)

    bin_metric = BiasMetrics(binary_model)
    prs = bin_metric.group_positivity_rates("bias")
    prsalias = bin_metric.demographic_parity("bias")

    assert prs == prsalias    
    assert len(prs.keys()) == 2
    assert prs[2] == 0.14


def test_get_bias_pr_multiclass(multiclass_model):
    mult_metric = BiasMetrics(multiclass_model)
    with pytest.raises(Exception):
        mult_metric.group_positivity_rates("bias")