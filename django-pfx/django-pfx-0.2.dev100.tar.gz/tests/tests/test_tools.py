from datetime import date
from unittest.mock import patch

from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin, print_response
from tests.models import Author


class TestTools(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        pass

    @patch('builtins.print')
    def test_key_error(self, mock_print):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@0.name-not-exists', 'not exists')

    @patch('builtins.print')
    def test_index_error(self, mock_print):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@99.name', 'gender')

    @patch('builtins.print')
    def test_print_response(self, mock_print):
        response = self.client.get(f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 200)
        print_response(response)

        mock_print.assert_any_call(
            '\n\n*********************http response*********************')
        mock_print.assert_any_call('Status : ', 200, 'OK')
        mock_print.assert_any_call('Headers : ')
        mock_print.assert_any_call("""  Content-Type: application/json
  Content-Length: %s
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en
""" % (response.headers['Content-Length']))
        mock_print.assert_any_call('Content : ')
        mock_print.assert_any_call("""{
    "books": [],
    "created_at": "%s",
    "first_name": "John Ronald Reuel",
    "gender": {
        "label": "Male",
        "value": "male"
    },
    "last_name": "Tolkien",
    "meta": {},
    "name_length": 25,
    "pk": %i,
    "resource_name": "John Ronald Reuel Tolkien",
    "slug": "jrr-tolkien"
}""" % (date.today(), self.author1.pk))
        mock_print.assert_any_call(
            '*******************************************************\n\n')
