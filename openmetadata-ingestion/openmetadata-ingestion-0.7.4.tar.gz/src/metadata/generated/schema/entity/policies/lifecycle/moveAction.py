# generated by datamodel-codegen:
#   filename:  schema/entity/policies/lifecycle/moveAction.json
#   timestamp: 2022-01-19T12:42:55+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra, Field, conint

from ....type import storage
from ...data import location
from ...services import storageService


class Destination(BaseModel):
    storageServiceType: Optional[storageService.StorageService] = Field(
        None, description='The storage service to move this entity to.'
    )
    storageClassType: Optional[storage.StorageClassType] = Field(
        None, description='The storage class to move this entity to.'
    )
    location: Optional[location.Location] = Field(
        None, description='The location where to move this entity to.'
    )


class LifecycleMoveAction(BaseModel):
    class Config:
        extra = Extra.forbid

    daysAfterCreation: Optional[conint(ge=1)] = Field(
        None,
        description='Number of days after creation of the entity that the move should be triggered.',
    )
    daysAfterModification: Optional[conint(ge=1)] = Field(
        None,
        description='Number of days after last modification of the entity that the move should be triggered.',
    )
    destination: Optional[Destination] = Field(
        None, description='Location where this entity needs to be moved to.'
    )
