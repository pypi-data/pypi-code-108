from unittest import mock

import jwt
from django.conf import settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from drf_auth_service.models import Service, ActivationCode, UserBlock
from drf_auth_service.settings import User
from drf_auth_service_tests.test_app.tests.user_permissions import USER_PERMISSIONS


class LoginTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin
):
    fixtures = [
        'test_app/fixtures/init_data.json',
    ]

    def setUp(self) -> None:
        self.service_header = {"HTTP_SERVICE_TOKEN": Service.objects.first().public_token}

    def test_login_refresh_logout(self):
        data_login = {"username": "tester", "password": "test"}
        response = self.client.post(reverse("authentication-login"), data_login, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.check_jwt_payload(response.json()['access'], data_login['username'])
        data_refresh = {"refresh": response.json()['refresh']}
        response = self.client.post(reverse("authentication-refresh"), data_refresh, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.check_jwt_payload(response.json()['access'], data_login['username'])
        response = self.client.get(reverse("authentication-logout"), **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)

    @mock.patch('drf_auth_service.users.permissions.USER_PERMISSIONS', USER_PERMISSIONS)
    def test_jwt_backend(self):
        data_login = {"username": "tester", "password": "test"}
        access_token = jwt.encode({"user_id": 1, "username": "something_wrong"}, settings.SECRET_KEY)
        response = self.client.post(
            reverse("authentication-login"), data_login,
            **{"HTTP_AUTHORIZATION": f"Token {access_token}"}
        )
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], "Service-Token is missing")
        user = User.objects.get(username=data_login['username'])
        token = RefreshToken.for_user(user)
        token['user_id'] = 20
        response = self.client.post(reverse("user-set-password", args=(user.username,)), {}, **{
            "HTTP_AUTHORIZATION": f"Token {str(token.access_token)}", **self.service_header
        })
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], "User not found")
        token = RefreshToken.for_user(user)
        token['user_id'] = user.id
        ActivationCode.objects.create(user=user, key_type=ActivationCode.CodeTypes.CONFIRM_ACCOUNT)
        response = self.client.post(reverse("service-list"), {}, **{
            "HTTP_AUTHORIZATION": f"Token {str(token.access_token)}", **self.service_header
        })
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], "User is not confirmed")
        UserBlock.objects.create(reason='test', user=user)
        response = self.client.post(reverse("user-set-password", args=(user.username,)), {}, **{
            "HTTP_AUTHORIZATION": f"Token {str(token.access_token)}", **self.service_header
        })
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], "User is blocked")

    def test_social(self):
        pass

    def check_jwt_payload(self, jwt_access_token, username):
        jwt_payload = jwt.decode(jwt_access_token, settings.SECRET_KEY)
        self.assertEqual(jwt_payload['username'], username)
