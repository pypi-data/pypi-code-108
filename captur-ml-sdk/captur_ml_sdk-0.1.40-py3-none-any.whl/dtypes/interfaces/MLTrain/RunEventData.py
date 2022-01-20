from pydantic import BaseModel
from typing import Optional


class RunEventData(BaseModel):
    gcs_source: str
    model_name: str
    base_model_id: str
    training_display_name: str
    request_id: str
    webhooks: str
    budget_milli_node_hours: int
    percentage_images_included: Optional[float]
