# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Boris Feld

This module contains the code related to JSON Schema

"""
import json
from os.path import dirname, join

from jsonschema.validators import validator_for


def get_validator(filename, allow_additional_properties=True):
    with open(join(dirname(__file__), join("schemas", filename))) as schema_file:
        schema = json.load(schema_file)

    if not allow_additional_properties:
        schema["additionalProperties"] = False

    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    return validator_class(schema)


def get_experiment_file_validator(allow_additional_properties=True):
    return get_validator("offline-experiment.schema.json", allow_additional_properties)


def get_ws_msg_validator(allow_additional_properties=True):
    return get_validator("offline-ws-msg.schema.json", allow_additional_properties)


def get_parameter_msg_validator(allow_additional_properties=True):
    return get_validator(
        "offline-parameter-msg.schema.json", allow_additional_properties
    )


def get_os_packages_msg_validator(allow_additional_properties=False):
    return get_validator(
        "offline-os-packages-msg.schema.json", allow_additional_properties
    )


def get_graph_msg_validator(allow_additional_properties=False):
    return get_validator("offline-graph-msg.schema.json", allow_additional_properties)


def get_system_details_msg_validator(allow_additional_properties=False):
    return get_validator(
        "offline-system-details-msg.schema.json", allow_additional_properties
    )


def get_cloud_details_msg_validator(allow_additional_properties=False):
    return get_validator(
        "offline-cloud-details-msg.schema.json", allow_additional_properties
    )


def get_upload_msg_validator(allow_additional_properties=True):
    return get_validator(
        "offline-file-upload-msg.schema.json", allow_additional_properties
    )


def get_remote_file_msg_validator(allow_additional_properties=True):
    return get_validator(
        "offline-remote-file-msg.schema.json", allow_additional_properties
    )


def get_3d_boxes_validator(allow_additional_properties=False):
    return get_validator(
        "3d-points-bounding-box.schema.json", allow_additional_properties
    )
