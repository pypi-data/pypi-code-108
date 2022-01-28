"""Public API to exporting."""
import json
from typing import Dict, Tuple, List, Optional

from redbrick_slicer.common.context import RBContext


def _clean_rb_label(label: Dict) -> Dict:
    """Clean any None fields."""
    for key, val in label.copy().items():
        if val is None:
            del label[key]
    return label


def _flat_rb_format(
    labels: List[Dict],
    items: List[str],
    items_presigned: List[str],
    name: str,
    created_by: str,
    task_id: str,
    current_stage_name: str,
    labels_path: Optional[str],
) -> Dict:
    """Get standard rb flat format, same as import format."""
    return {
        "labels": labels,
        "items": items,
        "itemsPresigned": items_presigned,
        "name": name,
        "taskId": task_id,
        "createdBy": created_by,
        "currentStageName": current_stage_name,
        "labelsPath": labels_path,
    }


def _parse_entry_latest(item: Dict) -> Dict:
    try:
        task_id = item["taskId"]
        task_data = item["latestTaskData"]
        datapoint = task_data["dataPoint"]
        items_presigned = datapoint["itemsPresigned"]
        items = datapoint["items"]
        name = datapoint["name"]
        created_by = task_data["createdByEmail"]
        labels = [
            _clean_rb_label(label) for label in json.loads(task_data["labelsData"])
        ]

        return _flat_rb_format(
            labels,
            items,
            items_presigned,
            name,
            created_by,
            task_id,
            item["currentStageName"],
            task_data["labelsPath"],
        )
    except (AttributeError, KeyError, TypeError, json.decoder.JSONDecodeError):
        return {}


class Export:
    """
    Primary interface to handling export from a project.

    This class has methods to export to various formats depending on
    your project type.
    """

    def __init__(self, context: RBContext, org_id: str, project_id: str) -> None:
        """Construct Export object."""
        self.context = context
        self.org_id = org_id
        self.project_id = project_id

    def get_raw_data_single(self, task_id: str) -> Tuple[Dict, Dict]:
        """Get task and taxonomy."""
        general_info = self.context.export.get_output_info(self.org_id, self.project_id)
        datapoint = self.context.export.get_datapoint_latest(
            self.org_id, self.project_id, task_id
        )
        task = _parse_entry_latest(datapoint)
        if not task:
            raise Exception("Task not found")
        return task, general_info["taxonomy"]
