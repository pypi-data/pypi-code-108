# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
from typing import (
    Dict,
    Set,
)

from dateutil.parser import isoparse
from gql import gql
from inflection import underscore
from qctrlcommons.exceptions import QctrlException
from rich.console import Console
from rich.table import Table

from .base import StaticQuery


class ActivityMonitorQuery(StaticQuery):
    """Retrieves recent activity."""

    query = gql(
        """
        query getActions($limit: Int, $offset: Int, $filterBy: ActionFilter) {
            actions(limit:$limit, offset:$offset, filterBy:$filterBy) {
                actions {
                    name
                    status
                    modelType
                    progress
                    createdAt
                    updatedAt
                    modelId
                }
                errors {
                    message
                }
            }
        }
    """
    )

    def _get_variable_values(  # pylint:disable=arguments-differ
        self, limit: int, offset: int, status: str = None, action_type: str = None
    ):

        if limit < 1:
            raise QctrlException("Limit cannot be less than 1.")

        if offset < 0:
            raise QctrlException("Offset cannot be less than 0.")

        if status:
            valid_statuses = self.get_valid_statuses()

            if status not in valid_statuses:
                raise QctrlException(
                    f"Status '{status}' is not valid. "
                    f"Please choose from a valid status type: "
                    f"{valid_statuses}"
                )

        if action_type:
            valid_action_types = self.get_valid_types()

            if action_type not in valid_action_types:
                raise QctrlException(
                    f"Action type '{action_type}' is not valid. "
                    f"Please choose from a valid action type: "
                    f"{valid_action_types}"
                )

        filter_by = {}

        if status:
            filter_by["status"] = {"exact": status}

        if action_type:
            filter_by["modelType"] = {"exact": action_type}

        return {"limit": limit, "offset": offset, "filterBy": filter_by}

    def _format_response(self, response: Dict, *_) -> None:
        def _snake_core_name(name):
            if name[:6] == "core__":
                name = underscore(name[6:])
            return name

        table = Table(title="Activity monitor", show_lines=True)
        console = Console()

        table.add_column("Action name\n(Type)", overflow="fold")
        table.add_column("ID", overflow="fold")
        table.add_column("Status", justify="center")
        table.add_column("Created at\nCompleted at")
        table.add_column("Runtime", overflow="fold")

        for row in response["actions"]["actions"]:
            name = _snake_core_name(row["name"])
            created_at = isoparse(row["createdAt"]).strftime("%Y-%m-%d %H:%M:%S")
            completed_at = (
                ""
                if row["status"] == "STARTED" or row["status"] == "PENDING"
                else isoparse(row["updatedAt"]).strftime("%Y-%m-%d %H:%M:%S")
            )
            runtime = isoparse(row["updatedAt"]) - isoparse(row["createdAt"])

            table.add_row(
                f'{name}\n({row["modelType"]})',
                f'{row["modelId"]}',
                f'{row["status"]}\n({row["progress"]:.0%}) ',
                f"{created_at}\n{completed_at} ",
                f"{str(runtime).split('.', maxsplit=1)[0]} ",
            )

        console.print(table)

    def _get_enum_values(self, enum_type: str) -> Set:
        """Retrieves the enum values from the schema.
        Parameters
        ----------
        enum_type: str
            Graphql enum type name
        Returns
        -------
        Set
            enum set value.
        Raises
        ------
        TypeError
            invalid enum type name.
        """
        field_type = self._client.schema.get_type(enum_type)

        if field_type is None:
            raise TypeError(f"unknown enum_type: {enum_type}")

        return set(field_type.values.keys())

    def get_valid_statuses(self) -> Set:
        """Returns the set of valid statuses."""
        return self._get_enum_values("ActionStatusEnum")

    def get_valid_types(self) -> Set:
        """Returns the set of valid types."""
        return self._get_enum_values("ActionTypeEnum")
