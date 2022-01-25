"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, List, TypeVar

from .datarobot_client import UserBlueprintTaskDefinition

from datarobot_bp_workshop.friendly_repr import FriendlyRepr
from datarobot_bp_workshop.task import Task, build_custom_task_versions
from datarobot_bp_workshop.user_blueprint_helper import UserBlueprintHelper
from datarobot_bp_workshop.utils import documentation, TaskOutputMethod
from datarobot_bp_workshop.workshop_interface import WorkshopInterface


class TaskFactory(object):
    def __init__(
        self, workshop: WorkshopInterface,
    ):
        self._workshop = workshop
        self.task_definition_lookup = workshop._task_definitions_by_task_code
        self.custom_task_definition_lookup = workshop._custom_tasks_by_id
        self.custom_task_version_definition_lookup = (
            workshop._custom_tasks_by_version_id
        )

    def get_key(self, task_definition: UserBlueprintTaskDefinition):
        if task_definition.custom_task_id is None:
            return task_definition.task_code

        return "{}_{}".format(task_definition.task_code, task_definition.custom_task_id)

    def __call__(self, task_definition: UserBlueprintTaskDefinition):
        """
        Parameters
        ----------
        task_definition: UserBlueprintTaskDefinition
        """
        arguments = UserBlueprintHelper.get_arguments(task_definition.arguments)

        # Important that this is an object, as we use __dict__
        class TaskParameters(FriendlyRepr):
            def __init__(zelf):
                for argument in arguments:
                    setattr(zelf, argument.key, argument.argument)

            def __friendly_repr__(self):
                return UserBlueprintHelper.get_docstring_for_arguments(
                    arguments, title=task_definition.label, minified=True
                )

        TaskParameters.__doc__ = UserBlueprintHelper.get_docstring_for_arguments(
            arguments, title=task_definition.label
        )

        class Helper(object):
            __doc__ = "\n".join(
                [
                    task_definition.label,
                    "",
                    task_definition.description,
                    "",
                    "Parameters",
                    "----------",
                    "output_method: string, one of ({}).".format(
                        ", ".join(
                            [
                                TaskOutputMethod.get_variable_name(m)
                                for m in task_definition.output_methods
                            ]
                        )
                    ),
                    "task_parameters: dict, which may contain:",
                ]
                + [
                    "\n  "
                    + "\n\n  ".join(
                        [
                            (
                                "{name} ({key}): {type}, (Default={default})"
                                "\n    Possible Values: {values}"
                            ).format(
                                name=a.argument.name,
                                key=a.key,
                                type=a.argument.type,
                                default=a.argument.default.__repr__(),
                                values=a.argument.values,
                            )
                            for a in UserBlueprintHelper.get_arguments(
                                task_definition.arguments
                            )
                        ]
                    )
                ]
            )

            description = task_definition.description
            label = task_definition.label
            task_code = task_definition.task_code

            def documentation(zelf, auto_open=False):
                return documentation(task_definition, auto_open)

            task_parameters = TaskParameters()

            def __call__(
                zelf,
                *inputs,
                output_method=None,
                task_parameters=None,
                output_method_parameters=None,
                x_transformations=None,
                y_transformations=None,
                freeze=False,
                version=None,
            ):
                return Task(
                    workshop=self._workshop,
                    task_code=task_definition.task_code,
                    output_method=output_method,
                    task_parameters=task_parameters,
                    output_method_parameters=output_method_parameters,
                    x_transformations=x_transformations,
                    y_transformations=y_transformations,
                    freeze=freeze,
                    custom_task_id=task_definition.custom_task_id,
                    version=version,
                )(*inputs)

            def __friendly_repr__(zelf):
                name = "{}: [{}{}]".format(
                    zelf.label,
                    task_definition.task_code,
                    ""
                    if task_definition.custom_task_id is None
                    else "_{}".format(task_definition.custom_task_id),
                )
                return "{} \n  - {}\n".format(
                    name, zelf.description or "(No description)"
                )

        tasks_class_attributes = dict(
            __doc__=Helper.__doc__,
            __call__=Helper.__call__,
            __friendly_repr__=Helper.__friendly_repr__,
            description=Helper.description,
            label=Helper.label,
            task_code=Helper.task_code,
            documentation=Helper.documentation,
            task_parameters=Helper.task_parameters,
        )

        if task_definition.custom_task_id:
            tasks_class_attributes["versions"] = build_custom_task_versions(
                task_definition
            )

        tasks_class_type = type(
            self.get_key(task_definition), (FriendlyRepr,), tasks_class_attributes
        )

        return tasks_class_type()


T = TypeVar("T")


class SimpleFactory(Generic[T]):
    """ Build a data-driven class and instantiate it. """

    def __init__(self, field_items: List[T]) -> None:
        self.field_items = field_items

    def __call__(
        self,
        get_key: Callable[[T], str],
        get_value: Callable[[T], Any],
        get_type: Callable[[T], str],
        get_description: Callable[[T], str],
        title: str,
        class_name: str,
    ):
        field_docstring_lines = [
            "{}: {}"
            "\n  {}".format(
                get_key(field_item), get_type(field_item), get_description(field_item),
            )
            for field_item in self.field_items
        ]

        docstring = "\n".join(
            [title, "", "Parameters", "----------"] + field_docstring_lines
        )

        def __friendly_repr__(zelf):
            return (
                title
                + "\n\n"
                + "{}".format(
                    ", ".join(get_key(field_item) for field_item in self.field_items)
                )
            )

        class_attributes = dict(
            {
                get_key(field_item): get_value(field_item)
                for field_item in self.field_items
            },
            __doc__=docstring,
            __friendly_repr__=__friendly_repr__,
        )

        class_type = type(class_name, (FriendlyRepr,), class_attributes)
        return class_type()
