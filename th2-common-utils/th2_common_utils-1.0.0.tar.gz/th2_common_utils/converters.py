# Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import enum
from typing import List, Callable

from google.protobuf.duration_pb2 import Duration
from th2_grpc_common.common_pb2 import Message, ListValue, Value, MessageMetadata, MessageID, ConnectionID, \
    RootMessageFilter, MessageFilter, MetadataFilter, RootComparisonSettings, ValueFilter, ListValueFilter, SimpleList


class ValueType(str, enum.Enum):
    WHICH_ONE_OF = 'kind'

    SIMPLE = 'simple_value'
    LIST = 'list_value'
    MESSAGE = 'message_value'


def message_to_dict_convert_value(value):
    value_kind = value.WhichOneof(ValueType.WHICH_ONE_OF)
    if value_kind == ValueType.SIMPLE:
        return value.simple_value
    elif value_kind == ValueType.LIST:
        return [message_to_dict_convert_value(list_item) for list_item in value.list_value.values]
    elif value_kind == ValueType.MESSAGE:
        return {field: message_to_dict_convert_value(value.message_value.fields[field])
                for field in value.message_value.fields}


def message_to_dict(message: Message):
    # Note, you will lose all metadata of the Message.
    return {field: message_to_dict_convert_value(message.fields[field]) for field in message.fields}


def dict_to_message_convert_value(value):
    if isinstance(value, Value):
        return value
    elif isinstance(value, (str, int, float)):
        return Value(simple_value=str(value))
    elif isinstance(value, list):
        return Value(list_value=ListValue(values=[dict_to_message_convert_value(x) for x in value]))
    elif isinstance(value, dict):
        return Value(message_value=Message(fields={key: dict_to_message_convert_value(value[key]) for key in value}))


def dict_to_message(fields: dict, session_alias=None, message_type=None):
    return Message(metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias=session_alias)),
                                            message_type=message_type),
                   fields={field: dict_to_message_convert_value(fields[field]) for field in fields})


def convert_filter_value(value, message_type=None, direction=None, values=False, metadata=False):
    if isinstance(value, ValueFilter):
        return value
    elif isinstance(value, (str, int, float)) and values is True:
        return ValueFilter(simple_filter=str(value))
    elif isinstance(value, (str, int, float)) and metadata is True:
        return MetadataFilter.SimpleFilter(value=str(value))
    elif isinstance(value, list) and values is True:
        return ValueFilter(list_filter=ListValueFilter(
            values=[convert_filter_value(x, values=values, metadata=metadata) for x in value]))
    elif isinstance(value, list) and metadata is True:
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=value))
    elif isinstance(value, dict):
        return ValueFilter(
            message_filter=MessageFilter(messageType=message_type,
                                         fields={key: convert_filter_value(value[key],
                                                                           values=values,
                                                                           metadata=metadata)
                                                 for key in value},
                                         direction=direction))


def dict_to_root_message_filter(message_type=None,
                                message_filter=None,
                                metadata_filter=None,
                                ignore_fields: List[str] = None,
                                check_repeating_group_order: bool = None,
                                time_precision: Duration = None,
                                decimal_precision: str = None):
    if message_filter is None:
        message_filter = {}
    if metadata_filter is None:
        metadata_filter = {}
    return RootMessageFilter(messageType=message_type,
                             message_filter=MessageFilter(fields={
                                 field: convert_filter_value(message_filter[field], values=True)
                                 for field in message_filter}),
                             metadata_filter=MetadataFilter(property_filters={
                                 value: convert_filter_value(metadata_filter[value], metadata=True)
                                 for value in metadata_filter}),
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))


def convert_value_into_typed_field(value, typed_value):
    field_value_kind = value.WhichOneof(ValueType.WHICH_ONE_OF)
    if field_value_kind == ValueType.SIMPLE:
        return type(typed_value)(value.simple_value)
    elif field_value_kind == ValueType.LIST:
        return [convert_value_into_typed_field(list_item, typed_value.add()) for list_item in value.list_value.values]
    elif field_value_kind == ValueType.MESSAGE:
        fields_typed = {
            field: convert_value_into_typed_field(value.message_value.fields[field], getattr(typed_value, field))
            for field in value.message_value.fields
        }
        return type(typed_value)(**fields_typed)


def message_to_typed_message(message, message_type: Callable):
    response_fields = [field.name for field in message_type().DESCRIPTOR.fields]
    fields_typed = {field: convert_value_into_typed_field(message.fields[field], getattr(message_type(), field))
                    for field in response_fields}
    return message_type(**fields_typed)
