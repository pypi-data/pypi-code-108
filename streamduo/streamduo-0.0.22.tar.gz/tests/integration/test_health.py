import os
from unittest import TestCase
from streamduo.client import Client

class TestHealth(TestCase):
    def test_check_health(self):
        health_controller = Client(os.getenv('AUTH_CLIENT_ID'), os.getenv('AUTH_CLIENT_SECRET')).get_health_controller()
        print(health_controller.check_health())
        assert health_controller.check_health().text == 'OK'

