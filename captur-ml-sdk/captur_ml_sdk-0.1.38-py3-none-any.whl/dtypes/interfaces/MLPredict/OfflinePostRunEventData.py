from pydantic import BaseModel
from typing import Optional


class OfflinePostRunEventData(BaseModel):
    gcs_destination: str
    model_id: str
    model_type: str
    request_id: str
    start_time: Optional[float] = .0
    end_time: Optional[float] = .0
    duration: Optional[float] = .0
    labels_source: Optional[str]
    webhooks: str
