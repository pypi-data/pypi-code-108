import responses
from unittest import TestCase
from responses.matchers import json_params_matcher
from streamduo.client import Client


class TestActor(TestCase):

    @responses.activate
    def test_get_machine_client(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        client_id = "cid_001"
        resp_payload = {"clientId": client_id,
                            "clientDisplayName": "client display name"}

        responses.add(responses.GET, f"{client.api_endpoint}/client/{client_id}",
                      json = resp_payload,
                      status=200)
        actor_controller = client.get_actor_controller()
        assert actor_controller.get_machine_client(client_id).json() == resp_payload

    @responses.activate
    def test_create_machine_client(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        client_display_name = "cdn"
        client_description = "cd"
        resp_payload = {"clientId": "client id",
                            "clientDisplayName": "client display name"}
        responses.add(responses.POST, f"{client.api_endpoint}/client",
                      match=[
                          json_params_matcher(
                              {
                                  'clientDisplayName': client_display_name,
                                   'clientDescription': client_description
                              }
                          )
                      ],
                      json = resp_payload,
                      status=200)
        actor_controller = client.get_actor_controller()
        assert actor_controller.create_machine_client(client_display_name, client_description).json() == resp_payload

    @responses.activate
    def test_delete_machine_client(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        client_id = "cid_001"

        responses.add(responses.DELETE, f"{client.api_endpoint}/client/{client_id}",
                      status=200)
        actor_controller = client.get_actor_controller()
        assert actor_controller.delete_machine_client(client_id).status_code == 200