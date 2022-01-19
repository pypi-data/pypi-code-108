# generated by datamodel-codegen:
#   filename:  schema/api/services/createStorageService.json
#   timestamp: 2022-01-19T12:42:55+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, constr

from ...type import storage


class CreateStorageServiceEntityRequest(BaseModel):
    name: constr(min_length=1, max_length=128) = Field(
        ..., description='Name that identifies the this entity instance uniquely'
    )
    description: Optional[str] = Field(
        None, description='Description of Storage entity.'
    )
    serviceType: Optional[storage.StorageServiceType] = None
