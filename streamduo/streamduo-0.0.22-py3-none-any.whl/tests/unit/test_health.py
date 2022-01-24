import responses
from unittest import TestCase

from streamduo.client import Client


class TestHealth(TestCase):

    @responses.activate
    def test_check_health(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        responses.add(responses.GET, f"{client.api_endpoint}/health",
                      body="OK", status=200)
        health_controller = client.get_health_controller()
        print(health_controller.check_health())
        assert health_controller.check_health().text == 'OK'
