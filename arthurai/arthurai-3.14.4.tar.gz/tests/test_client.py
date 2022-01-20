import os
import re
from http import HTTPStatus

import pytest
import responses

from tests import MockResponse

from arthurai import ArthurAI
from arthurai.common.constants import InputType, OutputType
from arthurai.client.validation import validate_multistatus_response_and_get_failures, validate_response_status
from arthurai.common.exceptions import ResponseServerError, ResponseClientError, ResponseRedirectError, \
    InternalValueError, UserValueError, UserTypeError
from tests.fixtures.mocks import ACCESS_KEY, BASE_URL, USER_ACCESS_KEY
from tests.helpers import mock_get, mock_post
from unittest.mock import patch


class TestClient:

    def _mock_get_user(self):
        mock_get(f"/api/v3/users/me", status=HTTPStatus.OK,
                 response_body={"organization_id": "65624ee6-9a73-4fe3-a7ff-8612f7d11c21", "role": "Model Owner"})

    def _mock_get_user_unauthorized(self):
        mock_get(f"/api/v3/users/me", status=HTTPStatus.UNAUTHORIZED,
                 response_body={"bad": "user"})

    def _mock_user_login(self):
        mock_post(f"/api/v3/login", status=HTTPStatus.OK, response_body={},
                  headers={"Set-Cookie": 'Authorization=' + USER_ACCESS_KEY})

    @pytest.mark.usefixtures('mock_cred_env_vars')
    def test_client_init_env_vars(self):
        client = ArthurAI(offline=True)
        assert client.client.api_base_url == 'http://mock/api/v3'
        assert client.client.session.headers.get('Authorization') == 'access_key'
        assert client.client.session.verify is False

        client = ArthurAI(url="this is a url", access_key="this is an access key", offline=True)
        assert client.client.api_base_url == "https://this is a url/api/v3"
        assert client.client.session.headers.get('Authorization') == "this is an access key"
        assert client.client.session.verify is False

        client = ArthurAI(url="http://this is a url", access_key="this is an access key", offline=True)
        assert client.client.api_base_url == "http://this is a url/api/v3"
        assert client.client.session.headers.get('Authorization') == "this is an access key"
        assert client.client.session.verify is False

        with pytest.raises(ValueError):
            ArthurAI(url="http://this is a url/apath", access_key="this is an access key", offline=True)

        with pytest.raises(ValueError):
            ArthurAI(url="http://this is a url?food=good", access_key="this is an access key", offline=True)

        with pytest.raises(ValueError):
            ArthurAI(url="fatfinger://this is a url", access_key="this is an access key", offline=True)

        with pytest.raises(ValueError):
            ArthurAI(url="https:", access_key="this is an access key", offline=True)

    @pytest.mark.usefixtures('mock_cred_env_vars_ssl_true')
    def test_client_init_env_vars_ssl_true(self):
        client = ArthurAI(url="http://this is a url", access_key="this is an access key", offline=True)
        assert client.client.session.verify is True

    @pytest.mark.usefixtures('mock_cred_env_vars_ssl_garbage')
    def test_client_init_env_vars_ssl_garbage(self):
        with pytest.raises(UserValueError):
            ArthurAI(url="http://this is a url", access_key="this is an access key", offline=True)

    @responses.activate
    def test_client_init(self):
        self._mock_get_user()

        ArthurAI(access_key=ACCESS_KEY, url=BASE_URL)
        assert len(responses.calls) == 1
        expectedResponse = {'organization_id': '65624ee6-9a73-4fe3-a7ff-8612f7d11c21', 'role': 'Model Owner'}
        assert expectedResponse == responses.calls[0].response.json()

    @responses.activate
    def test_client_init_config_param(self):
        self._mock_get_user()

        ArthurAI(config={'access_key': ACCESS_KEY, 'url': BASE_URL})
        assert len(responses.calls) == 1
        expectedResponse = {'organization_id': '65624ee6-9a73-4fe3-a7ff-8612f7d11c21', 'role': 'Model Owner'}
        assert expectedResponse == responses.calls[0].response.json()

    @responses.activate
    def test_client_init_bad_host(self):
        with pytest.raises(UserValueError, match=".*please ensure the URL is correct.*"):
            ArthurAI(access_key=ACCESS_KEY, url=BASE_URL)
        assert len(responses.calls) == 1

    @responses.activate
    def test_client_init_bad_access_key(self):
        self._mock_get_user_unauthorized()
        with pytest.raises(UserValueError, match=".*please ensure your access key is correct.*"):
            ArthurAI(access_key=ACCESS_KEY, url=BASE_URL)
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_old_client_login_with_username_password(self):
        self._mock_user_login()
        self._mock_get_user()

        with patch("arthurai.client.client.ArthurAI.get_service_accounts") as get_sa_mock:
            get_sa_mock.return_value = [{"id": "", "organization_id": "", "description": "",
                                            "token": ACCESS_KEY}]
            arthur = ArthurAI(login="arthur", password="password", url=BASE_URL)
            assert ACCESS_KEY == arthur.client.access_key

    @responses.activate
    def test_new_client_login_with_username_password(self):
        self._mock_user_login()
        self._mock_get_user()

        with patch("arthurai.client.client.ArthurAI.get_service_accounts") as get_sa_mock:
            get_sa_mock.return_value = None
            with patch("arthurai.client.client.ArthurAI.create_service_account") as get_create_mock:
                get_create_mock.return_value = {"id": "", "organization_id": "",
                                                    "description": "", "token": ACCESS_KEY}
                arthur = ArthurAI(login="arthur", password="password", url=BASE_URL)
                assert ACCESS_KEY == arthur.client.access_key
                assert arthur.verify_ssl is True
                assert arthur.client.session.verify is True

                arthur = ArthurAI(login="arthur", password="password", url=BASE_URL, verify_ssl=False)
                assert arthur.client.session.verify is False

    @responses.activate
    def test_client_init_offline(self):
        ArthurAI(access_key=ACCESS_KEY, url=BASE_URL, offline=True)
        assert len(responses.calls) == 0

    @responses.activate
    def test_client_init_offlines(self):
        mock_get(f"/api/v3/models/1234", status=200,
                 response_body={"organization_id": "65624ee6-9a73-4fe3-a7ff-8612f7d11c21", "role": "Model Owner"})
        ArthurAI(access_key=ACCESS_KEY, url=BASE_URL, offline=True)
        assert len(responses.calls) == 0

    @responses.activate
    def test_client_sets_model_id_and_user_header(self):
        model_data = {
            "id": "1234",
            "partner_model_id": "",
            "input_type": InputType.Tabular,
            "output_type": OutputType.Regression,
            "display_name": "",
            "description": "",
            "attributes": [],
        }
        mock_get("/api/v3/models/1234", status=200, response_body=model_data)

        self._mock_get_user()

        client = ArthurAI(access_key=ACCESS_KEY, url=BASE_URL)
        client.get_model('1234')

        assert len(responses.calls) == 2
        if "models" in responses.calls[1].request.url:
            header = responses.calls[1].request.headers
        else:
            header = responses.calls[0].request.headers
        assert 'User-Agent' in header
        print(header['User-Agent'])
        assert re.findall(r"^arthur-sdk\/\d.\d+.\d+ \(system=\w*, org=65624ee6-9a73-4fe3-a7ff-8612f7d11c21\)$",
                          header['User-Agent'])
        assert os.getenv("ARTHUR_LAST_MODEL_ID") == "1234"


class TestGetMultiStatusResponseFailures:
    # fixtures
    SUCCESS_RESULTS = [{"message": "ok", "status": HTTPStatus.OK}, {"message": "created", "status": HTTPStatus.CREATED}]
    USER_FAIL_RESULTS = [{"message": "not found", "status": HTTPStatus.NOT_FOUND}]
    INTERNAL_FAIL_RESULTS = [{"message": "failure", "status": HTTPStatus.INTERNAL_SERVER_ERROR},
                             {"message": "choose", "status": HTTPStatus.MULTIPLE_CHOICES}]
    SUCCESS_BODY = {"counts": {"success": len(SUCCESS_RESULTS), "failure": 0, "total": len(SUCCESS_RESULTS)},
                    "results": SUCCESS_RESULTS}
    FAILURES_BODY = {"counts": {"success": len(SUCCESS_RESULTS),
                                "failure": len(INTERNAL_FAIL_RESULTS) + len(USER_FAIL_RESULTS),
                                "total": len(SUCCESS_RESULTS) + len(INTERNAL_FAIL_RESULTS) + len(USER_FAIL_RESULTS)},
                     "results": SUCCESS_RESULTS + USER_FAIL_RESULTS + INTERNAL_FAIL_RESULTS}
    MISMATCHED_COUNTS_BODY = {"counts": {"success": len(SUCCESS_RESULTS), "failure": 0,
                                         "total": len(SUCCESS_RESULTS)},
                              "results": SUCCESS_RESULTS + USER_FAIL_RESULTS + INTERNAL_FAIL_RESULTS}

    def test_success(self):
        response = MockResponse(self.SUCCESS_BODY, HTTPStatus.MULTI_STATUS)
        actual_user_failures, actual_internal_failures = validate_multistatus_response_and_get_failures(response)
        assert actual_user_failures == []
        assert actual_internal_failures == []

    def test_failures(self):
        response = MockResponse(self.FAILURES_BODY, HTTPStatus.MULTI_STATUS)
        actual_user_failures, actual_internal_failures = validate_multistatus_response_and_get_failures(response)
        assert actual_user_failures == self.USER_FAIL_RESULTS
        assert actual_internal_failures == self.INTERNAL_FAIL_RESULTS

    def test_bad_status(self):
        response = MockResponse(self.SUCCESS_BODY, HTTPStatus.OK)
        with pytest.raises(ValueError):
            validate_multistatus_response_and_get_failures(response)

    def test_mismatched_counts(self):
        response = MockResponse(self.MISMATCHED_COUNTS_BODY, HTTPStatus.MULTI_STATUS)
        with pytest.raises(ValueError):
            validate_multistatus_response_and_get_failures(response)


# TODO: add testing around allowed exceptions and what gets raised first (e.g. expected 207 but 404 shouldn't raise
#  InternalValueError)
class TestValidateResponse:
    # fixtures
    JSON_BODY = {"status": "somestatus"}
    BYTES_BODY = b"bodybytes"

    def test_server_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.INTERNAL_SERVER_ERROR)
        with pytest.raises(ResponseServerError):
            validate_response_status(response)

    def test_client_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.NOT_FOUND)
        with pytest.raises(ResponseClientError):
            validate_response_status(response)

    def test_expected_404_no_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.NOT_FOUND)
        validate_response_status(response, expected_status_code=HTTPStatus.NOT_FOUND)

    def test_redirect_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.MOVED_PERMANENTLY)
        with pytest.raises(ResponseRedirectError):
            validate_response_status(response)

    def test_redirect_no_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.MOVED_PERMANENTLY)
        validate_response_status(response, allow_redirects=True)

    def test_ok_no_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.OK)
        validate_response_status(response)

    def test_unexpected_ok_error_response(self):
        response = MockResponse(self.JSON_BODY, HTTPStatus.OK)
        with pytest.raises(InternalValueError):
            validate_response_status(response, expected_status_code=HTTPStatus.CREATED)

    def test_server_error(self):
        code = HTTPStatus.INTERNAL_SERVER_ERROR
        with pytest.raises(ResponseServerError):
            validate_response_status(code)

    def test_client_error(self):
        code = HTTPStatus.NOT_FOUND
        with pytest.raises(ResponseClientError):
            validate_response_status(code)

    def test_expected_404_no_error(self):
        code = HTTPStatus.NOT_FOUND
        validate_response_status(code, expected_status_code=HTTPStatus.NOT_FOUND)

    def test_redirect_error(self):
        code = HTTPStatus.MOVED_PERMANENTLY
        with pytest.raises(ResponseRedirectError):
            validate_response_status(code)

    def test_redirect_no_error(self):
        code = HTTPStatus.MOVED_PERMANENTLY
        validate_response_status(code, allow_redirects=True)

    def test_ok_no_error(self):
        code = HTTPStatus.OK
        validate_response_status(code)

    def test_unexpected_ok_error(self):
        code = HTTPStatus.OK
        with pytest.raises(InternalValueError):
            validate_response_status(code, expected_status_code=HTTPStatus.CREATED)
