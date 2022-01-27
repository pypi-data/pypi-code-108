# Copyright (c) Qotto, 2021

import json
from datetime import datetime
from typing import Union, Any, Dict

from eventy.record import Record, Event, Request, Response
from eventy.record.record import RecordType
from eventy.serialization import RecordSerializer
from eventy.serialization.errors import SerializationError, UnknownRecordTypeError


class JsonSerializer(RecordSerializer):

    def encode(self, record: Record) -> bytes:
        record_dict: Dict[str, Any] = {
            'type': record.type.value,
            'namespace': record.namespace,
            'name': record.name,
            'protocol_version': record.protocol_version,
            'version': record.version,
            'source': record.source,
            'uuid': record.uuid,
            'correlation_id': record.correlation_id,
            'partition_key': record.partition_key,
            'date_timestamp': int(record.date.timestamp() * 1000),
            'date_iso8601': record.date.isoformat(),
        }
        if isinstance(record, Response):
            record_dict.update(
                {
                    'destination': record.destination,
                    'request_uuid': record.request_uuid,
                    'ok': record.ok,
                    'error_code': record.error_code,
                    'error_message': record.error_message,
                }
            )
        record_dict.update(
            {
                'context': record.context,
                'data': record.data
            }
        )
        return json.dumps(record_dict).encode('utf-8')

    def decode(self, encoded: bytes) -> Union[Event, Request, Response]:
        try:
            record_dict = json.loads(encoded)
            record_type = RecordType(record_dict.pop('type'))
            date = datetime.fromisoformat(record_dict.pop('date_iso8601'))
            record_dict.pop('date_timestamp')
            record_dict['date'] = date
            record: Union[Event, Request, Response]
            if record_type == RecordType.EVENT:
                return Event(**record_dict)
            elif record_type == RecordType.REQUEST:
                return Request(**record_dict)
            elif record_type == RecordType.RESPONSE:
                return Response(**record_dict)
            else:
                raise UnknownRecordTypeError(f"Type {record_type}.")
        except Exception as e:
            raise SerializationError from e
