# generated by datamodel-codegen:
#   filename:  schema/entity/policies/lifecycle/deleteAction.json
#   timestamp: 2022-01-19T12:42:55+00:00

from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel, Extra, Field, conint


class LifecycleDeleteAction1(BaseModel):
    class Config:
        extra = Extra.forbid

    daysAfterCreation: Optional[conint(ge=1)] = Field(
        None,
        description='Number of days after creation of the entity that the deletion should be triggered.',
    )
    daysAfterModification: Optional[conint(ge=1)] = Field(
        None,
        description='Number of days after last modification of the entity that the deletion should be triggered.',
    )


class LifecycleDeleteAction(BaseModel):
    class Config:
        extra = Extra.forbid

    __root__: Union[LifecycleDeleteAction1, Any, Any] = Field(
        ...,
        description='An action to delete or expire the entity.',
        title='LifecycleDeleteAction',
    )
