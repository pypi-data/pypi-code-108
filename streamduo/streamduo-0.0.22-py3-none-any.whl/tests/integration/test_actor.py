import os
from unittest import TestCase

from streamduo.client import Client


class TestActor(TestCase):

    def test_create_machine_client(self):

        actor_controller = Client(os.getenv('AUTH_CLIENT_ID'), os.getenv('AUTH_CLIENT_SECRET')).get_actor_controller()

        create_actor_response = actor_controller.create_machine_client("client display name test",
                                                                       "client description test")
        new_client_id = create_actor_response.json()['clientId']
        assert new_client_id is not None

        ## cleanup
        delete_response = actor_controller.delete_machine_client(new_client_id)
        assert delete_response.status_code == 200

        ## check get
        get_response = actor_controller.get_machine_client(new_client_id)
        assert get_response.status_code == 404

    def test_list_machine_client(self):

        actor_controller = Client(os.getenv('AUTH_CLIENT_ID'), os.getenv('AUTH_CLIENT_SECRET')).get_actor_controller()
        #clear out list
        client_list = actor_controller.get_clients()
        for client in client_list.json():
            print(client['clientId'])
            actor_controller.delete_machine_client(client['clientId'])
        client_list_new = actor_controller.get_clients()
        assert len(client_list_new.json()) == 0

        #create new client
        create_actor_response = actor_controller.create_machine_client("client display name test",
                                                                      "client description test")
        new_client_id = create_actor_response.json()['clientId']

        #get client list
        client_list = actor_controller.get_clients()

        new_client_found = False
        for client in client_list.json():
            if client['clientId'] == new_client_id:
                new_client_found = True
                break
        assert new_client_found == True

        ##cleanup
        actor_controller.delete_machine_client(new_client_id)

        client_list_new = actor_controller.get_clients()
        assert len(client_list_new.json()) == 0

    def test_delete_machine_client(self):
        # create stream
        display_name = 'test_stream'
        stream_controller = Client(os.getenv('AUTH_CLIENT_ID'), os.getenv('AUTH_CLIENT_SECRET')).get_stream_controller()
        new_stream_id = stream_controller.create_stream(display_name).json()['streamId']
        # create client on stream
        client_display_name = 'test_client'
        add_client_response = stream_controller.add_new_machine_client_to_stream(new_stream_id, client_display_name)
        ##get new client ID
        new_client_id = None
        for i in add_client_response.json()['streamActorPermissionRecords']:
            if i['actorDisplayName'] == client_display_name:
                new_client_id = i['actorId']
                break
        # delete client
        actor_controller = Client(os.getenv('AUTH_CLIENT_ID'), os.getenv('AUTH_CLIENT_SECRET')).get_actor_controller()
        actor_controller.delete_machine_client(new_client_id)
        # confirm client is null & perm not on stream anymore
        stream_response = stream_controller.get_stream(stream_id=new_stream_id)
        new_client_id = None
        for i in stream_response.json()['streamActorPermissionRecords']:
            if i['actorDisplayName'] == client_display_name:
                new_client_id = i['actorId']
                break
        assert new_client_id is None


        # cleanup
        stream_controller.delete_stream(new_stream_id)
        assert actor_controller.get_machine_client(new_client_id).status_code == 404
