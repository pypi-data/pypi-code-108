import json
import unittest

from django.contrib.auth.models import User
from django.test import Client, TestCase


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except Exception:
        user = User.objects.create_user(username, password='pass')
        return user


def get_user_pass(username):
    return 'pass'


class EMSWhenIWorkTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def set_user(self, username):
        get_user(username)
        self.client.login(username=username,
                          password=get_user_pass(username))

    def test_serviceorders(self):
        self.set_user('javerage')

        # Issue a GET request.
        response = self.client.get('/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_api_schedule(self):
        # Issue a GET request.
        response = self.client.get(
            '/api/v1/schedule/?StartDate=2016-01-02&EndDate=2016-01-02')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEquals(len(data), 3)
