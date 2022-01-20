"""Defines Visualize's policy scanner functionality.

This module implements the functionality for Visualzie to scan for
serialized search_task_pb2.PolicySearchTask serialized protos produced by
Masterful.
"""

import os
import sys

import google.protobuf.json_format as json_format

from masterful_gui.backend.apps.api import models
from masterful_gui.backend.proto import search_task_pb2

# The location where the scanner should look for serialzed policies.
_SCAN_DIR = f'{os.path.expanduser("~")}/.masterful/policies'

# The extension of a serialized policy proto file. The extension actually
# makes no difference, this is just to facilitate identifying the right files
# to read.
# WARNING: This matches the configuration of proto_serializer module in
# masterful_partners repo. You must change them both or you'll break
# assumptions and Visualize.
_EXTENSION = "pstpb"


def scan():
  """Scans the configured directory for serlized policy protos.
  
  This function deserializes policy protos on disk, converts them
  to Django's owm policy model, and persists them to the database (app model).
  If the database already had a record for that policy, it updates
  that records with the values extracted from the serialized policy. If it
  wasn't, this will persist it to the database.
  """
  if len(os.listdir(_SCAN_DIR)) == 0:
    #TODO(ray): Consider printing something to show in backend logs.
    return

  serialized_tasks = []
  for file in os.listdir(_SCAN_DIR):
    if file.split('.')[-1] != _EXTENSION:
      continue
    serialized_tasks.append(file)

  if len(serialized_tasks) == 0:
    return

  for serialized_task in serialized_tasks:
    task = search_task_pb2.PolicySearchTask()
    file_name = f'{_SCAN_DIR}/{serialized_task}'
    with open(file_name, "rb") as f:
      task.ParseFromString(f.read())

    task_dict = json_format.MessageToDict(task,
                                          use_integers_for_enums=False,
                                          including_default_value_fields=True,
                                          preserving_proto_field_name=True)

    task_exists = len(
        models.PolicySearchTask.objects.filter(pk=task.policy_name)) > 0
    if task_exists:
      existing_task = models.PolicySearchTask.objects.get(pk=task.policy_name)
      existing_task.approach_name = task.approach_name
      existing_task.presearch_model_val_metrics = task_dict.get(
          "presearch_model_val_metrics", {})
      existing_task.node_search_tasks = task_dict.get("node_search_tasks", {})
      existing_task.engine_version = task.engine_version
      existing_task.save()

    else:
      new_task = models.PolicySearchTask.objects.create(
          policy_name=task.policy_name,
          approach_name=task.approach_name,
          presearch_model_val_metrics=task_dict.get(
              "presearch_model_val_metrics", {}),
          node_search_tasks=task_dict.get("node_search_tasks", {}),
          engine_version=task.engine_version)
      new_task.save()