"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from keyword import iskeyword
from typing import Dict, List, Optional, Union, Any, Iterable

from .datarobot_client import (
    UserBlueprint,
    ParamValuePair,
    UserBlueprintTaskArgumentDefinition,
    UserBlueprintTaskData,
    UserBlueprintTaskDefinition,
    ColnameAndType,
    UserBlueprintsValidateTaskParameter,
    UserBlueprintHexColumnNameLookupEntry,
)

from .dynamic import DynamicClass
from .exceptions import TaskFrozenError, CycleException, CustomTaskNotFound
from .friendly_repr import FriendlyRepr
from .user_blueprint_helper import UserBlueprintHelper
from .utils import (
    Colors,
    HiddenList,
    TaskOutputMethod,
    colorize,
    documentation,
    refresh_cached,
    represents_input_data,
)
from .workshop_interface import WorkshopInterface

TaskDict = Dict[str, Union[dict, str, List[str], List[Dict]]]
TaskParametersDict = Dict[str, Optional[Any]]

_COLNAME_PARAM = "cn"
_COLNAMES_PARAM = "cns"
_SELECT_COLNAME_METHOD = "method"


def hex_or_identity(task: Union[str, Task]) -> str:
    """
    Convenience method for retrieving the identifier for a task.
    This is a hex value if it's a Task and itself if an input data type.

    Parameters
    ----------
    task: str or Task
        Either a string of type BlueprintColumnClass or Task object

    Returns
    -------
    str
        id which represents a task- either a hex or an input data type
    """
    return str(task.task_id if isinstance(task, Task) else task)


class Task(FriendlyRepr, DynamicClass):
    """
    Provides a mechanism to specify how to transform or provide predictions for input
    data.

    Should not be used directly. Use one of: `Workshop.Task`, `Workshop.Tasks.*`,
    `Workshop.CustomTask`, or `Workshop.CustomTasks.*` instead.

    Parameters
    ----------
    workshop: WorkshopInterface
        Reference to the workshop
    task_code: string
        Task Code
    output_method: string
        starting with member of TaskMethodShort and an optional set of arguments
    task_parameters: TaskParameters
        A class with allowed params as attributes.
    output_method_parameters: List[ParamValuePair]
        A list of parameters and values to the operation
        e.g. `[ParamValuePair(param='add_orig_colname', value=True)]`
    x_transformations: List[ParamValuePair]
        A list of ParamValuePair representing transformations to be applied
        to the input data, X.
    y_transformations: List[ParamValuePair]
        A list of ParamValuePair representing transformations to be applied
        to the input targets, Y.
    freeze: boolean
        Whether or not to freeze the vertex - i.e. hexes, model strings, and inputs are cached.
    original_id: str
        An id to associate with this task which will be used when serializing the task.
    custom_task_id: str
        An id representing the custom task content- only applicable if the task is "Custom"
    version: str or None
        An id representing the custom task version content- only applicable if the task is "Custom"
    """

    _attr_to_refresh = ["_cached_input_names", "_cached_hex"]

    def __init__(
        self,
        workshop: WorkshopInterface,
        task_code: str,
        output_method: Optional[str] = None,
        task_parameters: Union[List[ParamValuePair], dict] = None,
        output_method_parameters: Union[List[ParamValuePair], dict] = None,
        x_transformations: Union[List[ParamValuePair], dict] = None,
        y_transformations: Union[List[ParamValuePair], dict] = None,
        freeze: bool = False,
        original_id: Optional[str] = None,
        custom_task_id: Optional[str] = None,
        version: Optional[str] = None,
        hex_column_name_lookup: Optional[
            List[UserBlueprintHexColumnNameLookupEntry]
        ] = None,
    ):
        """
        Parameters
        ----------
        workshop: WorkshopInterface
            Reference to the workshop
        task_code: string
            Task Code
        output_method: string
            starting with member of TaskMethodShort and an optional set of arguments
        task_parameters: List[ParamValuePair] or dict
            A list of ParamValue, e.g. `[ParamValuePair(param='n', value=100)]
            Or a dictionary where keys are params and values are values.
        output_method_parameters: List[ParamValuePair] or dict
            A list of parameters and values to the operation
            e.g. `[ParamValuePair(param='add_orig_colname', value=True)]
            Or a dictionary where keys are params and values are values.
        x_transformations: List[ParamValuePair] or dict
            A list of ParamValuePair representing transformations to be applied
            to the input data, X. Or a dictionary where keys are params and values are values.
        y_transformations: List[ParamValuePair] or dict
            A list of ParamValuePair representing transformations to be applied
            to the input targets, Y. Or a dictionary where keys are params and values are values.
        freeze: boolean
            Whether or not to freeze the vertex - i.e. hexes, model strings, and inputs are cached.
        original_id: str
            An id to associate with this task which will be used when serializing the task.
        custom_task_id: str
            An id representing the custom task content- only applicable if the task is "Custom"
        version: str or None
            An id representing the custom task version content- only applicable if the task is
            "Custom"
        hex_column_name_lookup: List[UserBlueprintHexColumnNameLookupEntry], (Default=None)
            Extra columns which exist in the User Blueprint, to be decoded
        """
        self._inputs = []
        self._workshop = workshop
        self._task_definitions = workshop._task_definitions_by_task_code
        self._custom_task_definitions = workshop._custom_tasks_by_id
        self._custom_task_version_definitions = workshop._custom_tasks_by_version_id
        self._input_name_lookup = workshop._input_name_lookup
        self._task_code = task_code
        self._output_method = output_method
        self._selected_features: List[ColnameAndType] = []
        self._exclude_features: bool = False
        self._dynamic_generation_exceptions = []
        self._hex_column_name_lookup = (
            {
                item.hex: ColnameAndType(
                    colname=item.colname, hex=item.hex, type="UNKNOWN"
                )
                for item in hex_column_name_lookup
            }
            if hex_column_name_lookup is not None
            else {}
        )
        self.version = None
        self._versions = []

        # Auto-convert dictionary formatted arguments
        if isinstance(task_parameters, dict):
            task_parameters = self._to_param_values_from_dict(task_parameters)
        if isinstance(output_method_parameters, dict):
            output_method_parameters = self._to_param_values_from_dict(
                output_method_parameters
            )
        if isinstance(x_transformations, dict):
            x_transformations = self._to_param_values_from_dict(x_transformations)
        if isinstance(y_transformations, dict):
            y_transformations = self._to_param_values_from_dict(y_transformations)

        version_not_found = False
        version_id = None

        if task_parameters:
            task_parameter_value_lookup = {tp.param: tp.value for tp in task_parameters}
            if custom_task_id is None and version is None:
                if "version_id" in task_parameter_value_lookup:
                    version_id = task_parameter_value_lookup["version_id"]
                    if version_id in self._custom_task_version_definitions:
                        version = version_id
                    else:
                        version_not_found = True

            # TODO: Remove reference to internal parameter
            hex_colname = task_parameter_value_lookup.get(_COLNAME_PARAM)
            if hex_colname is not None:
                self._selected_features = self._decode_colnames([hex_colname])

            hex_colnames = task_parameter_value_lookup.get(_COLNAMES_PARAM)
            if hex_colnames is not None:
                self._selected_features = self._decode_colnames(hex_colnames)

            self._exclude_features = (
                task_parameter_value_lookup.get(_SELECT_COLNAME_METHOD, "include")
                == "exclude"
            )

        if custom_task_id is None and version is not None:
            custom_task_id = self._custom_task_version_definitions[
                version
            ].custom_task_id

        if custom_task_id is not None:
            if custom_task_id not in self._custom_task_definitions:
                raise CustomTaskNotFound(
                    "Supplied custom task id was not found. Call `<Workshop>.refresh()` "
                    "if the custom task was added since creation of the `Workshop` instance."
                )

        self._task_definition: UserBlueprintTaskDefinition = (
            self._task_definitions.get(task_code, None)
            if custom_task_id is None
            else self._custom_task_definitions[custom_task_id]
        )

        # Ensure we handle backwards compatibility / execution of unsupported tasks.
        if self._task_definition is None:
            self._task_definition = (
                (UnavailableCustomTaskDefinition(task_code, version_id))
                if version_not_found and version_id is not None
                else (UnsupportedTaskDefinition(task_code))
            )

        self._task_parameter_definitions = self._task_definition.arguments
        self._task_parameter_definitions_by_key: Dict[
            str, UserBlueprintTaskArgumentDefinition
        ] = {entry.key: entry.argument for entry in self._task_definition.arguments}
        self._task_parameter_definitions_name_to_key: Dict[str, str] = {
            entry.argument.name: entry.key for entry in self._task_parameter_definitions
        }

        # Custom Task Related Initialization
        self.custom_task_id = custom_task_id
        if self.custom_task_id is not None:
            self.version = (
                version
                if version is not None
                else self._task_definition.custom_task_versions[0].id
            )

        if self._output_method is None:
            self._output_method = (
                TaskOutputMethod.PREDICT
                if (TaskOutputMethod.PREDICT in self._task_definition.output_methods)
                else TaskOutputMethod.TRANSFORM
            )

        # Dynamically build classes and methods based on the task parameters
        self._dynamic_initialization(task_parameters)

        self._output_method_parameters: List[
            ParamValuePair
        ] = output_method_parameters or []

        # Direct data transformations
        # Ensure we properly represent x and y transformations as a dictionary
        self._x_transformations: List[ParamValuePair] = (
            copy.deepcopy(x_transformations) if x_transformations is not None else []
        )
        self._y_transformations: List[ParamValuePair] = (
            copy.deepcopy(y_transformations) if y_transformations is not None else []
        )

        # In case we'd like to map back to an original id for identification
        self.original_id = original_id

        # For performance, there are aspects we can cache
        self._frozen = freeze
        self._cached_hex = None
        self._cached_input_names = None

    def validate_task_parameters(
        self, color=True, only_output_errors=False, to_stdout=True
    ) -> List[UserBlueprintsValidateTaskParameter]:
        """ Perform task validation to ensure all parameters and their values are valid. """
        task_parameter_dict = self._task_parameters_dict

        with self._workshop.auto_rate_limiter:
            result = UserBlueprint.validate_task_parameters(
                output_method=self.output_method,
                task_code=self.task_code,
                task_parameters=[
                    {"param_name": param, "new_value": value}
                    for param, value in task_parameter_dict.items()
                ],
            )

        # Dictionary using unique key
        error_lookup = {error.param_name: error for error in result.errors}

        for error in result.errors:
            error.param_name = self._task_parameter_definitions_by_key[
                error.param_name
            ].name

        lines = []
        if result.errors:
            lines = [
                "{} ({})".format(self.label, self.task_code_or_custom_task_code),
                "",
            ]

            if self.selected_features:
                lines += [self._formatted_selected_features()]
            else:
                for k in sorted(task_parameter_dict.keys()):
                    line = "{name} ({key}) = {value}".format(
                        name=self._task_parameter_definitions_by_key[k].name,
                        key=k,
                        value=task_parameter_dict[k],
                    )
                    if k in error_lookup:
                        additions = [
                            "  {}".format(error_lookup[k].message),
                            "    {}".format(line),
                            "      - Must be a '{}' parameter defined by: {}".format(
                                self._task_parameter_definitions_by_key[k].type,
                                self._task_parameter_definitions_by_key[k].values,
                            ),
                            "",
                        ]
                        if color:
                            for i, item in enumerate(additions):
                                additions[i] = colorize(item, Colors.RED)

                        lines += additions

        elif not only_output_errors:
            lines = [
                "{} ({})".format(self.label, self.task_code_or_custom_task_code),
                "",
            ]
            success = "All parameters valid!"
            if color:
                success = colorize(success, Colors.GREEN)
            lines += [success, ""]

        if lines and to_stdout:
            print("\n".join(lines))

        return HiddenList(result.errors)

    def documentation(self, auto_open=False) -> str:
        """
        Return a link to the documentation of the task.
        Optionally automatically open it in a browser window.
        """
        return documentation(self._task_definition, auto_open=auto_open)

    @property
    def task_code(self) -> str:
        """ The unique code representing the class. E.g. "ABC". """
        return self._task_code

    @property
    def task_code_or_custom_task_code(self) -> str:
        """ Return the identifier of the task, either the task_code or the custom task id. """
        return (
            self._task_code
            if self.custom_task_id is None
            else ("{}_{}".format(self._task_code, self.custom_task_id))
        )

    @property
    def label(self) -> str:
        """ Build the human-friendly label to describe the task. """
        if self.selected_features:
            return "{}, {}".format(
                self._task_definition.label, self._formatted_selected_features()
            )
        return self._task_definition.label

    @property
    def description(self) -> str:
        """ The description of the task. """
        return self._task_definition.description

    @property
    def inputs(self) -> List[str]:
        """ A list of the inputs to the task. """
        return self._inputs

    @property
    def output_method(self) -> str:
        """ The output method of the task. """
        return self._output_method

    def get_task_parameter_by_name(self, name: str) -> Optional[Any]:
        """ Retrieve the value of a task parameter by it's human-readable name. """
        key = self._task_parameter_definitions_name_to_key.get(name)
        return self._task_parameters_dict.get(
            key, self._task_parameter_definitions_by_key[key].default
        )

    @property
    def is_estimator(self) -> bool:
        """ Whether or not the task can be used for prediction (stacked or otherwise). """
        return TaskOutputMethod.is_estimator(self._output_method)

    @property
    def using_default_output_method(self) -> bool:
        """ Return whether the task is using its default output method. """
        if self.is_estimator:
            return self.output_method == TaskOutputMethod.PREDICT
        return self.output_method == TaskOutputMethod.TRANSFORM

    @classmethod
    def deserialize(
        cls,
        workshop: WorkshopInterface,
        task_dict: TaskDict,
        original_id: Optional[str] = None,
    ) -> Task:
        """
        Take in a dictionary specifying how the task should be constructed,
        and construct an instance of the Task.
        """
        task = cls(
            workshop=workshop,
            task_code=task_dict["task_code"],
            output_method=task_dict["output_method"],
            task_parameters=cls._to_param_values_from_list_dict(
                task_dict["task_parameters"]
            ),
            output_method_parameters=cls._to_param_values_from_list_dict(
                task_dict["output_method_parameters"]
            ),
            x_transformations=cls._to_param_values_from_list_dict(
                task_dict["x_transformations"]
            ),
            y_transformations=cls._to_param_values_from_list_dict(
                task_dict["y_transformations"]
            ),
            original_id=original_id,
        )
        task._inputs = task_dict["inputs"]
        return task

    @classmethod
    def from_user_blueprint_task(
        cls,
        workshop: WorkshopInterface,
        task_data: UserBlueprintTaskData,
        original_id: str = None,
        hex_column_name_lookup: Optional[
            List[UserBlueprintHexColumnNameLookupEntry]
        ] = None,
    ) -> Task:
        """ Instantiate a `Task` using `UserBlueprintTaskData` from a `UserBlueprint`. """
        task = cls(
            workshop=workshop,
            task_code=task_data.task_code,
            output_method=task_data.output_method,
            task_parameters=task_data.task_parameters,
            output_method_parameters=task_data.output_method_parameters,
            x_transformations=task_data.x_transformations,
            y_transformations=task_data.y_transformations,
            original_id=original_id,
            hex_column_name_lookup=hex_column_name_lookup,
        )
        task._inputs = task_data.inputs
        return task

    def serialize(
        self, map_ids: Optional[Dict[str, Union[str, Task]]] = None, minify: bool = True
    ) -> TaskDict:
        """
        Convert the instance of the Task into the serialized form of a dictionary.
        """
        if map_ids is None:
            input_values = [
                i.original_or_task_id if isinstance(i, Task) else i for i in self.inputs
            ]
        else:
            input_values = sorted(Task._build_input_mapping(self.inputs, map_ids))

        task_parameters_dict = (
            self._minified_task_parameters if minify else self._task_parameters_dict
        )

        return {
            "inputs": input_values,
            "task_code": self._task_code,
            "task_parameters": self._to_list_from_dict(task_parameters_dict),
            "output_method": self._output_method,
            "output_method_parameters": self._to_list_dict_from_list_param_value(
                self._output_method_parameters
            ),
            "x_transformations": self._to_list_dict_from_list_param_value(
                self._x_transformations
            ),
            "y_transformations": self._to_list_dict_from_list_param_value(
                self._y_transformations
            ),
        }

    @property
    def task_id(self) -> str:
        """
        Produces a hex which will be identical for two Task with
        the same inputs, task string, and task type.
        """
        if self._is_frozen and self._cached_hex:
            return self._cached_hex
        self._ensure_no_cycles()
        stringified = json.dumps(self.serialize())
        to_be_hashed = str(stringified).encode("utf-8")
        self._cached_hex = str(hashlib.md5(to_be_hashed).hexdigest())
        return self._cached_hex

    @property
    def original_or_task_id(self) -> str:
        """
        If the task has an id associated with it manually, via `original_id`, return
        this id, otherwise return the generated `self.task_id`.
        """
        return self.original_id if self.original_id is not None else self.task_id

    @property
    def input_names(self) -> List[str]:
        """ Ordered representation of the input ids (things like 'NUM', '1', or <hex>) """
        if self._is_frozen and self._cached_input_names:
            return self._cached_input_names
        self._cached_input_names = sorted([hex_or_identity(i) for i in self._inputs])
        return self._cached_input_names

    @property
    def selected_features(self) -> List[ColnameAndType]:
        """ If specific features are selected, return them. """
        return self._selected_features

    @property
    def versions(self):
        """ For Custom Tasks Only: The possible versions for a given task. """
        return self._versions

    # Methods below this point are not meant to be called directly by users.

    def __friendly_repr__(self) -> str:
        inputs = [
            "{} ({})".format(i.label, i.task_code_or_custom_task_code)
            if isinstance(i, Task)
            else "{} Data".format(self._input_name_lookup[i])
            for i in self._inputs
        ]
        sections = [
            "{} ({})".format(self.label, self.task_code_or_custom_task_code),
            "",
            "Input Summary: {}".format(" | ".join(inputs) if inputs else "(None)"),
            "Output Method: {}".format(
                TaskOutputMethod.get_variable_name(self.output_method)
            ),
        ]

        if self.selected_features:
            sections += [self._formatted_selected_features()]

        task_parameters_dict = self._task_parameters_dict
        if task_parameters_dict:
            sections += [
                "\n".join(["", "Task Parameters:"]),
                "  "
                + "\n  ".join(
                    [
                        "{} ({}) = {}".format(
                            self._task_parameter_definitions_by_key[key].name,
                            key,
                            task_parameters_dict[key].__repr__(),
                        )
                        if self.custom_task_id is None or key != "version_id"
                        else ("version_id (version_id) = {}".format(self.version))
                        for key in sorted(task_parameters_dict.keys())
                    ]
                ),
            ]

        return "\n".join(sections)

    def _dynamic_initialization(self, task_parameters: List[ParamValuePair]):
        """
        Dynamically build classes and functions to allow a first-class API-driven experience.
        """
        # Update based on task parameters, and fill defaults
        task_parameters: List[ParamValuePair] = task_parameters or []
        task_parameter_keys = set([tp.param for tp in task_parameters])

        task_parameter_value_lookup = {tp.param: tp.value for tp in task_parameters}

        class TaskParameters(object):
            def __init__(zelf):
                zelf._modified_keys = set()

            def __setattr__(zelf, k, v):
                # It is imperative this is `is not` instead of `!=` as `!=` will perform
                # type coercion and `0 == False` which, when `0` is a select index, this should
                # fail, not pass.
                if k != "_modified_keys" and getattr(zelf, k, v) is not v:
                    zelf._modified_keys.add(k)
                if k == "version_id" and self.version != v:
                    # If setting this directly, keep version updated...
                    self.version = v
                super(TaskParameters, zelf).__setattr__(k, v)

        self.task_parameters = TaskParameters()
        keys_to_keep = set()
        arg_key_to_argument_pairs = {}

        arguments = UserBlueprintHelper.get_arguments(self._task_definition.arguments)
        for entry in arguments:
            key = entry.key
            value = entry.argument
            arg_key_to_argument_pairs[key] = value
            if key in task_parameter_keys:
                self._set_task_parameter(key, task_parameter_value_lookup[key])
                keys_to_keep.add(key)
            else:
                self._set_task_parameter(key, value.default)

        TaskParameters.__doc__ = UserBlueprintHelper.get_docstring_for_arguments(
            arguments, title=self._task_definition.label
        )

        def task_parameters_repr(zelf):
            sorted_keys = sorted(
                zelf.__dict__.keys(),
                key=lambda k: (
                    self._task_parameter_definitions_by_key[k].name
                    if k in self._task_parameter_definitions_by_key
                    else k
                ),
            )
            return "\n".join(
                [
                    "{} ({}) = {}".format(
                        self._task_parameter_definitions_by_key[k].name,
                        k,
                        zelf.__dict__[k].__repr__(),
                    )
                    for k in sorted_keys
                    if k != "_modified_keys"
                ]
            )

        TaskParameters.__repr__ = task_parameters_repr
        self._dynamic_set_parameter_methods(arg_key_to_argument_pairs)

        self.task_parameters._modified_keys = set(keys_to_keep)

        if self.version:
            self._versions = build_custom_task_versions(
                task_definition=self._task_definition
            )

    def _dynamic_set_parameter_methods(
        self, arg_key_to_argument_pairs: Dict[str, UserBlueprintTaskArgumentDefinition]
    ):
        """
        Dynamically generate `set_task_parameters` and `set_task_parameters_by_name.
        """
        # Rename params that are also keywords (e.g. 'is', 'in', 'and', 'or', etc.)
        lookup = {
            k + "_" if iskeyword(k) else k: v
            for k, v in arg_key_to_argument_pairs.items()
        }

        params_by_name = {
            lookup[key].name: lookup[key]
            for key in lookup.keys()
            if re.match("^[_a-zA-Z0-9]+$", lookup[key].name)
        }

        def get_parameter_docstring(
            argument: UserBlueprintTaskArgumentDefinition, key: Optional[str] = None
        ):
            field_name = argument.name if key is None else key
            template = "{field_name}: {type}, (Default={default})\n"
            template += "    Possible Values: {values}\n"
            return template.format(
                field_name=field_name,
                type=argument.type,
                default=argument.default.__repr__(),
                values=argument.values,
            )

        # Add `set_task_parameters`
        self._dynamic_generation_exceptions += self._wrap_function_with_kwargs_and_add_to_class(
            fn_name="set_task_parameters",
            fn_to_wrap=self._set_task_parameters,
            kwargs_dict=lookup,
            docstring=UserBlueprintHelper.get_docstring_for_lines(
                lines=[
                    get_parameter_docstring(lookup[key], key=key)
                    for key in sorted(lookup.keys())
                ],
                title="Set parameters by their key",
                minified=False,
            ),
        )

        # Add `set_task_parameters_by_name`
        self._dynamic_generation_exceptions += self._wrap_function_with_kwargs_and_add_to_class(
            "set_task_parameters_by_name",
            self._set_task_parameters_by_name,
            kwargs_dict=params_by_name,
            docstring=UserBlueprintHelper.get_docstring_for_lines(
                lines=[
                    get_parameter_docstring(params_by_name[name])
                    for name in sorted(params_by_name.keys())
                ],
                title="Set parameters by their name",
                minified=False,
            ),
        )

    def _map_inputs(self, mapping: Dict[str, Task]) -> Task:
        """
        Set the inputs according to a provided map from one set of ids or values to another.

        Useful for changing the order of the nodes (e.g. topological sorting).
        """
        self._inputs = Task._build_input_mapping(self._inputs, mapping)
        return self

    def _formatted_selected_features(self) -> str:
        """ A human readable representation of the selected features being used. """
        prefix = "{verb} {noun}: ".format(
            verb="Select" if not self._exclude_features else "Exclude",
            noun="Feature" if len(self.selected_features) == 1 else "Features",
        )
        return prefix + ", ".join(
            ["'{}'".format(f.colname) for f in self.selected_features]
        )

    def _domain(self) -> str:
        """ The hostname to use to access documentation. """
        return UserBlueprint._client.domain

    def _decode_colnames(self, hex_colnames: List[str]):
        """ Try to decode the column names if possible. """
        if hex_colnames is None:
            return []
        return [
            self._colname_and_type_from_hex(
                self._workshop, hex_colname, self._hex_column_name_lookup
            )
            for hex_colname in hex_colnames
        ]

    @property
    def _task_parameters_dict(self) -> TaskParametersDict:
        """ Serialize the TaskParameters instance into a dictionary. """
        task_parameters_dict = copy.deepcopy(self.task_parameters.__dict__)
        drop_keys = (
            set(task_parameters_dict.keys()) - self.task_parameters._modified_keys
        )
        for key in drop_keys:
            task_parameters_dict.pop(key, None)
        if self.custom_task_id is not None:
            task_parameters_dict["version_id"] = (
                self.version
                if self.version is not None
                else "latest_{}".format(self.custom_task_id)
            )
        return task_parameters_dict

    @property
    def _task_parameter_keys(self) -> List[str]:
        """ Get a list of the task parameters. """
        return sorted(self._task_parameters_dict.keys())

    @property
    def _minified_task_parameters(self) -> TaskParametersDict:
        """ Get all the TaskParameters which are not using their default values. """
        parameters = {}
        for k, v in self._task_parameters_dict.items():
            if self.custom_task_id is not None and k == "version_id":
                parameters[k] = v
                continue

            if k not in self._task_parameter_definitions_by_key:
                continue
            definition = self._task_parameter_definitions_by_key[k]
            default_value = definition.default

            def equivalent_to_default(
                value, default=default_value, allow_coercion=True
            ):
                if allow_coercion and value == default:
                    return True
                return any([value is default, str(value) == str(default)])

            def value_is_index_and_value(value):
                """
                Try to see if `value` is an index...
                But ensure we don't coerce a value existing in the possible values to be an index.
                """
                values = definition.values
                if isinstance(value, (str, int)) and str(value) not in [
                    str(val) for val in values
                ]:
                    try:
                        index = int(value)
                        if index < len(values):
                            return True, values[index]
                    except (ValueError, TypeError):
                        pass
                return False, None

            # Handle indexing into select
            if definition.type in ["select", "selectgrid"]:
                # Try to see if `v` is an index...
                is_index, val = value_is_index_and_value(v)
                if is_index and equivalent_to_default(val, allow_coercion=False):
                    continue

                # Try to see if `default` is an index...
                is_index, val = value_is_index_and_value(default_value)
                if is_index and equivalent_to_default(
                    v, default=val, allow_coercion=False
                ):
                    continue

            if equivalent_to_default(
                v, allow_coercion=definition.type not in ["select", "selectgrid"]
            ):
                continue

            parameters[k] = v

        return parameters

    def _set_task_parameters_by_name(self, **parameters) -> Task:
        """ Set task parameters by human-readable names in bulk. """
        for name, value in parameters.items():
            self._set_task_parameter_by_name(name, value)
        return self

    def _set_task_parameters(self, **parameters) -> Task:
        """ Set task parameters in bulk. """
        for k, v in parameters.items():
            if k.endswith("_") and iskeyword(k):
                k = k[:-1]
            self._set_task_parameter(k, v)
        return self

    def _set_task_parameter_by_name(self, name, value) -> Task:
        """ Set a specific task parameter by a human-readble name. """
        key = self._task_parameter_definitions_name_to_key.get(name)
        self._set_task_parameter(key, value)
        return self

    def _set_task_parameter(self, key, value) -> Task:
        """ Set a specific task parameter. """
        if self._is_frozen:
            raise TaskFrozenError(
                "This task is frozen and cannot be modified. Call `<Task>._unfreeze() first."
            )
        setattr(self.task_parameters, key, value)
        return self

    @staticmethod
    def _to_list_from_dict(input_dict: dict) -> List[dict]:
        """
        Turn a dynamically-keys dictionary representing parameters and values into
        the list of static keyed "param" and "value" dictionaries.
        """
        return sorted(
            [{"param": p, "value": v} for p, v in input_dict.items()],
            key=lambda x: x["param"],
        )

    @staticmethod
    def _to_list_dict_from_list_param_value(
        list_param_value: List[ParamValuePair],
    ) -> List[dict]:
        """
        Convert a list of `ParamValuePair` into a list of dictionaries with "param" and "value"
        keys with their respective values.
        """
        return sorted(
            [param_value.as_json() for param_value in list_param_value],
            key=lambda x: x["param"],
        )

    @staticmethod
    def _to_param_values_from_list_dict(
        input_list: List[Dict[str, str]]
    ) -> List[ParamValuePair]:
        """
        Convert a list of "param", "value" keyed dictionary
        into a list of `ParamValuePair`
        """
        return [ParamValuePair(**p_v) for p_v in input_list]

    @staticmethod
    def _to_param_values_from_dict(input_dict: Dict[str, str]) -> List[ParamValuePair]:
        """
        Convert a dict of parameters and values into a list of `ParamValuePair`
        """
        return [ParamValuePair(p, v) for p, v in input_dict.items()]

    @staticmethod
    def _build_input_mapping(
        inputs, mapping: Optional[Dict[str, Union[str, Task]]] = None
    ) -> List[str]:
        """
        Builds a map from one set of inputs to another, based on a provided map,
        while preserving any inputs which do not have a mapping. (e.g. input types).

        Useful for transforming index-based inputs to actual vertices.

        For example:
        ['NUM', '1', '2'] -> ['NUM', <Task:0x1>, <Task:0x2>]

        Parameters
        ----------
        inputs: dict(string, string or Task)
            Inputs to map to new keys or values.
        mapping: dict or None (Default=None)
            By default, there is no mapping, so there's nothing to change. But, if a
            dictionary is passed in, map the values accordingly.

        Returns
        -------
        dict or list
        """
        if mapping is None:
            return inputs
        return [mapping.get(hex_or_identity(vertex), vertex) for vertex in inputs]

    def _ensure_no_cycles(self, seen=None):
        """ Descend into the inputs of the current task to ensure there are no cycles. """
        if seen is None:
            seen = {id(self)}
        task_inputs = [inp for inp in self._inputs if isinstance(inp, Task)]
        for inp in task_inputs:
            if id(inp) in seen:
                # There's a cycle, so we can't properly resolve the hex
                raise CycleException("Cycle found: tasks cannot contain cycles.")
            else:
                seen_copy = copy.deepcopy(seen)
                seen_copy.add(id(inp))
                inp._ensure_no_cycles(seen_copy)
                seen_copy.remove(id(inp))

    def _refresh_cached(self, attr_to_exclude=None):
        """Refresh cached attributes (set to None) of Task.

        Parameters
        ----------
        attr_to_exclude:
            A list of attributes which are not to be refreshed.
        """
        refresh_cached(self, self._attr_to_refresh, attr_to_exclude)

    def _freeze(self):
        """ Internal only: freeze the task and its inputs for performance. """
        if self._is_frozen:
            return
        self._refresh_cached()
        for i in self._inputs:
            if isinstance(i, Task):
                i._freeze()
        self._frozen = True

    def _unfreeze(self):
        """ Internal only: unfreeze the task and its inputs for modification. """
        for i in self._inputs:
            if isinstance(i, Task):
                i._unfreeze()
        self._frozen = False

    def _assert_unfrozen(self):
        """ Ensure the task is frozen, or raise an exception. """
        if self._is_frozen:
            raise TaskFrozenError(
                "This task is frozen and cannot be modified. Call `<Task>._unfreeze() first."
            )

    def __setattr__(self, key, value):
        """ Ensure the task is not frozen before setting. """
        if key != "_frozen" and key not in self._attr_to_refresh:
            self._assert_unfrozen()
        super(Task, self).__setattr__(key, value)

    def __hash__(self):
        """ The hash representation of the task. """
        return int(self.task_id, 16)

    def __eq__(self, other):
        """ A way to determine if two tasks are identical in parameters and input. """
        if not isinstance(other, Task):
            return False
        return self.serialize() == other.serialize()

    @property
    def _is_frozen(self):
        return getattr(self, "_frozen", False)

    @classmethod
    def _colname_and_type_from_name(
        cls, workshop: WorkshopInterface, feature_name: str
    ) -> ColnameAndType:
        return workshop._colname_and_type_colname_lookup.get(feature_name)

    @classmethod
    def _colname_and_type_from_hex(
        cls,
        workshop: WorkshopInterface,
        feature_hex: str,
        alternate_lookup: Optional[Dict[str, ColnameAndType]] = None,
    ) -> ColnameAndType:
        subject = str(feature_hex)
        feature = workshop._colname_and_type_hex_lookup.get(subject)
        if feature is not None:
            return feature
        fallback = ColnameAndType(hex=subject, colname="_UNKNOWN_", type="UNKNOWN")
        if alternate_lookup is not None:
            fallback = alternate_lookup.get(subject, fallback)
        return fallback

    def __call__(self, *inputs, replace_inputs=False):
        """
        Calling a Task saves a reference to the provided input arguments
        as inputs to the caller, creating a directed graph.

        Any Task can be passed as input to a BlueprintGraph to create a full
        blueprint. At which point, it can be ensured that it's a valid DAG and be topologically
        sorted, along with other necessary verification of criteria necessary to be a valid
        DataRobot blueprint.

        The inputs may be one of: an input data type string, another Task,
        or a Blueprint.

        Parameters
        ----------
        functional_members: list(Task or string)
            Note: Any string passed must be a member of BlueprintColumnClass
        replace_inputs: bool
            Whether to replace the current inputs, instead of append to them
        """
        new_inputs = []
        for m in inputs:
            if isinstance(m, Task) or isinstance(m, str) and represents_input_data(m):
                new_inputs.append(m)
            else:
                raise TypeError(
                    "Inputs must either be a Task, or a string of the TaskInput"
                )
        if replace_inputs:
            self._inputs = new_inputs
        else:
            self._inputs += new_inputs
        return self


class FeatureSelection(Task):
    """
    A special type of task that selects features from project data.

    Please note: This feature is unreleased and may not be available on your account.
    """

    def __init__(
        self,
        workshop: WorkshopInterface,
        feature_names: Iterable[Union[str, Feature]],
        task_code="MCPICK",
        exclude: bool = False,
        **kwargs
    ):
        # Convert any `Feature`s to just the colname
        feature_names = [
            f.selected_features[0].colname if isinstance(f, Task) else f
            for f in feature_names
        ]

        # TODO: Remove the need to reference a specific task
        super(FeatureSelection, self).__init__(
            workshop=workshop,
            task_code=task_code,
            task_parameters=self.build_task_parameters(
                workshop, feature_names, exclude=exclude
            ),
            **kwargs
        )
        # Ensure we add the proper input
        data_types = sorted(
            set(
                self._colname_and_type_from_name(workshop, feature_name).type
                for feature_name in feature_names
            )
        )
        if len(data_types) > 1:
            raise ValueError(
                "Multiple data types found: {}, only 1 allowed.".format(data_types)
            )
        self(data_types[0])

    def select_features(self, feature_names: Iterable[str]) -> Task:
        """ Choose a specific feature, and only take input from this feature. """
        task_parameters = self.build_task_parameters(self._workshop, feature_names)
        return self._set_task_parameters(
            **{tp.param: tp.value for tp in task_parameters}
        )

    @classmethod
    def build_task_parameters(
        cls,
        workshop: WorkshopInterface,
        feature_names: Iterable[str],
        exclude: bool = False,
    ) -> List[ParamValuePair]:
        """ Build the task parameters for a FeatureSelection. """
        for feature_name in feature_names:
            if cls._colname_and_type_from_name(workshop, feature_name) is None:
                raise ValueError(
                    'The feature "{}" does not exist in this project.'.format(
                        feature_name
                    )
                )

        return [
            ParamValuePair(
                param=_COLNAMES_PARAM,
                value=[
                    str(cls._colname_and_type_from_name(workshop, feature_name).hex)
                    for feature_name in feature_names
                    if cls._colname_and_type_from_name(workshop, feature_name)
                    is not None
                ],
            ),
            ParamValuePair(
                param=_SELECT_COLNAME_METHOD, value="exclude" if exclude else "include"
            ),
        ]


class Feature(FeatureSelection):
    """ A special type of task that selects a feature from project data. """

    def __init__(
        self,
        workshop: WorkshopInterface,
        feature_name: str,
        task_code="SCPICK",
        **kwargs
    ):
        super(Feature, self).__init__(
            workshop=workshop,
            feature_names=[feature_name],
            task_code=task_code,
            **kwargs
        )

    @classmethod
    def build_task_parameters(
        cls,
        workshop: WorkshopInterface,
        feature_names: List[str],
        exclude: bool = False,
    ) -> List[ParamValuePair]:
        """ Build the task parameters for a Feature. """
        if len(feature_names) > 1:
            raise ValueError("Only a single feature is allowed.")

        feature_name = feature_names[0]
        feature = cls._colname_and_type_from_name(workshop, feature_name)
        if feature is None:
            raise ValueError(
                'The feature "{}" does not exist in this project.'.format(feature_name)
            )

        hex_feature = str(feature.hex)
        return [ParamValuePair(param=_COLNAME_PARAM, value=hex_feature)]


class UnsupportedTaskDefinition(UserBlueprintTaskDefinition):
    """ This task is not supported, but can still be used. """

    def __init__(self, task_code: str):
        print('Note: Unsupported task initialized: "{}"'.format(task_code))
        super(UnsupportedTaskDefinition, self).__init__(
            arguments=[],
            categories=[],
            description="This task is not supported, but can still be used.",
            icon=0,
            label=task_code,
            output_methods=[TaskOutputMethod.all()],
            task_code=task_code,
            time_series_only=False,
            url="",
            valid_inputs=[],
        )


class UnavailableCustomTaskDefinition(UserBlueprintTaskDefinition):
    """ This custom task is not available. """

    def __init__(self, task_code: str, version_id: str):
        print(
            (
                'Note: Unavailable custom task: "{}", with version: "{}". '
                "This custom task may no longer exist, or may be inaccessible to you. "
                "Please request the owner of the blueprint to share this task with you."
            ).format(task_code, version_id)
        )
        super(UnavailableCustomTaskDefinition, self).__init__(
            arguments=[],
            categories=[],
            description="This task is not available to you.",
            icon=0,
            label="Unknown Custom Task",
            output_methods=[TaskOutputMethod.all()],
            task_code=task_code,
            time_series_only=False,
            url="",
            valid_inputs=[],
        )


def build_custom_task_versions(task_definition: UserBlueprintTaskDefinition):
    """
    Create a readable list of versions with id and label for each, for a custom task.

    Parameters
    ----------
    task_definition: UserBlueprintTaskDefinition

    Returns
    -------
    Versions
        The list of versions of a custom task.
    """

    class Versions(FriendlyRepr):
        __doc__ = UserBlueprintHelper.get_docstring_for_versions(
            task_definition.custom_task_versions, title=task_definition.label,
        )

        def __init__(self):
            for version in task_definition.custom_task_versions:
                setattr(self, version.label.replace(".", "_"), version.id)

        def __friendly_repr__(self):
            return UserBlueprintHelper.get_docstring_for_versions(
                task_definition.custom_task_versions,
                title=task_definition.label,
                minified=True,
            )

    return Versions()
