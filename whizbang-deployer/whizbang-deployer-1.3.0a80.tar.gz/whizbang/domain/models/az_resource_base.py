from typing import Optional

from pydantic import BaseModel


class AzResourceBase(BaseModel):
    """[summary] Represents a Azure resource."""
    location: Optional[str]
    resource_group_name: Optional[str]
    resource_name: str


class AzResourceGroup(BaseModel):
    """[summary] Represents a Azure resource group."""
    resource_group_name: Optional[str]
    location: Optional[str]
