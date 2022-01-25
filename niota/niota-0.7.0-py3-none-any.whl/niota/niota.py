from datetime import datetime
import json
from typing import Dict

from niota import exceptions, signature
from niota.iota_client import IotaClient


class Niota():
    DEFAULT_PROVIDER = 'NUMBERSPROTOCOL'

    def __init__(
        self,
        base_url: str = None,
        jwt_token: str = None,
        private_key: str = None,
        public_key: str = None,
    ):
        self.iota_client = IotaClient(base_url, jwt_token)
        self.private_key = private_key
        self.public_key = public_key

    def create_message(
        self,
        raw_cid: str,
        ida_cid='',
        ida_mid='',
        ida_sha256sum='',
        metadata_cid='',
        provider=DEFAULT_PROVIDER,
        service_message='',
        sign=True,
    ):
        index = raw_cid
        ida_message = {
            'timestamp': self.get_current_timestamp(),
            'raw_cid': raw_cid,
            'ida_cid': ida_cid,
            'ida_mid': ida_mid,
            'ida_sha256sum': ida_sha256sum,
            'metadata_cid': metadata_cid,
            'provider': provider,
            'service_message': service_message,
        }
        serialized_payload = self.create_serialized_payload(ida_message, sign=sign)
        message = self.iota_client.create_message(index, serialized_payload)
        return message.data.messageId, index

    def get_current_timestamp(self):
        return int(datetime.utcnow().timestamp())

    def create_serialized_payload(self, data: Dict, sign=True):
        if sign and not (self.private_key and self.public_key):
            raise exceptions.SignatureKeyPairNotSet('private_key and public_key not set')
        serialized_data = json.dumps(data, sort_keys=True)
        if sign:
            base64_signature = signature.sign_message(self.private_key, serialized_data)
        serialized_payload = json.dumps(
            {
                'data': serialized_data,
                'signature': base64_signature,
            }
        )
        return serialized_payload
