import pytest
import json
from module_placeholder.config import read_config
from module_placeholder.api.http_status_codes import HTTP_OKAY, UNAUTHORISED

authentication_config = read_config("authentication.yml")
api_token = authentication_config['api_token']


@pytest.mark.api
def test_index_endpoint(client):
    response = client.get(f'/')
    assert response.status_code == HTTP_OKAY


@pytest.mark.api
def test_predict_endpoint(client):
    request_data = {
        "input_text": "Hello this is some input text"
    }
    response = client.post(f'/predict?api_key={api_token}', json=request_data)
    assert response.status_code == HTTP_OKAY


@pytest.mark.api
def test_predict_endpoint_no_api_key(client):
    response = client.post(f'/predict')
    assert response.status_code == UNAUTHORISED


@pytest.mark.api
def test_predict_endpoint_wrong_api_key(client):
    response = client.post(f'/predict?api_key={api_token}12345')
    assert response.status_code == UNAUTHORISED
