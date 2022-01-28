"""Public interface to labeling module."""
import json
from typing import Dict, Optional
import gzip
import requests

from redbrick_slicer.common.context import RBContext


class Labeling:
    """
    Perform programmatic labeling and review tasks.

    The Labeling class allows you to programmatically submit tasks.
    This can be useful for times when you want to make bulk actions
    e.g accepting several tasks, or make automated actions like using automated
    methods for review.
    """

    def __init__(self, context: RBContext, org_id: str, project_id: str) -> None:
        """Construct Labeling."""
        self.context = context
        self.org_id = org_id
        self.project_id = project_id

    def put_task(self, stage_name: str, task: Dict) -> None:
        """
        Put tasks with new labels or review result.

        >>> project.labeling.put_task(...)

        Parameters
        --------------
        stage_name: str
            The stage to which you want to submit the tasks. This must be the
            same stage as which you called get_tasks on.

        task: Dict
            Tasks with new labels or review result. Please see doc for format.
            https://docs.redbrickai.com/python-sdk/programmatically-label-and-review
        """
        task_id = task["taskId"]
        labels_path: Optional[str] = None
        task_blob = task.get("labelsBlob")
        if task_blob and isinstance(task_blob, bytes):
            presigned = self.context.labeling.presign_labels_path(
                self.org_id,
                self.project_id,
                task_id,
                "application/octet-stream",
            )
            labels_path = presigned["filePath"]
            requests.put(
                presigned["presignedUrl"],
                headers={
                    "Content-Encoding": "gzip",
                    "Content-Type": "application/octet-stream",
                },
                data=gzip.compress(task_blob),
            )
        labels = task["labels"]
        self.context.labeling.put_labeling_results(
            self.org_id,
            self.project_id,
            stage_name,
            task_id,
            json.dumps(labels),
            labels_path,
            not bool(task.get("draft")),
        )

    def assign_task(self, stage_name: str, task_id: str, email: str) -> None:
        """Assign task to specified email."""
        self.context.labeling.assign_task(
            self.org_id, self.project_id, stage_name, task_id, email
        )
