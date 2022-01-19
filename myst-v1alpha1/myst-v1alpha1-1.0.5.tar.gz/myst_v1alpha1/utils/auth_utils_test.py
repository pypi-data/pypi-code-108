import json
import os
import tempfile
import unittest

import google.oauth2.credentials
import mock
from google.oauth2.service_account import IDTokenCredentials

import myst_v1alpha1
from myst_v1alpha1 import UserCredentialsCache
from myst_v1alpha1.utils.auth_utils import create_bearer_authorization_header
from myst_v1alpha1.utils.auth_utils import get_credentials
from myst_v1alpha1.utils.auth_utils import get_service_account_credentials
from myst_v1alpha1.utils.auth_utils import get_user_credentials


class AuthUtilsTest(unittest.TestCase):
    def test_create_bearer_authorization_header(self):
        self.assertEqual(create_bearer_authorization_header(token="token"), {"Authorization": "Bearer token"})

    @mock.patch("myst_v1alpha1.utils.auth_utils.IDTokenCredentials")
    def test_get_credentials_from_service_account_key_file(self, id_token_credentials_patch):
        id_token_credentials_patch.from_service_account_file.return_value = mock.Mock(IDTokenCredentials)

        credentials = get_service_account_credentials(service_account_key_file_path="/path/to/first/key/file.json")

        # Test that the expected credentials object was created.
        self.assertIsInstance(credentials, IDTokenCredentials)

        # Test that the service account credentials was created with the expected argumnets.
        id_token_credentials_patch.from_service_account_file.assert_called_once_with(
            filename="/path/to/first/key/file.json", target_audience="https://api.myst.ai"
        )
        id_token_credentials_patch.from_service_account_file.reset_mock()

        # Test that we can get credentials when getting the service account key file path from the environment.
        with mock.patch.dict("os.environ", dict(MYST_APPLICATION_CREDENTIALS="/path/to/second/key/file.json")):
            credentials = get_service_account_credentials()

        # Test that the expected credentials object was created.
        self.assertIsInstance(credentials, IDTokenCredentials)

        # Test that the service account credentials was created with the expected arguments.
        id_token_credentials_patch.from_service_account_file.assert_called_once_with(
            filename="/path/to/second/key/file.json", target_audience="https://api.myst.ai"
        )
        id_token_credentials_patch.from_service_account_file.reset_mock()

        # Test that an exception is raised if we don't pass an explicit service account key file or define it in the
        # environment.
        self.assertRaises(ValueError, get_service_account_credentials)

    @mock.patch("myst_v1alpha1.user_credentials_cache.get_local_app_config_path")
    @mock.patch("myst_v1alpha1.utils.auth_utils.get_pkg_resource_path")
    @mock.patch("myst_v1alpha1.utils.auth_utils.InstalledAppFlow.from_client_secrets_file")
    def test_get_credentials_from_user(
        self, from_client_secrets_file_patch, get_pkg_resource_path_patch, get_local_app_config_path_patch
    ):
        # Mock out our package resource path helper so we don't actually grab the real client secret.
        get_pkg_resource_path_patch.return_value = "/path/to/google_oauth_client_not_so_secret.json"

        # Mock out Google OAuth 2.0 objects so we don't actually try to authenticate with the real service.
        local_server_credentials_mock = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token="mock_refresh_token_local_server",
            id_token="mock_id_token",
            token_uri="mock_token_uri",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            scopes=["mock_scope"],
        )

        console_credentials_mock = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token="mock_refresh_token_console",
            id_token="mock_id_token",
            token_uri="mock_token_uri",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            scopes=["mock_scope"],
        )
        installed_app_flow_mock = mock.Mock()
        from_client_secrets_file_patch.return_value = installed_app_flow_mock
        installed_app_flow_mock.run_local_server.return_value = local_server_credentials_mock
        installed_app_flow_mock.run_console.return_value = console_credentials_mock

        # Mock out the user credentials cache path so we don't read or write to the real cache.
        tempfile_path = tempfile.mktemp()
        get_local_app_config_path_patch.return_value = tempfile_path

        # Test with using web flow (local server).
        credentials = get_user_credentials(use_console=False, read_from_cache=False, write_to_cache=False)
        self.assertEqual(credentials, local_server_credentials_mock)

        from_client_secrets_file_patch.assert_called_with(
            client_secrets_file="/path/to/google_oauth_client_not_so_secret.json",
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        )
        installed_app_flow_mock.run_local_server.assert_called_once_with()

        # Reset mocks for next test.
        from_client_secrets_file_patch.reset_mock()
        installed_app_flow_mock.run_local_server.reset_mock()

        # Test with using console.
        credentials = get_user_credentials(use_console=True, read_from_cache=False, write_to_cache=False)
        self.assertEqual(credentials, console_credentials_mock)

        from_client_secrets_file_patch.assert_called_once_with(
            client_secrets_file="/path/to/google_oauth_client_not_so_secret.json",
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        )
        installed_app_flow_mock.run_console.assert_called_once_with()

        # Reset mocks for next test.
        from_client_secrets_file_patch.reset_mock()

        # Test that we kick off the Google OAuth 2.0 flow when we don't have any user credentials cached yet.
        credentials = get_user_credentials(read_from_cache=True, write_to_cache=True)
        self.assertEqual(credentials, local_server_credentials_mock)

        from_client_secrets_file_patch.assert_called_once_with(
            client_secrets_file="/path/to/google_oauth_client_not_so_secret.json",
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        )
        installed_app_flow_mock.run_local_server.assert_called_once_with()

        # Reset mocks for next test.
        from_client_secrets_file_patch.reset_mock()
        installed_app_flow_mock.run_local_server.reset_mock()

        # Test that the next time we go to get credentials from user, we grab the ones from the cache and don't kick off
        # the Google OAuth 2.0 flow. Note that since `write_to_cache` was `True` in the last call to
        # `get_user_credentials`, we also saved the user credentials to the cache.
        credentials = get_user_credentials(read_from_cache=True, write_to_cache=True)

        # Test that the credentials isn't the exact object returned by the Google OAuth 2.0 flow. But note that its
        # attributes will be the same since we cached a copy of that one with the previous test.
        self.assertIsNot(credentials, local_server_credentials_mock)

        # Test that the user credentials was loaded from the cache as expected.
        self.assertIsInstance(credentials, google.oauth2.credentials.Credentials)
        self.assertEqual(credentials.refresh_token, "mock_refresh_token_local_server")
        self.assertEqual(credentials.id_token, "mock_id_token")
        self.assertEqual(credentials.token_uri, "mock_token_uri")
        self.assertEqual(credentials.client_id, "mock_client_id")
        self.assertEqual(credentials.client_secret, "mock_client_secret")
        self.assertEqual(credentials.scopes, ["mock_scope"])

        # Test that we didn't initialize or kick of the Google OAuth 2.0 flow.
        self.assertFalse(from_client_secrets_file_patch.called)
        self.assertFalse(installed_app_flow_mock.run_local_server.called)

    @mock.patch("myst_v1alpha1.utils.auth_utils.get_service_account_credentials")
    @mock.patch("myst_v1alpha1.utils.auth_utils.get_user_credentials")
    def test_get_credentials(
        self, get_credentials_from_user_patch, get_credentials_from_service_account_key_file_patch
    ):
        # Mock user credentials.
        user_credentials_mock = mock.Mock()
        get_credentials_from_user_patch.return_value = user_credentials_mock

        # Mock service account credentials.
        service_account_credentials_mock = mock.Mock()
        get_credentials_from_service_account_key_file_patch.return_value = service_account_credentials_mock

        # Test getting user credentials using the web flow.
        credentials = get_credentials(use_service_account=False)
        self.assertEqual(credentials, user_credentials_mock)
        get_credentials_from_user_patch.assert_called_once_with(
            use_console=False, read_from_cache=True, write_to_cache=True
        )
        get_credentials_from_user_patch.reset_mock()

        # Test getting user credentials using the console flow.
        credentials = get_credentials(use_service_account=False, use_console=True)
        self.assertEqual(credentials, user_credentials_mock)
        get_credentials_from_user_patch.assert_called_once_with(
            use_console=True, read_from_cache=True, write_to_cache=True
        )
        get_credentials_from_user_patch.reset_mock()

        # Test getting service account credentials without passing an explicit service account key file path.
        credentials = get_credentials(use_service_account=True)
        self.assertEqual(credentials, service_account_credentials_mock)
        get_credentials_from_service_account_key_file_patch.assert_called_once_with(service_account_key_file_path=None)
        get_credentials_from_service_account_key_file_patch.reset_mock()

        # Test getting service account credentials passing an explicit service account key file path.
        credentials = get_credentials(use_service_account=True, service_account_key_file_path="/path/to/key/file.json")
        self.assertEqual(credentials, service_account_credentials_mock)
        get_credentials_from_service_account_key_file_patch.assert_called_once_with(
            service_account_key_file_path="/path/to/key/file.json"
        )
        get_credentials_from_service_account_key_file_patch.reset_mock()

        # Test argument validation.
        for use_service_account, use_console, service_account_key_file_path in [
            # Both `use_service_account` and `use_console` cannot be specified.
            (True, True, None),
            # If `service_account_key_file_path` is specified, `use_console` shouldn't be specified
            (False, True, "/path/to/key/file.json"),
        ]:
            with self.assertRaises(ValueError):
                get_credentials(
                    use_service_account=use_service_account,
                    use_console=use_console,
                    service_account_key_file_path=service_account_key_file_path,
                )

    @mock.patch("myst_v1alpha1.user_credentials_cache.get_local_app_config_path")
    def test_clear_user_credentials_cache(self, get_local_app_config_path_patch):
        # Note that we're testing `clear_user_credentials_cache` through the `myst` package top-level function,
        # `myst_v1alpha1.clear_user_credentials_cache` to test that that function is imported and works as expected.

        # Mock out the user credentials cache path so we don't read or write to the real cache.
        tempfile_path = tempfile.mktemp()
        get_local_app_config_path_patch.return_value = tempfile_path

        # Write some dummy credentials to the default user credentials cache.
        user_credentials_mock = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token="mock_refresh_token_local_server",
            id_token="mock_id_token",
            token_uri="mock_token_uri",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            scopes=["mock_scope"],
        )
        user_credentials_cache = UserCredentialsCache()
        user_credentials_cache.save(user_credentials_mock)

        # Test that those credentials were written; this isn't necessary for the test but makes the test more readable.
        with open(tempfile_path, "r") as user_credentials_file:
            self.assertEqual(
                json.load(user_credentials_file),
                {
                    "client_id": "mock_client_id",
                    "client_secret": "mock_client_secret",
                    "id_token": "mock_id_token",
                    "refresh_token": "mock_refresh_token_local_server",
                    "scopes": ["mock_scope"],
                    "token_uri": "mock_token_uri",
                },
            )

        myst_v1alpha1.clear_user_credentials_cache()

        # Test that the user credentials were cleared.
        self.assertFalse(os.path.exists(tempfile_path))

    @mock.patch("myst_v1alpha1.utils.auth_utils.get_credentials")
    def test_authenticate(self, get_credentials_patch):
        # Note that we're testing `authenticate` through the `myst` package top-level function `myst_v1alpha1.authenticate` to
        # test that that function is imported and works as expected.

        # Mock credentials.
        credentials_mock = mock.Mock()
        get_credentials_patch.return_value = credentials_mock

        other_credentials_mock = mock.Mock()

        # Test that by default we authenticate the client using user credentials (`use_service_account` is `False`).
        myst_v1alpha1.authenticate()

        self.assertEqual(myst_v1alpha1.get_client()._credentials, credentials_mock)
        get_credentials_patch.assert_called_once_with(
            service_account_key_file_path=None, use_console=False, use_service_account=False
        )
        get_credentials_patch.reset_mock()

        # Test that we can also pass through custom credentials.
        myst_v1alpha1.authenticate(credentials=other_credentials_mock)

        self.assertEqual(myst_v1alpha1.get_client()._credentials, other_credentials_mock)
        get_credentials_patch.assert_not_called()
        get_credentials_patch.reset_mock()

        # Test that we just pass through various combinations of arguments to `get_credentials`.
        for kwargs, expected_credentials in [
            (dict(use_service_account=False, use_console=True, service_account_key_file_path=None), credentials_mock),
            (dict(use_service_account=True, use_console=False, service_account_key_file_path=None), credentials_mock),
            (
                dict(
                    use_service_account=False, use_console=False, service_account_key_file_path="/path/to/key/file.json"
                ),
                credentials_mock,
            ),
            (
                dict(
                    use_service_account=False, use_console=False, service_account_key_file_path="/path/to/key/file.json"
                ),
                credentials_mock,
            ),
        ]:
            myst_v1alpha1.authenticate(**kwargs)

            # Test that we've authenticated the client with the expected credentials.
            self.assertEqual(myst_v1alpha1.get_client()._credentials, expected_credentials)

            # Test that we've called `get_credentials` with the expected arguments.
            get_credentials_patch.assert_called_once_with(**kwargs)
            get_credentials_patch.reset_mock()
