# Deprecated
from datetime import datetime
import json
from typing import Dict

import iota_client

from niota import signature


class IotaClient():
    """Deprecated IotaClient. Use niota.Niota or niota.IotaClient instead.
    """
    MAINNET_NODE_URLS = [['https://chrysalis-nodes.iota.org']]

    def __init__(self, private_key, public_key, index_prefix=''):
        self.private_key = private_key
        self.public_key = public_key
        self.index_prefix = index_prefix
        self.client = iota_client.Client(
            nodes_name_password=self.MAINNET_NODE_URLS,
            node_sync_disabled=True
        )

    def create_message(
        self, raw_cid, ida_cid='', ida_mid='', ida_sha256sum='',
        metadata_cid='', provider='NUMBERSPROTOCOL', service_message=''
    ):
        index = self._create_index(raw_cid)
        ida_message = self._create_ida_message(
            raw_cid=raw_cid,
            ida_cid=ida_cid,
            ida_mid=ida_mid,
            ida_sha256sum=ida_sha256sum,
            metadata_cid=metadata_cid,
            provider=provider,
            service_message=service_message,
        )
        message_id = self._broadcast_message(index, ida_message)
        return message_id, index

    def get_message_data(self, message_id: str):
        message = self.client.get_message_data(message_id)
        data_int_array = message['payload']['indexation'][0]['data']
        data_str = bytearray(data_int_array).decode()
        return data_str

    def get_message_ids_from_index(self, index: str):
        response = self.client.find_messages([index])
        message_ids = [i['message_id'] for i in response]
        return message_ids

    def verify_message_data(self, data_str: str):
        data_with_signature = json.loads(data_str)
        data = data_with_signature['data']
        base64_signature = data_with_signature['signature']
        signature.verify_signature(self.public_key, base64_signature, data, raise_exception=True)

    def _broadcast_message(self, index: str, data: Dict) -> str:
        serialized_data = json.dumps(data, sort_keys=True)
        base64_signature = signature.sign_message(self.private_key, serialized_data)
        serialized_data_with_signature = json.dumps(
            {
                'data': serialized_data,
                'signature': base64_signature,
            }
        )
        message_id_indexation = self.client.message(
            index=index,
            data_str=serialized_data_with_signature
        )
        return message_id_indexation['message_id']

    def _get_current_timestamp(self):
        return int(datetime.now().timestamp())

    def _create_ida_message(self, raw_cid, ida_cid, ida_mid, ida_sha256sum, metadata_cid, provider, service_message):
        timestamp = self._get_current_timestamp()
        ida_message = {
            'timestamp': timestamp,
            'raw_cid': raw_cid,
            'ida_cid': ida_cid,
            'ida_mid': ida_mid,
            'ida_sha256sum': ida_sha256sum,
            'metadata_cid': metadata_cid,
            'provider': provider,
            'service_message': service_message,
        }
        return ida_message

    def _create_index(self, raw_cid):
        return f'{self.index_prefix}{raw_cid}'
