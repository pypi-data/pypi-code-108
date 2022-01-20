# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pass_desc.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import framework_pb2 as framework__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pass_desc.proto',
  package='paddle.framework.proto',
  syntax='proto2',
  serialized_pb=_b('\n\x0fpass_desc.proto\x12\x16paddle.framework.proto\x1a\x0f\x66ramework.proto\"\x89\x03\n\x08PassDesc\x12\x34\n\x07pattern\x18\x01 \x02(\x0b\x32#.paddle.framework.proto.ProgramDesc\x12\x34\n\x07replace\x18\x02 \x02(\x0b\x32#.paddle.framework.proto.ProgramDesc\x12\x39\n\x08var_maps\x18\x03 \x03(\x0b\x32\'.paddle.framework.proto.PassDesc.VarMap\x12;\n\tattr_maps\x18\x04 \x03(\x0b\x32(.paddle.framework.proto.PassDesc.AttrMap\x1a\x32\n\x06VarMap\x12\x13\n\x0bpattern_var\x18\x01 \x02(\t\x12\x13\n\x0breplace_var\x18\x02 \x02(\t\x1a\x65\n\x07\x41ttrMap\x12\x16\n\x0epattern_op_idx\x18\x01 \x02(\x05\x12\x16\n\x0ereplace_op_idx\x18\x02 \x02(\x05\x12\x14\n\x0cpattern_name\x18\x03 \x02(\t\x12\x14\n\x0creplace_name\x18\x04 \x02(\t\"X\n\rMultiPassDesc\x12\x11\n\tpass_type\x18\x01 \x01(\t\x12\x34\n\npass_descs\x18\x02 \x03(\x0b\x32 .paddle.framework.proto.PassDesc')
  ,
  dependencies=[framework__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PASSDESC_VARMAP = _descriptor.Descriptor(
  name='VarMap',
  full_name='paddle.framework.proto.PassDesc.VarMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pattern_var', full_name='paddle.framework.proto.PassDesc.VarMap.pattern_var', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='replace_var', full_name='paddle.framework.proto.PassDesc.VarMap.replace_var', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=301,
  serialized_end=351,
)

_PASSDESC_ATTRMAP = _descriptor.Descriptor(
  name='AttrMap',
  full_name='paddle.framework.proto.PassDesc.AttrMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pattern_op_idx', full_name='paddle.framework.proto.PassDesc.AttrMap.pattern_op_idx', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='replace_op_idx', full_name='paddle.framework.proto.PassDesc.AttrMap.replace_op_idx', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pattern_name', full_name='paddle.framework.proto.PassDesc.AttrMap.pattern_name', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='replace_name', full_name='paddle.framework.proto.PassDesc.AttrMap.replace_name', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=353,
  serialized_end=454,
)

_PASSDESC = _descriptor.Descriptor(
  name='PassDesc',
  full_name='paddle.framework.proto.PassDesc',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pattern', full_name='paddle.framework.proto.PassDesc.pattern', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='replace', full_name='paddle.framework.proto.PassDesc.replace', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='var_maps', full_name='paddle.framework.proto.PassDesc.var_maps', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='attr_maps', full_name='paddle.framework.proto.PassDesc.attr_maps', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_PASSDESC_VARMAP, _PASSDESC_ATTRMAP, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=454,
)


_MULTIPASSDESC = _descriptor.Descriptor(
  name='MultiPassDesc',
  full_name='paddle.framework.proto.MultiPassDesc',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pass_type', full_name='paddle.framework.proto.MultiPassDesc.pass_type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pass_descs', full_name='paddle.framework.proto.MultiPassDesc.pass_descs', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=456,
  serialized_end=544,
)

_PASSDESC_VARMAP.containing_type = _PASSDESC
_PASSDESC_ATTRMAP.containing_type = _PASSDESC
_PASSDESC.fields_by_name['pattern'].message_type = framework__pb2._PROGRAMDESC
_PASSDESC.fields_by_name['replace'].message_type = framework__pb2._PROGRAMDESC
_PASSDESC.fields_by_name['var_maps'].message_type = _PASSDESC_VARMAP
_PASSDESC.fields_by_name['attr_maps'].message_type = _PASSDESC_ATTRMAP
_MULTIPASSDESC.fields_by_name['pass_descs'].message_type = _PASSDESC
DESCRIPTOR.message_types_by_name['PassDesc'] = _PASSDESC
DESCRIPTOR.message_types_by_name['MultiPassDesc'] = _MULTIPASSDESC

PassDesc = _reflection.GeneratedProtocolMessageType('PassDesc', (_message.Message,), dict(

  VarMap = _reflection.GeneratedProtocolMessageType('VarMap', (_message.Message,), dict(
    DESCRIPTOR = _PASSDESC_VARMAP,
    __module__ = 'pass_desc_pb2'
    # @@protoc_insertion_point(class_scope:paddle.framework.proto.PassDesc.VarMap)
    ))
  ,

  AttrMap = _reflection.GeneratedProtocolMessageType('AttrMap', (_message.Message,), dict(
    DESCRIPTOR = _PASSDESC_ATTRMAP,
    __module__ = 'pass_desc_pb2'
    # @@protoc_insertion_point(class_scope:paddle.framework.proto.PassDesc.AttrMap)
    ))
  ,
  DESCRIPTOR = _PASSDESC,
  __module__ = 'pass_desc_pb2'
  # @@protoc_insertion_point(class_scope:paddle.framework.proto.PassDesc)
  ))
_sym_db.RegisterMessage(PassDesc)
_sym_db.RegisterMessage(PassDesc.VarMap)
_sym_db.RegisterMessage(PassDesc.AttrMap)

MultiPassDesc = _reflection.GeneratedProtocolMessageType('MultiPassDesc', (_message.Message,), dict(
  DESCRIPTOR = _MULTIPASSDESC,
  __module__ = 'pass_desc_pb2'
  # @@protoc_insertion_point(class_scope:paddle.framework.proto.MultiPassDesc)
  ))
_sym_db.RegisterMessage(MultiPassDesc)


# @@protoc_insertion_point(module_scope)
