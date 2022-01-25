import requests

from niota import exceptions
from niota.encoder import hexstr_to_str, str_to_hexstr
from niota.models import CreateMessageResp, MessageResp, Payload, PayloadContent, SearchMessageResp


INDEXATION_MESSAGE_TYPE = 2


class IotaClient():
    DEFAULT_BASE_URL = 'https://chrysalis-nodes.iota.org'

    def __init__(self, base_url=None, jwt_token=None):
        self.base_url = base_url if base_url else self.DEFAULT_BASE_URL
        self.headers = {'Authorization': f'Bearer {jwt_token}'} if jwt_token else {}
        self.session = requests.Session()

    def _raise_for_error(self, resp: requests.Response):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if resp.status_code >= 500:
                raise exceptions.NodeInternalServerError(e.response.text) from None
            elif 'missing or malformed jwt' in resp.text:
                raise exceptions.InvalidJWT(e.response.text) from None
            elif 'message not found' in resp.text:
                raise exceptions.MessageNotFound(e.response.text) from None
            raise exceptions.UnknownError(e.response.text)

    def health(self):
        resp = self.session.get(f'{self.base_url}/health', headers=self.headers)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise exceptions.NodeUnhealthy

    def info(self):
        resp = self.session.get(f'{self.base_url}/api/v1/info', headers=self.headers)
        self._raise_for_error(resp)
        return resp.json()

    def create_message(self, index: str, data: str):
        payload = {
            'payload': {
                'type': INDEXATION_MESSAGE_TYPE,
                'index': str_to_hexstr(index),
                'data': str_to_hexstr(data),
            }
        }
        resp = self.session.post(f'{self.base_url}/api/v1/messages', headers=self.headers, json=payload)
        self._raise_for_error(resp)
        return CreateMessageResp(**resp.json())

    def search_message(self, index: str):
        params = {'index': str_to_hexstr(index)}
        resp = self.session.get(f'{self.base_url}/api/v1/messages', headers=self.headers, params=params)
        self._raise_for_error(resp)
        return SearchMessageResp(**resp.json())

    def get_message(self, message_id: str):
        resp = self.session.get(f'{self.base_url}/api/v1/messages/{message_id}', headers=self.headers)
        self._raise_for_error(resp)
        return MessageResp(**resp.json())

    def retrieve_payload_content(self, payload: Payload):
        return PayloadContent(
            index=hexstr_to_str(payload.index),
            data=hexstr_to_str(payload.data),
        )
