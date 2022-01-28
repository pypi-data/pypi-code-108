from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.models import Service
from drf_auth_service.settings import User


class BLockUnblockUserTest(
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

    def test_user_block_unblock(self):
        user = User.objects.get(username=self.username)
        self.assertFalse(user.is_blocked)
        data = {"reason": "test"}
        response = self.client.post(
            reverse("user-block", args=(self.username,)), data, **self.service_and_service_header
        )
        self.assert_status_equal(response, status.HTTP_200_OK)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.is_blocked)
        response = self.client.post(reverse(
            "user-unblock", args=(self.username,)), data, **self.service_and_service_header
        )
        self.assert_status_equal(response, status.HTTP_200_OK)
        user = User.objects.get(username=self.username)
        self.assertFalse(user.is_blocked)
