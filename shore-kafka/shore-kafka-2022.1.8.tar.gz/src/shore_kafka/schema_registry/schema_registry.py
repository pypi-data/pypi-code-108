import json
import logging
import struct
from ast import parse
from io import BytesIO

from pydantic import BaseModel
from confluent_kafka.schema_registry import (
    _MAGIC_BYTE,
    Schema,
    SchemaRegistryClient,
    SchemaRegistryError,
    SchemaReference,
)
from confluent_kafka.serialization import Deserializer, SerializationError, Serializer
from jsonschema import ValidationError, validate

logger = logging.getLogger(__file__)


class _ContextStringIO(BytesIO):
    """
    Wrapper to allow use of StringIO via 'with' constructs.
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


################################################################
# Serializer
################################################################
class ShoreSerializer(Serializer):
    """
    (NOTE)
        이것은 "confluent_kafka.schema_registry.json_schema.JSONSerializer"가 아님!
         - RecordNameStrategy를 따름.
         - TopicNameStrategy Schema Registry는 직접 등록해야 함. (Referenced Schema)
         - 주의! ShoreSerializer는 pydantic model만 받음!

        기존 confluent-kafka JSONSerializer의 단점:
         - 모든 메시지를 대상으로 schema lookup 수행 -> 낭비.
         - 초기화 시 schema_str을 요구 -> 불편.
         - Referenced Schema 지원 logic 오류. (1.7.0 기준)
    """

    __slots__ = ["sr_client", "topic", "field", "_schemas"]

    def __init__(self, sr_client: SchemaRegistryClient, topic: str, field: str) -> None:

        # validate params
        assert field in ["key", "value"], "field: 'key' or 'value' only!"

        # placeholders
        self.sr_client = sr_client
        self.topic = topic
        self.field = field
        self._schemas = dict()

        logger.info(f"serializer for '{topic}-{field}' is initialized")

    def __call__(self, obj):

        # do not serialize string object
        if obj is None or isinstance(obj, str):
            return obj

        # get schema if not in memory
        subject_name = self._get_subject_name(obj)
        if subject_name not in self._schemas.keys():
            logger.info(f"load schema for '{subject_name}' from schema registry.")
            self._get_schema(subject_name=subject_name, obj=obj)

        # pick schema for record
        schema = self._schemas[subject_name]

        # validate schema
        value = obj.dict()
        try:
            validate(instance=value, schema=schema["schema"])
        except ValidationError as ve:
            raise SerializationError(ve.message)

        # serializer and return
        with _ContextStringIO() as fo:
            # Write the magic byte and schema ID in network byte order (big endian)
            fo.write(struct.pack(">bI", _MAGIC_BYTE, schema["id"]))
            # JSON dump always writes a str never bytes https://docs.python.org/3/library/json.html
            fo.write(json.dumps(value).encode("utf8"))

            return fo.getvalue()

    def _get_schema(self, subject_name, obj):
        # register schema if not exist
        registered = self.sr_client.get_subjects()
        if subject_name not in registered:
            self._register_schema(subject_name=subject_name, obj=obj)

        # register topic schema (following TopicNameStrategy) if reference schema (following RecordNameStrategy) is given
        topic_subject_name = f"{self.topic}-{self.field}"
        if subject_name != topic_subject_name:
            logger.info("got referenced schema, check topic schema is registered.")
            self._register_topic_schema(topic_subject_name=topic_subject_name, subject_name=subject_name)

        # load schema from schema registry
        version = self.sr_client.get_latest_version(subject_name)
        _schema = {subject_name: {"schema": json.loads(version.schema.schema_str), "id": version.schema_id}}
        self._schemas.update(_schema)

    def _register_schema(self, subject_name, obj):
        schema_str = obj.schema_json()
        schema = Schema(schema_str=schema_str, schema_type="JSON")
        self.sr_client.register_schema(subject_name=subject_name, schema=schema)
        logger.info(f"new schema '{subject_name}' is registered!")

    def _register_topic_schema(self, topic_subject_name, subject_name):
        registered = self.sr_client.get_subjects()
        if topic_subject_name in registered:
            version = self.sr_client.get_latest_version(topic_subject_name)
            subject = json.loads(version.schema.schema_str)
            references = version.schema.references
        else:
            subject = {"title": topic_subject_name, "oneOf": []}
            references = []

        # evolve schema
        if subject_name not in [reference["subject"] for reference in references]:
            ref_name = f"{subject_name}.schema.json"
            ref_version = self.sr_client.get_latest_version(subject_name).version
            one_of = subject.get("oneOf", [])
            one_of += [{"$ref": ref_name}]
            subject.update({"oneOf": one_of})
            references += [{"name": ref_name, "subject": subject_name, "version": ref_version}]
            _references = [
                SchemaReference(name=ref["name"], subject=ref["subject"], version=ref["version"]) for ref in references
            ]
            schema = Schema(json.dumps(subject), schema_type="JSON", references=_references)
            self.sr_client.register_schema(topic_subject_name, schema)
            logger.warn(f"topic level subject '{topic_subject_name}' is evolved")

    @staticmethod
    def _get_subject_name(obj):
        """
        (NOTE) pydantic은 schema의 title을 아래와 같이 지정할 수 있음.

        class Something(BaseModel):
            var_a: int
            var_b: float

            class Config:
                title = "This is the title"

        """
        # valid pydantic!
        assert isinstance(obj, BaseModel), "ShoreProducer only accept string and PyDantic object!"

        if obj.Config.title is None:
            return obj.__class__.__name__
        return obj.Config.title


################################################################
# Deserializer
################################################################
class ShoreDeserializer(Deserializer):
    """
    (NOTE)
        이것은 "confluent_kafka.schema_registry.json_schema.JSONDeserializer"가 아님!
          - Referenced Schema를 처리 가능
          - Schema 없는 메시지를 처리 가능

        기존 confluent-kafka JSONDeserializer의 제약:
          - Referenced Schema 처리 기능 없음. (1.7.0 기준)
    """

    __slots__ = ["sr_client", "parse_unknown_schema", "_schemas", "_parsed_schemas"]

    def __init__(self, sr_client, parse_unknown_schema=False):

        # set properties
        self.sr_client = sr_client
        self.parse_unknown_schema = parse_unknown_schema

        # placeholders
        self._schemas = dict()
        self._parsed_schemas = dict()

    def __call__(self, value):
        """
        Deserializes Schema Registry formatted JSON to JSON object literal(dict).
        """
        if value is None:
            return None

        with _ContextStringIO(value) as payload:

            # schema registry 사용여부 확인
            magic, schema_id = struct.unpack(">bI", payload.read(5))
            if magic != _MAGIC_BYTE:
                if self.parse_unknown_schema:
                    try:
                        str_decoded = value.decode("utf-8")
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            return str_decoded
                    except Exception as ex:
                        logger.warn(f"{ex} - {value}")
                return value

            if schema_id not in self._schemas.keys():
                _schema = self.sr_client.get_schema(schema_id)
                self._schemas[schema_id] = _schema
                self._parsed_schemas[schema_id] = json.loads(_schema.schema_str)

            # JSON documents are self-describing; no need to query schema
            obj_dict = json.loads(payload.read())

            try:
                validate(instance=obj_dict, schema=self._parsed_schemas[schema_id])
            except ValidationError as ve:
                raise SerializationError(ve.message)

            return obj_dict
