from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.test import APIClient, TestAssertMixin


class BasicAPIErrorTest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        pass

    @override_settings(DEBUG=False)
    def test_resource_not_found(self):
        response = self.client.get('/api/error/404')
        self.assertRC(response, 404)

    @override_settings(DEBUG=False)
    @patch('builtins.print')
    def test_error500(self, mock_print):
        response = self.client.get('/api/error/500')
        self.assertRC(response, 500)
