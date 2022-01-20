# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: masterful/proto/metadata.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='masterful/proto/metadata.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x1emasterful/proto/metadata.proto\"\xc9\x07\n\x0b\x44\x61tasetSpec\x12!\n\x05split\x18\x01 \x01(\x0e\x32\x12.DatasetSpec.Split\x12\r\n\x05title\x18\x02 \x01(\t\x12\x19\n\x11total_cardinality\x18\x03 \x01(\x03\x12\x19\n\x11train_cardinality\x18\x04 \x01(\x03\x12\x17\n\x0fval_cardinality\x18\x05 \x01(\x03\x12\x18\n\x10test_cardinality\x18\x06 \x01(\x03\x12/\n\nlabels_map\x18\x07 \x03(\x0b\x32\x1b.DatasetSpec.LabelsMapEntry\x12J\n\x18total_label_distribution\x18\x08 \x03(\x0b\x32(.DatasetSpec.TotalLabelDistributionEntry\x12J\n\x18train_label_distribution\x18\t \x03(\x0b\x32(.DatasetSpec.TrainLabelDistributionEntry\x12\x46\n\x16val_label_distribution\x18\n \x03(\x0b\x32&.DatasetSpec.ValLabelDistributionEntry\x12H\n\x17test_label_distribution\x18\x0b \x03(\x0b\x32\'.DatasetSpec.TestLabelDistributionEntry\x12\x1e\n\nimage_spec\x18\x0c \x01(\x0b\x32\n.ImageSpec\x12!\n\x04task\x18\r \x01(\x0e\x32\x13.ComputerVisionTask\x12\x13\n\x0bnum_classes\x18\x0e \x01(\x05\x1a\x30\n\x0eLabelsMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a=\n\x1bTotalLabelDistributionEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\x1a=\n\x1bTrainLabelDistributionEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\x1a;\n\x19ValLabelDistributionEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\x1a<\n\x1aTestLabelDistributionEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\"A\n\x05Split\x12\x11\n\rSPLIT_UNKNOWN\x10\x00\x12\x07\n\x03\x41LL\x10\x01\x12\t\n\x05TRAIN\x10\x02\x12\x07\n\x03VAL\x10\x03\x12\x08\n\x04TEST\x10\x04\"\x91\x02\n\tImageSpec\x12$\n\x05range\x18\x01 \x01(\x0e\x32\x15.ImageSpec.ImageRange\x12\r\n\x05width\x18\x02 \x01(\x05\x12\x0e\n\x06height\x18\x03 \x01(\x05\x12\x10\n\x08\x63hannels\x18\x04 \x01(\t\x12\x15\n\rchannels_last\x18\x05 \x01(\x08\"\x95\x01\n\nImageRange\x12\x17\n\x13IMAGE_RANGE_UNKNOWN\x10\x00\x12\x0c\n\x08ZERO_ONE\x10\x01\x12\x13\n\x0fNEG_ONE_POS_ONE\x10\x02\x12\x0c\n\x08ZERO_255\x10\x03\x12\x16\n\x12IMAGENET_CAFFE_BGR\x10\x04\x12\x12\n\x0eIMAGENET_TORCH\x10\x05\x12\x11\n\rCIFAR10_TORCH\x10\x06*\xf3\x01\n\x12\x43omputerVisionTask\x12 \n\x1c\x43OMPUTER_VISION_TASK_UNKNOWN\x10\x00\x12\x12\n\x0e\x43LASSIFICATION\x10\x01\x12\x19\n\x15\x42INARY_CLASSIFICATION\x10\x02\x12\x1d\n\x19MULTILABEL_CLASSIFICATION\x10\x03\x12\r\n\tDETECTION\x10\x04\x12\x10\n\x0cLOCALIZATION\x10\x05\x12\x19\n\x15SEMANTIC_SEGMENTATION\x10\x06\x12\x19\n\x15INSTANCE_SEGMENTATION\x10\x07\x12\x16\n\x12KEYPOINT_DETECTION\x10\x08\x62\x06proto3')
)

_COMPUTERVISIONTASK = _descriptor.EnumDescriptor(
  name='ComputerVisionTask',
  full_name='ComputerVisionTask',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='COMPUTER_VISION_TASK_UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLASSIFICATION', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BINARY_CLASSIFICATION', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MULTILABEL_CLASSIFICATION', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DETECTION', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOCALIZATION', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SEMANTIC_SEGMENTATION', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INSTANCE_SEGMENTATION', index=7, number=7,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='KEYPOINT_DETECTION', index=8, number=8,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1283,
  serialized_end=1526,
)
_sym_db.RegisterEnumDescriptor(_COMPUTERVISIONTASK)

ComputerVisionTask = enum_type_wrapper.EnumTypeWrapper(_COMPUTERVISIONTASK)
COMPUTER_VISION_TASK_UNKNOWN = 0
CLASSIFICATION = 1
BINARY_CLASSIFICATION = 2
MULTILABEL_CLASSIFICATION = 3
DETECTION = 4
LOCALIZATION = 5
SEMANTIC_SEGMENTATION = 6
INSTANCE_SEGMENTATION = 7
KEYPOINT_DETECTION = 8


_DATASETSPEC_SPLIT = _descriptor.EnumDescriptor(
  name='Split',
  full_name='DatasetSpec.Split',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SPLIT_UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ALL', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRAIN', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VAL', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEST', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=939,
  serialized_end=1004,
)
_sym_db.RegisterEnumDescriptor(_DATASETSPEC_SPLIT)

_IMAGESPEC_IMAGERANGE = _descriptor.EnumDescriptor(
  name='ImageRange',
  full_name='ImageSpec.ImageRange',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='IMAGE_RANGE_UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ZERO_ONE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NEG_ONE_POS_ONE', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ZERO_255', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IMAGENET_CAFFE_BGR', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IMAGENET_TORCH', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CIFAR10_TORCH', index=6, number=6,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1131,
  serialized_end=1280,
)
_sym_db.RegisterEnumDescriptor(_IMAGESPEC_IMAGERANGE)


_DATASETSPEC_LABELSMAPENTRY = _descriptor.Descriptor(
  name='LabelsMapEntry',
  full_name='DatasetSpec.LabelsMapEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DatasetSpec.LabelsMapEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='DatasetSpec.LabelsMapEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=640,
  serialized_end=688,
)

_DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY = _descriptor.Descriptor(
  name='TotalLabelDistributionEntry',
  full_name='DatasetSpec.TotalLabelDistributionEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DatasetSpec.TotalLabelDistributionEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='DatasetSpec.TotalLabelDistributionEntry.value', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=690,
  serialized_end=751,
)

_DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY = _descriptor.Descriptor(
  name='TrainLabelDistributionEntry',
  full_name='DatasetSpec.TrainLabelDistributionEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DatasetSpec.TrainLabelDistributionEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='DatasetSpec.TrainLabelDistributionEntry.value', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=753,
  serialized_end=814,
)

_DATASETSPEC_VALLABELDISTRIBUTIONENTRY = _descriptor.Descriptor(
  name='ValLabelDistributionEntry',
  full_name='DatasetSpec.ValLabelDistributionEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DatasetSpec.ValLabelDistributionEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='DatasetSpec.ValLabelDistributionEntry.value', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=816,
  serialized_end=875,
)

_DATASETSPEC_TESTLABELDISTRIBUTIONENTRY = _descriptor.Descriptor(
  name='TestLabelDistributionEntry',
  full_name='DatasetSpec.TestLabelDistributionEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DatasetSpec.TestLabelDistributionEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='DatasetSpec.TestLabelDistributionEntry.value', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=877,
  serialized_end=937,
)

_DATASETSPEC = _descriptor.Descriptor(
  name='DatasetSpec',
  full_name='DatasetSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='split', full_name='DatasetSpec.split', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='title', full_name='DatasetSpec.title', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_cardinality', full_name='DatasetSpec.total_cardinality', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='train_cardinality', full_name='DatasetSpec.train_cardinality', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='val_cardinality', full_name='DatasetSpec.val_cardinality', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='test_cardinality', full_name='DatasetSpec.test_cardinality', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='labels_map', full_name='DatasetSpec.labels_map', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_label_distribution', full_name='DatasetSpec.total_label_distribution', index=7,
      number=8, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='train_label_distribution', full_name='DatasetSpec.train_label_distribution', index=8,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='val_label_distribution', full_name='DatasetSpec.val_label_distribution', index=9,
      number=10, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='test_label_distribution', full_name='DatasetSpec.test_label_distribution', index=10,
      number=11, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='image_spec', full_name='DatasetSpec.image_spec', index=11,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='task', full_name='DatasetSpec.task', index=12,
      number=13, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='num_classes', full_name='DatasetSpec.num_classes', index=13,
      number=14, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_DATASETSPEC_LABELSMAPENTRY, _DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY, _DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY, _DATASETSPEC_VALLABELDISTRIBUTIONENTRY, _DATASETSPEC_TESTLABELDISTRIBUTIONENTRY, ],
  enum_types=[
    _DATASETSPEC_SPLIT,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=1004,
)


_IMAGESPEC = _descriptor.Descriptor(
  name='ImageSpec',
  full_name='ImageSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='range', full_name='ImageSpec.range', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='width', full_name='ImageSpec.width', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='height', full_name='ImageSpec.height', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channels', full_name='ImageSpec.channels', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channels_last', full_name='ImageSpec.channels_last', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _IMAGESPEC_IMAGERANGE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1007,
  serialized_end=1280,
)

_DATASETSPEC_LABELSMAPENTRY.containing_type = _DATASETSPEC
_DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY.containing_type = _DATASETSPEC
_DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY.containing_type = _DATASETSPEC
_DATASETSPEC_VALLABELDISTRIBUTIONENTRY.containing_type = _DATASETSPEC
_DATASETSPEC_TESTLABELDISTRIBUTIONENTRY.containing_type = _DATASETSPEC
_DATASETSPEC.fields_by_name['split'].enum_type = _DATASETSPEC_SPLIT
_DATASETSPEC.fields_by_name['labels_map'].message_type = _DATASETSPEC_LABELSMAPENTRY
_DATASETSPEC.fields_by_name['total_label_distribution'].message_type = _DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY
_DATASETSPEC.fields_by_name['train_label_distribution'].message_type = _DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY
_DATASETSPEC.fields_by_name['val_label_distribution'].message_type = _DATASETSPEC_VALLABELDISTRIBUTIONENTRY
_DATASETSPEC.fields_by_name['test_label_distribution'].message_type = _DATASETSPEC_TESTLABELDISTRIBUTIONENTRY
_DATASETSPEC.fields_by_name['image_spec'].message_type = _IMAGESPEC
_DATASETSPEC.fields_by_name['task'].enum_type = _COMPUTERVISIONTASK
_DATASETSPEC_SPLIT.containing_type = _DATASETSPEC
_IMAGESPEC.fields_by_name['range'].enum_type = _IMAGESPEC_IMAGERANGE
_IMAGESPEC_IMAGERANGE.containing_type = _IMAGESPEC
DESCRIPTOR.message_types_by_name['DatasetSpec'] = _DATASETSPEC
DESCRIPTOR.message_types_by_name['ImageSpec'] = _IMAGESPEC
DESCRIPTOR.enum_types_by_name['ComputerVisionTask'] = _COMPUTERVISIONTASK
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DatasetSpec = _reflection.GeneratedProtocolMessageType('DatasetSpec', (_message.Message,), {

  'LabelsMapEntry' : _reflection.GeneratedProtocolMessageType('LabelsMapEntry', (_message.Message,), {
    'DESCRIPTOR' : _DATASETSPEC_LABELSMAPENTRY,
    '__module__' : 'masterful.proto.metadata_pb2'
    # @@protoc_insertion_point(class_scope:DatasetSpec.LabelsMapEntry)
    })
  ,

  'TotalLabelDistributionEntry' : _reflection.GeneratedProtocolMessageType('TotalLabelDistributionEntry', (_message.Message,), {
    'DESCRIPTOR' : _DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY,
    '__module__' : 'masterful.proto.metadata_pb2'
    # @@protoc_insertion_point(class_scope:DatasetSpec.TotalLabelDistributionEntry)
    })
  ,

  'TrainLabelDistributionEntry' : _reflection.GeneratedProtocolMessageType('TrainLabelDistributionEntry', (_message.Message,), {
    'DESCRIPTOR' : _DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY,
    '__module__' : 'masterful.proto.metadata_pb2'
    # @@protoc_insertion_point(class_scope:DatasetSpec.TrainLabelDistributionEntry)
    })
  ,

  'ValLabelDistributionEntry' : _reflection.GeneratedProtocolMessageType('ValLabelDistributionEntry', (_message.Message,), {
    'DESCRIPTOR' : _DATASETSPEC_VALLABELDISTRIBUTIONENTRY,
    '__module__' : 'masterful.proto.metadata_pb2'
    # @@protoc_insertion_point(class_scope:DatasetSpec.ValLabelDistributionEntry)
    })
  ,

  'TestLabelDistributionEntry' : _reflection.GeneratedProtocolMessageType('TestLabelDistributionEntry', (_message.Message,), {
    'DESCRIPTOR' : _DATASETSPEC_TESTLABELDISTRIBUTIONENTRY,
    '__module__' : 'masterful.proto.metadata_pb2'
    # @@protoc_insertion_point(class_scope:DatasetSpec.TestLabelDistributionEntry)
    })
  ,
  'DESCRIPTOR' : _DATASETSPEC,
  '__module__' : 'masterful.proto.metadata_pb2'
  # @@protoc_insertion_point(class_scope:DatasetSpec)
  })
_sym_db.RegisterMessage(DatasetSpec)
_sym_db.RegisterMessage(DatasetSpec.LabelsMapEntry)
_sym_db.RegisterMessage(DatasetSpec.TotalLabelDistributionEntry)
_sym_db.RegisterMessage(DatasetSpec.TrainLabelDistributionEntry)
_sym_db.RegisterMessage(DatasetSpec.ValLabelDistributionEntry)
_sym_db.RegisterMessage(DatasetSpec.TestLabelDistributionEntry)

ImageSpec = _reflection.GeneratedProtocolMessageType('ImageSpec', (_message.Message,), {
  'DESCRIPTOR' : _IMAGESPEC,
  '__module__' : 'masterful.proto.metadata_pb2'
  # @@protoc_insertion_point(class_scope:ImageSpec)
  })
_sym_db.RegisterMessage(ImageSpec)


_DATASETSPEC_LABELSMAPENTRY._options = None
_DATASETSPEC_TOTALLABELDISTRIBUTIONENTRY._options = None
_DATASETSPEC_TRAINLABELDISTRIBUTIONENTRY._options = None
_DATASETSPEC_VALLABELDISTRIBUTIONENTRY._options = None
_DATASETSPEC_TESTLABELDISTRIBUTIONENTRY._options = None
# @@protoc_insertion_point(module_scope)
