from typing import Dict, Any, Optional

from pydantic import BaseModel


class Node(BaseModel):
    label: str
    primary_key: Optional[str]
    properties: Optional[Dict[str, Any]]
