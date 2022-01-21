import pytest
import requests_mock

from resistant_documents_client.client import ResistantDocumentsClient


API_KEY = "abc"
API_URL = "https://test.endpoint"
HEADERS = {"Authorization": API_KEY}

ENDPOINTS = ["results", "quality", "content"]


@pytest.fixture(scope="function")
def client():
    return ResistantDocumentsClient(API_KEY, API_URL)


def test_submit(client):
    with requests_mock.Mocker() as m:
        m.post(f'{API_URL}/v1/pdf/submit', json={"upload_url": "https://test.upload/data", "submission_id": "id"}, request_headers=HEADERS)
        m.put("https://test.upload/data", status_code=200)
        submission_id = client.submit(b"abc")
        assert submission_id == "id"


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_endpoint_returns_data(client, endpoint_name):
    with requests_mock.Mocker() as m:
        result = {"message": "ok"}

        m.get(f'{API_URL}/v1/pdf/{endpoint_name}/id', request_headers=HEADERS, json=result)
        assert result == getattr(client, endpoint_name)("id")


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_endpoint_retries(client, endpoint_name):
    with requests_mock.Mocker() as m:
        result = {"message": "ok"}
        responses = [{"status_code": 404}, {"status_code": 404},
                     {"json": result, "status_code": 200}]

        m.get(f'{API_URL}/v1/pdf/{endpoint_name}/id', responses)
        assert result == getattr(client, endpoint_name)("id")


@pytest.mark.parametrize("endpoint_name", ENDPOINTS)
def test_results_throws_exception_when_no_data_exists(client, endpoint_name):
    with requests_mock.Mocker() as m:
        m.get(f'{API_URL}/v1/pdf/{endpoint_name}/id', status_code=404, request_headers=HEADERS)
        with pytest.raises(RuntimeError):
            getattr(client, endpoint_name)("id", max_num_retries=2)


def test_presign(client):
    with requests_mock.Mocker() as m:
        result = {"id": "id", "url": "url"}
        responses = [{"json": result, "status_code": 200}]
        m.post(f'{API_URL}/v1/pdf/presign/id', responses, request_headers=HEADERS)
        assert result == client.presign("id", expiration=1)
