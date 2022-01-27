# Copyright (c) Qotto, 2021
import json
import logging
import os
from datetime import datetime, timezone
from io import BytesIO
from typing import Union, Dict, Any, Optional, Iterator

import avro.schema
import semver
import yaml
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, AvroTypeException, DatumReader
from avro.schema import RecordSchema
from semver import VersionInfo

from eventy.record import Record, Event, Request, Response
from eventy.record.record import RecordType
from eventy.serialization import RecordSerializer
from eventy.serialization.errors import SerializationError, UnknownRecordTypeError

__all__ = [
    'AvroSerializer',
    'AvroDecodeError',
]

logger = logging.getLogger(__name__)


class AvroDecodeError(SerializationError):
    def __init__(self, decoded_data: dict) -> None:
        super().__init__(f"Failed to decode Record. Data decoded so far is: {decoded_data}")
        self.decoded_data = decoded_data


class AvroSerializer(RecordSerializer):
    """
    Avro serializer, encode and decode records in avro format.
    """

    def __init__(
        self,
    ):
        """
        Instantiate a serializer.
        """
        self.avro_schemas = {}

    def load_schemas_folder(
        self,
        schemas_folder: str, schemas_ext='.evsc.yaml', recursive=True
    ) -> None:
        """
        Parse all EVenty SChemas and register them to this AvroSerializer.
        """
        for schema_data in _load_schema_files(schemas_folder, schemas_ext, recursive):
            self.register_schema(schema_data)

    def register_schema(
        self,
        schema_data: Dict
    ) -> None:
        """
        Register an EVenty SChema so this AvroSerializer can encode eventy Records.

        :param schema_data:
        :return:
        """
        try:
            protocol_version = VersionInfo.parse(schema_data.pop('protocol_version'))
        except Exception:
            raise ValueError(f'Malformed schema_data, cannot parse protocol_version: {schema_data}.')

        try:
            namespace = schema_data.get('namespace')
            name = schema_data.get('name')
            qualified_name = f'{namespace}:{name}'
        except Exception:
            raise ValueError(f'Field namespace or name is missing: {schema_data}.')
        if qualified_name in self.avro_schemas:
            raise ValueError(f'Schema {qualified_name} already registered.')

        if protocol_version.match('>=3.0.0') and protocol_version.match('<4.0.0'):
            avro_schema = _gen_avro_schema_v3(**schema_data)
        else:
            raise ValueError(f'Cannot parse {qualified_name}, cannot handle protocol_version {protocol_version}.')

        logger.debug(f"Added avro schema for {qualified_name}.")
        self.avro_schemas[qualified_name] = avro_schema

    def encode(self, record: Record) -> bytes:
        """
        Encode an eventy Record as an avro record, with avro schema.

        :param record: An eventy Record
        :return: Encoded avro record
        """
        avro_schema = self.avro_schemas.get(record.qualified_name)
        if not avro_schema:
            raise SerializationError(f"Could not find avro schema for record {record.qualified_name}.")

        record_dict: Dict[str, Any] = {
            'record_namespace': record.namespace,
            'record_name': record.name,
            'type': record.type.value,
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

        try:
            bytes_io = BytesIO()
            with DataFileWriter(bytes_io, DatumWriter(), avro_schema) as writer:
                writer.append(record_dict)
                writer.flush()
                output_bytes = bytes_io.getvalue()
            return output_bytes
        except AvroTypeException as avro_exception:
            raise SerializationError(avro_exception)

    def decode(self, encoded: bytes) -> Union[Event, Request, Response]:
        """
        Decode avro record as an eventy Record.

        Convert record encoded with protocol_version <= 3.*.*.

        :param encoded: Encoded bytes
        :return: An eventy Record
        """
        try:
            reader = DataFileReader(BytesIO(encoded), DatumReader())
            avro_schema_data = json.loads(reader.meta.get('avro.schema').decode('utf-8'))
            avro_record_data = next(reader)
        except Exception as e:
            raise SerializationError from e

        try:
            protocol_version = VersionInfo.parse(avro_record_data.get('protocol_version'))
        except Exception:
            logger.info(f"There was no protocol_version in record {avro_schema_data.get('name')}, assuming 1.0.0.")
            protocol_version = semver.VersionInfo(1)

        if protocol_version.match('<3.0.0'):
            return _decode_avro_record_legacy(avro_schema_data, avro_record_data)
        elif protocol_version.match('<4.0.0'):
            return _decode_avro_record_v3(avro_schema_data, avro_record_data)
        else:
            raise ValueError(f"Cannot handle protocol_version {protocol_version}.")

    @classmethod
    def from_schemas_folder(
        cls,
        schemas_folder: str, schemas_ext='.evsc.yaml', recursive=True
    ) -> 'AvroSerializer':
        serializer = AvroSerializer()
        serializer.load_schemas_folder(schemas_folder, schemas_ext, recursive)
        return serializer


def _decode_avro_record_legacy(
    avro_schema_data: Dict[str, str],
    avro_record_data: Dict
) -> Union[Event, Request, Response]:
    """
    Convert any avro record to a 3.0.0 compatible eventy Record.

    :param avro_schema_data: Schema data associated with avro record
    :param avro_record_data: Record data in avro record
    :return: Eventy Record
    """
    # record data for eventy Record constructor
    record_data = dict()

    try:
        # get record type
        record_type = RecordType(avro_record_data.pop('type', 'EVENT'))

        # get mandatory data
        record_data['protocol_version'] = avro_record_data.pop('protocol_version', '1.0.0')

        name = avro_schema_data.get('name') or 'Unspecified'
        record_data['name'] = name

        namespace = avro_schema_data.get('namespace') or 'urn:unspecified'
        namespace = namespace.replace('.', ':')
        if not namespace.startswith('urn:'):
            namespace = 'urn:' + namespace
        record_data['namespace'] = namespace

        record_data['version'] = avro_record_data.pop('version', '1.0.0')
        source = avro_record_data.pop('source', 'urn:unspecified').replace('.', ':')
        if not source.startswith('urn:'):
            source = 'urn:' + source
        record_data['source'] = source

        # get optional data
        for meta_key in [
            'uuid', 'correlation_id', 'partition_key', 'context',
        ]:
            if meta_key in avro_record_data:
                record_data[meta_key] = avro_record_data.pop(meta_key)

        # get date from timestamp
        for timestamp_key in [
            'timestamp', 'timestamp_ms',
            'date_timestamp', 'date_timestamp_ms',
            'event_timestamp', 'event_timestamp_ms',
        ]:
            if timestamp_key in avro_record_data:
                timestamp = avro_record_data.pop(timestamp_key)
                if 'date' not in record_data:
                    record_data['date'] = datetime.fromtimestamp(timestamp / 1000, timezone.utc)

        # get date from iso string
        for date_iso_key in [
            'date_iso', 'date_iso8601',
        ]:
            if date_iso_key in avro_record_data:
                date_iso = avro_record_data.pop(date_iso_key)
                if 'date' not in record_data:
                    record_data['date'] = datetime.fromisoformat(date_iso)

        # add data fields
        record_data['data'] = dict()
        record_data['data'].update(avro_record_data.pop('data', {}))
        record_data['data'].update(avro_record_data)

        if record_type == RecordType.EVENT:
            return Event(**record_data)
        elif record_type == RecordType.REQUEST:
            return Request(**record_data)
        elif record_type == RecordType.RESPONSE:
            return Response(**record_data)
        else:
            raise UnknownRecordTypeError(f"Unknown type: {record_type}.")
    except Exception:
        raise AvroDecodeError(decoded_data=record_data)


def _decode_avro_record_v3(
    avro_schema_data: Dict[str, str],
    avro_record_data: Dict
) -> Union[Event, Request, Response]:
    """
    Convert a 3.*.* avro record to an eventy Record.

    :param avro_schema_data: Schema data associated with avro record
    :param avro_record_data: Record data in avro record
    :return: Eventy Record
    """
    record_type = RecordType(avro_record_data.pop('type'))

    date = datetime.fromisoformat(avro_record_data.pop('date_iso8601'))
    avro_record_data.pop('date_timestamp')

    avro_record_data['date'] = date

    name = avro_record_data.pop('record_name', avro_schema_data.get('name'))
    avro_record_data['name'] = name

    namespace = avro_record_data.pop(
        'record_namespace', f'urn:{avro_schema_data.get("namespace", "unspecified").replace(".", ":")}'
    )
    avro_record_data['namespace'] = namespace

    if record_type == RecordType.EVENT:
        return Event(**avro_record_data)
    elif record_type == RecordType.REQUEST:
        return Request(**avro_record_data)
    elif record_type == RecordType.RESPONSE:
        return Response(**avro_record_data)
    else:
        raise UnknownRecordTypeError(f"Unknown type: {record_type}.")


def _gen_avro_schema_v3(
    namespace: str,
    name: str,
    type: str,
    doc: Optional[str] = None,
    data_fields: Optional[list] = None,
) -> RecordSchema:
    """
    Generate a full avro RecordSchema from an EVenty SChema.

    :param namespace: Record namespace (eventy URN format)
    :param name: Record name
    :param type: Record type
    :param doc: Record documentation
    :param data_fields: Schema of Record.data fields
    :return: An avro RecordSchema
    """
    record_type = RecordType(type.upper())

    # avro namespace format is dot-separated without urn: prefix and without -, only _ allowed
    avro_namespace = namespace.replace('urn:', '').replace(':', '.').replace('-', '_')
    avro_name = name

    fields = [
        {
            'name': 'record_namespace',
            'type': 'string',
            'doc': 'Record namespace',
        },
        {
            'name': 'record_name',
            'type': 'string',
            'doc': 'Record name',
        },
        {
            'name': 'type',
            'type': {
                'name': 'RecordType',
                'type': 'enum',
                'symbols': [record_type.value]
            },
            'doc': 'Type of of record: one of EVENT, REQUEST or RESPONSE',
        },
        {
            'name': 'protocol_version',
            'type': 'string',
            'doc': 'Version of the Eventy protocol used for encoding this message (semver format: X.Y.Z)',
        },
        {
            'name': 'version',
            'type': 'string',
            'doc': 'Version of the schema used for encoding this message (semver format: X.Y.Z)',
        },
        {
            'name': 'source', 'type': 'string',
            'doc': 'Source of the record (URN of the producing service)',
        },
        {
            'name': 'uuid', 'type': 'string', 'logicalType': 'uuid',
            'doc': 'UUID for this record',
        },
        {
            'name': 'correlation_id', 'type': 'string',
            'doc': 'Identifier propagated across the system and to link associated records together',
        },
        {
            'name': 'partition_key', 'type': ['string', 'null'],
            'doc': 'A string determining to which partition your record will be assigned',
        },
        {
            'name': 'date_timestamp', 'type': 'long', 'logicalType': 'timestamp-millis',
            'doc': 'UNIX timestamp in milliseconds',
        },
        {
            'name': 'date_iso8601', 'type': 'string',
            'doc': 'ISO 8601 date with timezone',
        },
    ]
    if record_type == RecordType.RESPONSE:
        fields += [
            {
                'name': 'destination', 'type': 'string',
                'doc': 'URN of the destination service',
            },
            {
                'name': 'request_uuid', 'type': 'string',
                'doc': 'UUID of the associated request',
            },
            {
                'name': 'ok', 'type': 'boolean',
                'doc': 'Status: True if there was no error, false otherwise',
            },
            {
                'name': 'error_code', 'type': ['null', 'int'],
                'doc': 'Numeric code for the error, if ok is False, null otherwise',
            },
            {
                'name': 'error_message', 'type': ['null', 'string'],
                'doc': 'Description for the error, if ok is False, null otherwise',
            },
        ]
    context_field = {
        'name': 'context', 'type':
            {
                'type': 'map', 'values':
                {
                    'type': 'map',
                    'values': ['string', 'double', 'float', 'long', 'int', 'boolean', 'null']
                }
            },
        'doc': 'Context data, always propagated'
    }
    data_field: dict[str, Any] = {
        'name': 'data', 'type':
            {
                'type': 'record', 'name': f'{avro_name}_data', 'namespace': avro_namespace, 'fields':
                data_fields or []
            },
        'doc': 'Record payload',
    }
    if record_type == RecordType.RESPONSE:
        data_field = {
            'name': 'data', 'type': [
                {
                    'type': 'map',
                    'values': []
                },
                {
                    'type': 'record', 'name': f'{avro_name}_data', 'namespace': avro_namespace, 'fields':
                    data_fields or []
                },
            ],
            'doc': 'Record payload',
        }

    fields += [context_field, data_field, ]
    schema_dict = {
        'name': avro_name,
        'namespace': avro_namespace,
        'doc': doc or f'{name} {record_type} Record',
        'type': 'record',
        'fields': fields,
    }
    return avro.schema.parse(json.dumps(schema_dict))


def _load_schema_files(
    schemas_folder: str,
    schemas_ext: str,
    recursive: bool,
) -> Iterator[Dict]:
    with os.scandir(schemas_folder) as entries:
        entry: os.DirEntry
        for entry in entries:

            # load in sub folder if recursive option set
            if entry.is_dir():
                if recursive:
                    yield from _load_schema_files(entry.path, schemas_ext, recursive)
                else:
                    continue

            # ignores everything that is not a file
            if not entry.is_file():
                continue  # pragma: nocover

            # ignores hidden files
            if entry.name.startswith("."):
                continue  # pragma: nocover

            # ignores everything files with wrong extension
            if not entry.name.endswith(schemas_ext):
                continue  # pragma: nocover

            with open(entry.path) as avro_yml:
                yaml_data = yaml.load(avro_yml.read(), Loader=yaml.SafeLoader)
                yield yaml_data
