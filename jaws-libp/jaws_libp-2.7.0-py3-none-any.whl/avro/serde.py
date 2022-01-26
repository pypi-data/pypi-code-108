"""
    Serialization and Deserialization utilities
"""
import json
import pkgutil
from enum import Enum

import fastavro

from typing import Any, Dict, List, Union, Tuple, Type
from abc import abstractmethod, ABC
from confluent_kafka.schema_registry import SchemaReference, Schema, SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import StringSerializer, StringDeserializer, Serializer, Deserializer, \
    SerializationContext
from ..entities import AlarmLocation, AlarmPriority
from ..entities import SimpleProducer, AlarmInstance, AlarmActivationUnion, SimpleAlarming, \
    EPICSAlarming, NoteAlarming, DisabledOverride, FilteredOverride, LatchedOverride, MaskedOverride, \
    OnDelayedOverride, OffDelayedOverride, ShelvedOverride, AlarmOverrideUnion, OverriddenAlarmType, AlarmOverrideKey, \
    ShelvedReason, EPICSSEVR, EPICSSTAT, UnionEncoding, CALCProducer, EPICSProducer, AlarmClass, \
    EffectiveRegistration, EffectiveActivation, EffectiveAlarm, IntermediateMonolog, AlarmState, AlarmOverrideSet, \
    ProcessorTransitions
from ..references.avro import AvroDeserializerWithReferences, AvroSerializerWithReferences


def _unwrap_enum(value: [None, Tuple[str, str], str], enum_class: Type[Enum]) -> [None, Tuple[str, str], str]:
    """
        When instantiating classes using from_dict often a variable intended to be an enum is encountered that
        may actually be a String, a Tuple, or an Enum so this function attempts to convert to an Enum if needed.

        A tuple is allowed due to fastavro supporting tuples for complex types.

        :param value: The value to massage into the correct type
        :param enum_class: Enum class to instantiate
        :return: A value likely as an Enum or None
    """

    if value is None:
        result = None
    elif type(value) is tuple:
        result = enum_class[value[1]]
    elif type(value) is str:
        result = enum_class[value]
    else:  # return as is (hopefully already an Enum)
        result = value
    return result


class Serde(ABC):
    """
        Serialization and Deserialization base class (interface).   Converts to/from bytes (AVRO) to JAWS entities
        (classes and strings).

        Internally relies on the Confluent Kafka Python API, which converts bytes to/from Dicts, Tuples, or primitive
        types (which one is entity specific).  The Confluent lib itself relies on the fastavro lib.
    """
    @abstractmethod
    def from_json(self, data: str) -> Any:
        """
            Convert an entity to a JSON string.

            :param data: A JSON string
            :return: An entity class or string
        """
        pass

    @abstractmethod
    def to_json(self, data: Any) -> str:
        """
            Convert a JSON string to an entity.

            :param data: An entity class or string
            :return: A JSON string
        """
        pass

    @abstractmethod
    def serializer(self) -> Serializer:
        """
            Get the serializer.

            :return: The Serializer
        """
        pass

    @abstractmethod
    def deserializer(self) -> Deserializer:
        """
            Get the deserializer.

            :return: The Deserializer
        """
        pass


class StringSerde(Serde):
    """
        String Serde.
    """
    def from_json(self, data: str) -> str:
        return data

    def to_json(self, data: str) -> str:
        return data

    def serializer(self):
        return StringSerializer('utf_8')

    def deserializer(self):
        return StringDeserializer('utf_8')


class RegistryAvroSerde(Serde):
    """
        AVRO Serde which relies on Confluent Schema Registry.
    """
    def __init__(self, schema_registry_client: SchemaRegistryClient, schema: Schema, union_encoding: UnionEncoding):
        """
            Creates a new RegistryAvroSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param schema: The Schema
            :param union_encoding: The union encoding to use
        """
        self._schema_registry_client = schema_registry_client
        self._schema = schema
        self._union_encoding = union_encoding

    @abstractmethod
    def from_dict(self, data: Dict) -> Any:
        pass

    def _from_dict_with_ctx(self, data: Dict, ctx: SerializationContext) -> Any:
        return self.from_dict(data)

    def _from_union(self, unionobj: Union[Tuple[str, Dict[str, Any]],
                                          Dict[str, Dict[str, Any]]]) -> Tuple[str, Dict[str, Any]]:
        if type(unionobj) is tuple:
            uniontype = unionobj[0]
            uniondict = unionobj[1]
        elif type(unionobj is dict):
            value = next(iter(unionobj.items()))
            uniontype = value[0]
            uniondict = value[1]
        else:
            raise Exception("Unsupported union encoding")

        return uniontype, uniondict

    def _to_union(self, uniontype: str, uniondict: Dict[str, Any]) -> Union[Tuple[str, Dict[str, Any]],
                                                                            Dict[str, Any],
                                                                            Dict[str, Dict[str, Any]]]:
        if self._union_encoding is UnionEncoding.TUPLE:
            union = (uniontype, uniondict)
        elif self._union_encoding is UnionEncoding.DICT_WITH_TYPE:
            union = {uniontype: uniondict}
        else:
            union = uniondict

        return union

    @abstractmethod
    def to_dict(self, data: Any) -> Dict:
        pass

    def _to_dict_with_ctx(self, data: Any, ctx: SerializationContext) -> Dict:
        return self.to_dict(data)

    def from_json(self, data: str) -> Any:
        entity_dict = json.loads(data)
        entity = self.from_dict(entity_dict)

        return entity

    def to_json(self, data: Any) -> str:
        sorteddata = dict(sorted(self.to_dict(data).items()))
        jsondata = json.dumps(sorteddata)
        return jsondata

    def get_schema(self) -> Schema:
        """
            Get Schema.

            :return: The Schema
        """
        return self._schema

    def serializer(self) -> Serializer:
        return AvroSerializer(self._schema_registry_client,
                              self._schema.schema_str,
                              self._to_dict_with_ctx)

    def deserializer(self) -> Deserializer:
        return AvroDeserializer(self._schema_registry_client,
                                None,
                                self._from_dict_with_ctx,
                                True)


class RegistryAvroWithReferencesSerde(RegistryAvroSerde):
    """
        AVRO Registry Serde with Schema References support.
    """
    def __init__(self, schema_registry_client: SchemaRegistryClient, schema: Schema, union_encoding: UnionEncoding,
                 references: List[SchemaReference], named_schemas: Dict[str, Any]):
        """
            Create a new RegistryAvroWithReferencesSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param schema: The entity Schema
            :param union_encoding: The union encoding to use
            :param references: List of SchemaReference
            :param named_schemas: Dict of named schemas
        """
        self._references = references
        self._named_schemas = named_schemas

        super().__init__(schema_registry_client, schema, union_encoding)

    @abstractmethod
    def from_dict(self, data):
        pass

    @abstractmethod
    def to_dict(self, data):
        pass

    def references(self) -> List[SchemaReference]:
        """
            Get the Schema References.

            :return: The List of SchemaReference
        """
        return self._references

    def named_schemas(self) -> Dict[str, Any]:
        """
            Get the named schemas.

            :return: Return the named schemas
        """
        return self._named_schemas

    def serializer(self):
        return AvroSerializerWithReferences(schema_registry_client=self._schema_registry_client,
                                            schema=self.get_schema(),
                                            to_dict=self._to_dict_with_ctx,
                                            named_schemas=self.named_schemas())

    def deserializer(self):
        return AvroDeserializerWithReferences(self._schema_registry_client,
                                              None,
                                              self._from_dict_with_ctx,
                                              True,
                                              self.named_schemas())


class ClassSerde(RegistryAvroWithReferencesSerde):
    """
        Provides AlarmClass serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient):
        """
            Create a new LocationSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        priority_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmPriority.avsc")
        priority_schema_str = priority_bytes.decode('utf-8')

        named_schemas = {}

        ref_dict = json.loads(priority_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        priority_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmPriority", "alarm-priority", 1)
        references = [priority_schema_ref]

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmClass.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE, references, named_schemas)

    def to_dict(self, data: AlarmClass) -> Dict[str, str]:
        """
            Converts an AlarmClass to a dict.

            :param data: The AlarmClass
            :return: A dict
        """

        return {
            "category": data.category,
            "priority": data.priority.name,
            "rationale": data.rationale,
            "correctiveaction": data.corrective_action,
            "pointofcontactusername": data.point_of_contact_username,
            "latching": data.latching,
            "filterable": data.filterable,
            "ondelayseconds": data.on_delay_seconds,
            "offdelayseconds": data.off_delay_seconds
        }

    def from_dict(self, data: Dict[str, Any]) -> AlarmClass:
        """
            Converts a dict to an AlarmClass.

            Note: Generally the Dict values are Strings, but the priority field may be a Tuple or Enum.

            :param data: The dict
            :return: The AlarmClass
            """
        return AlarmClass(data.get('category'),
                          _unwrap_enum(data.get('priority'), AlarmPriority),
                          data.get('rationale'),
                          data.get('correctiveaction'),
                          data.get('pointofcontactusername'),
                          data.get('latching'),
                          data.get('filterable'),
                          data.get('ondelayseconds'),
                          data.get('offdelayseconds'))


class LocationSerde(RegistryAvroSerde):
    """
        Provides AlarmLocation serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient):
        """
            Create a new LocationSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmLocation.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", [])

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE)

    def to_dict(self, data: AlarmLocation) -> Dict[str, str]:
        """
        Converts AlarmLocation to a dict.

        :param data: The AlarmLocation
        :return: A dict
        """
        return {
            "parent": data.parent
        }

    def from_dict(self, data: Dict[str, str]) -> AlarmLocation:
        """
        Converts a dict to AlarmLocation.

        :param data: The dict
        :return: The AlarmLocation
        """
        return AlarmLocation(data['parent'])


class ActivationSerde(RegistryAvroSerde):
    """
        Provides AlarmActivationUnion serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient,
                 union_encoding: UnionEncoding = UnionEncoding.TUPLE):
        """
            Create a new ActivationSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param union_encoding: The union encoding to use
        """
        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmActivationUnion.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", [])

        super().__init__(schema_registry_client, schema, union_encoding)

    def to_dict(self, data: AlarmActivationUnion) -> Dict[str, Union[Tuple[str, Dict[str, str]],
                                                                     Dict[str, str],
                                                                     Dict[str, Dict[str, str]]]]:
        """
            Converts an AlarmActivationUnion to a dict.

            Note: The returned dict if not None is always keyed with "msg" and the value is either
            a (1) Tuple, (2) Dict, or (3) Dict with one key which is name of union entity and valued with Dict.  This
            is determined by union_encoding.

            :param data: The AlarmActivationUnion
            :return: A dict
        """
        if isinstance(data.msg, SimpleAlarming):
            uniontype = "org.jlab.jaws.entity.SimpleAlarming"
            uniondict = {}
        elif isinstance(data.msg, EPICSAlarming):
            uniontype = "org.jlab.jaws.entity.EPICSAlarming"
            uniondict = {"sevr": data.msg.sevr.name, "stat": data.msg.stat.name}
        elif isinstance(data.msg, NoteAlarming):
            uniontype = "org.jlab.jaws.entity.NoteAlarming"
            uniondict = {"note": data.msg.note}
        else:
            raise Exception("Unknown alarming union type: {}".format(data.msg))

        union = self._to_union(uniontype, uniondict)

        return {
            "msg": union
        }

    def from_dict(self, data: Dict[str, Union[Tuple[str, Dict[str, str]],
                                              Dict[str, Dict[str, str]]]]) -> AlarmActivationUnion:
        """
            Converts a dict to an AlarmActivationUnion.

            Note: UnionEncoding.POSSIBLY_AMBIGUOUS_DICT is not supported.  See to_dict().

            :param data: The dict
            :return: The AlarmActivationUnion
        """
        unionobj = data['msg']

        uniontype, uniondict = self._from_union(unionobj)

        if uniontype == "org.jlab.jaws.entity.NoteAlarming":
            obj = NoteAlarming(uniondict['note'])
        elif uniontype == "org.jlab.jaws.entity.EPICSAlarming":
            obj = EPICSAlarming(_unwrap_enum(uniondict['sevr'], EPICSSEVR), _unwrap_enum(uniondict['stat'],
                                                                                         EPICSSTAT))
        else:
            obj = SimpleAlarming()

        return AlarmActivationUnion(obj)


class InstanceSerde(RegistryAvroSerde):
    """
        Provides AlarmInstance serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient,
                 union_encoding: UnionEncoding = UnionEncoding.TUPLE):
        """
            Create a new InstanceSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param union_encoding: The union encoding to use
        """
        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmInstance.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", [])

        super().__init__(schema_registry_client, schema, union_encoding)

    def to_dict(self, data: AlarmInstance) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
            Converts an AlarmInstance to a dict.

            :param data: The AlarmInstance
            :return: A dict
        """
        if isinstance(data.producer, SimpleProducer):
            uniontype = "org.jlab.jaws.entity.SimpleProducer"
            uniondict = {}
        elif isinstance(data.producer, EPICSProducer):
            uniontype = "org.jlab.jaws.entity.EPICSProducer"
            uniondict = {"pv": data.producer.pv}
        elif isinstance(data.producer, CALCProducer):
            uniontype = "org.jlab.jaws.entity.CALCProducer"
            uniondict = {"expression": data.producer.expression}
        else:
            raise Exception("Unknown instance producer union type: {}".format(data.producer))

        union = self._to_union(uniontype, uniondict)

        return {
            "class": data.alarm_class,
            "producer": union,
            "location": data.location,
            "maskedby": data.masked_by,
            "screencommand": data.screen_command
        }

    def from_dict(self, data: Dict[str, Union[str, Any]]) -> AlarmInstance:
        """
            Converts a dict to an AlarmInstance.

            Note: UnionEncoding.POSSIBLY_AMBIGUOUS_DICT is not supported.

            :param data: The dict
            :return: The AlarmInstance
        """
        unionobj = data['producer']

        uniontype, uniondict = self._from_union(unionobj)

        if uniontype == "org.jlab.jaws.entity.CalcProducer":
            producer = CALCProducer(uniondict['expression'])
        elif uniontype == "org.jlab.jaws.entity.EPICSProducer":
            producer = EPICSProducer(uniondict['pv'])
        else:
            producer = SimpleProducer()

        return AlarmInstance(data.get('class'),
                             producer,
                             data.get('location'),
                             data.get('maskedby'),
                             data.get('screencommand'))


class OverrideSetSerde(RegistryAvroWithReferencesSerde):
    """
        Provides OverrideSet serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient) -> None:
        """
            Create a new OverrideSetSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """

        disabled_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/DisabledOverride.avsc")
        disabled_schema_str = disabled_bytes.decode('utf-8')

        filtered_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/FilteredOverride.avsc")
        filtered_schema_str = filtered_bytes.decode('utf-8')

        latched_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/LatchedOverride.avsc")
        latched_schema_str = latched_bytes.decode('utf-8')

        masked_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/MaskedOverride.avsc")
        masked_schema_str = masked_bytes.decode('utf-8')

        off_delayed_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/OffDelayedOverride.avsc")
        off_delayed_schema_str = off_delayed_bytes.decode('utf-8')

        on_delayed_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/OnDelayedOverride.avsc")
        on_delayed_schema_str = on_delayed_bytes.decode('utf-8')

        shelved_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/ShelvedOverride.avsc")
        shelved_schema_str = shelved_bytes.decode('utf-8')

        named_schemas = {}

        ref_dict = json.loads(disabled_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(filtered_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(latched_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(masked_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(off_delayed_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(on_delayed_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(shelved_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        disabled_schema_ref = SchemaReference("org.jlab.jaws.entity.DisabledOverride", "disabled-override", 1)
        filtered_schema_ref = SchemaReference("org.jlab.jaws.entity.FilteredOverride", "filtered-override", 1)
        latched_schema_ref = SchemaReference("org.jlab.jaws.entity.LatchedOverride", "latched-override", 1)
        masked_schema_ref = SchemaReference("org.jlab.jaws.entity.MaskedOverride", "masked-override", 1)
        off_delayed_schema_ref = SchemaReference("org.jlab.jaws.entity.OffDelayedOverride", "off-delayed-override", 1)
        on_delayed_schema_ref = SchemaReference("org.jlab.jaws.entity.OnDelayedOverride", "on-delayed-override", 1)
        shelved_schema_ref = SchemaReference("org.jlab.jaws.entity.ShelvedOverride", "shelved-override", 1)

        references = [disabled_schema_ref,
                      filtered_schema_ref,
                      latched_schema_ref,
                      masked_schema_ref,
                      off_delayed_schema_ref,
                      on_delayed_schema_ref,
                      shelved_schema_ref]

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmOverrideSet.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE, references, named_schemas)

    def to_dict(self, data: AlarmOverrideSet) -> Dict[str, Any]:
        """
            Converts AlarmOverrideSet to a dict.

            :param data: The AlarmOverrideSet
            :return: A dict
        """
        return {
            "disabled": {"comments": data.disabled.comments} if data.disabled is not None else None,
            "filtered": {"filtername": data.filtered.filtername} if data.filtered is not None else None,
            "latched": {} if data.latched is not None else None,
            "masked": {} if data.masked is not None else None,
            "ondelayed": {"expiration": data.ondelayed.expiration} if data.ondelayed is not None else None,
            "offdelayed": {"expiration": data.offdelayed.expiration} if data.offdelayed is not None else None,
            "shelved": {"expiration": data.shelved.expiration,
                        "comments": data.shelved.comments,
                        "oneshot": data.shelved.oneshot,
                        "reason": data.shelved.reason.name} if data.shelved is not None else None
        }

    def from_dict(self, data: Dict[str, Union[None, Any]]) -> AlarmOverrideSet:
        """
            Converts a dict to AlarmOverrideSet.

            :param data: The dict
            :return: The AlarmOverrideSet
        """
        return AlarmOverrideSet(DisabledOverride(data['disabled'][1]['comments'])
                                if data.get('disabled') is not None else None,
                                FilteredOverride(data['filtered'][1]['filtername'])
                                if data.get('filtered') is not None else None,
                                LatchedOverride()
                                if data.get('latched') is not None else None,
                                MaskedOverride()
                                if data.get('masked') is not None else None,
                                OnDelayedOverride(data['ondelayed'][1]['expiration'])
                                if data.get('ondelayed') is not None else None,
                                OffDelayedOverride(data['offdelayed'][1]['expiration'])
                                if data.get('offdelayed') is not None else None,
                                ShelvedOverride(data['shelved'][1]['expiration'],
                                                data['shelved'][1]['comments'],
                                                ShelvedReason[data['shelved'][1]['reason']],
                                                data['shelved'][1]['oneshot'])
                                if data.get('shelved') is not None else None)


class EffectiveRegistrationSerde(RegistryAvroWithReferencesSerde):
    """
        Provides EffectiveRegistration serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient) -> None:
        """
            Create a new EffectiveRegistrationSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        self._class_serde = ClassSerde(schema_registry_client)
        self._instance_serde = InstanceSerde(schema_registry_client)

        classes_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmClass", "alarm-classes-value", 1)
        registration_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmInstance",
                                                  "alarm-instances-value", 1)

        references = [classes_schema_ref, registration_schema_ref]

        classes_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmClass.avsc")
        classes_schema_str = classes_bytes.decode('utf-8')

        instance_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmInstance.avsc")
        instance_schema_str = instance_bytes.decode('utf-8')

        named_schemas = self._class_serde.named_schemas()

        ref_dict = json.loads(classes_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(instance_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveRegistration.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE, references, named_schemas)

    def to_dict(self, data: EffectiveRegistration) -> Dict[str, Any]:
        """
            Converts EffectiveRegistration to a dict.

            :param data: The EffectiveRegistration
            :return: A dict
        """
        return {
            "class": self._class_serde.to_dict(data.alarm_class) if data.alarm_class is not None else None,
            "instance": self._instance_serde.to_dict(data.instance) if data.instance is not None else None
        }

    def from_dict(self, data: Dict[str, Any]) -> EffectiveRegistration:
        """
            Converts a dict to EffectiveRegistration.

            :param data: The dict
            :return: The EffectiveRegistration
        """
        return EffectiveRegistration(
            self._class_serde.from_dict(data['class'][1]) if data.get('class') is not None else None,
            self._instance_serde.from_dict(data['instance'][1])
            if data.get('instance') is not None else None)


class EffectiveActivationSerde(RegistryAvroWithReferencesSerde):
    """
        Provides EffectiveActivation serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient) -> None:
        """
            Create a new EffectiveActivationSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        self._activation_serde = ActivationSerde(schema_registry_client)
        self._override_serde = OverrideSetSerde(schema_registry_client)

        activation_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmActivationUnion",
                                                "alarm-activations-value", 1)
        overrides_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmOverrideSet",
                                               "alarm-override-set", 1)
        state_schema_ref = SchemaReference("org.jlab.jaws.entity.AlarmState", "alarm-state", 1)

        references = [activation_schema_ref, overrides_schema_ref, state_schema_ref]

        activation_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmActivationUnion.avsc")
        activation_schema_str = activation_bytes.decode('utf-8')

        overrides_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmOverrideSet.avsc")
        overrides_schema_str = overrides_bytes.decode('utf-8')

        state_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmState.avsc")
        state_schema_str = state_bytes.decode('utf-8')

        named_schemas = self._override_serde.named_schemas()

        ref_dict = json.loads(activation_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(overrides_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(state_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveActivation.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE, references, named_schemas)

    def to_dict(self, data: EffectiveActivation) -> Dict[str, Any]:
        """
            Converts EffectiveActivation to a dict.

            :param data: The EffectiveActivation
            :return: A dict
        """
        return {
            "actual": self._activation_serde.to_dict(data.actual) if data.actual is not None else None,
            "overrides": self._override_serde.to_dict(data.overrides),
            "state": data.state.name
        }

    def from_dict(self, data: Dict[str, Any]) -> EffectiveActivation:
        """
            Converts a dict to EffectiveActivation.

            :param data: The dict
            :return: The EffectiveActivation
        """
        return EffectiveActivation(
            self._activation_serde.from_dict(data['actual'][1])
            if data.get('actual') is not None else None,
            self._override_serde.from_dict(data['overrides']),
            _unwrap_enum(data['state'], AlarmState))


class EffectiveAlarmSerde(RegistryAvroWithReferencesSerde):
    """
        Provides EffectiveAlarm serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient) -> None:
        """
            Create a new EffectiveAlarmSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        self._effective_registration_serde = EffectiveRegistrationSerde(schema_registry_client)
        self._effective_activation_serde = EffectiveActivationSerde(schema_registry_client)

        registration_schema_ref = SchemaReference("org.jlab.jaws.entity.EffectiveRegistration",
                                                  "effective-registrations-value", 1)
        activation_schema_ref = SchemaReference("org.jlab.jaws.entity.EffectiveActivation",
                                                "effective-activations-value", 1)

        references = [registration_schema_ref, activation_schema_ref]

        registrations_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveRegistration.avsc")
        registrations_schema_str = registrations_bytes.decode('utf-8')

        activation_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveActivation.avsc")
        activation_schema_str = activation_bytes.decode('utf-8')

        named_schemas = self._effective_registration_serde.named_schemas()
        named_schemas.update(self._effective_activation_serde.named_schemas())

        ref_dict = json.loads(registrations_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        ref_dict = json.loads(activation_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveAlarm.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE, references, named_schemas)

    def to_dict(self, data: EffectiveAlarm) -> Dict[str, Any]:
        """
            Converts EffectiveAlarm to a dict.

            :param data: The EffectiveAlarm
            :return: A dict
        """
        return {
            "registration": self._effective_registration_serde.to_dict(data.registration),
            "activation": self._effective_activation_serde.to_dict(data.activation)
        }

    def from_dict(self, data: Dict[str, Any]) -> EffectiveAlarm:
        """
            Converts a dict to EffectiveAlarm.

            :param data: The dict
            :return: The EffectiveAlarm
        """
        return EffectiveAlarm(self._effective_registration_serde.from_dict(data['registration']),
                              self._effective_activation_serde.from_dict(data['activation']))


class OverrideKeySerde(RegistryAvroSerde):
    """
        Provides OverrideKey serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient) -> None:
        """
            Create a new OverrideKeySerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmOverrideKey.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", [])

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE)

    def to_dict(self, data: AlarmOverrideKey) -> Dict[str, str]:
        """
        Converts an AlarmOverrideKey to a dict.

        :param data: The AlarmOverrideKey
        :return: A dict
        """
        return {
            "name": data.name,
            "type": data.type.name
        }

    def from_dict(self, data: Dict[str, Union[Tuple, str]]) -> AlarmOverrideKey:
        """
        Converts a dict to an AlarmOverrideKey.

        :param data: The dict
        :return: The AlarmOverrideKey
        """
        return AlarmOverrideKey(data['name'], _unwrap_enum(data['type'], OverriddenAlarmType))


class OverrideSerde(RegistryAvroWithReferencesSerde):
    """
        Provides Override serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient,
                 union_encoding: UnionEncoding = UnionEncoding.TUPLE):
        """
            Create a new OverrideSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param union_encoding: The union encoding to use
        """

        self._union_encoding = union_encoding

        disabled_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/DisabledOverride.avsc")
        disabled_schema_str = disabled_bytes.decode('utf-8')

        filtered_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/FilteredOverride.avsc")
        filtered_schema_str = filtered_bytes.decode('utf-8')

        latched_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/LatchedOverride.avsc")
        latched_schema_str = latched_bytes.decode('utf-8')

        masked_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/MaskedOverride.avsc")
        masked_schema_str = masked_bytes.decode('utf-8')

        off_delayed_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/OffDelayedOverride.avsc")
        off_delayed_schema_str = off_delayed_bytes.decode('utf-8')

        on_delayed_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/OnDelayedOverride.avsc")
        on_delayed_schema_str = on_delayed_bytes.decode('utf-8')

        shelved_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/ShelvedOverride.avsc")
        shelved_schema_str = shelved_bytes.decode('utf-8')

        named_schemas = {}

        ref_dict = json.loads(disabled_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(filtered_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(latched_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(masked_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(off_delayed_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(on_delayed_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)
        ref_dict = json.loads(shelved_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        disabled_schema_ref = SchemaReference("org.jlab.jaws.entity.DisabledOverride", "disabled-override", 1)
        filtered_schema_ref = SchemaReference("org.jlab.jaws.entity.FilteredOverride", "filtered-override", 1)
        latched_schema_ref = SchemaReference("org.jlab.jaws.entity.LatchedOverride", "latched-override", 1)
        masked_schema_ref = SchemaReference("org.jlab.jaws.entity.MaskedOverride", "masked-override", 1)
        off_delayed_schema_ref = SchemaReference("org.jlab.jaws.entity.OffDelayedOverride", "off-delayed-override", 1)
        on_delayed_schema_ref = SchemaReference("org.jlab.jaws.entity.OnDelayedOverride", "on-delayed-override", 1)
        shelved_schema_ref = SchemaReference("org.jlab.jaws.entity.ShelvedOverride", "shelved-override", 1)

        references = [disabled_schema_ref,
                      filtered_schema_ref,
                      latched_schema_ref,
                      masked_schema_ref,
                      off_delayed_schema_ref,
                      on_delayed_schema_ref,
                      shelved_schema_ref]

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/AlarmOverrideUnion.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, union_encoding, references, named_schemas)

    def to_dict(self, data: AlarmOverrideUnion) -> Dict[str, Any]:
        """
            Converts an AlarmOverrideUnion to a dict.

            :param data: The AlarmOverrideUnion
            :return: A dict
        """
        if isinstance(data.msg, DisabledOverride):
            uniontype = "org.jlab.jaws.entity.DisabledOverride"
            uniondict = {"comments": data.msg.comments}
        elif isinstance(data.msg, FilteredOverride):
            uniontype = "org.jlab.jaws.entity.FilteredOverride"
            uniondict = {"filtername": data.msg.filtername}
        elif isinstance(data.msg, LatchedOverride):
            uniontype = "org.jlab.jaws.entity.LatchedOverride"
            uniondict = {}
        elif isinstance(data.msg, MaskedOverride):
            uniontype = "org.jlab.jaws.entity.MaskedOverride"
            uniondict = {}
        elif isinstance(data.msg, OnDelayedOverride):
            uniontype = "org.jlab.jaws.entity.OnDelayedOverride"
            uniondict = {"expiration": data.msg.expiration}
        elif isinstance(data.msg, OffDelayedOverride):
            uniontype = "org.jlab.jaws.entity.OffDelayedOverride"
            uniondict = {"expiration": data.msg.expiration}
        elif isinstance(data.msg, ShelvedOverride):
            uniontype = "org.jlab.jaws.entity.ShelvedOverride"
            uniondict = {"expiration": data.msg.expiration, "comments": data.msg.comments,
                         "reason": data.msg.reason.name, "oneshot": data.msg.oneshot}
        else:
            print("Unknown alarming union type: {}".format(data.msg))
            uniontype = None
            uniondict = None

        union = self._to_union(uniontype, uniondict)

        return {
            "msg": union
        }

    def from_dict(self, data: Dict[str, Any]) -> AlarmOverrideUnion:
        """
            Converts a dict to an AlarmOverrideUnion.

            Note: Both UnionEncoding.TUPLE and UnionEncoding.DICT_WITH_TYPE are supported,
            but UnionEncoding.POSSIBLY_AMBIGUOUS_DICT is not supported at this time
            because I'm lazy and not going to try to guess what type is in your union (and it's not always possible
            in some scenarios).

            :param data: The dict
            :return: The AlarmOverrideUnion
        """
        unionobj = data['msg']

        uniontype, uniondict = self._from_union(unionobj)

        if uniontype == "org.jlab.jaws.entity.DisabledOverride":
            obj = DisabledOverride(uniondict['comments'])
        elif uniontype == "org.jlab.jaws.entity.FilteredOverride":
            obj = FilteredOverride(uniondict['filtername'])
        elif uniontype == "org.jlab.jaws.entity.LatchedOverride":
            obj = LatchedOverride()
        elif uniontype == "org.jlab.jaws.entity.MaskedOverride":
            obj = MaskedOverride()
        elif uniontype == "org.jlab.jaws.entity.OnDelayedOverride":
            obj = OnDelayedOverride(uniondict['expiration'])
        elif uniontype == "org.jlab.jaws.entity.OffDelayedOverride":
            obj = OffDelayedOverride(uniondict['expiration'])
        elif uniontype == "org.jlab.jaws.entity.ShelvedOverride":
            obj = ShelvedOverride(uniondict['expiration'], uniondict['comments'],
                                  _unwrap_enum(uniondict['reason'], ShelvedReason), uniondict['oneshot'])
        else:
            print("Unknown alarming type: {}".format(data['msg']))
            obj = None

        return AlarmOverrideUnion(obj)


class ProcessorTransitionsSerde(RegistryAvroSerde):
    """
        Provides ProcessorTransitions serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient):
        """
            Create a new ProcessorTransitionSerde.

            :param schema_registry_client: The SchemaRegistryClient
        """
        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/ProcessorTransition.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", [])

        super().__init__(schema_registry_client, schema, UnionEncoding.DICT_WITH_TYPE)

    def to_dict(self, data: ProcessorTransitions) -> Dict[str, bool]:
        """
            Converts ProcessorTransitions to a dict

            :param data: The ProcessorTransitions
            :return: A dict
        """
        return {
            "transitionToActive": data.transitionToActive,
            "transitionToNormal": data.transitionToNormal,
            "latching": data.latching,
            "unshelving": data.unshelving,
            "masking": data.masking,
            "unmasking": data.unmasking,
            "ondelaying": data.ondelaying,
            "offdelaying": data.offdelaying
        }

    def from_dict(self, data: Dict[str, bool]) -> ProcessorTransitions:
        """
        Converts a dict to ProcessorTransitions.

        :param data: The dict
        :return: The ProcessorTransitions
        """
        return ProcessorTransitions(data['transitionToActive'],
                                    data['transitionToNormal'],
                                    data['latching'],
                                    data['unshelving'],
                                    data['masking'],
                                    data['unmasking'],
                                    data['ondelaying'],
                                    data['offdelaying'])


class IntermediateMonologSerde(RegistryAvroWithReferencesSerde):
    """
        Provides IntermediateMonolog serde utilities
    """

    def __init__(self, schema_registry_client: SchemaRegistryClient,
                 union_encoding: UnionEncoding = UnionEncoding.DICT_WITH_TYPE):
        """
            Create a new IntermediateMonologSerde.

            :param schema_registry_client: The SchemaRegistryClient
            :param union_encoding: The union encoding to use
        """
        self._union_encoding = union_encoding
        self._effective_registration_serde = EffectiveRegistrationSerde(schema_registry_client)
        self._effective_activation_serde = EffectiveActivationSerde(schema_registry_client)
        self._processor_transition_serde = ProcessorTransitionsSerde(schema_registry_client)

        registration_schema_ref = SchemaReference("org.jlab.jaws.entity.EffectiveRegistration",
                                                  "effective-registrations-value", 1)
        activation_schema_ref = SchemaReference("org.jlab.jaws.entity.EffectiveActivation",
                                                "effective-activations-value", 1)
        transitions_schema_ref = SchemaReference("org.jlab.jaws.entity.ProcessorTransitions",
                                                 "processor-transitions", 1)

        references = [registration_schema_ref, activation_schema_ref, transitions_schema_ref]

        registrations_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveRegistration.avsc")
        registrations_schema_str = registrations_bytes.decode('utf-8')

        activation_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/EffectiveActivation.avsc")
        activation_schema_str = activation_bytes.decode('utf-8')

        transitions_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/ProcessorTransitions.avsc")
        transitions_schema_str = transitions_bytes.decode('utf-8')

        named_schemas = self._effective_registration_serde.named_schemas()
        named_schemas.update(self._effective_activation_serde.named_schemas())

        ref_dict = json.loads(registrations_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        ref_dict = json.loads(activation_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        ref_dict = json.loads(transitions_schema_str)
        fastavro.parse_schema(ref_dict, named_schemas=named_schemas)

        schema_bytes = pkgutil.get_data("jlab_jaws", "avro/schemas/IntermediateMonolog.avsc")
        schema_str = schema_bytes.decode('utf-8')

        schema = Schema(schema_str, "AVRO", references)

        super().__init__(schema_registry_client, schema, union_encoding, references, named_schemas)

    def to_dict(self, data: IntermediateMonolog) -> Dict[str, Any]:
        """
            Converts IntermediateMonolog to a dict.

            :param data: The IntermediateMonolog
            :return: A dict
        """
        return {
            "registration": self._effective_registration_serde.to_dict(data.registration),
            "activation": self._effective_activation_serde.to_dict(data.activation),
            "transitions": self._processor_transition_serde.to_dict(data.transitions)
        }

    def from_dict(self, data: Dict[str, Any]) -> IntermediateMonolog:
        """
            Converts a dict to IntermediateMonolog.

            :param data: The dict
            :return: The IntermediateMonolog
        """
        return IntermediateMonolog(self._effective_registration_serde.from_dict(data['registration']),
                                   self._effective_activation_serde.from_dict(data['activation']),
                                   self._processor_transition_serde.from_dict(data['transitions']))
