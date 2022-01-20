from pydantic import BaseModel
from typing import Optional


class OfflineRunEventData(BaseModel):
    gcs_source: str
    gcs_destination: str
    model_id: str
    model_type: str
    job_display_name: str
    request_id: str
    labels_source: Optional[str]
    webhooks: str
