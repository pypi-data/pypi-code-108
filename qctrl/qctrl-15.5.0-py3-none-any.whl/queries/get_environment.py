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
    Any,
    Dict,
)

from gql import gql

from .base import StaticQuery


class EnvironmentQuery(StaticQuery):  # pylint:disable=too-few-public-methods
    """Retrieves info about the current environment."""

    query = gql(
        """
        query getEnvironment {
            environment {
                environment {
                    workers {
                        name
                        queues
                        totalProcesses
                        activeTasks
                        reservedTasks
                        queuedTasks
                    }
                }
                errors {
                    message
                }
            }
        }
    """
    )

    @staticmethod
    def _get_availability(data: Dict[str, Any]) -> str:
        """
        Calculates the queue/worker availability
        based on active tasks and total processes.

        Parameters
        ----------
        data: Dict[str, Any]
            worker or queue data
        Returns
        -------
        float
            availability
        """
        num_active = float(data["activeTasks"])
        num_total = float(data["totalProcesses"])

        result = 1 - num_active / num_total
        return f"{result*100:.1f}%"


class GetWorkerInfoQuery(EnvironmentQuery):  # pylint:disable=too-few-public-methods
    """Formats the environment info by worker."""

    def _format_response(self, response: dict, *_) -> str:

        result = (
            f'{"Worker Name":<60} '
            f'{"Queue(s)":<30} '
            f'{"Total Processes":<20} '
            f'{"Active Tasks":<20} '
            f'{"Availability":<20} '
            f'{"Reserved Tasks":<20} '
            "\n"
        )

        for worker in response["environment"]["environment"]["workers"]:
            result += (
                "\n"
                f'{worker["name"]:<60} '
                f'{", ".join(worker["queues"]):<30} '
                f'{worker["totalProcesses"]:<20} '
                f'{worker["activeTasks"]:<20} '
                f"{self._get_availability(worker):<20}"
                f'{worker["reservedTasks"]:<20}'
                "\n"
            )

        return result


class GetQueueInfoQuery(EnvironmentQuery):  # pylint:disable=too-few-public-methods
    """Formats the environment info by queue."""

    def _format_response(self, response: Dict, *_) -> str:
        """
        Formats the query output into a readable table-like manner.

        Parameters
        ----------
        response : Dict
            environment raw query result.

        Returns
        -------
        str
            formatted query output.

        Raises
        ------
        QctrlGqlException
            Any handled error that occurred on the server
        """
        result = (
            f'{"Queue":<60} '
            f'{"Workers":<30} '
            f'{"Total Processes":<20} '
            f'{"Active Tasks":<20} '
            f'{"Availability":<20} '
            f'{"Queued Tasks":<20} '
            "\n"
        )
        env_info = {
            "worker": 0,
            "totalProcesses": 0,
            "activeTasks": 0,
            "Availability": 0,
            "queuedTasks": 0,
        }
        queues = {}

        for worker in response["environment"]["environment"]["workers"]:
            # assume one worker belongs to one queue only
            queue = worker["queues"][0]
            if queue not in queues:
                queues.update({queue: env_info.copy()})
            queues[queue]["worker"] += 1
            queues[queue]["totalProcesses"] += worker["totalProcesses"]
            queues[queue]["activeTasks"] += worker["activeTasks"]
            queues[queue]["queuedTasks"] += worker["queuedTasks"]
            queues[queue]["Availability"] = self._get_availability(queues[queue])

        for queue_name, queue_info in queues.items():
            result += (
                "\n"
                f"{queue_name:<60} "
                f'{queue_info["worker"]:<30} '
                f'{queue_info["totalProcesses"]:<20} '
                f'{queue_info["activeTasks"]:<20} '
                f'{queue_info["Availability"]:<20} '
                f'{queue_info["queuedTasks"]:<20} '
                "\n"
            )

        return result
