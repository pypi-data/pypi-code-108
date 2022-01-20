import pytest
import mock
import os

from arthurai.client.client import new_requests_client
from arthurai.core.models import ArthurModel, ArthurAttribute
from arthurai.client.http.requests import HTTPClient
from tests.base_test import BaseTest


@pytest.fixture(scope="function")
def mock_cred_env_vars():
    with mock.patch.dict(os.environ, {"ARTHUR_API_KEY": "access_key", "ARTHUR_ENDPOINT_URL": BaseTest._base_url, "VERIFY_SSL": "False"}):
        yield


@pytest.fixture(scope="function")
def mock_cred_env_vars_ssl_true():
    with mock.patch.dict(os.environ, {"ARTHUR_API_KEY": "access_key", "ARTHUR_ENDPOINT_URL": BaseTest._base_url, "VERIFY_SSL": "True"}):
        yield


@pytest.fixture(scope="function")
def mock_cred_env_vars_ssl_garbage():
    with mock.patch.dict(os.environ, {"ARTHUR_API_KEY": "access_key", "ARTHUR_ENDPOINT_URL": BaseTest._base_url, "VERIFY_SSL": "bernie"}):
        yield


@pytest.fixture(scope="function")
def binary_classification_model() -> ArthurModel:
    binary_classification_model = {
        "id": "4a57c553-e787-4307-88f1-3747ec9130f5",
        "partner_model_id": "binary_classification_model",
        "input_type": "TABULAR",
        "output_type": "MULTICLASS",
        "archived": False,
        "created_at": "2020-10-26T21:43:24.632335Z",
        "updated_at": "2020-10-26T21:43:26.364596Z",
        "attributes": [
            ArthurAttribute(
                id="1d4bec8d-84a6-4ae7-a7ea-1a2230bb977c",
                name="input",
                value_type="INTEGER",
                stage="PIPELINE_INPUT",
                position=1,
                categorical=False,
                monitor_for_bias=False,
                is_positive_predicted_attribute=False
            ),
            ArthurAttribute(
                id="254c8f5f-f4b8-4943-89bf-db106d5ca835",
                name="pos_predicted_probability",
                value_type="FLOAT",
                stage="PREDICTED_VALUE",
                position=1,
                categorical=False,
                min_range=0,
                max_range=1,
                monitor_for_bias=False,
                is_unique=False,
                is_positive_predicted_attribute=True,
                attribute_link="pos_gt"
            ),
            ArthurAttribute(
                id="ac97a47f-f755-451e-956c-d1ed52403915",
                name="pos_gt",
                value_type="INTEGER",
                stage="GROUND_TRUTH",
                position=1,
                categorical=False,
                min_range=0,
                max_range=1,
                monitor_for_bias=False,
                is_unique=True,
                is_positive_predicted_attribute=False,
                attribute_link="pos_predicted_probability"
            ),
            ArthurAttribute(
                id="c2e626df-ee4c-403f-818b-f4f2d9180eab",
                name="neg_gt",
                value_type="INTEGER",
                stage="GROUND_TRUTH",
                position=2,
                categorical=False,
                min_range=0,
                max_range=1,
                monitor_for_bias=False,
                is_unique=True,
                is_positive_predicted_attribute=False,
                attribute_link="neg_predicted_probability"
            ),
            ArthurAttribute(
                id="d4f04345-c92c-4959-9d92-7fe35924efeb",
                name="neg_predicted_probability",
                value_type="FLOAT",
                stage="PREDICTED_VALUE",
                position=2,
                categorical=False,
                min_range=0,
                max_range=1,
                monitor_for_bias=False,
                is_unique=False,
                is_positive_predicted_attribute=False,
                attribute_link="neg_gt"
            ),
        ],
        "tags": [],
        "classifier_threshold": 0.5,
        "explainability": {
            "enabled": False
        },
        "is_batch": False,
        "text_delimiter": ","
    }
    yield ArthurModel(client=new_requests_client(url="test.ai", offline=True), **binary_classification_model)
