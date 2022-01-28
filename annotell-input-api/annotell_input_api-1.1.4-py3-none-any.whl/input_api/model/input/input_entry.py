from dataclasses import dataclass
from typing import Optional, List
from annotell.input_api.model.abstract.abstract_models import Response
from datetime import datetime
from enum import Enum
from annotell.input_api.util import ts_to_dt


class InputStatus(str, Enum):
    Pending = "pending"
    Processing = "processing"
    Created = "created"
    Failed = "failed"
    InvalidatedBadContent = "invalidated:broken-input"
    InvalidatedSlamRerun = "invalidated:slam-rerun"
    InvalidatedDuplicate = "invalidated:duplicate"
    InvalidatedIncorrectlyCreated = "invalidated:incorrectly-created"


@dataclass
class Input(Response):
    uuid: str
    external_id: str
    batch: str
    input_type: str
    status: InputStatus
    created: datetime
    calibration_id: Optional[str]
    view_link: Optional[str]
    error_message: Optional[str]

    @staticmethod
    def from_json(js: dict):
        return Input(
            uuid=js["internalId"],
            external_id=js["externalId"],
            batch=js["batchId"],
            input_type=js["inputType"],
            status=js["status"],
            created=ts_to_dt(js["created"]),
            view_link=js.get("viewLink"),
            calibration_id=js.get("calibrationId"),
            error_message=js.get("errorMessage")
        )
