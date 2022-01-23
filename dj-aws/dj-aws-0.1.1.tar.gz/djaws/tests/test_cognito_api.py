import json
from importlib.resources import open_text
from unittest import mock

from botocore.exceptions import ClientError
from django.test import TestCase

from djaws import cognito_api
from djaws.cognito.exceptions import (CognitoUsernameExistsError, CognitoUserPasswordValidationError,
                                    CognitoUserNotAuthorizedError)


class SignupNewUserTests(TestCase):
    """
    Signup New User Tests
    """

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cognito', 'signup_new_user.json') as signup_json:
            cls.r_signup_data = json.loads(signup_json.read())
        cls.signup_new_user = {
            'client_id': 'abcdefghijk',
            'name': 'John Doe',
            'username': 'user123',
            'password': 'password',
            'phone_number': '+15551234567'
        }

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_signup_new_user_200(self, mock_client):
        mock_client.sign_up.return_value = self.r_signup_data

        r_signup = cognito_api.signup_new_user(
            mock_client,
            **self.signup_new_user
        )

        self.assertEquals(r_signup.as_json, cognito_api.SignupNewUserResponse(self.r_signup_data).as_json)

        self.assertEquals(r_signup.code_deliver_details.attribute_name, 'phone_number')
        self.assertEquals(r_signup.code_deliver_details.destination, '+*******7639')
        self.assertEquals(r_signup.code_deliver_details.delivery_medium, 'SMS')

        self.assertEquals(r_signup.user_confirmed, False)

        self.assertEquals(r_signup.user_sub, '215ee8ac-d572-4b23-9327-78896f078f0e')

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_signup_invalid_password_error(self, mock_client):
        mock_client.sign_up.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'InvalidPasswordException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUserPasswordValidationError):
            cognito_api.signup_new_user(
                mock_client,
                **self.signup_new_user
            )

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_signup_not_authorized_error(self, mock_client):
        mock_client.sign_up.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUserNotAuthorizedError):
            cognito_api.signup_new_user(
                mock_client,
                **self.signup_new_user
            )

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_signup_username_exists_error(self, mock_client):
        mock_client.sign_up.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'UsernameExistsException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUsernameExistsError):
            cognito_api.signup_new_user(
                mock_client,
                **self.signup_new_user
            )


class AdminConfirmNewUserTests(TestCase):
    """
    Admin Confirm New User Tests
    """

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cognito', 'admin_confirm_sign_up.json') as admin_confirm_json:
            cls.r_confirm_data = json.loads(admin_confirm_json.read())
        cls.admin_confirm_sign_up = {
            'username': 'user123',
            'user_pool_id': 'test-pool-id-1'
        }

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_ok(self, mock_client):
        mock_client.admin_confirm_sign_up.return_value = self.r_confirm_data

        r_confirm = cognito_api.admin_confirm_sign_up(
            mock_client,
            **self.admin_confirm_sign_up
        )

        self.assertEquals(r_confirm.as_json, cognito_api.AdminConfirmNewUserResponse(self.r_confirm_data).as_json)

        self.assertEquals(r_confirm.response_metadata.request_id, '8551f29a-c72b-44ab-abc8-014247bd0f09')
        self.assertEquals(r_confirm.response_metadata.http_status_code, 200)

        self.assertEquals(r_confirm.response_metadata.http_headers.date, 'Sat, 16 Oct 2021 04:49:22 GMT')
        self.assertEquals(r_confirm.response_metadata.http_headers.content_type, 'application/x-amz-json-1.1')
        self.assertEquals(r_confirm.response_metadata.http_headers.content_length, '2')
        self.assertEquals(r_confirm.response_metadata.http_headers.connection, 'keep-alive')
        self.assertEquals(
            r_confirm.response_metadata.http_headers.x_amzn_requestid,
            '8551f29a-c72b-44ab-abc8-014247bd0f09'
        )

        self.assertEquals(r_confirm.response_metadata.retry_attempts, 0)

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_admin_confirm_sign_up_invalid_password_error(self, mock_client):
        mock_client.admin_confirm_sign_up.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'InvalidPasswordException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUserPasswordValidationError):
            cognito_api.admin_confirm_sign_up(
                mock_client,
                **self.admin_confirm_sign_up
            )


class LoginTests(TestCase):
    """
    Login Tests
    """

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cognito', 'initiate_auth.json') as initiate_auth_json:
            cls.r_login_data = json.loads(initiate_auth_json.read())
        cls.login = {
            'user_pool_client_id': 'test-pool-client-id-1',
            'username': 'user123',
            'password': 'password',
        }

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_login_200(self, mock_client):
        mock_client.initiate_auth.return_value = self.r_login_data

        r_login = cognito_api.login(
            mock_client,
            **self.login
        )

        self.assertEquals(r_login.as_json, cognito_api.InitAuthResponse(self.r_login_data).as_json)
        self.assertEquals(r_login.user_id, 'ef6b26e0-7868-4941-818a-816eb9ad8c6c')
        self.assertTrue(r_login.is_admin_user)

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_login_not_authorized_error(self, mock_client):
        mock_client.initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUserNotAuthorizedError):
            cognito_api.login(
                mock_client,
                **self.login
            )


class AdminLoginTests(TestCase):
    """
    Admin Login Tests
    """

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cognito', 'initiate_auth.json') as initiate_auth_json:
            cls.r_admin_login_data = json.loads(initiate_auth_json.read())
        cls.admin_login = {
            'user_pool_client_id': 'test-pool-client-id-1',
            'user_pool_id': 'test-pool-id-1',
            'username': 'user123',
            'password': 'password',
        }

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_admin_login_200(self, mock_client):
        mock_client.admin_initiate_auth.return_value = self.r_admin_login_data

        r_login = cognito_api.admin_login(
            mock_client,
            **self.admin_login
        )

        self.assertEquals(r_login.as_json, cognito_api.InitAuthResponse(self.r_admin_login_data).as_json)
        self.assertEquals(r_login.user_id, 'ef6b26e0-7868-4941-818a-816eb9ad8c6c')
        self.assertTrue(r_login.is_admin_user)

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_CognitoUserNotAuthorizedError(self, mock_client):
        mock_client.admin_initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'get_parameter'
        )

        with self.assertRaises(CognitoUserNotAuthorizedError):
            cognito_api.admin_login(
                mock_client,
                **self.admin_login
            )


class AdminRefreshAccessToken(TestCase):
    """
    Admin Refresh Access Token Tests
    """

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cognito', 'initiate_auth.json') as initiate_auth_json:
            cls.r_admin_refresh_access_token_data = json.loads(initiate_auth_json.read())
        cls.admin_refresh_access_token = {
            'user_pool_client_id': 'test-pool-client-id-1',
            'user_pool_id': 'test-pool-id-1',
            'refresh_token': 'refresh-token-1',
        }

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_ok(self, mock_client):
        mock_client.admin_initiate_auth.return_value = self.r_admin_refresh_access_token_data

        r_admin_refresh_access_token = cognito_api.admin_refresh_access_token(
            mock_client,
            **self.admin_refresh_access_token
        )

        self.assertEquals(
            r_admin_refresh_access_token.as_json,
            cognito_api.InitAuthResponse(self.r_admin_refresh_access_token_data).as_json
        )
        self.assertEquals(r_admin_refresh_access_token.user_id, 'ef6b26e0-7868-4941-818a-816eb9ad8c6c')
        self.assertTrue(r_admin_refresh_access_token.is_admin_user)

    @mock.patch.object(cognito_api, 'new_cognito_client')
    def test_CognitoUserNotAuthorizedError(self, mock_client):
        mock_client.admin_initiate_auth.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'admin_initiate_auth'
        )

        with self.assertRaises(CognitoUserNotAuthorizedError):
            cognito_api.admin_refresh_access_token(
                mock_client,
                **self.admin_refresh_access_token
            )
