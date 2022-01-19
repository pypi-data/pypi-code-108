from pydantic import BaseModel, root_validator
from typing import Optional

# from utils import check_file_exists


class ModelMetaRequest(BaseModel):
    images_csv: str
    labels_manifest: Optional[str]

    class Config:
        arbitrary_types_allowed = True
