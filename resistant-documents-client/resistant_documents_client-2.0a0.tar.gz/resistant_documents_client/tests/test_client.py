import pytest
import requests_mock
from freezegun import freeze_time

from resistant_documents_client.client import ResistantDocumentsClient

CLIENT_ID = "client1"
CLIENT_SECRET = "client_secret"
TOKEN_URL = "https://get.token.com/v1/token"
ACCESS_TOKEN = "abc"
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

API_URL = "https://api.endpoint"
ENDPOINTS = ["fraud", "quality", "content"]


@pytest.fixture
def client_mock():
    with requests_mock.Mocker() as m:
        m.post(TOKEN_URL, json={"expires_in": 3600, "access_token": ACCESS_TOKEN})
        client = ResistantDocumentsClient(CLIENT_ID, CLIENT_SECRET, TOKEN_URL, API_URL)
        yield client, m


def test_token_refreshed_correctly():
    fraud_result = {"status_code": 200, "score": "HIGH_RISK"}
    with freeze_time() as frozen_datetime:
        with requests_mock.Mocker() as m:
            m.post(TOKEN_URL, json={"expires_in": 3600, "access_token": ACCESS_TOKEN})
            fraud_url = f'{API_URL}/v2/submission/id/fraud'
            m.get(fraud_url, request_headers=HEADERS, json=fraud_result)

            client = ResistantDocumentsClient(CLIENT_ID, CLIENT_SECRET, TOKEN_URL, API_URL)

            exp_url_history = [TOKEN_URL]
            for _ in range(3):
                assert fraud_result == client.fraud("id")
                exp_url_history.append(fraud_url)
            assert exp_url_history == [r.url for r in m.request_history]
            frozen_datetime.tick(3700)

            assert fraud_result == client.fraud("id")
            exp_url_history += [TOKEN_URL, fraud_url]
            assert exp_url_history == [r.url for r in m.request_history]


def test_submit(client_mock):
    client, m = client_mock
    desired_id = "id"
    m.post(f"{API_URL}/v2/submission", json={"upload_url": "https://test.upload/data", "submission_id": desired_id}, request_headers=HEADERS)
    m.put("https://test.upload/data", status_code=200)
    assert client.submit(b"abc", "query_1", "ONLY_QUALITY") == desired_id


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_endpoint_returns_data(client_mock, endpoint_name):
    client, m = client_mock
    result = {"message": "ok"}

    m.get(f'{API_URL}/v2/submission/id/{endpoint_name}', request_headers=HEADERS, json=result)
    assert result == getattr(client, endpoint_name)("id")


def test_submit_endpoint_retries(client_mock):
    client, m = client_mock
    responses = [{"status_code": 500}, {"status_code": 500}, {"json": {"upload_url": "https://test.upload/data", "submission_id": "id"}}]
    m.post(f"{API_URL}/v2/submission", response_list=responses, request_headers=HEADERS)
    m.put("https://test.upload/data", status_code=200)
    assert client.submit(b"abc", "query_1", "ONLY_QUALITY") == "id"


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_poll_retries(client_mock, endpoint_name):
    client, m = client_mock
    result = {"message": "ok"}
    responses = [{"status_code": 404}, {"status_code": 404},
                 {"json": result, "status_code": 200}]

    m.get(f'{API_URL}/v2/submission/id/{endpoint_name}', responses)
    assert result == getattr(client, endpoint_name)("id")


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_results_throws_exception_when_no_data_exists(client_mock, endpoint_name):
    client, m = client_mock
    m.get(f'{API_URL}/v2/submission/id/{endpoint_name}', status_code=404, request_headers=HEADERS)
    with pytest.raises(RuntimeError):
        getattr(client, endpoint_name)("id", max_num_retries=2)


def test_fraud_presign(client_mock):
    client, m = client_mock
    m.get(f'{API_URL}/v2/submission/id/fraud', status_code=400, request_headers=HEADERS)
    presign_s3_url = "https://s3.download.aws.com/some_object"
    m.get(f'{API_URL}/v2/submission/id/fraud?presign=true', status_code=200, json={"download_url": presign_s3_url}, request_headers=HEADERS)
    response = {"status": "SUCCESS"}
    m.get(presign_s3_url, json=response)

    act_response = client.fraud("id", 1)
    assert act_response == response
