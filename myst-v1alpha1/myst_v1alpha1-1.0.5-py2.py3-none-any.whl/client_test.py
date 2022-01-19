import unittest

import mock
import responses
from google.auth.credentials import AnonymousCredentials
from requests import Session

from myst_v1alpha1.client import Client
from myst_v1alpha1.exceptions import UnAuthenticatedError


class ClientTest(unittest.TestCase):
    @mock.patch("myst_v1alpha1.client.GoogleIDTokenAuth")
    @mock.patch("myst_v1alpha1.utils.core_utils.get_package_version")
    def test_client(self, get_package_version_patch, google_id_token_auth_patch):
        get_package_version_patch.return_value = "0.0.0"

        # Test without passing credentials to the client.
        client = Client()

        # Test that both credentials and auth should not be set yet.
        self.assertIsNone(client._credentials)
        self.assertIsNone(client._auth)

        # Test that the session was initialized properly.
        self.assertIsInstance(client._session, Session)
        self.assertIsNone(client._session.auth)

        # Note that you'll need to bump this version when releasing a new version of the package!
        self.assertEqual(client._session.headers.get("User-Agent"), "Myst/v1alpha1 PythonBindings/0.0.0")

        # Test that trying to access the session through the `session` property before the client is authenticated
        # raises an exception.
        self.assertRaises(UnAuthenticatedError, getattr, client, "session")

        # Test with passing credentials to the client.
        credentials_mock = mock.Mock()

        # Mock out the `GoogleIDTokenAuth` used to apply authorization headers to requests made by the session.
        google_id_token_auth_mock = mock.Mock()
        google_id_token_auth_patch.return_value = google_id_token_auth_mock
        client = Client(credentials=credentials_mock)

        # Test that both credentials and auth were initialized properly, and that the credentials were refreshed
        # to actually fetch the access token from the Google OAuth 2.0 service.
        self.assertEqual(client._credentials, credentials_mock)
        self.assertEqual(client._auth, google_id_token_auth_mock)
        google_id_token_auth_patch.assert_called_once_with(credentials=credentials_mock)

        # Test that the session was initialized properly with the expected error handlers and auth.
        self.assertIsInstance(client._session, Session)
        self.assertEqual(client._session.auth, google_id_token_auth_mock)

        # Test that we can also now access the session through the `session` property.
        self.assertIsInstance(client.session, Session)

    @mock.patch("myst_v1alpha1.client.GoogleIDTokenAuth")
    def test_authenticate(self, google_id_token_auth_patch):
        # Test that we can also authenticate the client asynchronously using `Client.authenticate`.
        client = Client()

        # Test that both credentials and auth should not be set yet.
        self.assertIsNone(client._credentials)
        self.assertIsNone(client._auth)
        self.assertIsInstance(client._session, Session)
        self.assertIsNone(client._session.auth)

        # Mock out the credentials.
        credentials_mock = mock.Mock()

        # Mock out the `GoogleIDTokenAuth` used to apply authorization headers to requests made by the session.
        google_id_token_auth_mock = mock.Mock()
        google_id_token_auth_patch.return_value = google_id_token_auth_mock

        client.authenticate(credentials=credentials_mock)

        # Test that both credentials and auth were initialized properly, and that the credentials were refreshed
        # to actually fetch the access token from the Google OAuth 2.0 service.
        self.assertEqual(client._credentials, credentials_mock)
        self.assertEqual(client._auth, google_id_token_auth_mock)
        google_id_token_auth_patch.assert_called_once_with(credentials=credentials_mock)

        # Test that auth was added to the session.
        self.assertIsInstance(client._session, Session)
        self.assertEqual(client._session.auth, google_id_token_auth_mock)

    @responses.activate
    def test_get(self):
        # Mock response
        responses.add(responses.GET, "https://mock-endpoint.com", json={"message": "Hello!"})

        client = Client(credentials=AnonymousCredentials())
        json_response = client.get("https://mock-endpoint.com")

        self.assertIsInstance(json_response, dict)
        self.assertEqual(json_response, {"message": "Hello!"})

        # Mock error response
        responses.add(responses.GET, "https://mock-endpoint.com/error", json={"message": "Hello!"}, status=400)

        self.assertRaises(IOError, client.get, "https://mock-endpoint.com/error")
