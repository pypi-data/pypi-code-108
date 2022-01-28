"""Abstract interface to exporting."""
from typing import Optional, Dict
from abc import ABC, abstractmethod


class LabelingControllerInterface(ABC):
    """Abstract interface to Labeling APIs."""

    @abstractmethod
    def presign_labels_path(
        self,
        org_id: str,
        project_id: str,
        task_id: str,
        file_type: str,
    ) -> Dict:
        """Presign labels path."""

    @abstractmethod
    def put_labeling_results(
        self,
        org_id: str,
        project_id: str,
        stage_name: str,
        task_id: str,
        labels_data: str,
        labels_path: Optional[str] = None,
        finished: bool = True,
    ) -> None:
        """Put Labeling results."""

    @abstractmethod
    def assign_task(
        self, org_id: str, project_id: str, stage_name: str, task_id: str, email: str
    ) -> None:
        """Assign task to specified email."""
