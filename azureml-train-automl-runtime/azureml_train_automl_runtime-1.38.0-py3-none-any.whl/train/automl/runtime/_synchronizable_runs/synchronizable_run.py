# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict

from azureml.automl.core.shared import logging_utilities
from azureml.core import Run


logger = logging.getLogger(__name__)


class SynchronizableRun(Run):
    """
    A synchronizable run is a run that accepts local, in-memory modifications to run properties and tags.
    On an azureml.core.Run object, every call to set_properties and set_tags triggers a call to the RH service.
    SynchronizableRun aims to call the RH service more sparingly. Properties and tags are set in memory as
    frequently as desired. When the run is synchronized, all modified properties and tags are batch updated to RH.
    """

    def __init__(self, experiment, run_id, **kwargs):
        super().__init__(experiment, run_id, **kwargs)

        # The dictionaries below store properties and tags that will be uploaded to the server
        # when the run is synchronized.
        self._properties_to_sync = {}  # type: Dict[str, str]
        self._tags_to_sync = {}  # type: Dict[str, str]

    @property
    def properties(self) -> Dict[str, str]:
        return {**super().properties, **self._properties_to_sync}

    @property
    def tags(self) -> Dict[str, str]:
        return {**super().tags, **self._tags_to_sync}

    def add_properties(self, properties: Dict[str, str]) -> None:
        self._properties_to_sync.update(properties)

    def get_properties(self) -> Dict[str, str]:
        return {**super().get_properties(), **self._properties_to_sync}

    def get_tags(self) -> Dict[str, str]:
        return {**super().get_tags(), **self._tags_to_sync}

    def set_tags(self, tags: Dict[str, str]) -> None:
        self._tags_to_sync.update(tags)

    def synchronize(self) -> None:
        """Upload any unsynchronized run properties and tags to RH."""
        if self._properties_to_sync:
            super().add_properties(self._properties_to_sync)
            self._properties_to_sync.clear()

        if self._tags_to_sync:
            super().set_tags(self._tags_to_sync)
            self._tags_to_sync.clear()
