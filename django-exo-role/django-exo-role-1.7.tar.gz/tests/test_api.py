from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from exo_role.models import ExORole, CertificationRole, Category


class TestAPITestCase(APITestCase):

    def test_api_roles_list(self):
        # PREPARE DATA
        url = reverse('exo-role:roles-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()), ExORole.objects.count())

    def test_api_roles_certification_list(self):
        # PREPARE DATA
        url = reverse('exo-role:certifications-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()), CertificationRole.objects.count())

    def test_api_categories_list(self):
        # PREPARE DATA
        url = reverse('exo-role:category-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()), Category.objects.count())
