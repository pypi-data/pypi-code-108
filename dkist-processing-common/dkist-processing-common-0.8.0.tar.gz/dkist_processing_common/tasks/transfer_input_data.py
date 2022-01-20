"""
Task(s) for the transfer in of data sources for a processing pipeline
"""
import logging
from pathlib import Path
from typing import List

from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowDataTaskBase
from dkist_processing_common.tasks.mixin.globus import GlobusMixin
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin
from dkist_processing_common.tasks.mixin.metadata_store import MetadataStoreMixin

__all__ = ["TransferL0Data"]

logger = logging.getLogger(__name__)


class TransferL0Data(WorkflowDataTaskBase, GlobusMixin, MetadataStoreMixin, InputDatasetMixin):
    """
    Transfers Level 0 data to the scratch store
    """

    def download_input_dataset(self):
        raw_input_dataset = self.metadata_store_input_dataset_document
        self.write(file_obj=raw_input_dataset.encode("utf8"), tags=Tag.input_dataset())

    def format_transfer_items(self) -> List[GlobusTransferItem]:
        transfer_items = []
        bucket = self.input_dataset_bucket
        for frame in self.input_dataset_frames:
            source_path = Path("/", bucket, frame)
            destination_path = self.scratch.absolute_path(frame)
            transfer_items.append(
                GlobusTransferItem(
                    source_path=source_path,
                    destination_path=destination_path,
                    recursive=False,
                )
            )
        return transfer_items

    def tag_input_data(self, transfer_items: List[GlobusTransferItem]):
        scratch_items = [
            self.scratch.scratch_base_path / ti.destination_path for ti in transfer_items
        ]
        for si in scratch_items:
            self.tag(si, tags=[Tag.input(), Tag.frame()])

    def run(self) -> None:
        with self.apm_step("Change Status to InProgress"):
            self.metadata_store_change_recipe_run_to_inprogress()

        with self.apm_step("Download Input Dataset"):
            self.download_input_dataset()

        with self.apm_step("Format Transfer Items"):
            transfer_items = self.format_transfer_items()

        if not transfer_items:
            raise ValueError("No input dataset frames found")

        with self.apm_step("Transfer Inputs via Globus"):
            self.globus_transfer_object_store_to_scratch(
                transfer_items=transfer_items,
                label=f"Transfer Inputs for Recipe Run {self.recipe_run_id}",
            )

        with self.apm_step("Tag Input Data"):
            self.tag_input_data(transfer_items=transfer_items)
