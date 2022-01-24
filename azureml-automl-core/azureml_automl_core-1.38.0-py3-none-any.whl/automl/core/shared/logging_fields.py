# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging fields."""
from typing import Any, Dict, List, Tuple
import copy
import re

from azureml.telemetry.contracts import (Event, RequiredFields, RequiredFieldKeys, StandardFields,
                                         StandardFieldKeys, ExtensionFields, ExtensionFieldKeys)


TELEMETRY_AUTOML_COMPONENT_KEY = 'automl'


class AutoMLExtensionFieldKeys:
    ACTIVITY_STATUS_KEY = "ActivityStatus"
    AUTOML_CLIENT_KEY = "AutomlClient"
    AUTOML_CORE_SDK_VERSION_KEY = "AutomlCoreSdkVersion"
    AUTOML_SDK_VERSION_KEY = "AutomlSdkVersion"
    COMPLETION_STATUS_KEY = "CompletionStatus"
    DURATION_IN_MILLISECONDS_KEY = "DurationMs"
    EXCEPTION_CLASS_KEY = "ExceptionClass"
    EXCEPTION_TARGET_KEY = "ExceptionTarget"
    EXPERIMENT_ID_KEY = "ExperimentId"
    INNER_ERROR_CODE_KEY = "InnerErrorCode"
    IS_CRITICAL_KEY = "IsCritical"
    PARENT_RUN_UUID_KEY = "ParentRunUuid"
    RUN_UUID_KEY = "RunUuid"
    TRACEBACK_MESSAGE_KEY = "TracebackMessage"

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for AutoMLExtension fields."""
        current_keys = [
            AutoMLExtensionFieldKeys.ACTIVITY_STATUS_KEY,
            AutoMLExtensionFieldKeys.AUTOML_CLIENT_KEY,
            AutoMLExtensionFieldKeys.AUTOML_CORE_SDK_VERSION_KEY,
            AutoMLExtensionFieldKeys.AUTOML_SDK_VERSION_KEY,
            AutoMLExtensionFieldKeys.COMPLETION_STATUS_KEY,
            AutoMLExtensionFieldKeys.DURATION_IN_MILLISECONDS_KEY,
            AutoMLExtensionFieldKeys.EXCEPTION_CLASS_KEY,
            AutoMLExtensionFieldKeys.EXCEPTION_TARGET_KEY,
            AutoMLExtensionFieldKeys.EXPERIMENT_ID_KEY,
            AutoMLExtensionFieldKeys.INNER_ERROR_CODE_KEY,
            AutoMLExtensionFieldKeys.IS_CRITICAL_KEY,
            AutoMLExtensionFieldKeys.PARENT_RUN_UUID_KEY,
            AutoMLExtensionFieldKeys.RUN_UUID_KEY,
            AutoMLExtensionFieldKeys.TRACEBACK_MESSAGE_KEY
        ]

        current_keys.extend(ExtensionFieldKeys.keys())      # type: List[str]
        return current_keys


WHITELISTED_PROPERTIES = [StandardFieldKeys.ALGORITHM_TYPE_KEY,
                          StandardFieldKeys.CLIENT_OS_KEY,
                          StandardFieldKeys.COMPUTE_TYPE_KEY,
                          StandardFieldKeys.FAILURE_REASON_KEY,
                          StandardFieldKeys.ITERATION_KEY,
                          StandardFieldKeys.PARENT_RUN_ID_KEY,
                          StandardFieldKeys.RUN_ID_KEY,
                          StandardFieldKeys.TASK_RESULT_KEY,
                          StandardFieldKeys.WORKSPACE_REGION_KEY,
                          StandardFieldKeys.DURATION_KEY,
                          AutoMLExtensionFieldKeys.ACTIVITY_STATUS_KEY,
                          AutoMLExtensionFieldKeys.AUTOML_CLIENT_KEY,
                          AutoMLExtensionFieldKeys.AUTOML_CORE_SDK_VERSION_KEY,
                          AutoMLExtensionFieldKeys.AUTOML_SDK_VERSION_KEY,
                          AutoMLExtensionFieldKeys.COMPLETION_STATUS_KEY,
                          AutoMLExtensionFieldKeys.DURATION_IN_MILLISECONDS_KEY,
                          AutoMLExtensionFieldKeys.EXCEPTION_CLASS_KEY,
                          AutoMLExtensionFieldKeys.EXCEPTION_TARGET_KEY,
                          AutoMLExtensionFieldKeys.INNER_ERROR_CODE_KEY,
                          AutoMLExtensionFieldKeys.IS_CRITICAL_KEY,
                          AutoMLExtensionFieldKeys.PARENT_RUN_UUID_KEY,
                          AutoMLExtensionFieldKeys.RUN_UUID_KEY]


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake_case(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_to_camel_case(name):
    return ''.join(x.capitalize() or '_' for x in name.split('_'))


def update_schematized_fields(
        custom_dimensions: Dict[str, Any]) -> Tuple[RequiredFields, StandardFields, ExtensionFields]:
    """
    Update schematized fields.

    Update required, standard, extension fields based on custom_dimensions.
    Since the schematized fields are shared with the C# SDK, we will be using
    camel case in the dimensions. Appropriate converters are used.
    """
    cd = copy.deepcopy(custom_dimensions)
    _required_fields = RequiredFields()
    _standard_fields = StandardFields()
    _extension_fields = ExtensionFields()
    for camel_key in RequiredFieldKeys.keys():
        snake_key = camel_to_snake_case(camel_key)
        if snake_key in cd:
            _required_fields[camel_key] = cd.pop(snake_key)

    for camel_key in StandardFieldKeys.keys():
        snake_key = camel_to_snake_case(camel_key)
        if snake_key in cd:
            _standard_fields[camel_key] = cd.pop(snake_key)

    for camel_key in AutoMLExtensionFieldKeys.keys():
        snake_key = camel_to_snake_case(camel_key)
        if snake_key in cd:
            _extension_fields[camel_key] = cd.pop(snake_key)

    for snake_key in cd:
        _extension_fields[snake_to_camel_case(snake_key)] = cd[snake_key]

    _standard_fields[StandardFieldKeys.ALGORITHM_TYPE_KEY] = \
        cd.get('task_type', None)
    _standard_fields[StandardFieldKeys.COMPUTE_TYPE_KEY] = \
        cd.get('compute_target', None)

    return _required_fields, _standard_fields, _extension_fields
