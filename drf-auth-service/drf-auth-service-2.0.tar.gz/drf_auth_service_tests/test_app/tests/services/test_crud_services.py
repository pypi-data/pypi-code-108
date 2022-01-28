from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from drf_auth_service.models import Service


class ServiceTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin
):
    fixtures = [
        'test_app/fixtures/init_data.json',
    ]

    def test_service_crud(self):
        response = self.client.post(reverse("service-list"), {"name": "test"})
        service_id = response.json()['id']
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Service, name="test")
        response = self.client.get(reverse("service-detail", args=(service_id,)))
        self.assertEqual(response.json()['name'], 'test')
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.patch(reverse("service-detail", args=(1,)), {"name": "another_test"})
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue(Service.objects.filter(name='another_test').exists())
        response = self.client.get(reverse("service-configs", args=(1,)))
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.patch(reverse("service-configs", args=(1,)), {"send_confirmation": True})
        self.assertTrue(response.json()["send_confirmation"])
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.delete(reverse("service-detail", args=(1,)))
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Service.objects.filter(name='another_test').exists())

