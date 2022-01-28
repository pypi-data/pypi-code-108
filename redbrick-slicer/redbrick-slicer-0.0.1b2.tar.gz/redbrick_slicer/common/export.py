"""Abstract interface to exporting data from a project."""

from typing import Dict
from abc import ABC, abstractmethod


class ExportControllerInterface(ABC):
    """Abstract interface to define methods for Export."""

    @abstractmethod
    def get_output_info(
        self,
        org_id: str,
        project_id: str,
    ) -> Dict:
        """Get info about the output labelset and taxonomy."""

    @abstractmethod
    def get_datapoint_latest(self, org_id: str, project_id: str, task_id: str) -> Dict:
        """Get the latest labels for a single datapoint."""
