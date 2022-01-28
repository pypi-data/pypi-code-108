from unittest import mock

import jwt
from django.conf import settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.common.enums import RegisterType
from drf_auth_service.models import Service, ActivationCode
from drf_auth_service.settings import User
from drf_auth_service_tests.test_app.backends import CustomHtmlTemplateBackend, CustomTwilioBackend


class AuthorizationViewTest(
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
        self.secret_header = {"HTTP_SECRET_TOKEN": Service.objects.first().secret_token}

    @mock.patch("drf_auth_service.common.email_backends.HtmlTemplateBackend", CustomHtmlTemplateBackend)
    def test_register_resend_confirmation_and_confirm_type_email(self):
        data = {"username": "john", "password": "secret", "register_type": RegisterType.EMAIL}
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        data.update({"username": "tester@gmail.com"})
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        data.update({"username": "test@test.com"})
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_instance_exists(User, username=data["username"])
        self.check_resend_activation_and_activate(username=data['username'])

    @mock.patch("drf_auth_service.common.sms_backends.TwilioBackend", CustomTwilioBackend)
    def test_register_resend_confirmation_and_confirm_type_phone_number(self):
        data = {"username": "john", "password": "secret", "register_type": RegisterType.PHONE_NUMBER}
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        data.update({"username": "3736107597"})
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        data.update({"username": "37361079597"})
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_instance_exists(User, username=data["username"])
        self.check_resend_activation_and_activate(username=data['username'])

    def test_register_type_nickname(self):
        data = {"username": "john", "password": "secret", "register_type": RegisterType.NICKNAME}
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_instance_exists(User, username=data["username"])

    @mock.patch("drf_auth_service.common.sms_backends.TwilioBackend", CustomTwilioBackend)
    def test_register_type_phone_number_code(self):
        data = {"username": "john", "password": "test", "register_type": RegisterType.PHONE_NUMBER_CODE}
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        data.update({"username": "37361079587"})
        response = self.client.post(reverse("authentication-register"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_instance_exists(User, username=data["username"])

    def check_jwt_payload(self, jwt_access_token, username):
        jwt_payload = jwt.decode(jwt_access_token, settings.SECRET_KEY)
        self.assertEqual(jwt_payload['username'], username)

    def check_resend_activation_and_activate(self, username):
        user = User.objects.get(username=username)
        self.assert_instance_exists(ActivationCode, user=user)
        response = self.client.post(
            reverse("user-resend-confirmation", args=(username,)), **self.service_header, **self.secret_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        activation_code = user.activation_code.first().key
        self.assertFalse(user.is_confirmed)
        response = self.client.post(reverse("user-confirm"), {"token": activation_code}, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue(user.is_confirmed)
        self.check_jwt_payload(response.json()['access'], username)
