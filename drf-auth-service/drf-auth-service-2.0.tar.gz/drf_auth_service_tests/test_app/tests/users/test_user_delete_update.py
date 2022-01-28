from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.models import Service


class UpdateDeleteUserTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin
):
    fixtures = [
        'test_app/fixtures/init_data.json',
    ]

    def setUp(self) -> None:
        self.username = 'tester'
        self.service_and_service_header = {
            "HTTP_SERVICE_TOKEN": Service.objects.first().public_token,
            "HTTP_SECRET_TOKEN": Service.objects.first().secret_token
        }

    def test_user_delete_update(self):
        response = self.client.put(
            reverse("user-detail", args=(self.username,)), {"username": "test"}, **self.service_and_service_header
        )
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.delete(reverse("user-detail", args=("test",)), **self.service_and_service_header)
        self.assert_status_equal(response, status.HTTP_200_OK)
