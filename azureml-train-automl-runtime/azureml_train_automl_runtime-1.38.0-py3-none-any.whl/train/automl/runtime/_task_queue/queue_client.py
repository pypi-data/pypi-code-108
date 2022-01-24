# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This module provides features receive tasks from azure storage queue."""
from typing import Any
import json

from azure.storage.queue import QueueClient as AzureQueueClient, QueueMessage

from azureml._restclient.models import IterationTask
from azureml.automl.core.shared._diagnostics.contract import Contract

from .queued_task import QueuedTask
from .utilities import compress, decompress


class QueueClient:
    """This class provides features to receive tasks from azure storage queue.

    This class is used in the task server on all nodes.
    """

    # A single queue message can be up to 64 KB in size.
    # https://pypi.org/project/azure-storage-queue/
    MESSAGE_SIZE_LIMIT_IN_BYTES = 64 * 1024

    QUEUE_NAME_FORMAT = "queue-{parent_run_id}"
    TERMINATE_QUEUE = "Terminate"

    def __init__(self, parent_run_id: str, account_name: str, account_key: str, protocol: str, endpoint: str):
        """
        Init the queue client.
        :param parent_run_id: parent run id for AutoML run
        :param account_name: storage name
        :param account_key: storage account key
        :param protocol: protocol to use for connection
        :param endpoint: endpoint to use for connection
        """
        # Queue name must be lowercase, numbers, hyphens only
        # AutoML run id is of format AutoML_<guid>, so replace the underscore with hyphen
        # queue name must be between 3 to 63 characters long
        self.queue_name = self.QUEUE_NAME_FORMAT.format(parent_run_id=parent_run_id.lower().replace('_', '-'))

        self._queue_client = None
        self._con_str = (
            "DefaultEndpointsProtocol={protocol};AccountName={account_name};"
            "AccountKey={account_key};EndpointSuffix={endpoint}".format(
                protocol=protocol, account_name=account_name, account_key=account_key, endpoint=endpoint
            )
        )

    @property
    def queue_client(self) -> AzureQueueClient:
        """
        Init the queue client if not and then return it.
        :return: queue client created from connection string
        """
        self._queue_client = self._queue_client or AzureQueueClient.from_connection_string(self._con_str,
                                                                                           self.queue_name)

        return self._queue_client

    def _receive_message(self, visibility_timeout: int = 30) -> QueueMessage:
        """
        De-queue next message from queue.
        We request next message along with visibility timeout to mark the message invisible until we delete.
        This prevents other nodes from possibly getting the same message.
        Once message is dequeued, we decompress the message and return the QueueMessage.
        :param visibility_timeout: making the task invisible for specified time while queue is being deleted.
        :return: de-queued message
        """
        pages = self.queue_client.receive_messages(
            visibility_timeout=visibility_timeout
        ).by_page()

        try:
            page = next(pages)
            message = next(page)
        except StopIteration:
            return None

        self.queue_client.delete_message(message)
        message.content = decompress(message.content)

        return message

    def _enqueue_iteration_task(self, task: IterationTask) -> None:
        """
        Create a task and return the task id.
        This function to enqueue from SDK side is used for testing purposes only for now.

        :param task: IterationTask that contains run id and pipeline info for the particular iteration
        """
        task_in_json_str = json.dumps(task.serialize())
        message = compress(task_in_json_str)
        Contract.assert_true(
            len(message.encode("utf-8")) < self.MESSAGE_SIZE_LIMIT_IN_BYTES,
            "A single queue message can be up to 64 KB in size",
            log_safe=True
        )

        # Sending message with default TTL of 7 days
        # Ref:
        # https://docs.microsoft.com/en-us/python/api/azure-storage-queue/azure.storage.queue.aio.queueclient?view=azure-python#send-message-content----kwargs-
        # TODO: update message TTL to be min(experiment_timeout, 7 days)
        self.queue_client.send_message(content=message)

    def get_next_task(self, visibility_timeout: int = 30) -> Any:
        """
        Return a task from the azure storage queue.
        Calls _receive_message() to retrieve the next queued message and from the message,
        extract the task that will be used for the child iteration.

        :param visibility_timeout: making the task invisible for specified time while queue is being deleted.
        :return iteration task that contains IterationTask
        """
        message = self._receive_message(visibility_timeout=visibility_timeout)

        return QueuedTask.from_queue_message(message)

    async def close(self) -> None:
        """Close the client if it is not None."""
        if self._queue_client:
            await self._queue_client.close()
            self._queue_client = None
