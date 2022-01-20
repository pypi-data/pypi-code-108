"""Defines Visualize's dataset spec proto scanner functionality.

This module implements the functionality for Visualzie to scan for
serialized metadata_pb2.DatasetSpec serialized protos produced by
Masterful.
"""

import os

import google.protobuf.json_format as json_format

from masterful_gui.backend.apps.api import models
from masterful_gui.backend.proto import metadata_pb2

# The location where the scanner should look for serialzed protos.
_SCAN_DIR = f'{os.path.expanduser("~")}/.masterful'

# The extension of a serialized policy proto file. The extension actually
# makes no difference, this is just to facilitate identifying the right files
# to read.
# WARNING: This matches the configuration of proto_serializer module in
# masterful_partners repo. You must change them both or you'll break
# assumptions and Visualize.
_EXTENSION = "dspb"


def scan():
  """Scans the configured directory for serlized dataset spec protos.
  
  This function deserializes dataset spec protos on disk, converts them
  to Django's owm dataset spec model, and persists them to the database
  (app model).
  If the database already had a record for that dataset, it updates
  that records with the values extracted from the serialized dataset spec. If
  it wasn't, this will persist it to the database.
  """
  if len(os.listdir(_SCAN_DIR)) == 0:
    #TODO(ray): Consider printing something to show in backend logs.
    return

  serialized_protos = []
  for file in os.listdir(_SCAN_DIR):
    if file.split('.')[-1] != _EXTENSION:
      continue
    serialized_protos.append(file)

  if len(serialized_protos) == 0:
    return

  for serialized_proto in serialized_protos:
    proto = metadata_pb2.DatasetSpec()
    file_name = f'{_SCAN_DIR}/{serialized_proto}'
    with open(file_name, "rb") as f:
      proto.ParseFromString(f.read())

    proto_dict = json_format.MessageToDict(proto,
                                           use_integers_for_enums=False,
                                           including_default_value_fields=True,
                                           preserving_proto_field_name=True)

    model_exists = len(models.DatasetSpec.objects.filter(pk=proto.title)) > 0
    if model_exists:
      existing_model = models.DatasetSpec.objects.get(pk=proto.title)
      existing_model.split = proto_dict.get("split")
      existing_model.total_cardinality = proto.total_cardinality
      existing_model.train_cardinality = proto.train_cardinality
      existing_model.val_cardinality = proto.val_cardinality
      existing_model.test_cardinality = proto.test_cardinality
      existing_model.labels_map = proto_dict.get("labels_map", {})
      existing_model.total_label_distribution = proto_dict.get(
          "total_label_distribution", {})
      existing_model.train_label_distribution = proto_dict.get(
          "train_label_distribution", {})
      existing_model.val_label_distribution = proto_dict.get(
          "val_label_distribution", {})
      existing_model.test_label_distribution = proto_dict.get(
          "test_label_distribution", {})
      existing_model.image_spec = proto_dict.get("image_spec", {})
      existing_model.task = proto_dict.get("task")
      existing_model.num_classes = proto.num_classes
      existing_model.save()

    else:
      new_model = models.DatasetSpec.objects.create(
          title=proto.title,
          split=proto_dict.get("split"),
          total_cardinality=proto.total_cardinality,
          train_cardinality=proto.train_cardinality,
          val_cardinality=proto.val_cardinality,
          test_cardinality=proto.test_cardinality,
          labels_map=proto_dict.get("labels_map", {}),
          total_label_distribution=proto_dict.get("total_label_distribution",
                                                  {}),
          train_label_distribution=proto_dict.get("train_label_distribution",
                                                  {}),
          val_label_distribution=proto_dict.get("val_label_distribution", {}),
          test_label_distribution=proto_dict.get("test_label_distribution", {}),
          image_spec=proto_dict.get("image_spec", {}),
          task=proto_dict.get("task"),
          num_classes=proto.num_classes)
      new_model.save()