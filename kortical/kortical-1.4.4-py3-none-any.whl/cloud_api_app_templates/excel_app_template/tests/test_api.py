import pytest
import json
from module_placeholder.config import read_config
from module_placeholder.api.http_status_codes import HTTP_OKAY, UNAUTHORISED

authentication_config = read_config("authentication.yml")
api_token = authentication_config['api_token']


@pytest.mark.api
def test_latest_churn_endpoint(client):
    response = client.get(f'/latest_churn.xlsx?api_key={api_token}')
    assert response.status_code == HTTP_OKAY
    assert response.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.data) > 0
    assert type(response.data) == bytes


@pytest.mark.api
def test_latest_churn_endpoint_no_api_key(client):
    response = client.get(f'/latest_churn.xlsx')
    assert response.status_code == UNAUTHORISED


@pytest.mark.api
def test_latest_churn_endpoint_wrong_api_key(client):
    response = client.get(f'/latest_churn.xlsx?api_key={api_token}12345')
    assert response.status_code == UNAUTHORISED