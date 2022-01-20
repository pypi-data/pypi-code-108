# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spaceone/api/cost_analysis/v1/job.proto
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
  name='spaceone/api/cost_analysis/v1/job.proto',
  package='spaceone.api.cost_analysis.v1',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\'spaceone/api/cost_analysis/v1/job.proto\x12\x1dspaceone.api.cost_analysis.v1\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1cgoogle/api/annotations.proto\x1a spaceone/api/core/v1/query.proto\"/\n\nJobRequest\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\"@\n\rGetJobRequest\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12\x11\n\tdomain_id\x18\x02 \x01(\t\x12\x0c\n\x04only\x18\x03 \x03(\t\"\x91\x02\n\x08JobQuery\x12*\n\x05query\x18\x01 \x01(\x0b\x32\x1b.spaceone.api.core.v1.Query\x12\x0e\n\x06job_id\x18\x02 \x01(\t\x12>\n\x06status\x18\x03 \x01(\x0e\x32..spaceone.api.cost_analysis.v1.JobQuery.Status\x12\x16\n\x0e\x64\x61ta_source_id\x18\x0b \x01(\t\x12\x11\n\tdomain_id\x18\x0c \x01(\t\"^\n\x06Status\x12\x0e\n\nSCOPE_NONE\x10\x00\x12\x0f\n\x0bIN_PROGRESS\x10\x01\x12\x0b\n\x07SUCCESS\x10\x02\x12\x0b\n\x07\x46\x41ILURE\x10\x03\x12\x0b\n\x07TIMEOUT\x10\x04\x12\x0c\n\x08\x43\x41NCELED\x10\x05\")\n\x0b\x43hangedInfo\x12\r\n\x05start\x18\x01 \x01(\t\x12\x0b\n\x03\x65nd\x18\x02 \x01(\t\"\xb5\x03\n\x07JobInfo\x12\x0e\n\x06job_id\x18\x01 \x01(\t\x12=\n\x06status\x18\x02 \x01(\x0e\x32-.spaceone.api.cost_analysis.v1.JobInfo.Status\x12\x12\n\nerror_code\x18\x03 \x01(\t\x12\x15\n\rerror_message\x18\x04 \x01(\t\x12\x13\n\x0btotal_tasks\x18\x05 \x01(\x05\x12\x16\n\x0eremained_tasks\x18\x06 \x01(\x05\x12\x16\n\x0e\x64\x61ta_source_id\x18\x0b \x01(\t\x12\x11\n\tdomain_id\x18\x0c \x01(\t\x12\x12\n\ncreated_at\x18\x15 \x01(\t\x12\x12\n\nupdated_at\x18\x16 \x01(\t\x12\x13\n\x0b\x66inished_at\x18\x17 \x01(\t\x12;\n\x07\x63hanged\x18\x18 \x03(\x0b\x32*.spaceone.api.cost_analysis.v1.ChangedInfo\"^\n\x06Status\x12\x0e\n\nSCOPE_NONE\x10\x00\x12\x0f\n\x0bIN_PROGRESS\x10\x01\x12\x0b\n\x07SUCCESS\x10\x02\x12\x0b\n\x07\x46\x41ILURE\x10\x03\x12\x0b\n\x07TIMEOUT\x10\x04\x12\x0c\n\x08\x43\x41NCELED\x10\x05\"X\n\x08JobsInfo\x12\x37\n\x07results\x18\x01 \x03(\x0b\x32&.spaceone.api.cost_analysis.v1.JobInfo\x12\x13\n\x0btotal_count\x18\x02 \x01(\x05\"W\n\x0cJobStatQuery\x12\x34\n\x05query\x18\x01 \x01(\x0b\x32%.spaceone.api.core.v1.StatisticsQuery\x12\x11\n\tdomain_id\x18\x02 \x01(\t2\xa7\x04\n\x03Job\x12\x8a\x01\n\x06\x63\x61ncel\x12).spaceone.api.cost_analysis.v1.JobRequest\x1a&.spaceone.api.cost_analysis.v1.JobInfo\"-\x82\xd3\xe4\x93\x02\'\"%/cost-analysis/v1/job/{job_id}/cancel\x12\x83\x01\n\x03get\x12,.spaceone.api.cost_analysis.v1.GetJobRequest\x1a&.spaceone.api.cost_analysis.v1.JobInfo\"&\x82\xd3\xe4\x93\x02 \x12\x1e/cost-analysis/v1/job/{job_id}\x12\x99\x01\n\x04list\x12\'.spaceone.api.cost_analysis.v1.JobQuery\x1a\'.spaceone.api.cost_analysis.v1.JobsInfo\"?\x82\xd3\xe4\x93\x02\x39\x12\x16/cost-analysis/v1/jobsZ\x1f\"\x1d/cost-analysis/v1/jobs/search\x12q\n\x04stat\x12+.spaceone.api.cost_analysis.v1.JobStatQuery\x1a\x17.google.protobuf.Struct\"#\x82\xd3\xe4\x93\x02\x1d\"\x1b/cost-analysis/v1/jobs/statb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,google_dot_api_dot_annotations__pb2.DESCRIPTOR,spaceone_dot_api_dot_core_dot_v1_dot_query__pb2.DESCRIPTOR,])



_JOBQUERY_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='spaceone.api.cost_analysis.v1.JobQuery.Status',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SCOPE_NONE', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='IN_PROGRESS', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FAILURE', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TIMEOUT', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CANCELED', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=492,
  serialized_end=586,
)
_sym_db.RegisterEnumDescriptor(_JOBQUERY_STATUS)

_JOBINFO_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='spaceone.api.cost_analysis.v1.JobInfo.Status',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SCOPE_NONE', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='IN_PROGRESS', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FAILURE', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TIMEOUT', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CANCELED', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=492,
  serialized_end=586,
)
_sym_db.RegisterEnumDescriptor(_JOBINFO_STATUS)


_JOBREQUEST = _descriptor.Descriptor(
  name='JobRequest',
  full_name='spaceone.api.cost_analysis.v1.JobRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='job_id', full_name='spaceone.api.cost_analysis.v1.JobRequest.job_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.cost_analysis.v1.JobRequest.domain_id', index=1,
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
  serialized_start=197,
  serialized_end=244,
)


_GETJOBREQUEST = _descriptor.Descriptor(
  name='GetJobRequest',
  full_name='spaceone.api.cost_analysis.v1.GetJobRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='job_id', full_name='spaceone.api.cost_analysis.v1.GetJobRequest.job_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.cost_analysis.v1.GetJobRequest.domain_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='only', full_name='spaceone.api.cost_analysis.v1.GetJobRequest.only', index=2,
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
  serialized_start=246,
  serialized_end=310,
)


_JOBQUERY = _descriptor.Descriptor(
  name='JobQuery',
  full_name='spaceone.api.cost_analysis.v1.JobQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='query', full_name='spaceone.api.cost_analysis.v1.JobQuery.query', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='job_id', full_name='spaceone.api.cost_analysis.v1.JobQuery.job_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='spaceone.api.cost_analysis.v1.JobQuery.status', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data_source_id', full_name='spaceone.api.cost_analysis.v1.JobQuery.data_source_id', index=3,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.cost_analysis.v1.JobQuery.domain_id', index=4,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _JOBQUERY_STATUS,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=313,
  serialized_end=586,
)


_CHANGEDINFO = _descriptor.Descriptor(
  name='ChangedInfo',
  full_name='spaceone.api.cost_analysis.v1.ChangedInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='start', full_name='spaceone.api.cost_analysis.v1.ChangedInfo.start', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='end', full_name='spaceone.api.cost_analysis.v1.ChangedInfo.end', index=1,
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
  serialized_start=588,
  serialized_end=629,
)


_JOBINFO = _descriptor.Descriptor(
  name='JobInfo',
  full_name='spaceone.api.cost_analysis.v1.JobInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='job_id', full_name='spaceone.api.cost_analysis.v1.JobInfo.job_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='spaceone.api.cost_analysis.v1.JobInfo.status', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error_code', full_name='spaceone.api.cost_analysis.v1.JobInfo.error_code', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='spaceone.api.cost_analysis.v1.JobInfo.error_message', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_tasks', full_name='spaceone.api.cost_analysis.v1.JobInfo.total_tasks', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='remained_tasks', full_name='spaceone.api.cost_analysis.v1.JobInfo.remained_tasks', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data_source_id', full_name='spaceone.api.cost_analysis.v1.JobInfo.data_source_id', index=6,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.cost_analysis.v1.JobInfo.domain_id', index=7,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='created_at', full_name='spaceone.api.cost_analysis.v1.JobInfo.created_at', index=8,
      number=21, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='updated_at', full_name='spaceone.api.cost_analysis.v1.JobInfo.updated_at', index=9,
      number=22, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='finished_at', full_name='spaceone.api.cost_analysis.v1.JobInfo.finished_at', index=10,
      number=23, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='changed', full_name='spaceone.api.cost_analysis.v1.JobInfo.changed', index=11,
      number=24, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _JOBINFO_STATUS,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=632,
  serialized_end=1069,
)


_JOBSINFO = _descriptor.Descriptor(
  name='JobsInfo',
  full_name='spaceone.api.cost_analysis.v1.JobsInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='results', full_name='spaceone.api.cost_analysis.v1.JobsInfo.results', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_count', full_name='spaceone.api.cost_analysis.v1.JobsInfo.total_count', index=1,
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
  serialized_start=1071,
  serialized_end=1159,
)


_JOBSTATQUERY = _descriptor.Descriptor(
  name='JobStatQuery',
  full_name='spaceone.api.cost_analysis.v1.JobStatQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='query', full_name='spaceone.api.cost_analysis.v1.JobStatQuery.query', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='domain_id', full_name='spaceone.api.cost_analysis.v1.JobStatQuery.domain_id', index=1,
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
  serialized_start=1161,
  serialized_end=1248,
)

_JOBQUERY.fields_by_name['query'].message_type = spaceone_dot_api_dot_core_dot_v1_dot_query__pb2._QUERY
_JOBQUERY.fields_by_name['status'].enum_type = _JOBQUERY_STATUS
_JOBQUERY_STATUS.containing_type = _JOBQUERY
_JOBINFO.fields_by_name['status'].enum_type = _JOBINFO_STATUS
_JOBINFO.fields_by_name['changed'].message_type = _CHANGEDINFO
_JOBINFO_STATUS.containing_type = _JOBINFO
_JOBSINFO.fields_by_name['results'].message_type = _JOBINFO
_JOBSTATQUERY.fields_by_name['query'].message_type = spaceone_dot_api_dot_core_dot_v1_dot_query__pb2._STATISTICSQUERY
DESCRIPTOR.message_types_by_name['JobRequest'] = _JOBREQUEST
DESCRIPTOR.message_types_by_name['GetJobRequest'] = _GETJOBREQUEST
DESCRIPTOR.message_types_by_name['JobQuery'] = _JOBQUERY
DESCRIPTOR.message_types_by_name['ChangedInfo'] = _CHANGEDINFO
DESCRIPTOR.message_types_by_name['JobInfo'] = _JOBINFO
DESCRIPTOR.message_types_by_name['JobsInfo'] = _JOBSINFO
DESCRIPTOR.message_types_by_name['JobStatQuery'] = _JOBSTATQUERY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

JobRequest = _reflection.GeneratedProtocolMessageType('JobRequest', (_message.Message,), {
  'DESCRIPTOR' : _JOBREQUEST,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.JobRequest)
  })
_sym_db.RegisterMessage(JobRequest)

GetJobRequest = _reflection.GeneratedProtocolMessageType('GetJobRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETJOBREQUEST,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.GetJobRequest)
  })
_sym_db.RegisterMessage(GetJobRequest)

JobQuery = _reflection.GeneratedProtocolMessageType('JobQuery', (_message.Message,), {
  'DESCRIPTOR' : _JOBQUERY,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.JobQuery)
  })
_sym_db.RegisterMessage(JobQuery)

ChangedInfo = _reflection.GeneratedProtocolMessageType('ChangedInfo', (_message.Message,), {
  'DESCRIPTOR' : _CHANGEDINFO,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.ChangedInfo)
  })
_sym_db.RegisterMessage(ChangedInfo)

JobInfo = _reflection.GeneratedProtocolMessageType('JobInfo', (_message.Message,), {
  'DESCRIPTOR' : _JOBINFO,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.JobInfo)
  })
_sym_db.RegisterMessage(JobInfo)

JobsInfo = _reflection.GeneratedProtocolMessageType('JobsInfo', (_message.Message,), {
  'DESCRIPTOR' : _JOBSINFO,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.JobsInfo)
  })
_sym_db.RegisterMessage(JobsInfo)

JobStatQuery = _reflection.GeneratedProtocolMessageType('JobStatQuery', (_message.Message,), {
  'DESCRIPTOR' : _JOBSTATQUERY,
  '__module__' : 'spaceone.api.cost_analysis.v1.job_pb2'
  # @@protoc_insertion_point(class_scope:spaceone.api.cost_analysis.v1.JobStatQuery)
  })
_sym_db.RegisterMessage(JobStatQuery)



_JOB = _descriptor.ServiceDescriptor(
  name='Job',
  full_name='spaceone.api.cost_analysis.v1.Job',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1251,
  serialized_end=1802,
  methods=[
  _descriptor.MethodDescriptor(
    name='cancel',
    full_name='spaceone.api.cost_analysis.v1.Job.cancel',
    index=0,
    containing_service=None,
    input_type=_JOBREQUEST,
    output_type=_JOBINFO,
    serialized_options=b'\202\323\344\223\002\'\"%/cost-analysis/v1/job/{job_id}/cancel',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='get',
    full_name='spaceone.api.cost_analysis.v1.Job.get',
    index=1,
    containing_service=None,
    input_type=_GETJOBREQUEST,
    output_type=_JOBINFO,
    serialized_options=b'\202\323\344\223\002 \022\036/cost-analysis/v1/job/{job_id}',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='list',
    full_name='spaceone.api.cost_analysis.v1.Job.list',
    index=2,
    containing_service=None,
    input_type=_JOBQUERY,
    output_type=_JOBSINFO,
    serialized_options=b'\202\323\344\223\0029\022\026/cost-analysis/v1/jobsZ\037\"\035/cost-analysis/v1/jobs/search',
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='stat',
    full_name='spaceone.api.cost_analysis.v1.Job.stat',
    index=3,
    containing_service=None,
    input_type=_JOBSTATQUERY,
    output_type=google_dot_protobuf_dot_struct__pb2._STRUCT,
    serialized_options=b'\202\323\344\223\002\035\"\033/cost-analysis/v1/jobs/stat',
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_JOB)

DESCRIPTOR.services_by_name['Job'] = _JOB

# @@protoc_insertion_point(module_scope)
