#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from collections import defaultdict
import json

from datarobot.utils import camelize


def assert_version(version, version_json):
    assert version.id == version_json["id"]
    assert version.environment_id == version_json["environmentId"]
    assert version.label == version_json["label"]
    assert version.description == version_json["description"]
    assert version.build_status == version_json["buildStatus"]
    assert version.created_at == version_json["created"]
    assert version.docker_context_size == version_json.get("dockerContextSize")
    assert version.docker_image_size == version_json.get("dockerImageSize")


def assert_custom_task(task_obj, task_json):
    non_optional = [
        "id",
        "target_type",
        "created_at",
        "updated_at",
        "name",
        "description",
        "language",
        "created_by",
    ]
    for obj_key in non_optional:
        assert_key(task_obj, task_json, obj_key)

    optional = [
        "calibrate_predictions",
    ]
    for obj_key in optional:
        assert_optional_key(task_obj, task_json, obj_key)

    version_obj = task_obj.latest_version
    version_json = task_json["latestVersion"]
    if version_obj is None:
        assert version_json is None, (version_obj, version_json)
    else:
        assert_custom_task_version(version_obj, version_json)


def assert_custom_model_version(version, version_json):
    model_version_only_keys = (
        "custom_model_id",
        "network_egress_policy",
        "maximum_memory",
        "replicas",
    )
    for key in model_version_only_keys:
        assert_key(version, version_json, key)

    _assert_custom_version_common_fields(version, version_json)


def assert_custom_task_version(version, version_json):
    assert_key(version, version_json, "custom_task_id")

    _assert_custom_version_common_fields(version, version_json)

    obj_arguments = version.arguments
    json_arguments = version_json.get("arguments", [])
    assert_custom_version_arguments(obj_arguments, json_arguments)


def _assert_custom_version_common_fields(version, version_json):
    non_optional = [
        "id",
        "label",
        "description",
        "version_minor",
        "version_major",
        "is_frozen",
        "created_at",
    ]
    for obj_key in non_optional:
        assert_key(version, version_json, obj_key)

    optional = [
        "base_environment_id",
        "required_metadata",
        "base_environment_version_id",
    ]
    for obj_key in optional:
        assert_optional_key(version, version_json, obj_key)

    if version.base_environment_id is not None:
        assert version.base_environment_version_id is not None

    object_items = version.items
    json_items = version_json["items"]
    assert_items(object_items, json_items)

    object_values = version.required_metadata_values or []
    json_values = version_json.get("requiredMetadataValues", [])
    assert_required_metadata_values(object_values, json_values)

    obj_dependencies = version.dependencies
    json_dependencies = version_json.get("dependencies", [])
    assert_dependencies(obj_dependencies, json_dependencies)


def assert_items(object_items, json_items):
    assert len(object_items) == len(json_items)
    for item, item_json in zip(object_items, json_items):
        for key in ("id", "file_name", "file_path", "file_source", "created_at"):
            assert_key(item, item_json, key)


def assert_required_metadata_values(object_values, json_values):
    assert len(object_values) == len(json_values)
    for item, item_json in zip(object_values, json_values):
        for key in ("field_name", "value"):
            assert_key(item, item_json, key)


def assert_dependencies(obj_dependencies, json_dependencies):
    assert len(obj_dependencies) == len(json_dependencies)
    for dependency, dependency_json in zip(obj_dependencies, json_dependencies):
        for key in ("package_name", "line", "line_number"):
            assert_key(dependency, dependency_json, key)

        for constraint, constraint_json in zip(
            dependency.constraints, dependency_json["constraints"]
        ):
            for key in ("version", "constraint_type"):
                assert_key(constraint, constraint_json, key)


def assert_custom_version_arguments(obj_arguments, json_arguments):
    assert len(obj_arguments) == len(json_arguments)
    for argument, argument_json in zip(obj_arguments, json_arguments):
        assert argument.key == argument_json["key"]
        for key in {"name", "type", "default", "values"}:
            assert_key(argument.argument, argument_json["argument"], key)


def assert_key(api_obj, json_data, obj_attribute):
    is_optional_key = False
    _assert_attribute(api_obj, json_data, obj_attribute, is_optional_key)


def assert_optional_key(api_obj, json_data, obj_attribute):
    is_optional_key = True
    _assert_attribute(api_obj, json_data, obj_attribute, is_optional_key)


def _assert_attribute(api_obj, json_data, obj_attribute, is_json_value_optional):
    json_attribute = camelize(obj_attribute)
    if obj_attribute in ("created_at", "updated_at"):
        json_attribute = obj_attribute.replace("_at", "")

    if is_json_value_optional:
        json_value = json_data.get(json_attribute)
    else:
        json_value = json_data[json_attribute]
    obj_value = getattr(api_obj, obj_attribute)

    assert obj_value == json_value, (obj_attribute, obj_value, json_value)


def assert_custom_model_version_dependency_build(
    build_info, build_info_json, custom_model_id, custom_model_version_id
):
    assert build_info.custom_model_id == custom_model_id
    assert build_info.custom_model_version_id == custom_model_version_id

    assert build_info.started_at == build_info_json["buildStart"]
    assert build_info.completed_at == build_info_json["buildEnd"]
    assert build_info.build_status == build_info_json["buildStatus"]


def change_response_value(value):
    """When you want to copy a response dict but change the values"""
    if isinstance(value, bool):
        return not value
    elif isinstance(value, int):
        return value + 1
    elif isinstance(value, str):
        return value + "x"
    elif isinstance(value, list):
        return value + value
    elif isinstance(value, dict):
        return {k + "x": v for k, v in value.items()}
    else:
        return value


def assert_single_api_call(calls, action, url_ending, request_body=None):
    # type: (responses.CallList, str, str, dict) -> None
    assert len(calls) == 1
    only_request = calls[0].request
    assert only_request.method == action
    assert only_request.url.endswith(url_ending)
    if request_body:
        actual_body = json.loads(only_request.body)
        assert actual_body == request_body, actual_body


def fields_to_dict(encoder):
    # type: (MultipartEncoder) -> defaultdict
    fields = defaultdict(list)
    for k, v in encoder.fields:
        fields[k].append(v)
    return fields


def assert_custom_task_version_dependency_build(
    custom_task_version_dependency_build, custom_task_version_dependency_build_server_data
):
    server_data = custom_task_version_dependency_build_server_data
    assert custom_task_version_dependency_build.custom_task_id == server_data["customTaskId"]
    assert (
        custom_task_version_dependency_build.custom_task_version_id
        == server_data["customTaskVersionId"]
    )
    assert custom_task_version_dependency_build.started_at == server_data["buildStart"]
    assert custom_task_version_dependency_build.completed_at == server_data["buildEnd"]
    assert custom_task_version_dependency_build.build_status == server_data["buildStatus"]
    assert (
        custom_task_version_dependency_build.build_log_location == server_data["buildLogLocation"]
    )
