# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This module provides task representations."""
from typing import Any, Optional
import json

from azure.storage.queue import QueueMessage
from azureml._restclient.models import IterationTask


class QueuedTask:
    """Represents an AutoML task in the Queue.

    Each message in Azure Storage Queue represents one task dto for an iteration.
    :ivar :class:`~azure.storage.queue.models.QueueMessage` message:
        reference to the QueueMessage object.
    """

    def __init__(self, message: Optional[QueueMessage] = None, task: Optional[IterationTask] = None):
        """Initialize an instance.

        :param azure.storage.queue.models.QueueMessage message:
            A :class:`~azure.storage.queue.models.QueueMessage` object representing the information passed.
        :param IterationTask task: task dto that stores pipeline info for the current child iteration.
        """
        self._message = message
        self._task = task

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message: QueueMessage) -> None:
        self._message = message

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task: IterationTask) -> None:
        self._task = task

    @staticmethod
    def from_queue_message(message: QueueMessage) -> Any:
        obj = json.loads(message.content)
        task = IterationTask.deserialize(obj)
        return QueuedTask(message=message.content, task=task)

    def to_json(self):
        """Return a json string for the instance.

        Don't serialize None or message.
        """
        return json.dumps({"task": self.task.serialize()})
