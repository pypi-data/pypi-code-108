import pytest
import json
from module_placeholder.config import read_config
from module_placeholder.api.http_status_codes import HTTP_OKAY, UNAUTHORISED

authentication_config = read_config("authentication.yml")
api_token = authentication_config['api_token']


@pytest.mark.api
def test_update_bigquery_endpoint(client):
    response = client.get(f'/update_bigquery?api_key={api_token}')
    assert response.status_code == HTTP_OKAY
    assert response.content_type == "text/html; charset=utf-8"


@pytest.mark.api
def test_update_bigquery_endpoint_no_api_key(client):
    response = client.get(f'/update_bigquery')
    assert response.status_code == UNAUTHORISED


@pytest.mark.api
def test_update_bigquery_endpoint_wrong_api_key(client):
    response = client.get(f'/update_bigquery?api_key={api_token}12345')
    assert response.status_code == UNAUTHORISED