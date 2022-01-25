from pydantic import BaseModel
from typing import Optional


class Granularity(BaseModel):
    name: str
    dimensionType: Optional[str]
