import responses
from unittest import TestCase

from streamduo.client import Client, PublicClient
from streamduo.models.read_record_request import ReadRecordRequest
from streamduo.models.record import Record
from streamduo.models.record_request import ReadRecordRequestType


class TestActor(TestCase):

    @responses.activate
    def test_write_record(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        record_controller = client.get_record_controller()
        ## Setup
        stream_id = "streamId001"

        ## Payload
        payload = {
            'Part Description': 'Widget A',
            'Price': 10.00,
            'Inventory': 20000
        }

        ## Response
        resp_record = Record()
        resp_record.recordId = "rec_id123"
        resp_record.dataPayload = payload

        # Mock
        responses.add(responses.POST, f"{client.api_endpoint}/stream/{stream_id}/record",
                      json=resp_record.to_json(),
                      status=200)

        assert record_controller.write_record(stream_id=stream_id, json_payload=payload).status_code == 200
        assert record_controller.write_record(stream_id=stream_id, json_payload=payload).json()['dataPayload'] == payload

    @responses.activate
    def test_read_record(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        record_controller = client.get_record_controller()
        ## Setup
        stream_id = "streamId001"
        record_id = "rec_id123"

        ## Payload
        payload = {
            'Part Description': 'Widget A',
            'Price': 10.00,
            'Inventory': 20000
        }

        ## Response
        resp_record = Record()
        resp_record.recordId = record_id
        resp_record.dataPayload = payload

        # Read Req
        read_request = ReadRecordRequest()
        read_request.readRecordRequestType = ReadRecordRequestType.SINGLE


        # Mock
        responses.add(responses.POST, f"{client.api_endpoint}/stream/{stream_id}/record-request",
                      json=[resp_record.to_json()],
                      status=200)

        assert record_controller.read_record(stream_id=stream_id, record_id=record_id, mark_as_read=True).status_code == 200
        assert record_controller.read_record(stream_id=stream_id, record_id=record_id, mark_as_read=True).json()[0]['dataPayload'] == payload

    @responses.activate
    def test_write_record_public(self):
        client = PublicClient()
        record_controller = client.get_record_controller()
        ## Setup
        stream_id = "streamId001"

        ## Payload
        payload = {
            'Part Description': 'Widget A',
            'Price': 10.00,
            'Inventory': 20000
        }

        ## Response
        resp_record = Record()
        resp_record.recordId = "rec_id123"
        resp_record.dataPayload = payload

        # Mock
        responses.add(responses.POST, f"{client.api_endpoint}/public/stream/{stream_id}/record",
                      json=resp_record.to_json(),
                      status=200)

        assert record_controller.write_record(stream_id=stream_id, json_payload=payload).status_code == 200
        assert record_controller.write_record(stream_id=stream_id, json_payload=payload).json()['dataPayload'] == payload

    @responses.activate
    def test_simple_read_unread_records(self):
        responses.add(responses.POST, Client.auth_endpoint,
                      json={'access_token': "fake-token"}, status=200)
        client = Client("client_id", "client_secret")
        record_controller = client.get_record_controller()
        ## Setup
        stream_id = "streamId001"

        ## Response
        response_list = []
        resp_record = Record()
        resp_record.recordId = "recordID1"
        resp_record.dataPayload = {
            'Part Description': 'Widget A',
            'Price': 10.00,
            'Inventory': 20000
        }
        response_list.append(resp_record)
        resp_record = Record()
        resp_record.recordId = "recordID2"
        resp_record.dataPayload = {
            'Part Description': 'Widget B',
            'Price': 110.00,
            'Inventory': 210000
        }
        response_list.append(resp_record)

        # Mock
        responses.add(responses.GET, f"{client.api_endpoint}/stream/{stream_id}/record/unread",
                      json=[x.to_json() for x in response_list],
                      status=200)

        assert record_controller.simple_read_unread_records(stream_id=stream_id).status_code == 200
        assert record_controller.simple_read_unread_records(stream_id=stream_id).json()[0][
                   'recordId'] == "recordID1"