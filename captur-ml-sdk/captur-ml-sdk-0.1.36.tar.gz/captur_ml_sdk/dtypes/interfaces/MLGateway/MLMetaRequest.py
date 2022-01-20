from pydantic import BaseModel
from typing import Optional


class ModelMetaRequest(BaseModel):
    images_csv: str
    labels_manifest: Optional[str]

    class Config:
        arbitrary_types_allowed = True
