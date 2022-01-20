"""
Mixin to add methods to a Task to support globus transfers
"""
import logging
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import List
from typing import Union

from globus_sdk import ClientCredentialsAuthorizer
from globus_sdk import ConfidentialAppAuthClient
from globus_sdk import GlobusError
from globus_sdk import TransferData

from dkist_processing_common._util.globus import TransferClient

# from globus_sdk import TransferClient  # use this after upgrading to globus-sdk 3.x


logger = logging.getLogger(__name__)


@dataclass
class GlobusTransferItem:
    source_path: Union[str, Path]
    destination_path: Union[str, Path]
    recursive: bool = False  # file


class GlobusMixin:
    @property
    def globus_transfer_client(self) -> TransferClient:
        if getattr(self, "_globus_transfer_client", False):
            return self._globus_transfer_client
        confidential_client = ConfidentialAppAuthClient(
            client_id=environ.get("GLOBUS_CLIENT_ID"),
            client_secret=environ.get("GLOBUS_CLIENT_SECRET"),
        )
        authorizer = ClientCredentialsAuthorizer(
            confidential_client, scopes="urn:globus:auth:scope:transfer.api.globus.org:all"
        )
        self._globus_transfer_client = TransferClient(authorizer=authorizer)
        return self._globus_transfer_client

    @property
    def globus_object_store_endpoint(self) -> str:
        return environ.get("OBJECT_STORE_ENDPOINT")

    @property
    def globus_scratch_endpoint(self) -> str:
        return environ.get("SCRATCH_ENDPOINT")

    def globus_transfer_scratch_to_object_store(
        self,
        transfer_items: List[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        self.globus_transfer(
            source_endpoint=self.globus_scratch_endpoint,
            destination_endpoint=self.globus_object_store_endpoint,
            transfer_items=transfer_items,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def globus_transfer_object_store_to_scratch(
        self,
        transfer_items: List[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        self.globus_transfer(
            source_endpoint=self.globus_object_store_endpoint,
            destination_endpoint=self.globus_scratch_endpoint,
            transfer_items=transfer_items,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def globus_transfer(
        self,
        source_endpoint: str,
        destination_endpoint: str,
        transfer_items: List[GlobusTransferItem],
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> None:
        transfer_data = self._globus_transfer_configuration(
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )
        for item in transfer_items:
            transfer_data.add_item(
                source_path=item.source_path,
                destination_path=item.destination_path,
                recursive=item.recursive,
            )
        self._blocking_globus_transfer(transfer_data=transfer_data)

    def _globus_transfer_configuration(
        self,
        source_endpoint: str,
        destination_endpoint: str,
        label: str = None,
        sync_level: str = None,
        verify_checksum: bool = True,
    ) -> TransferData:
        label = label or "Data Processing Transfer"
        return TransferData(
            transfer_client=self.globus_transfer_client,
            source_endpoint=source_endpoint,
            destination_endpoint=destination_endpoint,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
        )

    def _blocking_globus_transfer(self, transfer_data: TransferData) -> None:
        tc = self.globus_transfer_client
        logger.info(f"Starting globus transfer: label={transfer_data.get('label')}")
        transfer_result = tc.submit_transfer(transfer_data)
        task_id = transfer_result["task_id"]
        while not tc.task_wait(task_id=task_id, polling_interval=60):
            for event in tc.task_event_list(task_id=task_id, num_results=None):
                if event["is_error"]:
                    tc.cancel_task(task_id=task_id)
                    message = f"Transfer unsuccessful: {event['description']=}, {event['details']=}, recipe_run_id={self.recipe_run_id}, {task_id=}"
                    logger.error(message)
                    raise GlobusError(message)
        logger.info(
            f"Transfer Completed Successfully: recipe_run_id={self.recipe_run_id}, {task_id=}"
        )
