import base64
import datetime

import json
from json import JSONEncoder

from google.protobuf.json_format import MessageToJson, ParseDict
from google.protobuf.descriptor import FieldDescriptor

from databricks_registry_webhooks.exceptions import RegistryWebhooksException 
from collections import defaultdict
from functools import partial


_PROTOBUF_INT64_FIELDS = [
    FieldDescriptor.TYPE_INT64,
    FieldDescriptor.TYPE_UINT64,
    FieldDescriptor.TYPE_FIXED64,
    FieldDescriptor.TYPE_SFIXED64,
    FieldDescriptor.TYPE_SINT64,
]


def _mark_int64_fields_for_proto_maps(proto_map, value_field_type):
    """Converts a proto map to JSON, preserving only int64-related fields."""
    json_dict = {}
    for key, value in proto_map.items():
        # The value of a protobuf map can only be a scalar or a message (not a map or repeated
        # field).
        if value_field_type == FieldDescriptor.TYPE_MESSAGE:
            json_dict[key] = _mark_int64_fields(value)
        elif value_field_type in _PROTOBUF_INT64_FIELDS:
            json_dict[key] = int(value)
        elif isinstance(key, int):
            json_dict[key] = value
    return json_dict


def _mark_int64_fields(proto_message):
    """Converts a proto message to JSON, preserving only int64-related fields."""
    json_dict = {}
    for field, value in proto_message.ListFields():
        if (
            # These three conditions check if this field is a protobuf map.
            # See the official implementation: https://bit.ly/3EMx1rl
            field.type == FieldDescriptor.TYPE_MESSAGE
            and field.message_type.has_options
            and field.message_type.GetOptions().map_entry
        ):
            # Deal with proto map fields separately in another function.
            json_dict[field.name] = _mark_int64_fields_for_proto_maps(
                value, field.message_type.fields_by_name["value"].type
            )
            continue

        if field.type == FieldDescriptor.TYPE_MESSAGE:
            ftype = partial(_mark_int64_fields)
        elif field.type in _PROTOBUF_INT64_FIELDS:
            ftype = int
        else:
            # Skip all non-int64 fields.
            continue

        json_dict[field.name] = (
            [ftype(v) for v in value]
            if field.label == FieldDescriptor.LABEL_REPEATED
            else ftype(value)
        )
    return json_dict


def _merge_json_dicts(from_dict, to_dict):
    """Merges the json elements of from_dict into to_dict. Only works for json dicts
    converted from proto messages
    """
    for key, value in from_dict.items():
        if isinstance(key, int) and str(key) in to_dict:
            # When the key (i.e. the proto field name) is an integer, it must be a proto map field
            # with integer as the key. For example:
            # from_dict is {'field_map': {1: '2', 3: '4'}}
            # to_dict is {'field_map': {'1': '2', '3': '4'}}
            # So we need to replace the str keys with int keys in to_dict.
            to_dict[key] = to_dict[str(key)]
            del to_dict[str(key)]

        if key not in to_dict:
            continue

        if isinstance(value, dict):
            _merge_json_dicts(from_dict[key], to_dict[key])
        elif isinstance(value, list):
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    _merge_json_dicts(v, to_dict[key][i])
                else:
                    to_dict[key][i] = v
        else:
            to_dict[key] = from_dict[key]
    return to_dict


def message_to_json(message):
    """Converts a message to JSON, using snake_case for field names."""

    # Google's MessageToJson API converts int64 proto fields to JSON strings.
    # For more info, see https://github.com/protocolbuffers/protobuf/issues/2954
    json_dict_with_int64_as_str = json.loads(
        MessageToJson(message, preserving_proto_field_name=True)
    )
    # We convert this proto message into a JSON dict where only int64 proto fields
    # are preserved, and they are treated as JSON numbers, not strings.
    json_dict_with_int64_fields_only = _mark_int64_fields(message)
    # By merging these two JSON dicts, we end up with a JSON dict where int64 proto fields are not
    # converted to JSON strings. Int64 keys in proto maps will always be converted to JSON strings
    # because JSON doesn't support non-string keys.
    json_dict_with_int64_as_numbers = _merge_json_dicts(
        json_dict_with_int64_fields_only, json_dict_with_int64_as_str
    )
    return json.dumps(json_dict_with_int64_as_numbers, indent=2)


def parse_dict(js_dict, message):
    """Parses a JSON dictionary into a message proto, ignoring unknown fields in the JSON."""
    ParseDict(js_dict=js_dict, message=message, ignore_unknown_fields=True)
