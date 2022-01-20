# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spaceone/api/config/v1/user_config.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2
from spaceone.api.core.v1 import query_pb2 as spaceone_dot_api_dot_core_dot_v1_dot_query__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='spaceone/api/config/v1/user_config.proto',
  package='spaceone.api.config.v1',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n(spaceone/api/config/v1/user_config.proto\x12\x16spaceone.api.config.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1cgoogle/api/annotations.proto\x1a spaceone/api/core/v1/query.proto\"\x88\x01\n\x17\x43reateUserConfigRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12%\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\x12%\n\x04tags\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x11\n\tdomain_id\x18\x04 \x01(\t\"\x88\x01\n\x17UpdateUserConfigRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12%\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\x12%\n\x04tags\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x11\n\tdomain_id\x18\x04 \x01(\t\"4\n\x11UserConfigRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\"E\n\x14GetUserConfigRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\x12\x0c\n\x04only\x18\x03 \x03(\t\"o\n\x0fUserConfigQuery\x12*\n\x05query\x18\x01 \x01(\x0b\x32\x1b.spaceone.api.core.v1.Query\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07user_id\x18\x03 \x01(\t\x12\x11\n\tdomain_id\x18\x04 \x01(\t\"\xa4\x01\n\x0eUserConfigInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12%\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\x12%\n\x04tags\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x0f\n\x07user_id\x18\x04 \x01(\t\x12\x11\n\tdomain_id\x18\x05 \x01(\t\x12\x12\n\ncreated_at\x18\x06 \x01(\t\"_\n\x0fUserConfigsInfo\x12\x37\n\x07results\x18\x01 \x03(\x0b\x32&.spaceone.api.config.v1.UserConfigInfo\x12\x13\n\x0btotal_count\x18\x02 \x01(\x05\"^\n\x13UserConfigStatQuery\x12\x34\n\x05query\x18\x01 \x01(\x0b\x32%.spaceone.api.core.v1.StatisticsQuery\x12\x11\n\tdomain_id\x18\x02 \x01(\t2\xa7\x06\n\nUserConfig\x12\x82\x01\n\x06\x63reate\x12/.spaceone.api.config.v1.CreateUserConfigRequest\x1a&.spaceone.api.config.v1.UserConfigInfo\"\x1f\x82\xd3\xe4\x93\x02\x19\"\x17/config/v1/user-configs\x12\x88\x01\n\x06update\x12/.spaceone.api.config.v1.UpdateUserConfigRequest\x1a&.spaceone.api.config.v1.UserConfigInfo\"%\x82\xd3\xe4\x93\x02\x1f\x1a\x1d/config/v1/user-config/{name}\x12r\n\x06\x64\x65lete\x12).spaceone.api.config.v1.UserConfigRequest\x1a\x16.google.protobuf.Empty\"%\x82\xd3\xe4\x93\x02\x1f*\x1d/config/v1/user-config/{name}\x12\x82\x01\n\x03get\x12,.spaceone.api.config.v1.GetUserConfigRequest\x1a&.spaceone.api.config.v1.UserConfigInfo\"%\x82\xd3\xe4\x93\x02\x1f\x12\x1d/config/v1/user-config/{name}\x12\x9b\x01\n\x04list\x12\'.spaceone.api.config.v1.UserConfigQuery\x1a\'.spaceone.api.config.v1.UserConfigsInfo\"A\x82\xd3\xe4\x93\x02;\x12\x17/config/v1/user-configsZ \"\x1e/config/v1/user-configs/search\x12r\n\x04stat\x12+.spaceone.api.config.v1.UserConfigStatQuery\x1a\x17.google.protobuf.Struct\"$\x82\xd3\xe4\x93\x02\x1e\"\x1c/config/v1/user-configs/statb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,google_dot_api_dot_annotations__pb2.DESCRIPTOR,spaceone_dot_api_dot_core_dot_v1_dot_query__pb2.DESCRIPTOR,])




_CREATEUSERCONFIGREQUEST = _descriptor.Descriptor(
  name='CreateUserConfigRequest',
  full_name='spaceone.api.config.v1.CreateUserConfigRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.CreateUserConfigRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='spaceone.api.config.v1.CreateUserConfigRequest.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='spaceone.api.config.v1.CreateUserConfigRequest.tags', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.CreateUserConfigRequest.domain_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=192,
  serialized_end=328,
)


_UPDATEUSERCONFIGREQUEST = _descriptor.Descriptor(
  name='UpdateUserConfigRequest',
  full_name='spaceone.api.config.v1.UpdateUserConfigRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.UpdateUserConfigRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='spaceone.api.config.v1.UpdateUserConfigRequest.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='spaceone.api.config.v1.UpdateUserConfigRequest.tags', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.UpdateUserConfigRequest.domain_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=331,
  serialized_end=467,
)


_USERCONFIGREQUEST = _descriptor.Descriptor(
  name='UserConfigRequest',
  full_name='spaceone.api.config.v1.UserConfigRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.UserConfigRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.UserConfigRequest.domain_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=469,
  serialized_end=521,
)


_GETUSERCONFIGREQUEST = _descriptor.Descriptor(
  name='GetUserConfigRequest',
  full_name='spaceone.api.config.v1.GetUserConfigRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.GetUserConfigRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.GetUserConfigRequest.domain_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='only', full_name='spaceone.api.config.v1.GetUserConfigRequest.only', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=523,
  serialized_end=592,
)


_USERCONFIGQUERY = _descriptor.Descriptor(
  name='UserConfigQuery',
  full_name='spaceone.api.config.v1.UserConfigQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='query', full_name='spaceone.api.config.v1.UserConfigQuery.query', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.UserConfigQuery.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='user_id', full_name='spaceone.api.config.v1.UserConfigQuery.user_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.UserConfigQuery.domain_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=594,
  serialized_end=705,
)


_USERCONFIGINFO = _descriptor.Descriptor(
  name='UserConfigInfo',
  full_name='spaceone.api.config.v1.UserConfigInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='spaceone.api.config.v1.UserConfigInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='spaceone.api.config.v1.UserConfigInfo.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='spaceone.api.config.v1.UserConfigInfo.tags', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='user_id', full_name='spaceone.api.config.v1.UserConfigInfo.user_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.UserConfigInfo.domain_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='created_at', full_name='spaceone.api.config.v1.UserConfigInfo.created_at', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=708,
  serialized_end=872,
)


_USERCONFIGSINFO = _descriptor.Descriptor(
  name='UserConfigsInfo',
  full_name='spaceone.api.config.v1.UserConfigsInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='results', full_name='spaceone.api.config.v1.UserConfigsInfo.results', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_count', full_name='spaceone.api.config.v1.UserConfigsInfo.total_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=874,
  serialized_end=969,
)


_USERCONFIGSTATQUERY = _descriptor.Descriptor(
  name='UserConfigStatQuery',
  full_name='spaceone.api.config.v1.UserConfigStatQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='query', full_name='spaceone.api.config.v1.UserConfigStatQuery.query', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.config.v1.UserConfigStatQuery.domain_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=971,
  serialized_end=1065,
)

_CREATEUSERCONFIGREQUEST.fields_by_name['data'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_CREATEUSERCONFIGREQUEST.fields_by_name['tags'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_UPDATEUSERCONFIGREQUEST.fields_by_name['data'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_UPDATEUSERCONFIGREQUEST.fields_by_name['tags'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_USERCONFIGQUERY.fields_by_name['query'].message_type = spaceone_dot_api_dot_core_dot_v1_dot_query__pb2._QUERY
_USERCONFIGINFO.fields_by_name['data'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_USERCONFIGINFO.fields_by_name['tags'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_USERCONFIGSINFO.fields_by_name['results'].message_type = _USERCONFIGINFO
_USERCONFIGSTATQUERY.fields_by_name['query'].message_type = spaceone_dot_api_dot_core_dot_v1_dot_query__pb2._STATISTICSQUERY
DESCRIPTOR.message_types_by_name['CreateUserConfigRequest'] = _CREATEUSERCONFIGREQUEST
DESCRIPTOR.message_types_by_name['UpdateUserConfigRequest'] = _UPDATEUSERCONFIGREQUEST
DESCRIPTOR.message_types_by_name['UserConfigRequest'] = _USERCONFIGREQUEST
DESCRIPTOR.message_types_by_name['GetUserConfigRequest'] = _GETUSERCONFIGREQUEST
DESCRIPTOR.message_types_by_name['UserConfigQuery'] = _USERCONFIGQUERY
DESCRIPTOR.message_types_by_name['UserConfigInfo'] = _USERCONFIGINFO
DESCRIPTOR.message_types_by_name['UserConfigsInfo'] = _USERCONFIGSINFO
DESCRIPTOR.message_types_by_name['UserConfigStatQuery'] = _USERCONFIGSTATQUERY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CreateUserConfigRequest = _reflection.GeneratedProtocolMessageType('CreateUserConfigRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEUSERCONFIGREQUEST,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.CreateUserConfigRequest)
  })
_sym_db.RegisterMessage(CreateUserConfigRequest)

UpdateUserConfigRequest = _reflection.GeneratedProtocolMessageType('UpdateUserConfigRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEUSERCONFIGREQUEST,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UpdateUserConfigRequest)
  })
_sym_db.RegisterMessage(UpdateUserConfigRequest)

UserConfigRequest = _reflection.GeneratedProtocolMessageType('UserConfigRequest', (_message.Message,), {
  'DESCRIPTOR' : _USERCONFIGREQUEST,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UserConfigRequest)
  })
_sym_db.RegisterMessage(UserConfigRequest)

GetUserConfigRequest = _reflection.GeneratedProtocolMessageType('GetUserConfigRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETUSERCONFIGREQUEST,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.GetUserConfigRequest)
  })
_sym_db.RegisterMessage(GetUserConfigRequest)

UserConfigQuery = _reflection.GeneratedProtocolMessageType('UserConfigQuery', (_message.Message,), {
  'DESCRIPTOR' : _USERCONFIGQUERY,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UserConfigQuery)
  })
_sym_db.RegisterMessage(UserConfigQuery)

UserConfigInfo = _reflection.GeneratedProtocolMessageType('UserConfigInfo', (_message.Message,), {
  'DESCRIPTOR' : _USERCONFIGINFO,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UserConfigInfo)
  })
_sym_db.RegisterMessage(UserConfigInfo)

UserConfigsInfo = _reflection.GeneratedProtocolMessageType('UserConfigsInfo', (_message.Message,), {
  'DESCRIPTOR' : _USERCONFIGSINFO,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UserConfigsInfo)
  })
_sym_db.RegisterMessage(UserConfigsInfo)

UserConfigStatQuery = _reflection.GeneratedProtocolMessageType('UserConfigStatQuery', (_message.Message,), {
  'DESCRIPTOR' : _USERCONFIGSTATQUERY,
  '__module__' : 'spaceone.api.config.v1.user_config_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.config.v1.UserConfigStatQuery)
  })
_sym_db.RegisterMessage(UserConfigStatQuery)



_USERCONFIG = _descriptor.ServiceDescriptor(
  name='UserConfig',
  full_name='spaceone.api.config.v1.UserConfig',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1068,
  serialized_end=1875,
  methods=[
  _descriptor.MethodDescriptor(
    name='create',
    full_name='spaceone.api.config.v1.UserConfig.create',
    index=0,
    containing_service=None,
    input_type=_CREATEUSERCONFIGREQUEST,
    output_type=_USERCONFIGINFO,
    serialized_options=b'\202\323\344\223\002\031\"\027/config/v1/user-configs',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='update',
    full_name='spaceone.api.config.v1.UserConfig.update',
    index=1,
    containing_service=None,
    input_type=_UPDATEUSERCONFIGREQUEST,
    output_type=_USERCONFIGINFO,
    serialized_options=b'\202\323\344\223\002\037\032\035/config/v1/user-config/{name}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='delete',
    full_name='spaceone.api.config.v1.UserConfig.delete',
    index=2,
    containing_service=None,
    input_type=_USERCONFIGREQUEST,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=b'\202\323\344\223\002\037*\035/config/v1/user-config/{name}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='get',
    full_name='spaceone.api.config.v1.UserConfig.get',
    index=3,
    containing_service=None,
    input_type=_GETUSERCONFIGREQUEST,
    output_type=_USERCONFIGINFO,
    serialized_options=b'\202\323\344\223\002\037\022\035/config/v1/user-config/{name}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='list',
    full_name='spaceone.api.config.v1.UserConfig.list',
    index=4,
    containing_service=None,
    input_type=_USERCONFIGQUERY,
    output_type=_USERCONFIGSINFO,
    serialized_options=b'\202\323\344\223\002;\022\027/config/v1/user-configsZ \"\036/config/v1/user-configs/search',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='stat',
    full_name='spaceone.api.config.v1.UserConfig.stat',
    index=5,
    containing_service=None,
    input_type=_USERCONFIGSTATQUERY,
    output_type=google_dot_protobuf_dot_struct__pb2._STRUCT,
    serialized_options=b'\202\323\344\223\002\036\"\034/config/v1/user-configs/stat',
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_USERCONFIG)

DESCRIPTOR.services_by_name['UserConfig'] = _USERCONFIG

# @@protoc_insertion_point(module_scope)
