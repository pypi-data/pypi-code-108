from unittest import mock

from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.models import Service, SSOUser
from drf_auth_service_tests.test_app.backends import CustomHtmlTemplateBackend, CustomTwilioBackend


class ResetPasswordTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin
):
    fixtures = [
        'test_app/fixtures/init_data.json',
    ]

    def setUp(self) -> None:
        self.password_raw = 'testovici'
        self.service_header = {"HTTP_SERVICE_TOKEN": Service.objects.first().public_token}

    @mock.patch("drf_auth_service.common.email_backends.HtmlTemplateBackend", CustomHtmlTemplateBackend)
    def test_send_reset_password_email(self):
        self.check_reset_password("tester@gmail.com")
        self.confirm_reset_password("tester@gmail.com")

    @mock.patch("drf_auth_service.common.sms_backends.TwilioBackend", CustomTwilioBackend)
    def test_send_reset_password_phone_number(self):
        self.check_reset_password("37361111111")
        self.confirm_reset_password("37361111111")

    @mock.patch("drf_auth_service.common.sms_backends.TwilioBackend", CustomTwilioBackend)
    def test_send_reset_password_phone_number_code(self):
        self.check_reset_password("37361111112")
        self.confirm_reset_password("37361111112")

    def check_reset_password(self, username):
        data = {"username": username}
        response = self.client.post(reverse("authentication-reset-password"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def confirm_reset_password(self, username):
        token = SSOUser.objects.get(username=username).activation_code.first().key
        data = {
            "username": username,
            "password": self.password_raw,
            "confirm_password": self.password_raw,
            "token": token
        }
        response = self.client.post(reverse("authentication-reset-password-confirm"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(reverse("authentication-login"), data, **self.service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)

