import jwt
from django.conf import settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.models import Service


class SetPasswordTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin
):
    fixtures = [
        'test_app/fixtures/init_data.json',
    ]

    def setUp(self) -> None:
        self.service_and_service_header = {
            "HTTP_SERVICE_TOKEN": Service.objects.first().public_token,
            "HTTP_SECRET_TOKEN": Service.objects.first().secret_token
        }

    def test_set_password_and_login(self):
        data = {"username": "tester", "password": "another_test", "confirm_password": "another_test"}
        response = self.client.post(
            reverse("user-set-password", args=("tester",)), data, **self.service_and_service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(reverse("authentication-login"), data, **self.service_and_service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.check_jwt_payload(response.json()['access'], data['username'])

    def check_jwt_payload(self, jwt_access_token, username):
        jwt_payload = jwt.decode(jwt_access_token, settings.SECRET_KEY)
        self.assertEqual(jwt_payload['username'], username)
