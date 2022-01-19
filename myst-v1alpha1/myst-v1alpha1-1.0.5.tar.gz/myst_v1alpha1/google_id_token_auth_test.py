import unittest

import google.auth.credentials
import google.oauth2.credentials
import mock
import responses
from google.oauth2.service_account import IDTokenCredentials
from requests import Session

from myst_v1alpha1.google_id_token_auth import GoogleIDTokenAuth


class AuthTest(unittest.TestCase):
    def test_google_id_token_auth(self):
        # Mock out service account credentials.
        service_account_credentials_mock = mock.Mock(IDTokenCredentials)
        service_account_credentials_mock.token = "service_account_token"

        # Test the `GoogleIDTokenAuth` with service account credentials.
        google_id_token_auth = GoogleIDTokenAuth(credentials=service_account_credentials_mock)
        self.assertEqual(google_id_token_auth.id_token, "service_account_token")

        # Mock out user credentials.
        user_credentials_mock = google.oauth2.credentials.Credentials(token=None, id_token="user_token")

        # Test the `GoogleIDTokenAuth` with user credentials.
        google_id_token_auth = GoogleIDTokenAuth(credentials=user_credentials_mock)
        self.assertEqual(google_id_token_auth.id_token, "user_token")

        # Test the `GoogleIDTokenAuth` with anonymous credentials.
        google_id_token_auth = GoogleIDTokenAuth(credentials=google.auth.credentials.AnonymousCredentials())
        self.assertEqual(google_id_token_auth.id_token, None)

        # Test with an unsupported credentials type.
        mock_credentials = mock.Mock()
        google_id_token_auth = GoogleIDTokenAuth(credentials=mock_credentials)
        with self.assertRaises(TypeError):
            _ = google_id_token_auth.id_token

    @mock.patch("google.oauth2.credentials.Credentials.refresh")
    @mock.patch("myst_v1alpha1.google_id_token_auth.Request")
    def test_google_id_token_refresh(self, google_auth_transport_request_patch, user_credentials_refresh_patch):
        # Mock out the Google auth objects so we don't actually use try to refresh with the real Google OAuth 2.0
        # service.
        google_auth_transport_request_mock = mock.Mock()
        google_auth_transport_request_patch.return_value = google_auth_transport_request_mock

        # Test refreshing using user credentials.
        user_credentials_mock = google.oauth2.credentials.Credentials(token=None, id_token="user_token")
        google_id_token_auth = GoogleIDTokenAuth(credentials=user_credentials_mock)
        google_id_token_auth.refresh()
        user_credentials_refresh_patch.assert_called_once_with(request=google_auth_transport_request_mock)
        user_credentials_refresh_patch.reset_mock()

        # Test refreshing valid user credentials.
        user_credentials_mock = google.oauth2.credentials.Credentials(token="valid_token", id_token="user_token")
        google_id_token_auth = GoogleIDTokenAuth(credentials=user_credentials_mock)
        google_id_token_auth.refresh()
        user_credentials_refresh_patch.assert_not_called()
        user_credentials_refresh_patch.reset_mock()

        # Test refreshing using service account credentials.
        # Mock out service account credentials.
        service_account_credentials_mock = mock.Mock(IDTokenCredentials)
        service_account_credentials_mock.token = "service_account_token"
        service_account_credentials_mock.valid = False

        google_id_token_auth = GoogleIDTokenAuth(credentials=service_account_credentials_mock)
        google_id_token_auth.refresh()
        service_account_credentials_mock.refresh.assert_called_once_with(request=google_auth_transport_request_mock)
        service_account_credentials_mock.refresh.reset_mock()

        # Test that refreshing using anonymous credentials doesn't do anything since you can't refresh anonymous
        # credentials.
        anonymous_credentials = google.auth.credentials.AnonymousCredentials()
        google_id_token_auth = GoogleIDTokenAuth(credentials=anonymous_credentials)
        google_id_token_auth.refresh()

        # Test that we didn't try to refresh anything.
        user_credentials_refresh_patch.assert_not_called()
        service_account_credentials_mock.refresh.assert_not_called()

    @responses.activate
    def test_google_id_token_auth_call(self):
        # Mock a route to hit with the session to check the auth headers.
        responses.add(responses.GET, "https://fake-endpoint.com", json={"message": "Success!"}, status=200)

        # Create a session to add the `GoogleIDTokenAuth` to.
        session = Session()
        session.auth = GoogleIDTokenAuth(
            credentials=google.oauth2.credentials.Credentials(token=None, id_token="user_token")
        )

        response = session.get("https://fake-endpoint.com")

        # Test that the expected auth was added to the request.
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertEqual(request.headers.get("Authorization"), "Bearer user_token")

        # Test that we get back the expected response; note that this isn't the purpose of this test case but it
        # improves test readability.
        self.assertEqual(response.json(), {"message": "Success!"})
        self.assertEqual(response.status_code, 200)

        # Test that using `AnonymousCredentials` doesn't add any authorization headers to the request.
        session = Session()
        session.auth = GoogleIDTokenAuth(credentials=google.auth.credentials.AnonymousCredentials())

        response = session.get("https://fake-endpoint.com")

        # Test that no `Authorization` header was added to the request.
        self.assertEqual(len(responses.calls), 2)
        request = responses.calls[1].request
        self.assertNotIn("Authorization", request.headers)

        # Test that we get back the expected response; note that this isn't the purpose of this test case but it
        # improves test readability.
        self.assertEqual(response.json(), {"message": "Success!"})
        self.assertEqual(response.status_code, 200)
