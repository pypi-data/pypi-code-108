# Copyright 2020 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# See: https://github.com/confluentinc/confluent-kafka-python/pull/1088
#

from json import loads
from struct import unpack, pack

from confluent_kafka.schema_registry import topic_subject_name_strategy, _MAGIC_BYTE
from confluent_kafka.schema_registry.avro import AvroDeserializer, _ContextStringIO, _schema_loads, AvroSerializer
from confluent_kafka.serialization import SerializationError
from fastavro import parse_schema, schemaless_reader, schemaless_writer


class AvroSerializerWithReferences(AvroSerializer):
    __slots__ = ['_hash', '_auto_register', '_known_subjects', '_parsed_schema',
                 '_registry', '_schema', '_schema_id', '_schema_name',
                 '_subject_name_func', '_to_dict', '_named_schemas']

    _default_conf = {'auto.register.schemas': True,
                     'subject.name.strategy': topic_subject_name_strategy}

    def __init__(self, schema_registry_client, schema,
                 to_dict=None, conf=None, named_schemas={}):
        self._registry = schema_registry_client
        self._schema_id = None
        self._known_subjects = set()

        if to_dict is not None and not callable(to_dict):
            raise ValueError("to_dict must be callable with the signature"
                             " to_dict(object, SerializationContext)->dict")

        self._to_dict = to_dict
        self._named_schemas = named_schemas

        conf_copy = self._default_conf.copy()
        if conf is not None:
            conf_copy.update(conf)

        self._auto_register = conf_copy.pop('auto.register.schemas')
        if not isinstance(self._auto_register, bool):
            raise ValueError("auto.register.schemas must be a boolean value")

        self._subject_name_func = conf_copy.pop('subject.name.strategy')
        if not callable(self._subject_name_func):
            raise ValueError("subject.name.strategy must be callable")

        schema_dict = loads(schema.schema_str)
        parsed_schema = parse_schema(schema_dict, named_schemas=self._named_schemas)
        schema_name = parsed_schema.get('name', schema_dict['type'])

        self._schema = schema
        self._schema_name = schema_name
        self._parsed_schema = parsed_schema

    def __call__(self, obj, ctx):
        if obj is None:
            return None

        subject = self._subject_name_func(ctx, self._schema_name)

        if self._auto_register and subject not in self._known_subjects:
            self._schema_id = self._registry.register_schema(subject,
                                                             self._schema)
            self._known_subjects.add(subject)
        elif not self._auto_register and subject not in self._known_subjects:
            registered_schema = self._registry.lookup_schema(subject,
                                                             self._schema)
            self._schema_id = registered_schema.schema_id
            self._known_subjects.add(subject)

        if self._to_dict is not None:
            value = self._to_dict(obj, ctx)
        else:
            value = obj

        with _ContextStringIO() as fo:
            fo.write(pack('>bI', _MAGIC_BYTE, self._schema_id))
            schemaless_writer(fo, self._parsed_schema, value)

            return fo.getvalue()


class AvroDeserializerWithReferences(AvroDeserializer):
    __slots__ = ['_reader_schema', '_registry', '_from_dict', '_writer_schemas', '_return_record_name',
                 '_named_schemas']

    def __init__(self, schema_registry_client, schema=None, from_dict=None, return_record_name=False, named_schemas={}):
        self._registry = schema_registry_client
        self._writer_schemas = {}

        self._reader_schema = schema
        self._named_schemas = named_schemas

        if from_dict is not None and not callable(from_dict):
            raise ValueError("from_dict must be callable with the signature"
                             " from_dict(SerializationContext, dict) -> object")
        self._from_dict = from_dict

        self._return_record_name = return_record_name
        if not isinstance(self._return_record_name, bool):
            raise ValueError("return_record_name must be a boolean value")

    def __call__(self, value, ctx):
        if value is None:
            return None

        if len(value) <= 5:
            raise SerializationError("Message too small. This message was not"
                                     " produced with a Confluent"
                                     " Schema Registry serializer")

        with _ContextStringIO(value) as payload:
            magic, schema_id = unpack('>bI', payload.read(5))
            if magic != _MAGIC_BYTE:
                raise SerializationError("Unknown magic byte. This message was"
                                         " not produced with a Confluent"
                                         " Schema Registry serializer")

            writer_schema = self._writer_schemas.get(schema_id, None)

            if writer_schema is None:
                schema = self._registry.get_schema(schema_id)
                prepared_schema = _schema_loads(schema.schema_str)
                writer_schema = parse_schema(loads(
                    prepared_schema.schema_str), named_schemas=self._named_schemas)
                self._writer_schemas[schema_id] = writer_schema

            obj_dict = schemaless_reader(payload,
                                         writer_schema,
                                         self._reader_schema,
                                         self._return_record_name)

            if self._from_dict is not None:
                return self._from_dict(obj_dict, ctx)

            return obj_dict
